import uuid
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _

# =================================================
# This file contains the common models used across the project E,g Abstract classes.
# ================================================


class TimeStampedModel(models.Model):
    date_created = models.DateTimeField(
        verbose_name=_("Date Created"),
        help_text=_("The date and time when the object was created."),
        default=timezone.now,
        blank=True,
    )
    uniqueId = models.CharField(
        verbose_name=_("Unique ID"),
        help_text=_("A unique identifier for the object."),
        max_length=100,
        default=uuid.uuid4,
        blank=True,
        editable=False,
    )
    class Meta:
        abstract = True
