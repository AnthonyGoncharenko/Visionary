from wtforms.fields import StringField, MultipleFileField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms.widgets import TextArea


class PostUpload(FlaskForm):
    blog_title = StringField(label=('Blog Title'), 
        validators=[DataRequired()]) 
    blog = StringField(widget=TextArea())
    image_file = FileField('Image', validators=[FileAllowed(['tiff', 'svs', 'jpg', 'jpeg', 'png'], 'Image Data Only!')])
    submit = SubmitField(label=('Submit'))

