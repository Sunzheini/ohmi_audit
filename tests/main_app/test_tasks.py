from django.test import TestCase, override_settings

from ohmi_audit.main_app.tasks import long_running_task


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class CeleryTaskTests(TestCase):
    def test_long_running_task_eager(self):
        # In EAGER mode, delay executes synchronously and returns result immediately
        result = long_running_task.delay(duration=1)
        self.assertTrue(result.successful())
        self.assertIn('Completed', result.get())
