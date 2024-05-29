import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
app = Celery("main")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.broker_connection_retry_on_startup = True

app.conf.beat_schedule = {
    'every-30-seconds': {
        'task': 'products.utils.testtest', 
        'schedule': 30.0, 
    },
}
