# This file contains all the routes and the code to process and render the associated web pages and post requests
from flask import Blueprint, current_app, render_template, abort, redirect, url_for, request
from werkzeug.utils import secure_filename
from models import *
from forms import *
from common import *
import os

frontend = Blueprint('frontend', __name__,
                     template_folder='templates')


# helper to determine if the file extension uploaded is usable
def is_file_extension_allowed(filename):
    extension = extract_file_extension(filename)
    return extension in current_app.config["ALLOWED_EXTENSIONS"]


# front page
@frontend.route('/')
def index():
    return render_template("index.html")


# form for uploading work. Rendered using WTForms
@frontend.route('/upload_work')
def upload_work():  # put application's code here
    return render_template("upload_work.html", form=UploadForm())


# list of work uploaded
@frontend.route('/work_list')
def work_list():
    work = Work.query.all()
    return render_template("work_list.html", work_list=work)


# results page, this is where the grade and feedback will be displayed
@frontend.route('/result/<int:test_id>')
def results_page(test_id):
    results_folder = current_app.config['RESULTS_FOLDER']
    # get the entry from the database
    work = Work.query.get(test_id)
    # if the submission has been processed read the result from the drive
    if work.processed:
        try:
            result = open(os.path.join(results_folder, str(work.id) + ".txt")).read()
        except FileNotFoundError:
            result = "Result could not be found"
    # otherwise
    else:
        result = None
    return render_template('results_page.html', work=work, result=result)


# this handles uploading files to be marked
# Normally WTForms would be used for validation here, but unfortunately this wouldn't work right for some reason.
# When using WTForms the form would be marked invalid regardless of if it was filled out correctly.
# Debugging the issue went nowhere fast, so it was more expedient to validate manually.
# If this issue could be fixed in the future it might be worthwhile to start using WTForms here
@frontend.route('/upload', methods=['POST'])
def upload_file():
    # get the folder to be uploaded into
    upload_folder = current_app.config['UPLOAD_FOLDER']
    form = UploadForm(request.form)
    # check the file is actually present in the HTML form
    if len(request.files) == 1:
        filename = secure_filename(request.files['file'].filename)
        # check the file extension is allowed
        if is_file_extension_allowed(filename):
            # create the work table entry
            work = Work()
            work.filename = filename
            work.title = form.title.data
            work.author = form.author.data
            work.status = "unmarked"
            work.processed = False
            # add the entry to the database
            db.session.add(work)
            db.session.commit()
            db.session.refresh(work)
            # save the file to the correct upload folder, prepending the ID of the submission to the start in order to
            # prevent overwriting other submissions of the same name
            request.files['file'].save(os.path.join(upload_folder, str(work.id) + "_" + filename))
            return render_template("successful_upload.html", id=work.id)
    return render_template("upload_form_validation_error.html")
