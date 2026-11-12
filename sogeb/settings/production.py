"""Recette et production : sécurité renforcée. Les secrets viennent des variables d'environnement (.env)."""
import os

from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = [h.strip() for h in os.environ["DJANGO_ALLOWED_HOSTS"].split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS]

# HTTPS : Nginx termine le chiffrement et transmet l'information à Django
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 8 * 60 * 60  # déconnexion après 8 heures
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

# Adresse IP réelle du visiteur transmise par Nginx (blocage des tentatives de connexion)
AXES_IPWARE_META_PRECEDENCE_ORDER = ["HTTP_X_REAL_IP", "REMOTE_ADDR"]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}

LOGGING["root"]["level"] = "INFO"  # noqa: F405
