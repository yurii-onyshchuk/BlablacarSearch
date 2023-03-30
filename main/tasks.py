from Blablacar.celery import app
from main.services import task_service


@app.task
def check_new_trips():
    task_service.check_new_trips()
