from wtforms.fields import StringField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField


class DocumentUploadForm(FlaskForm):
    """DocumentUploadForm Object meant to create the form for submitting Whole Slide Image Data

    The form has 2 fields which are the EmailField, and the MultipleFileField. 
        The EmailField will have the pathologist set their email, so that when the image classification is done,
            they will be notified by email.
        The MultipleFileField will have the pathologist choose which of the Whole Slide Image files that they want to
            upload to the ML model.
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    file = MultipleFileField('Images', validators=[FileAllowed(['tiff', 'svs', 'jpg', 'jpeg', 'png'], 'Whole Slide Image Data Only!')])
    # file = MultipleFileField('Images', validators=[
    #     FileRequired('DocumentUploadForm: File Required'), 
    #     FileAllowed(['tiff', 'svs', 'jpg', 'jpeg', 'png'], 'Whole Slide Image Data Only!')
    # ])
    submit = SubmitField('Submit Images')

