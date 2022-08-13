from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)


class SignUpForm(FlaskForm):
    username = StringField(label=('Username'), 
        validators=[DataRequired(), 
        Length(min=6,max=64)]) 
    email = StringField(label=('Email'), 
        validators=[DataRequired(), 
        Email(), 
        Length(max=120)])
    password = PasswordField(label=('Password'), 
        validators=[DataRequired(), 
        Length(min=8, message='Password should be at least %(min)d characters long')])
    confirm_password = PasswordField(
        label=('Confirm Password'), 
        validators=[DataRequired(message='*Required'),
        EqualTo('password', message='Both password fields must be equal!')])

    submit = SubmitField(label=('Submit'))
