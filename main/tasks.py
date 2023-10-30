from Blablacar.celery import app
from main.services import task_service


@app.task
def check_new_trips():
    """A Celery task for checking and processing new trips based on user tasks.

    This task triggers the `check_new_trips` function from the `task_service` module,
    which checks for new trips that match the criteria specified in user tasks and
    processes them accordingly.
    """
    task_service.check_new_trips()
