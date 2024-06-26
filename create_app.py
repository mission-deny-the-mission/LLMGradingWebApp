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
from dotenv import load_dotenv
import os

# set default values for various configuration options
PROMPT = "Grade the following work to an A level standard from A to F giving feedback:\n"
MODEL = "llama3"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'odf'}
SECRET_KEY = os.urandom(32)
RESULTS_FOLDER = "results"

SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"
OLLAMA_URL = "http://localhost:11434"

# if a .env file is present load it
load_dotenv()

# attempt to load configuration values from the environment
if "PROMPT" in os.environ:
    PROMPT = os.environ["PROMPT"]
if "MODEL" in os.environ:
    MODEL = os.environ["MODEL"]
if "UPLOAD_FOLDER" in os.environ:
    UPLOAD_FOLDER = os.environ["UPLOAD_FOLDER"]
if "RESULTS_FOLDER" in os.environ:
    RESULTS_FOLDER = os.environ["RESULTS_FOLDER"]
if "SQLALCHEMY_DATABASE_URI" in os.environ:
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
if "OLLAMA_URL" in os.environ:
    OLLAMA_URL = os.environ["OLLAMA_URL"]


# this function creates the app object
# it could be described as an app factory, though it's a function rather than a method
# this function also creates the worker thread that submits work to ollama
def create_app(run_worker=True):
    app = Flask(__name__)
    Bootstrap(app)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["OLLAMA_URL"] = OLLAMA_URL
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
