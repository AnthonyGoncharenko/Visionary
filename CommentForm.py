from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import (DataRequired, Length)

class CommentForm(FlaskForm):
    comment_content = StringField(label=('Content'), 
        validators=[DataRequired(), Length(max = 512)])
    submit = SubmitField(label=('Submit'))