from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import (DataRequired, ValidationError)

class SignInForm(FlaskForm):
    username = StringField(label=('Username'), 
        validators=[DataRequired()]) 
    password = PasswordField(label=('Password'), 
        validators=[DataRequired()])
    submit = SubmitField(label=('Submit'))
