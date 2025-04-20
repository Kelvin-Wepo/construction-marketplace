from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])
    attachment = FileField('Attachment', validators=[
        FileAllowed(['jpg', 'png', 'pdf', 'doc', 'docx'], 'Images and documents only!')
    ])
    job_id = SelectField('Related Job', coerce=int)
    submit = SubmitField('Send')
