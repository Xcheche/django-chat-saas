"""
Database models for the profiles app.

CustomUser extends Django's built-in user so we can add profile fields later
(e.g. subscription tier, API usage limits) without migrating away from auth.
"""

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
from common.models import TimeStampedModel
from config import settings
from .enums import AccountStatus
from django.utils.translation import gettext_lazy as _
from .manager import CustomUserManager




# ============================================
# Custom User Model
# ============================================
class CustomUser(AbstractUser, TimeStampedModel):
    """
    Project-wide user model (see AUTH_USER_MODEL in settings).
    Uses email as the unique identifier for authentication instead of username.
    """

    username = None

    email = models.EmailField(
        _("Email Address"),
        unique=True,
        db_index=True,
    )

    full_name = models.CharField(
        _("Full Name"),
        max_length=150,
        blank=True,
        default="",
    )

    # Your account security fields
    account_status = models.CharField(
        _("Account Status"),
        max_length=10,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        db_index=True,
    )

    failed_login_attempts = models.PositiveSmallIntegerField(
        _("Failed Login Attempts"),
        default=0,
    )

    locked_until = models.DateTimeField(
        _("Locked Until"),
        null=True,
        blank=True,
    )

    lock_email_sent = models.BooleanField(
        _("Lock Email Sent"),
        default=False,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} - {self.full_name}"

    @property
    def is_temporarily_locked(self):
        return (
            self.account_status == AccountStatus.LOCKED
            and self.locked_until is not None
            and self.locked_until > timezone.now()
        )

    @property
    def has_expired_lock(self):
        return (
            self.account_status == AccountStatus.LOCKED
            and self.locked_until is not None
            and self.locked_until <= timezone.now()
        )

    def reset_login_security(self):
        self.account_status = AccountStatus.ACTIVE
        self.failed_login_attempts = 0
        self.locked_until = None
        self.lock_email_sent = False
        self.save(
            update_fields=[
                "account_status",
                "failed_login_attempts",
                "locked_until",
                "lock_email_sent",
            ]
        )

    class Meta:
        verbose_name = _("Custom User")
        verbose_name_plural = _("Custom Users")


# ============================================
# User Profile Model
# ============================================
class Profiles(TimeStampedModel):
    """
    User profile model.

    This model is linked to the CustomUser model via a one-to-one relationship.
    It can be used to store additional information about users, such as
    subscription tier, API usage limits, and other profile-related data.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    credits = models.IntegerField(_("Credits"), default=1000)
    # Date_created and uniqueId fields are inherited from TimeStampedModel

    def __str__(self):
        return f"{self.user.email} -{self.uniqueId}"

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    #   override the save method to set the date_created field when a new profile is created
    def save(self, *args, **kwargs):
        """
        Override the save method to set the date_created field when a new profile is created.
        """
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid.uuid4()).replace("-", "")
        super(Profiles, self).save(*args, **kwargs)


class ResetLink(TimeStampedModel):
    """
    Model to store password reset links for users.

    This model is linked to the CustomUser model via a foreign key relationship.
    It can be used to manage password reset requests and track their expiration.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    uniqueId = models.CharField(
        verbose_name=_("Reset Token"),
        max_length=100,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    expires_at = models.DateTimeField(verbose_name=_("Expires At"))
    used_at = models.DateTimeField(
        verbose_name=_("Used At"),
        null=True,
        blank=True,
    )

    @property
    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()

    def __str__(self):
        return f"Reset link for {self.user.email} - {self.uniqueId}"

    class Meta:
        verbose_name = _("Reset Link")
        verbose_name_plural = _("Reset Links")

    def save(self, *args, **kwargs):
        """
        Override the save method to set the date_created field when a new reset link is created.
        """
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        super(ResetLink, self).save(*args, **kwargs)
