from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    service_type = SelectField('Service Type', choices=[
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('carpentry', 'Carpentry'),
        ('painting', 'Painting'),
        ('roofing', 'Roofing'),
        ('masonry', 'Masonry'),
        ('landscaping', 'Landscaping'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    duration_days = IntegerField('Duration (days)', validators=[DataRequired(), NumberRange(min=1)])
    budget = FloatField('Budget ($)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Post Job')

class BidForm(FlaskForm):
    amount = FloatField('Bid Amount ($)', validators=[DataRequired(), NumberRange(min=1)])
    message = TextAreaField('Message to Client', validators=[DataRequired()])
    estimated_days = IntegerField('Estimated Days to Complete', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Submit Bid')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent')
    ], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')
