from math import ceil

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from ..enums import AccountStatus
from ..forms import UserLoginForm
from ..models import CustomUser
from .anonymous_required import anonymous_required
from common.emails import (
    send_account_locked_email,
    send_account_unlocked_email,
    send_login_success_email,
)






#=================================================
#============Login View==========================
#=================================================
@anonymous_required
def login_view(request):
    """
    Authenticate users and temporarily lock an account after
    repeated failed login attempts.
    """

    if request.user.is_authenticated:
        return redirect("profiles:home")

    def generic_error(attempts_remaining):
        return (
            "Invalid login details or account temporarily unavailable. "
            f"You have {attempts_remaining} attempt(s) remaining before "
            "your account is temporarily locked."
        )

    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            remember_me = form.cleaned_data["remember_me"]

            with transaction.atomic():
                user_record = (
                    CustomUser.objects
                    .select_for_update()
                    .filter(email__iexact=email)
                    .first()
                )

                # Do not reveal whether the email is registered.
                if user_record is None:
                    messages.error(
                        request,
                        generic_error(settings.MAX_LOGIN_ATTEMPTS),
                    )

                    return render(
                        request,
                        "profiles/login.html",
                        {"form": form},
                    )

                # Permanently disabled account.
                if not user_record.is_active:
                    messages.error(
                        request,
                        generic_error(settings.MAX_LOGIN_ATTEMPTS),
                    )

                    return render(
                        request,
                        "profiles/login.html",
                        {"form": form},
                    )

                # Administratively suspended account.
                if (
                    user_record.account_status
                    == AccountStatus.SUSPENDED
                ):
                    messages.error(
                        request,
                        "This account is currently suspended. "
                        "Please contact support.",
                    )

                    return render(
                        request,
                        "profiles/login.html",
                        {"form": form},
                    )

                # Temporary lock is still active.
                if user_record.is_temporarily_locked:
                    remaining_minutes = max(
                        1,
                        ceil(
                            (
                                user_record.locked_until
                                - timezone.now()
                            ).total_seconds()
                            / 60
                        ),
                    )
                    messages.error(
                        request,
                        "Your account is temporarily locked. "
                        f"Please try again in {remaining_minutes} minute(s).",
                    )

                    return render(
                        request,
                        "profiles/login.html",
                        {"form": form},
                    )

                # The temporary lock has expired.
                if user_record.has_expired_lock:
                    user_record.reset_login_security()

                    transaction.on_commit(
                        lambda user=user_record:
                        send_account_unlocked_email(user=user)
                    )

                # USERNAME_FIELD is email, so Django accepts
                # the email through the username argument.
                authenticated_user = authenticate(
                    request,
                    username=email,
                    password=password,
                )

                # Successful authentication.
                if authenticated_user is not None:
                    authenticated_user.reset_login_security()

                    login(request, authenticated_user)
                    if remember_me:
                        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                    else:
                        request.session.set_expiry(0)

                    # Check for last_login before updating custom user models.
                    if hasattr(authenticated_user, "last_login"):
                        authenticated_user.last_login = timezone.now()
                        authenticated_user.save(
                            update_fields=["last_login"]
                        )

                    # Send an email after a successful login.
                    send_login_success_email(
                        user=authenticated_user,
                        ip_address=request.client_ip,
                        login_time=timezone.localtime(),
                    )
                    messages.success(
                        request,
                        "You have logged in successfully.",
                    )
                    return redirect("profiles:home")

                # Authentication failed.
                user_record.failed_login_attempts += 1

                reached_limit = (
                    user_record.failed_login_attempts
                    >= settings.MAX_LOGIN_ATTEMPTS
                )

                if reached_limit:
                    user_record.account_status = AccountStatus.LOCKED

                    user_record.locked_until = (
                        timezone.now()
                        + settings.ACCOUNT_LOCK_DURATION
                    )

                    should_send_email = (
                        not user_record.lock_email_sent
                    )

                    user_record.lock_email_sent = True

                    user_record.save(
                        update_fields=[
                            "failed_login_attempts",
                            "account_status",
                            "locked_until",
                            "lock_email_sent",
                        ]
                    )

                    if should_send_email:
                        client_ip = request.client_ip

                        attempted_at = timezone.localtime()

                        transaction.on_commit(
                            lambda user=user_record,
                            ip=client_ip,
                            attempt_time=attempted_at:
                            send_account_locked_email(
                                user=user,
                                ip_address=ip,
                                attempted_at=attempt_time,
                            )
                        )

                    messages.error(
                        request,
                        "Your account has been temporarily locked "
                        "because of multiple failed login attempts.",
                    )

                else:
                    user_record.save(
                        update_fields=[
                            "failed_login_attempts",
                        ]
                    )

                    attempts_remaining = max(
                        0,
                        settings.MAX_LOGIN_ATTEMPTS
                        - user_record.failed_login_attempts,
                    )
                    messages.error(
                        request,
                        generic_error(attempts_remaining),
                    )

    else:
        form = UserLoginForm()

    return render(
        request,
        "profiles/login.html",
        {"form": form},
    )
