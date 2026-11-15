"""Poste de développement : mode débogage, SQLite, courriels affichés dans le terminal.

Avec SOGEB_TUNNEL=1 (posé par LANCER_TUNNEL.bat), le site est servi pour un lien public temporaire
https://….trycloudflare.com : le mode débogage est coupé pour ne pas afficher le détail des erreurs
à l'extérieur, et seules les adresses du tunnel sont acceptées en plus du poste local.
"""
import os

from .base import *  # noqa: F401,F403

TUNNEL = os.environ.get("SOGEB_TUNNEL") == "1"

DEBUG = not TUNNEL
SECRET_KEY = "dev-uniquement-ne-pas-utiliser-en-production"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

if TUNNEL:
    ALLOWED_HOSTS += [".trycloudflare.com"]
    CSRF_TRUSTED_ORIGINS = ["https://*.trycloudflare.com"]
    # Le tunnel arrive en HTTP sur le poste mais le visiteur est en HTTPS.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Toutes les requêtes du tunnel viennent de 127.0.0.1 : on lit la vraie adresse du visiteur
    # pour que le blocage après 5 échecs de connexion ne bloque pas tout le monde.
    AXES_IPWARE_META_PRECEDENCE_ORDER = ["HTTP_CF_CONNECTING_IP", "REMOTE_ADDR"]
