from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    """Form for User Sign-In"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class SignUpForm(FlaskForm):
    """Form for User Sign-Up"""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class PostForm(FlaskForm):
    """Form for making a post"""

    title = TextAreaField('Title', validators=[DataRequired()])
    post = TextAreaField('Content', validators=[DataRequired()])