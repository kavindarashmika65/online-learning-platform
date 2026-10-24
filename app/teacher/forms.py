from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    price = DecimalField('Price (LKR)', validators=[DataRequired()])
    submit = SubmitField('Create Course')

class LessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired(), Length(min=3, max=100)])
    video_url = StringField('YouTube Video URL')
    pdf_file = FileField('Upload PDF Note', validators=[FileAllowed(['pdf'], 'PDFs only!')])
    submit = SubmitField('Add Lesson')    
# පරණ කේතයන්ට යටින් මෙය එක් කරන්න
class BankDetailsForm(FlaskForm):
    bank_name = StringField('Bank Name', validators=[DataRequired(), Length(max=100)])
    branch = StringField('Branch', validators=[DataRequired(), Length(max=100)])
    account_name = StringField('Account Name', validators=[DataRequired(), Length(max=100)])
    account_number = StringField('Account Number', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Save Bank Details')    