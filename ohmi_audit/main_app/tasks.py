import time
from celery import shared_task


@shared_task(bind=True)
def long_running_task(self, duration=5):
    """A test task that simulates a long-running process"""
    for i in range(duration):
        time.sleep(1)
        self.update_state(state='PROGRESS', meta={'current': i, 'total': duration})
    return f"Completed {duration} second task"
