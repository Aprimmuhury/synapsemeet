"""ASGI config for SynapseMeet (supports future websocket/live-caption channels)."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'synapsemeet.settings')
application = get_asgi_application()
