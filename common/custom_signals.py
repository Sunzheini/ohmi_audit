from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print(f"User {user.username} logged in at {timezone.now()}")
    # You can also log to a database:
    # LoginLog.objects.create(user=user, timestamp=timezone.now())