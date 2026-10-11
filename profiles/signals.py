from django.db.models.signals import post_save
from django.dispatch import receiver

from config import settings
from .models import Profiles
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


# =================================================
# This file contains the signals for the profiles app. It defines signal handlers that are triggered when certain events occur in the app, such as when a new user is created or when a user's profile is updated.
# ================================================
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profiles.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    instance.profiles.save()
