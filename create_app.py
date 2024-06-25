from flask import Flask, flash, request, redirect, url_for, render_template
#from celery import Celery
from werkzeug.utils import secure_filename
from common import extract_file_extension
from forms import *
from models import *
from time import sleep
from flask_bootstrap import Bootstrap
from nav import nav
from routes import frontend
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

def create_app(run_worker = True):
    app = Flask(__name__)
    Bootstrap(app)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["RESULTS_FOLDER"] = RESULTS_FOLDER
    app.config["PROMPT"] = PROMPT
    app.config["MODEL"] = MODEL
    app.register_blueprint(frontend)
    db.init_app(app)
    nav.init_app(app)
    if run_worker:
        worker_instance = Worker(app)
        worker_instance.start()
    return app

class Worker(threading.Thread):
    upload_folder = ""
    def __init__(self, app):
        super(Worker, self).__init__()
        self.upload_folder = app.config['UPLOAD_FOLDER']
        self.result_folder = app.config['RESULTS_FOLDER']
        self.prompt = app.config['PROMPT']
        self.model = app.config['MODEL']
        self.client = Client(host="http://ollama:11434")
        self.app = app

    def run(self):
        with self.app.app_context():
            while True:
                work_to_grade = Work.query.filter_by(processed=False).all()
                for work in work_to_grade:
                    full_file_path = os.path.join(self.upload_folder, str(work.id) + "_" + work.filename)
                    if extract_file_extension(work.filename) == "txt":
                        file = open(full_file_path, 'r')
                        text = file.read()
                    else:
                        text = str(textract.process(full_file_path))
                    response_text = self.client.generate(model=self.model, prompt=(self.prompt + text))["response"]
                    open(os.path.join(self.result_folder, str(work.id) + ".txt"), "w").write(response_text)
                    work.processed = True
                    work.status = "Graded successfully"
                db.session.commit()
                sleep(1)
