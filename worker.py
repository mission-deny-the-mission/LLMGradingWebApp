from common import extract_file_extension
from models import *
from app import db
from time import sleep
import ollama
import textract
import os
import threading

PROMPT = "Grade the following work from A to F giving feedback"
MODEL = "tinyllama"

class Worker(threading.Thread):
    upload_folder = ""
    def __init__(self, upload_folder):
        super(Worker, self).__init__()
        self.upload_folder = upload_folder
        print("checkpoint 1")

    def run(self):
        while True:
            print("checkpoint 2")
            to_grade = Work.query.filter_by(processed=True).all()
            for result in to_grade:
                full_file_path = os.path.join(upload_folder, result.file_name)
                if extract_file_extension(result.filename):
                    file = open(result.filename, 'r')
                    text = file.read(full_file_path)
                else:
                    text = textract.process(full_file_path)
                response = ollama.generate(model=MODEL, prompt=(PROMPT + text))
                result.grade = response
                result.processed = True
                result.status = "Graded successfully"
            db.session.commit()
            if len(to_grade) == 0:
                sleep(1)
