from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Password hashing
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

app.config.from_object('config')
db = SQLAlchemy(app)

from app import views, models

# LoginManager parts
import os
from flask_login import LoginManager
from config import basedir


# Setup Flask-User
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from app.models import User
from app.forms import CustomRegister

db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
user_manager = UserManager(db_adapter, app,register_form=CustomRegister)     # Initialize Flask-User

from flask_mail import Mail
mail = Mail(app)

from flask_misaka import Misaka
Misaka(app,tables=True)