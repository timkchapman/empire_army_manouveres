from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length

class FortificationsForm(FlaskForm):
    fortification = SelectField('Select Force', validators=[DataRequired()])
    ritual = SelectField('Ritual', validators=[DataRequired()])
    fortification_is_besieged = BooleanField('Fort is Besieged?', validators=[DataRequired()])
    strength = StringField('Enter Strength', validators=[DataRequired(), Length(min=1, max=4)])