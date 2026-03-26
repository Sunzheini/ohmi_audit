import logging
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ohmi_audit.settings')

app = Celery('ohmi_audit')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

logger = logging.getLogger('ohmi_audit')


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    logger.debug("Celery debug_task request: %r", self.request)
