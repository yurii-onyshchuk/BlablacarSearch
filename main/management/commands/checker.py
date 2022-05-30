from django.core.management import BaseCommand
from main.utils import Checker


class Command(BaseCommand):
    help = 'Перевірка наявності необхідних поїздок'

    def handle(self, *args, **options):
        checker = Checker()
        checker.run_check_cycle()
