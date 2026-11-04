from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class NoteForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    group_id = SelectField("Group", coerce=int, choices=[])
    content = TextAreaField("Content", validators=[Length(max=20000)])
    submit = SubmitField("Save note")
