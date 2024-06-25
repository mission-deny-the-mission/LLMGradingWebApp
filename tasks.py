import os.path

from celery import shared_task
from celery.contrib.AbortableTask import AbortableTask
from ollama import Client

from models import Work, db
from common import extract_file_name

OLLAMA_HOST = "http://ollama:11343"
PROMPT = "Grade the following work from A to F giving feedback:\n"
MODEL = "llama3"

client = Client(host=OLLAMA_HOST)

@shared_task(bind=True, base=AbortableTask)
def process_work(self, work_id):
    work = Work.get_by_id(work_id)
    full_file_path = os.path.join(self.upload_folder, work.filename)
    if extract_file_extension(full_file_path) == "txt":
        file = open(full_file_path, "r")
        text = file.read()
    else:
        text = str(textract.process(full_file_path))
    response_text = client.generate(model=MODEL, prompt = (PROMPT + text))["response"]
    open(os.path.join(RESULTS_FOLDER, work_id), "w").write(response_text)
    work.processed = True
    work.status = "Graded successfully"
    db.session.commit()
