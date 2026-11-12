#!/bin/sh
# Mise à jour du site en recette ou en production (à lancer depuis le dossier du projet sur le serveur).
set -eu
echo "1/5 Récupération du code validé"
git pull --ff-only
echo "2/5 Sauvegarde avant mise à jour"
./scripts/sauvegarde.sh
echo "3/5 Construction de l'application"
docker compose build app
echo "4/5 Migrations de la base de données"
docker compose run --rm app python manage.py migrate --noinput
echo "5/5 Redémarrage de l'application"
docker compose up -d app nginx
docker compose exec nginx nginx -s reload
echo "Mise à jour terminée. Vérifier les pages principales."
