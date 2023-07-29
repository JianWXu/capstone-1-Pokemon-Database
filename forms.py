from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, EmailField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length
from wtforms.fields import Field
from flask_wtf.file import FileField, FileAllowed, FileRequired


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
    upload = FileField('Upload Photos', name="file", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])


class EditPost(FlaskForm):
    """Form for editting a post"""

    title = TextAreaField('Title', validators=[DataRequired()])
    content = TextAreaField('Your Post Content', validators=[DataRequired()])
    country = SelectField('Country', choices=[
                          ('CA', 'Canada'), ('USA', 'United States of America')])
    upload = FileField('Upload Photos', name="file", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])


class SearchPokemon(FlaskForm):
    """Search for a pokemon"""

    pokemon = StringField('', default='')

    # def __call__(self, field, **kwargs):
    #     return field.data if field.data else ""
