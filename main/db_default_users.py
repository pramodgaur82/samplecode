# Add the first admin user (and associated dummy data)
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Password hashing
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

app.config.from_object('config')
db = SQLAlchemy(app)

from app import views, models

# LoginManager parts
import os
from flask.ext.login import LoginManager
from config import basedir


# Setup Flask-User
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from app.models import User, Role, Abstract

db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

from datetime import date
today = date.today()

if not User.query.filter(User.email=='romesh.abey@gmail.com').first():
    u = User(email='romesh.abey@gmail.com', affiliation='University of Oxford', first_name='Romesh',last_name='Abeysuriya',active=True,password=user_manager.hash_password('Asdf11'),confirmed_at=today,is_admin=True)
    u.roles.append(Role(name='admin'))
    db.session.add(u)
    db.session.commit()
