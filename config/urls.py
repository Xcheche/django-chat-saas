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

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path("", include("profiles.urls", namespace="profiles")),
]

# Development-only: debug toolbar and local media/static serving
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
