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
from celery import Celery, Task
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



def make_celery(app: Flask) -> Celery:
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY_CONFIG"])

    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(run_worker = True):
    app = Flask(__name__)
    Bootstrap(app)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["CELERY_CONFIG"] = {"broker_url": "redis://redis", "result_backend": "redis://redis"}
    app.register_blueprint(frontend)
    celery = make_celery(app)
    celery.set_default()
    db.init_app(app)
    nav.init_app(app)
    # if run_worker:
    #     worker_instance = Worker(app)
    #     worker_instance.start()
    return app, celery

# class Worker(threading.Thread):
#     upload_folder = ""
#     def __init__(self, app):
#         super(Worker, self).__init__()
#         self.upload_folder = app.config['UPLOAD_FOLDER']
#         self.client = Client(host="http://ollama:11343")
#         self.app = app
#
#     def run(self):
#         with self.app.app_context():
#             while True:
#                 print("checkpoint")
#                 to_grade = Work.query.filter_by(processed=False).all()
#                 for result in to_grade:
#                     full_file_path = os.path.join(self.upload_folder, result.filename)
#                     if extract_file_extension(result.filename) == "txt":
#                         file = open(full_file_path, 'r')
#                         text = file.read(file)
#                     else:
#                         text = str(textract.process(full_file_path))
#                     response_text = self.client.generate(model=MODEL, prompt=(PROMPT + text))["response"]
#                     open(os.path.join(RESULTS_FOLDER, str(result.id) + ".txt"), "w").write(response_text)
#                     result.processed = True
#                     result.status = "Graded successfully"
#                 db.session.commit()
#                 if len(to_grade) == 0:
#                     sleep(1)