import time
from celery import shared_task

from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True)
def long_running_task(self, duration=5):
    """A test task that simulates a long-running process"""
    for i in range(duration):
        time.sleep(1)
        self.update_state(state='PROGRESS', meta={'current': i, 'total': duration})
    return f"Completed {duration} second task"


@shared_task
def send_email_task(subject, message, recipient):
    """Task to send emails asynchronously"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=False,
    )
    return f"Email sent to {recipient}"
