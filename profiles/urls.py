"""
URL routing for the profiles app.

All chat traffic goes through the home view at the site root ("/").
"""

from django.urls import path

from . import views

# Namespace allows {% url 'profiles:home' %} in templates
app_name = "profiles"

urlpatterns = [
    # Single endpoint: GET renders chat UI, POST handles AJAX messages
    path("", views.home, name="home"),
    # Authentication endpoints
    path("logout/", views.logout_view, name="logout"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("verify-email/", views.code_verification, name="code_verification"),
    path("resend-code/", views.resend_code, name="resend_code"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path(
        "reset-password/<str:unique_id>/",
        views.reset_password,
        name="reset_password",
    ),
]
