# Add a set of dummy users
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

names = ['Siobhan Seale', 'Marcel Seegmiller', 'Lita Alessi', 'Wiley Spight', 'Minerva Rettig', 'Iluminada Lipari', 'Moses Pidgeon', 'Tisa Dedeaux', 'Francisco Kurland', 'Tammara Sinner', 'Charles Strong', 'Zena Morfin', 'Marlin Finklea', 'Josefine Kilbane', 'Sina Hunter', 'Karren Dunkley', 'Shea Cutter', 'Eugenie Persinger', 'Velia Heaton']
for n in names:
	ns = n.split()
	u = User(email='%s.%s@gmail.com' % (ns[0],ns[1]), affiliation='University of Oxford', first_name=ns[0],last_name=ns[1],active=True,password=user_manager.hash_password('a'),confirmed_at=today,is_admin=False)
	db.session.add(u)
	db.session.commit()
