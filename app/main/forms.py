from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

GROUP_COLORS = [
    ("#22d3ee", "Aqua"),
    ("#fb923c", "Peach"),
    ("#a78bfa", "Lilac"),
    ("#4ade80", "Green"),
    ("#f472b6", "Pink"),
]


class GroupForm(FlaskForm):
    name = StringField("Group name", validators=[DataRequired(), Length(max=60)])
    color = SelectField("Colour", choices=GROUP_COLORS, default="#22d3ee")
    submit = SubmitField("Save group")
