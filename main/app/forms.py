from flask_wtf import Form, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField, TextAreaField, HiddenField, RadioField, IntegerField
from wtforms.validators import DataRequired,EqualTo,Email,Required,Length,Optional
from wtforms.widgets import HiddenInput
from flask_user.forms import RegisterForm

from app.models import User, Abstract, Role, Tag
from sqlalchemy import and_,not_,desc
from flask import current_app as app

unis = ['','Aston University','Cardiff University','Ulster University','University College London','University of Birmingham ','University of Cambridge','University of Glasgow','University of Nottingham','University of Oxford','University of York','Other']
dietary_options = ['No special requirements','Vegetarian','Gluten free','Dairy free','Halal']
poster_categories = ['','Clinical','Cognitive','Methods']

class RequiredIfFieldEqualTo(Required):
    # a validator which makes a field optional if
    # another field has a desired value

    def __init__(self, other_field_name, value, *args, **kwargs):
        self.other_field_name = other_field_name
        self.value = value
        super(RequiredIfFieldEqualTo, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if other_field.data == self.value:
            super(RequiredIfFieldEqualTo, self).__call__(form, field)

class UserInfoForm(Form):
    # Personal information
    title = StringField('Title',validators=[Length(max=255)])
    first_name = StringField('First name',validators=[DataRequired(),Length(max=255)])
    last_name = StringField('Surname',validators=[DataRequired(),Length(max=255)])
    email = StringField('Email')
    affiliation = StringField('Affiliation',validators=[DataRequired(),Length(max=255)])

    intends_workshop = BooleanField('Attending educational workshop (22nd March)')
    intends_dinner = BooleanField('Attending conference dinner (23rd March)')
    dietary_requirements = SelectField('Dietary requirements',choices=[(x,x) for x in dietary_options],validators=[DataRequired()])

    intends_poster = BooleanField('Intention to submit poster')
    intends_talk = BooleanField('Intention to submit talk')

    submit = SubmitField('Save')

class AdminUserInfoForm(UserInfoForm):
    # Extra admin fields on top of the standard page shown to users
    is_attending = BooleanField('Is attending')
    is_active = BooleanField('Is active')
    is_admin = BooleanField('Is admin')
    new_password = StringField('Password (enter cleartext to set new password)')

    id = IntegerField('id',validators=[Optional()],widget=HiddenInput())
    delete = SubmitField('Delete user')
    activate = SubmitField('Activate user')

class EditAbstractForm(Form):
    id = IntegerField('id',validators=[Optional()],widget=HiddenInput())
    is_talk = BooleanField('I would also like to have this abstract considered for a short talk')
    title = StringField('Title',validators=[DataRequired(),Length(max=255)])
    category = SelectField('Category',choices=[(x,x) for x in poster_categories],default=1,validators=[Length(max=255),DataRequired()])
    abstract = TextAreaField('Abstract (1500 characters max)',validators=[RequiredIfFieldEqualTo('is_talk',True),Length(max=1500)])
    submit = SubmitField('Save')
    delete = SubmitField('Delete abstract')

class AdminAbstractForm(Form):
    id = IntegerField('id',validators=[Optional()],widget=HiddenInput())
    session_poster = RadioField('Poster review', choices=[(0,'Not reviewed'),(-1,'Reject poster'),(1,'Accept (Session 1)'),(2,'Accept (Session 2)')],coerce=int)
    session_talk = RadioField('Talk review', choices=[(0,'Not reviewed'),(-1,'Reject talk'),(1,'Accept talk')],coerce=int)
    return_to_talk = HiddenField('return_to_talk')
    submit = SubmitField('Save')
    delete = SubmitField('Delete abstract')
    
class CustomRegister(RegisterForm):
    title = StringField('Title',validators=[Length(max=255)])
    first_name = StringField('First name', validators=[Length(max=255),Required('First name is required')])
    last_name  = StringField('Last name',  validators=[Length(max=255),Required('Last name is required')])
    affiliation = SelectField('Affiliation',choices=[(x,x) for x in unis],validators=[DataRequired()])
    temp_custom_affiliation = StringField('Specify affiliation',validators=[RequiredIfFieldEqualTo('affiliation','Other'),Length(max=255)])

    intends_workshop = BooleanField('Attending educational workshop (22nd March)')
    intends_dinner = BooleanField('Attending conference dinner (23rd March)')
    dietary_requirements = SelectField('Dietary requirements',choices=[(x,x) for x in dietary_options],default=1,validators=[DataRequired()])

    intends_poster = BooleanField('I plan to submit a poster')
    intends_talk = BooleanField('I plan to submit a short talk')

    recaptcha = RecaptchaField()

    is_attending = BooleanField('is_attending',widget=HiddenInput())

    # At form creation, query the database and store the number of users to pass to the template engine
    def __init__(self,a=None):
        super(CustomRegister,self).__init__(a)
        u = User.query.all()
        self.n_users = len(u) # Get *all* users so that those who have signed up still count towards the hard limit
        self.n_dinner = [x.intends_dinner for x in u].count(True)

    	if self.n_users >= app.config['LIMIT_WAITLIST']:
    		self.is_attending.data = False

        if self.n_dinner >= app.config['LIMIT_DINNER']:
            del self.intends_dinner
            del self.dietary_requirements
