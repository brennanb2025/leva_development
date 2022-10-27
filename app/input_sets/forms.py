from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
    PasswordField,
    DateField,
    IntegerField,
    SelectField
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    URL
)

from app.input_sets.models import Select

class LoginForm(FlaskForm): #these have csrf validators but I turned them off because I'm doing it manually
    email = StringField('Email')
    password = PasswordField('Password')
    submit = SubmitField('Sign In')
        
class RegistrationForm(FlaskForm):
    first_name = StringField('First')
    last_name = StringField('Last')
    email = StringField('Email')
    password = PasswordField('Password')
    password2 = PasswordField('Repeat Password')
    # Changed from "city" to "hometown" for the beta test
    city_name = StringField('Hometown')
    current_occupation = StringField('Current Occupation')
    # Changed from "Business" to "organization" for the beta test
    business = StringField('Organization')
    # Changed from "Division" to "Year" for the beta test, changed from free text to selector
    # division = StringField('Year')
    year_choices = [("Freshman", "Freshman"), ("Sophomore", "Sophomore"), ("Junior", "Junior"), ("Senior", "Senior")]
    division = SelectField("Year", choices=year_choices)
    submit = SubmitField('Register')

class EditPasswordForm(FlaskForm):
    password = PasswordField('Password')
    password2 = PasswordField('Repeat Password')
    submit = SubmitField('Change Password')

class EditFirstNameForm(FlaskForm):
    first_name = StringField('Change first name')
    submit = SubmitField('Change first name')

class EditCityForm(FlaskForm):
    city_name = StringField('Change city')
    submit = SubmitField('Change city')

class EditCurrentOccupationForm(FlaskForm):
    current_occupation = StringField('Change current occupation')
    submit = SubmitField('Change current occupation')

class EditLastNameForm(FlaskForm):
    last_name = StringField('Change last name')
    submit = SubmitField('Change last name')

class EditPersonalityForm(FlaskForm):
    personality_1 = StringField('Word/phrase 1')
    personality_2 = StringField('Word/phrase 2')
    personality_3 = StringField('Word/phrase 3')
    submit = SubmitField('Update personality traits')

class EditDivisionForm(FlaskForm):
    division = StringField('Change division')
    submit = SubmitField('Change division')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')