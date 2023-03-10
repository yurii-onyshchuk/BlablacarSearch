from Blablacar.celery import app

from . import utils


@app.task
def check_new_trips():
    utils.check_new_trips()
