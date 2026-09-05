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
]
