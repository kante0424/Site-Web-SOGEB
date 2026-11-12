#!/bin/sh
# Sauvegarde de la base et des médias (à planifier chaque nuit avec cron sur le serveur).
# Exemple de ligne cron : 30 2 * * * cd /opt/sogeb-site && ./scripts/sauvegarde.sh >> backups/sauvegarde.log 2>&1
set -eu
DOSSIER="${DOSSIER_SAUVEGARDE:-./backups}"
DATE=$(date +%Y-%m-%d_%H%M)
mkdir -p "$DOSSIER"

docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' > "$DOSSIER/base_$DATE.dump"
docker compose run --rm -T --no-deps -v "$(realpath "$DOSSIER")":/sauvegarde app \
  tar -czf "/sauvegarde/medias_$DATE.tar.gz" -C /app media

# Conservation : 30 jours
find "$DOSSIER" -name 'base_*.dump' -mtime +30 -delete
find "$DOSSIER" -name 'medias_*.tar.gz' -mtime +30 -delete
echo "Sauvegarde terminée : $DATE"
