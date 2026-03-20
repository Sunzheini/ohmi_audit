# sample signal
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Audit


@receiver(post_save, sender=Audit)
def my_model_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"New MyModel instance created: {instance}")
    else:
        print(f"MyModel instance updated: {instance}")
