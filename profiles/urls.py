"""
URL routing for the profiles app.

All chat traffic goes through the home view at the site root ("/").
"""

from django.urls import path

from . import views

# Namespace allows {% url 'profiles:home' %} in templates
app_name = "profiles"

urlpatterns = [
    path("", views.home, name="home"),
    # AJAX endpoint for checking the status of a chat task
    path("chat-status/<str:task_id>/", views.chat_task_status, name="chat_task_status"),
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