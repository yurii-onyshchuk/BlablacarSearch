import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Blablacar.settings')
app = Celery('Blablacar')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'check-new-trips': {
        'task': 'main.tasks.check_new_trips',
        'schedule': crontab('*/2'),
    },
}
