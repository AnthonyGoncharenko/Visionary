from wtforms.fields import StringField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField


class DocumentUploadForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    file = MultipleFileField('Images', validators=[FileAllowed(['tiff', 'svs', 'jpg', 'jpeg', 'png'], 'Image files only.')])
    submit = SubmitField('Submit Images')

