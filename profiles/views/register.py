
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from random import randint

from ..enums import AccountStatus
from ..forms import UserRegisterForm
from ..models import CustomUser
from .anonymous_required import anonymous_required
from common.emails import send_new_verification_code_email


#================================================
#============Register View=======================
#================================================
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

