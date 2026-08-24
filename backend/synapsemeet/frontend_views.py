"""Serve the bundled frontend from the Django application."""
from pathlib import Path

from django.conf import settings
from django.http import Http404
from django.views.static import serve


FRONTEND_ROOT = Path(settings.BASE_DIR).parent / 'frontend'


def frontend(request, path=''):
    """Return an app page or asset from the repository frontend directory."""
    requested_path = path or 'index.html'
    file_path = FRONTEND_ROOT / requested_path
    if not file_path.is_file():
        raise Http404
    return serve(request, requested_path, document_root=str(FRONTEND_ROOT))