from Blablacar.celery import app
from .utils import Checker, get_message_text, get_message_data, send_mail
from .models import Task


@app.task
def check_new_trips():
    tasks = Task.objects.filter(notification=True)
    for task in tasks:
        checker = Checker(task)
        found_trip = checker.single_check()
        if found_trip:
            for trip in found_trip:
                message_text = get_message_text(trip)
                message_data = get_message_data(task, message_text)
                send_mail(**message_data)
