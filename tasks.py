from celery import shared_task
from celery.contrib.AbortableTask import AbortableTask

from extensions import db
from models import Work

@shared_task(bind=True, base=AbortableTask):
def process_work(self, work_id):
    work = Work.get_by_id(work_id)
