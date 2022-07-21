from Blablacar.celery import app
from main import utils


@app.task
def check_new_trips():
    utils.check_new_trips()
