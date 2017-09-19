# Transfer the database to the local machine and run this script to generate QR codes
# And then write them to QR codes
print 'Generating QR codes'
import shutil
import os
try:
    shutil.rmtree('qr_codes')
except:
    pass

os.mkdir('qr_codes')
import qrcode
from app.models import User
users = User.query.all();
for u in users:
    with open('qr_codes/%s.png' % (u.email),'w') as f:
        img = qrcode.make('http://meguk2017.com/game?u=%s' % (u.link))
        img.save(f)

import qrcode.image.svg
factory = qrcode.image.svg.SvgPathImage

img = qrcode.make('Some data here', image_factory=factory)
for u in users:
    with open('qr_codes/code_%d.svg' % (u.id),'w') as f:
        img = qrcode.make('http://meguk2017.com/game?u=%s' % (u.link),image_factory=factory)
        img.save(f)