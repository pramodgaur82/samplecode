# Transfer the database to the local machine and run this script to generate QR codes
# And then write them to QR codes

from joblib import Parallel, delayed
import shutil
import os
import codecs

import sys
sys.path.insert(0, '../main')

templatefile = 'meguk_badges-01.svg'
# qr_dir = '/Users/romesh/git_repos/meguk2017.com/main/qr_codes'


from app.models import User
users = User.query.filter(User.is_attending).order_by(User.last_name).all()

speakers = [86,237,238,94,104,147,241,82,95,210]

new = [172,293]
users = [u for u in users if u.id in new]
# for u in users:
#     print u.first_name,u.last_name

# import sys
# sys.exit()

# users = users[0:8]
# long_affiliations = [286,106,211,133,40,193,169,261,279,204,154,38,122,143,210,277,219,281,180,178,179,181,187,163,260,155,167,235,246,75]
# long_surname = [193,108,148,35,89,204,249,18,229,243,46,186,280,12,68,90,95,125,134,136,236,271,1,43,44,97,103,124,128,130]
# users = [u for u in users if u.id in long_surname]

def fixup(u):
    # By not writing back to the database, these changes are not persistent
    u.title = u.title.replace('.','').title().strip()
    if u.title.lower().startswith('prof') or u.title.lower().startswith('assist prof'):
        u.title = 'Prof'
    if u.title.lower() == 'phd' or u.title.lower() == 'reader' or u.title.lower() == 'md' or u.title.lower().startswith('md phd'):
        u.title = 'Dr'
    if u.title.lower().startswith('director') or u.title.lower().startswith('instrument')  or u.title.lower() == 'phd student' or u.title.lower() == 'msc':
        u.title = ''
    u.title = u.title.strip()
    if len(u.title) > 0:
        u.title = u.title + ' '

    # Fix institutions
    if u.affiliation.lower().startswith('mrc cognition and brain'):
        u.affiliation = 'MRC Cognition and Brain Sciences Unit'
    if u.affiliation.lower().startswith('national university of ireland'):
        u.affiliation = 'National University of Ireland'
    if u.affiliation.strip().lower() =='n/a' or u.affiliation.strip().lower() =='independent':
        u.affiliation = ''
    if u.affiliation.lower().startswith('phd student at shahid beheshti university'):
        u.affiliation = 'Shahid Beheshti University'

    return u


def write_blank(n):
    tempfile = 'temp_%d.svg' % (n)

    with codecs.open(tempfile,'w',"utf-8") as f:
        for line in open(templatefile,'rU'):
            # if 'QRCODE' in line:
            #     line = '<image overflow="visible" width="370" height="370" xlink:href="file://%s/code_%d.svg" transform="matrix(0.1761 0 0 0.1761 217.2749 3)" />' % (qr_dir,u.id)
            if 'id="WorkshopMark"' in line:
                line = '<g id="WorkshopMark" visibility="hidden">'
            if 'id="DinnerMark"' in line:
                line = '<g id="DinnerMark" visibility="hidden">'
            if 'id="BleedMark"' in line:
                line = '<g id="BleedMark" visibility="hidden">'
            if 'id="SpeakerMark"' in line:
                line = '<g id="SpeakerMark" visibility="hidden">'
            if 'FIRSTNAME' in line:
                line = line.replace('FIRSTNAME','')
            if 'LASTNAME' in line:
                line = line.replace('LASTNAME','')
            if 'INSTITUTIONNAME' in line:
                line = line.replace('INSTITUTIONNAME','')
            if 'EMAILADDRESS' in line:
                line = line.replace('EMAILADDRESS','')
            f.write(line.strip() + '\n')

    os.system('cairosvg %s > blank_%s.pdf' % (tempfile,n))
    os.remove(tempfile)
    return 'blank_%s.pdf' % (n)

def write_tag(u):
    tempfile = 'temp_%d.svg' % (u.id)
    u = fixup(u)

    with codecs.open(tempfile,'w',"utf-8") as f:
        for line in open(templatefile,'rU'):
            # if 'QRCODE' in line:
            #     line = '<image overflow="visible" width="370" height="370" xlink:href="file://%s/code_%d.svg" transform="matrix(0.1761 0 0 0.1761 217.2749 3)" />' % (qr_dir,u.id)
            if not u.intends_workshop and 'id="WorkshopMark"' in line:
                line = '<g id="WorkshopMark" visibility="hidden">'
            if not u.intends_dinner and 'id="DinnerMark"' in line:
                line = '<g id="DinnerMark" visibility="hidden">'
            if 'id="BleedMark"' in line:
                line = '<g id="BleedMark" visibility="hidden">'
            if 'id="SpeakerMark"' in line and u.id not in speakers:
                line = '<g id="SpeakerMark" visibility="hidden">'
            if 'FIRSTNAME' in line:
                line = line.replace('FIRSTNAME','%s%s' % (u.title,u.first_name.title()))
            if 'LASTNAME' in line:
                line = line.replace('LASTNAME','%s' % (u.last_name.upper()))
            if 'INSTITUTIONNAME' in line:
                line = line.replace('INSTITUTIONNAME','%s' % (u.affiliation))
                if len(u.affiliation) > 30 and len(u.affiliation) < 40:
                    line = line.replace('16.133','14')
                if len(u.affiliation) >= 40 and len(u.affiliation) < 48:
                    line = line.replace('16.133','12')
                elif len(u.affiliation) >= 48:
                    line = line.replace('16.133','11')

            if 'EMAILADDRESS' in line:
                line = line.replace('EMAILADDRESS','%s' % (u.email))
            f.write(line.strip() + '\n')

    os.system('cairosvg %s > final_%s.pdf' % (tempfile,u.id))
    os.remove(tempfile)
    return 'final_%s.pdf' % (u.id)

if __name__ == '__main__':
    fnames = Parallel(n_jobs=8)(delayed(write_tag)(u) for u in users)
    #fnames = fnames + Parallel(n_jobs=8)(delayed(write_blank)(u) for u in range(0,5))
    os.system('cairosvg meguk_badges-02.svg > back.pdf')

    fnames2 = [x + ' back.pdf' for x in fnames]

    os.system('"/System/Library/Automator/Combine PDF Pages.action/Contents/Resources/join.py" -o final.pdf %s' % (' '.join(fnames2)))
    os.system('rm %s' % (' '.join(fnames)))