# sample signal
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Audit

logger = logging.getLogger('ohmi_audit')


@receiver(post_save, sender=Audit)
def my_model_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info("New Audit instance created: %s", instance)
    else:
        logger.info("Audit instance updated: %s", instance)
