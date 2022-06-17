from Blablacar.celery import app
from .utils import Checker


@app.task
def check_new_trips():
    Checker.check_new_trips()
