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

# Setup Flask-User
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from app.models import User, Role, Abstract

db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

from datetime import date
today = date.today()

import random

n_users = 50;
import names

from app import forms

for i in xrange(0,n_users):
	print i
	ns = [names.get_first_name(),names.get_last_name()]
	u = User(email='%s.%s@gmail.com' % (ns[0],ns[1]), affiliation=forms.unis[random.randint(1,len(forms.unis)-1)], first_name=ns[0],last_name=ns[1],active=True,password=user_manager.hash_password('a'),confirmed_at=today,is_admin=False)
	
	u.is_attending = bool(random.randint(0,1));
	u.intends_workshop = bool(random.randint(0,1));
	u.intends_poster = bool(random.randint(0,1));
	u.intends_talk = bool(random.randint(0,1));
	u.intends_dinner = bool(random.randint(0,1));
	u.dietary_requirements = forms.dietary_options[random.randint(0,len(forms.dietary_options)-1)]

	db.session.add(u)
	db.session.commit()

	if bool(random.randint(0,1)): # 50% chance they make an abstract
		a = Abstract(author_id = u.id,title="%s's abstract" % (u.first_name),category=forms.poster_categories[random.randint(1,3)])
		if bool(random.randint(0,1)): # 50% chance its a talk
			a.is_talk = True
			a.abstract = 'Asdf asdf'
		db.session.add(a)
	db.session.commit()
