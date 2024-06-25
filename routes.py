from flask import Blueprint, current_app, render_template, abort, redirect, url_for, request
from werkzeug.utils import secure_filename
from models import *
from forms import *
import os

frontend = Blueprint('frontend', __name__,
                     template_folder='templates')

def is_file_extension_allowed(filename):
    extension = extract_file_extension(filename)
    return extension in ALLOWED_EXTENSIONS

@frontend.route('/')
def index():
    return render_template("index.html")


@frontend.route('/upload_work')
def upload_work():  # put application's code here
    return render_template("upload_work.html", form=UploadForm())


@frontend.route('/work_list')
def work_list():
    work = Work.query.all()
    return render_template("work_list.html", results_list=work)


@frontend.route('/result/<int:test_id>')
def results_page(test_id):
    results_folder = current_app.config['RESULTS_FOLDER']
    work = Work.query.get(test_id)
    if work.processed:
        result = open(os.path.join(results_folder, str(work.id) + ".txt")).read()
    else:
        result = None
    return render_template('results_page.html', work=work, result=result)

@frontend.route('/upload', methods=['POST'])
def upload_file():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    form = UploadForm(request.form)
    #   file = request.files['document']
    if len(request.files) == 1:
        filename = secure_filename(request.files['file'].filename)
        work = Work()
        work.filename = filename
        work.title = form.title.data
        work.author = form.author.data
        work.status = "unmarked"
        work.processed = False
        db.session.add(work)
        db.session.commit()
        db.session.refresh(work)
        request.files['file'].save(os.path.join(upload_folder, str(work.id) + "_" + filename))
        return render_template("successful_upload.html", id=work.id)
    else:
        return render_template("upload_form_validation_error.html")