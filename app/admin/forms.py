from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class AdminMessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=160)])
    submit = SubmitField('Send SMS')
