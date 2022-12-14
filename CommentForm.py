from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import (DataRequired, Length)

class CommentForm(FlaskForm):
    comment_content = TextAreaField(
        label=('Leave a Comment:'),
        validators=[DataRequired(), Length(max = 512)])
    submit = SubmitField(label=('Submit'))