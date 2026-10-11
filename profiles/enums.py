# enums.py


from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountStatus(models.TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    LOCKED = "LOCKED", _("Temporarily locked")
    SUSPENDED = "SUSPENDED", _("Suspended")
