from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import (DataRequired, Length)

class AuthorForm(FlaskForm):
    author_name = StringField(
        label=("Find an Author's Profile"),
        validators=[DataRequired(), Length(max = 512)])
    submit = SubmitField(label=('Submit'))