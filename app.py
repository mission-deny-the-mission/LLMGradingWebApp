from flask import Flask, flash, request, redirect, url_for, render_template
#from celery import Celery
from werkzeug.utils import secure_filename
from common import extract_file_extension
from forms import *
from models import *
from time import sleep
from flask_bootstrap import Bootstrap
from nav import nav
#from worker import Worker
import os
from ollama import Client
import textract
import os
import threading

PROMPT = "Grade the following work from A to F giving feedback:\n"
MODEL = "llama3"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
SECRET_KEY = os.urandom(32)
RESULTS_FOLDER = "results"


app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
nav.init_app(app)

class Worker(threading.Thread):
    upload_folder = ""
    def __init__(self, upload_folder):
        super(Worker, self).__init__()
        self.upload_folder = upload_folder
        self.client = Client(host="http://ollama:11343")

    def run(self):
        with app.app_context():
            while True:
                print("checkpoint")
                to_grade = Work.query.filter_by(processed=False).all()
                for result in to_grade:
                    full_file_path = os.path.join(self.upload_folder, result.filename)
                    if extract_file_extension(result.filename) == "txt":
                        file = open(full_file_path, 'r')
                        text = file.read(file)
                    else:
                        text = str(textract.process(full_file_path))
                    response_text = self.client.generate(model=MODEL, prompt=(PROMPT + text))["response"]
                    open(os.path.join(RESULTS_FOLDER, str(result.id) + ".txt"), "w").write(response_text)
                    result.processed = True
                    result.status = "Graded successfully"
                db.session.commit()
                if len(to_grade) == 0:
                    sleep(1)

def is_file_extension_allowed(filename):
    extension = extract_file_extension(filename)
    return extension in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload_work')
def upload_work():  # put application's code here
    return render_template("upload_work.html", form=UploadForm())


@app.route('/work_list')
def work_list():
    work = Work.query.all()
    return render_template("work_list.html", results_list=work)


@app.route('/result/<int:test_id>')
def results_page(test_id):
    work = Work.query.get(test_id)
    if work.processed:
        result = open(os.path.join(RESULTS_FOLDER, str(work.id) + ".txt")).read()
    else:
        result = None
    return render_template('results_page.html', work=work, result=result)


# @app.route('/upload', methods=['POST'])
# def upload_file():
#     form = UploadForm(request.form)
#     #   file = request.files['document']
#     if form.validate_on_submit() and form.file.data:
#         #       filename = secure_filename(form.document.name)
#         #       fileHandle = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "w")
#         #       fileHandle.write(form.document.data)
#         #       fileHandle.close()
#         #       filename = secure_filename(file.filename)
#         #       file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         filename = secure_filename(form.file.data.filename)
#         form.file.data.save(os.path.join('uploads', filename))
#         Work(filename, form.title.data, form.author.data, "", "", False)
#         db.session.add(Work)
#         db.session.commit()
#         return redirect(url_for('result', test_id=Work.id))
#     else:
#         return open("static/upload_form_validation_error.html").read()

@app.route('/upload', methods=['POST'])
def upload_file():
    form = UploadForm(request.form)
    #   file = request.files['document']
    if len(request.files) == 1:
        filename = secure_filename(request.files['file'].filename)
        request.files['file'].save(os.path.join('uploads', filename))
        work = Work()
        work.filename = filename
        work.title = form.title.data
        work.author = form.author.data
        work.status = "unmarked"
        work.processed = False
        db.session.add(work)
        db.session.commit()
        db.session.refresh(work)
        return render_template("successful_upload.html", id=work.id)
    else:
        return render_template("upload_form_validation_error.html")

@app.route('/successful_upload')
def successful_upload():
    pass


if __name__ == '__main__':
    worker_instance = Worker(app.config['UPLOAD_FOLDER'])
    worker_instance.start()
    app.run()
