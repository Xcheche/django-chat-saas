"""Django admin configuration for users and user profiles."""

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from common.emails import send_html_email
from .enums import AccountStatus
from .models import CustomUser, Profiles, ChatRecord


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Manage email-authenticated users and their account security state."""

    list_display = (
        "email",
        "full_name",
        "account_status",
        "failed_login_attempts",
        "locked_until",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "account_status",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "email",
        "full_name",
    )

    ordering = ("-date_joined",)

    readonly_fields = (
        "failed_login_attempts",
        "locked_until",
        "lock_email_sent",
        "last_login",
        "date_joined",
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal Information"),
            {
                "fields": ("full_name",),
            },
        ),
        (
            _("Account Security"),
            {
                "fields": (
                    "account_status",
                    "failed_login_attempts",
                    "locked_until",
                    "lock_email_sent",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
        (
            _("Personal Information"),
            {
                "fields": (
                    "full_name",
                ),
            },
        ),
    )

    # These actions keep account status changes consistent and notify users.
    actions = (
        "suspend_accounts",
        "restore_accounts",
        "unlock_accounts",
    )

    @admin.action(
        description=_("Suspend selected accounts"),
    )
    def suspend_accounts(self, request, queryset):
        updated_count = 0

        for user in queryset:
            if user.account_status == AccountStatus.SUSPENDED:
                continue

            user.account_status = AccountStatus.SUSPENDED
            user.failed_login_attempts = 0
            user.locked_until = None
            user.lock_email_sent = False

            user.save(
                update_fields=[
                    "account_status",
                    "failed_login_attempts",
                    "locked_until",
                    "lock_email_sent",
                ]
            )

            send_html_email(
                subject="Your account has been suspended",
                recipient=user.email,
                template_name="emails/account_suspended.html",
                context={
                    "user": user,
                },
            )

            updated_count += 1

        self.message_user(
            request,
            _("%(count)d account(s) suspended.")
            % {
                "count": updated_count,
            },
            level=messages.SUCCESS,
        )

    @admin.action(
        description=_("Restore selected suspended accounts"),
    )
    def restore_accounts(self, request, queryset):
        updated_count = 0

        for user in queryset:
            if user.account_status != AccountStatus.SUSPENDED:
                continue

            user.account_status = AccountStatus.ACTIVE
            user.failed_login_attempts = 0
            user.locked_until = None
            user.lock_email_sent = False

            user.save(
                update_fields=[
                    "account_status",
                    "failed_login_attempts",
                    "locked_until",
                    "lock_email_sent",
                ]
            )

            send_html_email(
                subject="Your account has been restored",
                recipient=user.email,
                template_name="emails/account_restored.html",
                context={
                    "user": user,
                },
            )

            updated_count += 1

        self.message_user(
            request,
            _("%(count)d account(s) restored.")
            % {
                "count": updated_count,
            },
            level=messages.SUCCESS,
        )

    @admin.action(
        description=_("Unlock selected temporarily locked accounts"),
    )
    def unlock_accounts(self, request, queryset):
        updated_count = 0

        for user in queryset:
            if user.account_status != AccountStatus.LOCKED:
                continue

            user.reset_login_security()
            updated_count += 1

        self.message_user(
            request,
            _("%(count)d account(s) unlocked.")
            % {
                "count": updated_count,
            },
            level=messages.SUCCESS,
        )

@admin.register(Profiles)
class ProfileAdmin(admin.ModelAdmin):
    """Display profile records with searchable fields from the related user."""

    list_display = (
        "user",
        "user_email",
        "user_full_name",
        "credits",
    )

    search_fields = (
        "user__email",
        "user__full_name",
        "credits",
    )

    ordering = ("user__date_joined",)

    @admin.display(ordering="user__email", description="Email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(ordering="user__full_name", description="Full name")
    def user_full_name(self, obj):
        return obj.user.full_name
    


#======================================
# ChatRecord Admin
#======================================


class ChatRecordAdmin(admin.ModelAdmin):
    """Admin interface for managing chat records."""
    list_display = (
        "profiles",
        "prompt",
        "userGenerated",
        "date_created",
    )
    search_fields = (
        "profiles__user__email",
        "prompt",
    )
    ordering = ("-date_created",)
    # Security to prevent bad actor form accessing the admin panel and viewing other users' chat records
    def get_queryset(self, request):
        """Limit the queryset to only show chat records for the logged-in user's profile."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers can see all records
        return qs.filter(profiles__user=request.user)  # Regular users see only their own records

admin.site.register(ChatRecord, ChatRecordAdmin)    