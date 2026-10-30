# accounts/emails.py

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Import gettext_lazy for lazy translation of strings
from django.utils.translation import gettext_lazy as _

# Email sending functions for various user account events, such as login success, account lock/unlock, and verification codes.
def send_html_email(
    *,
    subject: str,
    recipient: str,
    template_name: str,
    context: dict | None = None,
) -> None:
    """
    Render and send an HTML email with a plain-text fallback.
    """
    email_context = {
        "site_name": settings.SITE_NAME,
        **(context or {}),
    }

    html_content = render_to_string(
        template_name,
        email_context,
    )

    plain_text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )

    email.attach_alternative(
        html_content,
        "text/html",
    )

    email.send(fail_silently=False)

# Send an email when a user successfully logs in.
def send_login_success_email(*, user, ip_address: str, login_time) -> None:
    send_html_email(
        subject="Successful Login Notification",
        recipient=user.email,
        template_name="emails/login_success.html",
        context={
            "user": user,
            "ip_address": ip_address,
            "login_time": login_time,
            "site_name": settings.SITE_NAME,
        },
    )



# Send an email when a user's account is locked.
def send_account_locked_email(
    *,
    user,
    ip_address: str,
    attempted_at,
) -> None:
    lock_duration = int(settings.ACCOUNT_LOCK_DURATION.total_seconds() / 60)

    send_html_email(
        subject="Account Locked - Security Alert",
        recipient=user.email,
        template_name="emails/account_locked.html",
        context={
            "user": user,
            "ip_address": ip_address,
            "attempted_at": attempted_at,
            "lock_duration": lock_duration,
        },
    )

# Send an email when a user's account is unlocked.
def send_account_unlocked_email(*, user) -> None:
    send_html_email(
        subject="Your Account Has Been Unlocked",
        recipient=user.email,
        template_name="emails/account_unlocked.html",
        context={
            "user": user,
        },
    )
# Send an email with a verification code for new user registration.
def send_new_verification_code_email(recipient: str, code: str) -> None:
    send_mail(
        subject="Verify your email address",
        message=f"Your verification code is {code}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )

# Send an email with a verification code for password reset.
def send_password_reset_email(*, user, reset_url: str) -> None:
    send_html_email(
        subject="Reset your password",
        recipient=user.email,
        template_name="emails/password_reset.html",
        context={
            "user": user,
            "reset_url": reset_url,
        },
    )


def send_chat_retention_email(*, recipient: str, deleted_count: int, cutoff) -> None:
    send_html_email(
        subject="Chat Retention Cleanup Completed",
        recipient=recipient,
        template_name="emails/chat_retention.html",
        context={
            "deleted_count": deleted_count,
            "cutoff": cutoff,
        },
    )
