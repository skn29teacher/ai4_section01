"""Importable WSGI entry point. Set NOTE_DEMO_CONFIG before importing."""
from app import create_app

application = create_app()
