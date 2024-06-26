from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.fields.simple import TextAreaField, StringField
from wtforms.validators import DataRequired

# form used for uploading stuff
# this is a WTForm
class UploadForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    author = StringField('author', validators=[DataRequired()])
    file = FileField('document', validators=[FileRequired(), FileAllowed(['doc', 'docx', 'pdf', 'txt'])])