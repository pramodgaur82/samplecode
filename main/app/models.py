from app import db
from flask_user import UserMixin

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    
    # User auth information
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User system information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    confirmed_at = db.Column(db.DateTime())
    is_admin = db.Column('is_admin', db.Boolean(), nullable=False, server_default='0')
    roles = db.relationship('Role', secondary='user_roles',backref=db.backref('users', lazy='dynamic'))

    # Personal information
    title = db.Column(db.String(255), nullable=False, server_default='')
    first_name = db.Column(db.String(255), nullable=False, server_default='')
    last_name = db.Column(db.String(255), nullable=False, server_default='')
    affiliation = db.Column(db.String(255), nullable=False, server_default='')
    temp_custom_affiliation = db.Column(db.String(255), nullable=True, server_default='')

    is_attending = db.Column('is_attending', db.Boolean(), nullable=False, server_default='0')
    intends_workshop = db.Column('intends_workshop', db.Boolean(), nullable=False, server_default='1')
    intends_poster = db.Column('intends_poster', db.Boolean(), nullable=False, server_default='0')
    intends_talk = db.Column('intends_talk', db.Boolean(), nullable=False, server_default='0')
    intends_dinner = db.Column('intends_dinner', db.Boolean(), nullable=False, server_default='0')
    dietary_requirements = db.Column(db.String(255), nullable=False, server_default='')

    team = db.Column('game_team', db.Integer())
    link = db.Column(db.String(255))

    def __repr__(self):
        return '<User %r>' % (self.email)

class Abstract(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(255))
    category = db.Column(db.String(255))
    abstract = db.Column(db.Text())
    is_talk = db.Column('is_talk', db.Boolean(), nullable=False, server_default='0')
    session_poster = db.Column(db.Integer, server_default='0') # Default session is 0 (rejected)
    session_talk = db.Column(db.Integer, server_default='0') # -1 if rejected, 0 if todo, 1 if accepted

    def __repr__(self):
        return '<Abstract %r>' % (self.title)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    source = db.Column(db.Integer, db.ForeignKey('user.id'))
    destination = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime())
   
    def __repr__(self):
        return '<Tag %r>' % (self.id)
        
### ---------------------
### FLASK-USER ROLE ORMS

# Define the Role data model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles data model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
