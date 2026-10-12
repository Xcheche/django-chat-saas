from django.contrib import messages
from django.shortcuts import redirect   
from django.utils import timezone
from random import randint
from django.conf import settings
from common.emails import send_new_verification_code_email
from .anonymous_required import anonymous_required


#=================================================
#============Resend Code View====================   
#=================================================
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
