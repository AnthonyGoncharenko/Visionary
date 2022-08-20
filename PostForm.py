from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, TextAreaField
from wtforms.validators import (DataRequired, ValidationError)

def FileSizeLimit():
    def file_length_check(form, field):
        if len(field.data.read()) > 8388608:
            raise ValidationError("File size must be less than 8 MB")
    return file_length_check

class PostForm(FlaskForm):
    post_title = StringField(label=('Post Title'), 
        validators=[DataRequired()])
    post_image = FileField(label=('Post Image'), 
        validators=[DataRequired(), FileSizeLimit()])
    post_content = TextAreaField(label=('Post Content'), 
        validators=[DataRequired()])
    submit = SubmitField(label=('Submit'))