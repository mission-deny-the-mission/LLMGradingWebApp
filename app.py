from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from common import extract_file_extension
from forms import *
from models import *
from worker import Worker
import os

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

def is_file_extension_allowed(filename):
    extension = extract_file_extension(filename)
    return extension in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return open('static/index.html').read()

@app.route('/upload_work')
def upload_work():  # put application's code here
    return render_template("upload_work.html", form=UploadForm())

@app.route('/results_list')
def results_list():
    work = Work.query.all()
    return render_template("results_list.html", results_list=work)

@app.route('/result/<int:test_id>')
def result(test_id):
    work = Work.query.get(test_id)
    return render_template('result.html', work=work)

@app.route('/upload', methods=['POST'])
def upload_file():
    form = UploadForm(request.form)
    if form.validate() and form.document.data:
        filename = secure_filename(form.document.name)
        fileHandle = open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        fileHandle.write(form.document.data)
        fileHandle.close()
        Work(filename, form.title.data, form.author.data, "", "", False)
        db.session.add(Work)
        db.session.commit()
        return redirect(url_for('result', test_id=Work.id))
    else:
        return open("static/upload_form_validation_error.html").read()

@app.route('/successful_upload')
def successful_upload():
    pass

if __name__ == '__main__':
    worker_instance = Worker(app.config['UPLOAD_FOLDER'])
    worker_instance.start()
    app.run()
