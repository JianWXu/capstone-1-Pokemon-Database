from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, EmailField, SelectField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    """Form for User Sign-In"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class SignUpForm(FlaskForm):
    """Form for User Sign-Up"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('Email', validators=[DataRequired()])
    country = StringField('Country')


class PostForm(FlaskForm):
    """Form for making a post"""

    title = TextAreaField('Title', validators=[DataRequired()])
    content = TextAreaField('Your Post Content', validators=[DataRequired()])
    country = SelectField('Country', choices=[
                          ('CA', 'Canada'), ('USA', 'United States of America')])


class EditPost(FlaskForm):
    """Form for editting a post"""

    title = TextAreaField('Title', validators=[DataRequired()])
    content = TextAreaField('Your Post Content', validators=[DataRequired()])
    country = SelectField('Country', choices=[
                          ('CA', 'Canada'), ('USA', 'United States of America')])