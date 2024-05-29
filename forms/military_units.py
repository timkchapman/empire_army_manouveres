from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

class MilitaryUnitsForm(FlaskForm):
    military_units = StringField('Military Units', validators=[DataRequired()])
    supported_force = SelectField('Supported Army', validators=[DataRequired()])