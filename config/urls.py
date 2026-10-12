"""
Root URL configuration for the django-chat-saas project.

Routes:
  - /supersecret/  → Django admin (custom path from settings.ADMIN_URL)
  - /              → profiles app (chat UI + AJAX)
  - /__debug__/    → Django Debug Toolbar (DEBUG mode only)
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.settings import ADMIN_URL
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path(
            f"{ADMIN_URL}logout/",
            LogoutView.as_view(next_page=f"/{ADMIN_URL}login/"),
            name="admin_logout",
        ),
    path(ADMIN_URL, admin.site.urls),
    path("", include("profiles.urls", namespace="profiles")),
    # Django Debug Toolbar (only in DEBUG mode)
    path("__debug__/", include("debug_toolbar.urls")),
    # Django browser reload
    path("__reload__/", include("django_browser_reload.urls")),
]

# Development-only: debug toolbar and local media/static serving
if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#TODO: Fix browser reload issue with Django 6.0 and Django Debug Toolbar. See
#TODO: Fix debug toolbar issue with Django 6.0 and Django Debug Toolbar. See