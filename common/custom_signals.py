import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger('ohmi_audit')


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info("User %s logged in at %s", user.username, timezone.now())
    # You can also log to a database:
    # LoginLog.objects.create(user=user, timestamp=timezone.now())
