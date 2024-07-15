import time

from django.core.management import BaseCommand

from main.services.task_service import check_new_trips


class Command(BaseCommand):
    """Management command to periodically check for new trips.

    This management command checks for new trips at regular intervals and performs the necessary actions.

    Usage:
        python manage.py check_trips
    """

    help = 'Перевірка наявності необхідних поїздок'

    def handle(self, *args, **options):
        """Handle the command execution.

        This method is called when the management command is executed. It calls the check_new_trips function
        and sleeps for 120 seconds before checking again. It continues to run indefinitely to periodically check for
        new trips.
        """
        while True:
            check_new_trips()
            time.sleep(120)
