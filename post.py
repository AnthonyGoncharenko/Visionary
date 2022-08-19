from flask_wtf import FlaskForm, ValidationError
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import (DataRequired, ValidationError)

class post(FlaskForm):
    post_title = StringField(label=('Post Title'), 
        validators=[DataRequired()])
    post_image = FileField(label=('Post Image'), 
        validators=[DataRequired(), FileSizeLimit()])
    post_content = StringField(label=('Post Content'), 
        validators=[DataRequired()])
    submit = SubmitField(label=('Submit'))

def FileSizeLimit():
    def file_length_check(form, field):
        if len(field.data.read()) > 8388608:
            raise ValidationError("File size must be less than 8 MB")
    return file_length_check