"""SynapseMeet root URL configuration."""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenRefreshView

from .frontend_views import frontend

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth (register / login / refresh)
    path('api/auth/', include('accounts.urls')),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Core meeting resources
    path('api/meetings/', include('meetings.urls')),

    # AI transcription / summary / action items
    path('api/ai/', include('ai_assistant.urls')),

    # Keep the API routes above this catch-all so Django can serve the PWA
    # and its assets from the same origin.
    path('', frontend, name='frontend-index'),
    re_path(r'^(?P<path>.*)$', frontend, name='frontend'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
