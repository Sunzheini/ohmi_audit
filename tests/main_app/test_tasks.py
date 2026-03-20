import pytest
from django.test import override_settings

from ohmi_audit.main_app.tasks import long_running_task


@pytest.mark.django_db
class TestCeleryTasks:
    def test_long_running_task_eager(self, settings):
        # Configure Celery to run in EAGER mode for testing
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.CELERY_TASK_EAGER_PROPAGATES = True
        
        # In EAGER mode, delay executes synchronously and returns result immediately
        result = long_running_task.delay(duration=1)
        assert result.successful()
        assert 'Completed' in result.get()
