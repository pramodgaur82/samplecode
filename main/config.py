WTF_CSRF_ENABLED = True
SECRET_KEY = '<MEGUK2018 - a random string here>'

# Database commands
import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

BCRYPT_LOG_ROUNDS = 12 # Number of password hasing rounds, larger is more secure but slower


CSRF_ENABLED = True

# Flask-Mail settings
USER_ENABLE_USERNAME           = False      # Register and Login with username
USER_ENABLE_CHANGE_USERNAME	 = False
USER_APP_NAME        = "MEGUK2017"                # Used by email templates

USER_AFTER_LOGIN_ENDPOINT    = 'manage_registration'   
USER_AFTER_CONFIRM_ENDPOINT  = 'manage_registration'              # v0.5.3 and up
USER_AFTER_REGISTER_ENDPOINT = 'after_register'

MAIL_USERNAME =           None
MAIL_PASSWORD =           None
MAIL_DEFAULT_SENDER =     '"Registration" <noreply@meguk2017.com>'
MAIL_SERVER = 'localhost'
MAIL_PORT = 25

## FOR TESTING
USER_ENABLE_LOGIN_WITHOUT_CONFIRM = False
#USER_ENABLE_CONFIRM_EMAIL      = False

## RECAPTCHA
RECAPTCHA_PUBLIC_KEY = '<MEGUK2018 - enter your keys here>'
RECAPTCHA_PRIVATE_KEY= '<MEGUK2018 - enter your keys here>'
# RECAPTCHA_API_SERVER	optional Specify your Recaptcha API server.
# RECAPTCHA_PARAMETERS = {'hl': 'zh', 'render': 'explicit'}
# RECAPTCHA_DATA_ATTRS = {'theme': 'dark'}


CONFERENCE_ABSTRACT_SUBMISSION_OPEN = False # If False, abstract tools will be disabled
CONFERENCE_REGISTRATION_OPEN = True # If False, users cannot register
CONFERENCE_EDIT_SELF_OPEN = True # If False, users cannot edit their details

LIMIT_DINNER = 200
LIMIT_WAITLIST = 250
