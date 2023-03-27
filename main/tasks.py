from Blablacar.celery import app
from main.services.task_service import check_new_trips


@app.task
def check_new_trips():
    check_new_trips()
