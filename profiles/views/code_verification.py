from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login
from django.db import IntegrityError
from ..forms import VerifyCodeForm
from ..models import CustomUser
from .anonymous_required import anonymous_required



#================================================
#============Code Verification View=============
#================================================
@anonymous_required
def code_verification(request):
    if request.method == "POST":
        form = VerifyCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data["code"]
            expected_code = request.session.get("register_code")
            if expected_code and entered_code == expected_code:
                email = request.session["email"]

                try:
                    user = CustomUser.objects.create_user(
                        email=email,
                        full_name=request.session["full_name"],
                        password=request.session["password"],
                    )
                except IntegrityError:
                    for key in (
                        "email",
                        "full_name",
                        "password",
                        "register_code",
                        "code_tries",
                    ):
                        request.session.pop(key, None)
                    messages.error(
                        request,
                        "This email is already registered. Please log in.",
                    )
                    return redirect("profiles:login")

                login(request, user)
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
