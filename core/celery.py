import os
from celery import Celery
import bugsnag
from bugsnag.celery import connect_failure_handler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {

 'test_task_starter': {
           'task': 'scraper.tasks.get_facebook_data',
           'schedule': 10.0,
       },
}
app.conf.broker_url = 'amqp://guest:guest@localhost:5672/'
BUGSNAG = {
    "api_key": "f145d9647c155d83f6746e4273bf4ed2",
    "endpoint": os.environ.get('BUGSNAG_API', 'https://notify.bugsnag.com'),
    "asynchronous": False,
}
bugsnag.configure(**BUGSNAG)

connect_failure_handler()
