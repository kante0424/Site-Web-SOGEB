"""Poste de développement : mode débogage, SQLite, courriels affichés dans le terminal."""
from .base import *  # noqa: F401,F403

DEBUG = True
SECRET_KEY = "dev-uniquement-ne-pas-utiliser-en-production"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
