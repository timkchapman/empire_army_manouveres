from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length

class ForcesForm(FlaskForm):
    force = SelectField('Select Force', validators=[DataRequired()])
    quality = StringField('Force Quality', validators=[DataRequired()])
    order = SelectField('Order', validators=[DataRequired()])
    ritual = SelectField('Ritual', validators=[DataRequired()])
    strength = StringField('Enter Strength', validators=[DataRequired(), Length(min=1, max=4)])