from django.core.management import BaseCommand
from main.utils import Checker
import time


class Command(BaseCommand):
    """Just to start checking on Windows without Celery"""

    help = 'Перевірка наявності необхідних поїздок'

    def handle(self, *args, **options):
        while True:
            Checker.check_new_trips()
            time.sleep(120)
