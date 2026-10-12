"""
Views for the profiles app.

The home view serves two roles:
  - GET  → render the chat page (Bootstrap UI + jQuery AJAX form)
  - POST → accept AJAX chat requests and return JSON { "answer": "..." }
"""

from django.contrib import auth
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from random import randint
from common.emails import (
    send_account_locked_email,
    send_account_unlocked_email,
    send_new_verification_code_email,
    send_password_reset_email,
)
from .profiles.enums import AccountStatus
from .profiles.forms import (
    ForgotPasswordForm,
    ResetPasswordForm,
    UserLoginForm,
    UserRegisterForm,
    VerifyCodeForm,
)
from .profiles.models import CustomUser, ResetLink

CustomUser = get_user_model()

# ============ AI engine for generating chat responses==========
from .profiles.ai_engine import generateChatResponse


# =================================================
# Decorator to restrict access to views for authenticated users.
# ================================================
def anonymous_required(function=None, redirect_url=None):
    """
    Decorator to restrict access to views for authenticated users.

    If the user is authenticated, they will be redirected to the specified
    redirect_url (default is settings.LOGIN_REDIRECT_URL).
    """
    if not redirect_url:
        redirect_url = settings.LOGIN_REDIRECT_URL

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


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
                    messages.error(
                        request,
                        "Your account is temporarily locked. "
                        "Please try again later.",
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
                # Checks for the last_login attribute before updating it to avoid potential errors with custom user models that may not have this field.
                    if hasattr(authenticated_user, "last_login"):
                        authenticated_user.last_login = timezone.now()
                        authenticated_user.save(
                            update_fields=["last_login"]
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


# =============================================
# ===============Register view for the chat application.
# =============================================

@anonymous_required
def register_view(request):
    if request.method == "GET":
        for key in ("email", "full_name", "password", "register_code", "code_tries"):
            request.session.pop(key, None)

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            full_name = form.cleaned_data["full_name"]
            request.session["email"] = email
            request.session["full_name"] = full_name
            request.session["password"] = form.cleaned_data["password1"]
            register_code = str(randint(100000, 999999))
            request.session["register_code"] = register_code
            request.session["resend_available_at"] = (
                int(timezone.now().timestamp())
                + settings.RESEND_CODE_COOLDOWN_SECONDS
            )
            try:
                send_new_verification_code_email(email, register_code)
            except Exception:
                messages.error(request, "We could not send your verification code.")
                return render(request, "profiles/register.html", {"form": form})
            messages.success(
                request,
                "Your verification code was sent. Check your email to continue.",
            )
            return redirect("profiles:code_verification")

    if request.method == "GET":
        form = UserRegisterForm()
    return render(request, "profiles/register.html", {"form": form})


@anonymous_required
def resend_code(request):
    email = request.session.get("email")

    if not email:
        messages.error(request, "Your registration session has expired. Please register again.")
        return redirect("profiles:register")

    now = int(timezone.now().timestamp())
    resend_available_at = request.session.get("resend_available_at", 0)
    if now < resend_available_at:
        messages.warning(request, "Please wait before requesting another code.")
        return redirect("profiles:code_verification")

    register_code = str(randint(100000, 999999))
    request.session["register_code"] = register_code
    request.session["code_tries"] = 0
    request.session["resend_available_at"] = (
        now + settings.RESEND_CODE_COOLDOWN_SECONDS
    )

    try:
        send_new_verification_code_email(email, register_code)
    except Exception:
        messages.error(request, "We could not send your verification code.")
    else:
        messages.success(request, "A new verification code was sent. Check your email.")

    return redirect("profiles:code_verification")


@anonymous_required
def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            user = (
                CustomUser.objects
                .filter(email__iexact=form.cleaned_data["email"], is_active=True)
                .first()
            )

            if user is not None:
                ResetLink.objects.filter(user=user, used_at__isnull=True).update(
                    used_at=timezone.now()
                )
                reset_link = ResetLink.objects.create(
                    user=user,
                    expires_at=(
                        timezone.now()
                        + timedelta(
                            seconds=settings.PASSWORD_RESET_LINK_TIMEOUT_SECONDS
                        )
                    ),
                )
                reset_url = request.build_absolute_uri(
                    reverse(
                        "profiles:reset_password",
                        kwargs={"unique_id": reset_link.uniqueId},
                    )
                )
                try:
                    send_password_reset_email(user=user, reset_url=reset_url)
                except Exception:
                    reset_link.delete()

            messages.success(
                request,
                "If an account exists for that email, a password reset link has been sent.",
            )
            return redirect("profiles:forgot_password")
    else:
        form = ForgotPasswordForm()

    return render(request, "profiles/forgot_password.html", {"form": form})


@anonymous_required
def reset_password(request, unique_id):
    try:
        reset_link = ResetLink.objects.select_related("user").get(
            uniqueId=unique_id
        )
    except ResetLink.DoesNotExist:
        raise Http404("This password reset link is invalid or expired.")

    if not reset_link.is_valid or not reset_link.user.is_active:
        raise Http404("This password reset link is invalid or expired.")

    if request.method == "POST":
        form = ResetPasswordForm(reset_link.user, request.POST)
        if form.is_valid():
            form.save()
            reset_link.used_at = timezone.now()
            reset_link.save(update_fields=["used_at"])
            messages.success(
                request,
                "Your password has been reset. You can now log in.",
            )
            return redirect("profiles:login")
    else:
        form = ResetPasswordForm(reset_link.user)

    return render(request, "profiles/reset_password.html", {"form": form})


@anonymous_required
def code_verification(request):
    if request.method == "POST":
        form = VerifyCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data["code"]
            expected_code = request.session.get("register_code")
            if expected_code and entered_code == expected_code:
                user = CustomUser.objects.create_user(
                    email=request.session["email"],
                    full_name=request.session["full_name"],
                    password=request.session["password"],
                )
                auth.login(request, user)
                for key in ("email", "full_name", "password", "register_code", "code_tries"):
                    request.session.pop(key, None)
                return redirect("profiles:home")

            request.session["code_tries"] = request.session.get("code_tries", 0) + 1
            if request.session["code_tries"] >= 5:
                for key in ("email", "full_name", "password", "register_code", "code_tries"):
                    request.session.pop(key, None)
                messages.error(request, "You have exceeded the maximum number of attempts. Please register again.")
                return redirect("profiles:register")
            messages.error(request, "Incorrect code. Please try again.")

    else:
        form = VerifyCodeForm()

    remaining = max(
        0,
        request.session.get("resend_available_at", 0)
        - int(timezone.now().timestamp()),
    )
    return render(
        request,
        "profiles/code_verification.html",
        {"form": form, "resend_cooldown_remaining": remaining},
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("profiles:login")


@login_required
def home(request):
    """
    Chat page and AJAX endpoint for chat requests.
    """
    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()

        # Guard against empty submissions before calling the LLM
        if not prompt:
            return JsonResponse({"answer": "Please enter a message."}, status=400)

        response = {}
        response["answer"] = generateChatResponse(prompt)
        return JsonResponse(response)

    # GET: render the chat interface
    context = {}
    return render(request, "profiles/index.html", context)
