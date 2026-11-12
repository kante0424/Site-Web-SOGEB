# Image de l'application Wagtail (recette et production)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=sogeb.settings.production

# Pillow (traitement des images JPEG/WebP) embarque ses propres bibliothèques : aucun paquet système requis.

# Utilisateur sans privilèges
RUN useradd --create-home --uid 1000 sogeb
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=sogeb:sogeb . .
RUN mkdir -p /app/staticfiles /app/staticfiles_partage /app/media \
    && chown -R sogeb:sogeb /app/staticfiles /app/staticfiles_partage /app/media

USER sogeb
# Valeurs factices uniquement pour rassembler les fichiers statiques pendant la construction
RUN DJANGO_SECRET_KEY=build DJANGO_ALLOWED_HOSTS=localhost python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "sogeb.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-"]
