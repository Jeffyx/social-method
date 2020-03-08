from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, ValidationError, TextField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from werkzeug.utils import secure_filename
from app import User

class ContactForm(FlaskForm):
  file_ = FileField(validators=[FileRequired()])
  name = TextField("Name",  validators=[DataRequired()])
  email = TextField("Email",  validators=[DataRequired(), Email()])
  subject = TextField("Subject",  validators=[DataRequired()])
  message = TextAreaField("Message",  validators=[DataRequired()])
  submit = SubmitField("Send")
  
  
class LoginForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember_me = BooleanField('Remember Me')
  submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  password2 = PasswordField(
      'Repeat Password', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Register')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
      raise ValidationError('Please use a different username.')

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user is not None:
      raise ValidationError('Please use a different email address.')