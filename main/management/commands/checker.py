from django.core.management import BaseCommand
from main.utils import check_new_trips
import time


class Command(BaseCommand):
    """Just to start checking on Windows without Celery"""

    help = 'Перевірка наявності необхідних поїздок'

    def handle(self, *args, **options):
        while True:
            check_new_trips()
            time.sleep(120)
