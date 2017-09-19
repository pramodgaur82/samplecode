# Some examples of database manipulation

from app import db, models
u = models.User(firstname='asdf', surname='fadasa', email='asdf@email.com')
u = models.User(firstname='asdf2', surname='fadasa2', email='asdf@email.com')
db.session.add(u)
db.session.commit()

u = models.User.query.get(1)
p = models.Poster(title='poster title', abstract='my abstract', author=u)
db.session.add(p)
db.session.commit()

# Print all users
print models.User.query.all()

# get all posts from a user
u = models.User.query.get(1)
print u.posters.all() # All posters

# Clear the database
users = models.User.query.all()
for u in users:
    db.session.delete(u)

posters = models.Poster.query.all()
for p in posters:
    db.session.delete(p)

db.session.commit()


