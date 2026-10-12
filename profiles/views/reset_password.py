from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from ..forms import ResetPasswordForm
from ..models import ResetLink
from .anonymous_required import anonymous_required




#=================================================
#============Reset Password View=================
#=================================================
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

