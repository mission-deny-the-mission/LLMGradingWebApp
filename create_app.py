from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from common import extract_file_extension
from forms import *
from models import *
from time import sleep
from flask_bootstrap import Bootstrap
from nav import nav
from routes import frontend
from worker import Worker
import os

PROMPT = "Grade the following work from A to F giving feedback:\n"
MODEL = "llama3"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'odf'}
SECRET_KEY = os.urandom(32)
RESULTS_FOLDER = "results"

# this function creates the app object
# it could be described as an app factory, though it's a function rather than a method
# this function also creates the worker thread that submits work to ollama
def create_app(run_worker = True):
    app = Flask(__name__)
    Bootstrap(app)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["RESULTS_FOLDER"] = RESULTS_FOLDER
    app.config["PROMPT"] = PROMPT
    app.config["MODEL"] = MODEL
    app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS
    app.register_blueprint(frontend)
    db.init_app(app)
    nav.init_app(app)
    if run_worker:
        worker_instance = Worker(app)
        worker_instance.start()
    return app
