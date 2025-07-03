from django.apps import AppConfig


class MainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ohmi_audit.main_app'

    def ready(self):
        # Import signals to ensure they are registered when the app is ready
        import common.custom_signals
