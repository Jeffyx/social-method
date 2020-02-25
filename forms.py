from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, ValidationError, TextField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, Email
from werkzeug.utils import secure_filename

class ContactForm(FlaskForm):
  file_ = FileField(validators=[FileRequired()])
  name = TextField("Name",  validators=[DataRequired()])
  email = TextField("Email",  validators=[DataRequired(), Email()])
  subject = TextField("Subject",  validators=[DataRequired()])
  message = TextAreaField("Message",  validators=[DataRequired()])
  submit = SubmitField("Send")
  
  