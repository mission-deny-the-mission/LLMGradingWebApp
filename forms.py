from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms.fields.simple import TextAreaField, StringField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    author = StringField('author', validators=[DataRequired()])
    document = FileField('document', validators=[FileAllowed(['doc', 'docx', 'pdf', 'txt'])])