from django.conf import settings
from django.contrib.auth.decorators import user_passes_test



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
