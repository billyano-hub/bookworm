from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired,FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import Email, DataRequired,EqualTo,Length

class RegForm(FlaskForm):
    fullname = StringField("First Name",validators=[DataRequired("First Name cannot be empty")])
    email = StringField("Email Address",validators=[Email(message="enter correct email format"),DataRequired("Please enter email")])
    pwd = PasswordField("Enter Password",validators=[DataRequired()])
    confpwd = PasswordField("Confirm Password",validators=[EqualTo('pwd', message=("password must be the same"))])
    message = TextAreaField("Your Profile")
    btnsubmit = SubmitField("Register!")

class DpForm(FlaskForm):
    dp= FileField("Upload a Profile Picture",validators=[FileRequired(),FileAllowed(['jpg', 'png','jpeg'])])
    btnupload=SubmitField("Upload Picture")

class ProfileForm(FlaskForm):
    fullname = StringField("First Name",validators=[DataRequired("First Name cannot be empty")])
    btnsubmit=SubmitField("Update Profile")

class ContactForm(FlaskForm):
    email = StringField("Email Address",validators=[DataRequired()])
    btnsubmit=SubmitField("Contact Us!")

class DonationForm(FlaskForm):
    fullname = StringField("Full Name",validators=[DataRequired("First Name cannot be empty"),DataRequired("Please enter email")])
    email = StringField("Email Address",validators=[DataRequired('Enter your correct email')])
    amt=StringField('specify amount',validators=[DataRequired('Amount cannot be empty')])
    btnsubmit=SubmitField("Donate")
