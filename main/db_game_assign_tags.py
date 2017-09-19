# Run this script on the server to add the tags to the database

import random
random.seed(1)
import hashlib
from sqlalchemy import and_,not_,desc
from app import db, models
from app.models import User

# Add the email hashes (for scan links) to the database
users = User.query.all()
for u in users:
    u.link = hashlib.sha1(u.email).hexdigest()[1:12]
    db.session.add(u)
db.session.commit()

# Only operate on users who are definitely coming to the conference
u = User.query.filter(and_(User.confirmed_at,User.is_attending)).all()

# Assign these users to teams
pool = set(users) 
slen = len(pool) / 3 # we need 3 subsets
set1 = set(random.sample(pool, slen)) # 1st random subset
pool -= set1
set2 = set(random.sample(pool, slen)) # 2nd random subset
pool -= set2
set3 = pool # 3rd random subset
for u in set1:
    u.team = 0
    db.session.add(u)
    db.session.commit()
for u in set2:
    u.team = 1
    db.session.add(u)
    db.session.commit()
for u in set3:
    u.team = 2
    db.session.add(u)
    db.session.commit()

# Clear all tags
tags = models.Tag.query.all()
for t in tags:
    db.session.delete(t)
db.session.commit()

# Make new tags
for u in users:
    u2 = [x for x in users if x.id != u.id and x.team != u.team] # List of users excluding the tagging user and same team
    targets = random.sample(u2,3)
    for target in targets:
        t = models.Tag(source=u.id,destination=target.id)
        db.session.add(t)
        db.session.commit()
