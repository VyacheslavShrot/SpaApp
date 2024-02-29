import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery("spa")
app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)
app.conf.result_backend = 'redis://redis'

app.autodiscover_tasks()
