from ollama import Client
from models import *
from time import sleep
from common import *
import textract
import threading
import os

# This class does the actual work of marking submissions with ollama
# Note: there are probably better ways of doing this, hence the extra git branch with Celery.
# Unfortunately Celery won't actually import properly because of a dependency issue, so this is the best way to
# implement this until a workaround or alternative can be found. It also reduces the number of support services
# required as celery requires the redis in-memory database
class Worker(threading.Thread):
    upload_folder = ""
    def __init__(self, app):
        super(Worker, self).__init__()
        self.upload_folder = app.config['UPLOAD_FOLDER']
        self.result_folder = app.config['RESULTS_FOLDER']
        self.prompt = app.config['PROMPT']
        self.model = app.config['MODEL']
        self.client = Client(app.config['OLLAMA_URL'])
        print("using url: ", app.config['OLLAMA_URL'])
        self.app = app

    def run(self):
        with self.app.app_context():
            # The idea here is to run indefinitely continually looking for unprocessed entries in the database
            # this is achieved with a while True loop
            while True:
                # fetch all unprocessed submissions using SQLAlchemy
                work_to_grade = Work.query.filter_by(processed=False).all()
                # iterate through each unprocessed entry
                for work in work_to_grade:
                    # calculate the full fill path
                    # the id of the submission is prepended to the front of the submission filename during upload
                    # to prevent overwriting any submissions with the same name
                    full_file_path = os.path.join(self.upload_folder, str(work.id) + "_" + work.filename)
                    # if the file in question is a txt then extracting it is unnecessary
                    if extract_file_extension(work.filename) == "txt":
                        file = open(full_file_path, 'r')
                        text = file.read()
                    else:
                        # extract text from documents using textract
                        text = str(textract.process(full_file_path))
                    try:
                        # get a response from an LLM using ollama
                        response_text = self.client.generate(model=self.model, prompt=(self.prompt + text))["response"]
                        # save the response to a file
                        open(os.path.join(self.result_folder, str(work.id) + ".txt"), "w").write(response_text)
                    except Exception as e:
                        print(e)
                        # if an error occurred note this in the status field of the database
                        work.processed = True
                        work.status = "Error encountered while processing submission: "
                    else:
                        # update the database entry to reflect that the submission has been processed
                        work.processed = True
                        work.status = "Graded successfully"
                db.session.commit()
                sleep(1)