"""
Database models for the profiles app.

CustomUser extends Django's built-in user so we can add profile fields later
(e.g. subscription tier, API usage limits) without migrating away from auth.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Project-wide user model (see AUTH_USER_MODEL in settings).

    Currently identical to AbstractUser; placeholder for future SaaS fields.
    """

    pass
