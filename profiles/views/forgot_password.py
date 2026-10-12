
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from ..forms import ForgotPasswordForm
from ..models import CustomUser, ResetLink
from .anonymous_required import anonymous_required
from common.emails import send_password_reset_email

#=================================================
#============Forgot Password View==========================
#=================================================
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
