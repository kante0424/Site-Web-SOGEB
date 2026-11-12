# Site web institutionnel de la SOGEB

Site de la Société de Gestion et d'Exploitation du Backbone National (SOGEB S.A), construit avec
**Wagtail 7.4 LTS** (Django 5.2 LTS, Python). Voir aussi `06_Conception_technique/` dans le dossier du projet.

## Démarrer sur un poste de développement (Windows)

Prérequis : [Python 3.12](https://www.python.org/downloads/) (cocher « Add python.exe to PATH » à l'installation).

```powershell
cd sogeb-site
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py initialiser_sogeb
python manage.py createsuperuser
python manage.py runserver
```

- Site : http://localhost:8000
- Administration : http://localhost:8000/gestion/

En développement, la base est un simple fichier `db.sqlite3` et les courriels s'affichent dans le terminal.
Pour repartir de zéro : supprimer `db.sqlite3` et le dossier `media/`, puis relancer `migrate` et `initialiser_sogeb`.

Sous Linux ou macOS, remplacer `.venv\Scripts\activate` par `source .venv/bin/activate`.

## Lancer les tests

```powershell
python manage.py test apps
```

Les tests vérifient que les pages s'affichent, que les brouillons restent invisibles, qu'il n'y a qu'un titre H1 par
page, que le formulaire de contact fonctionne et bloque les robots, et qu'un contributeur ne peut pas publier.

## Organisation du code

| Dossier | Contenu |
|---|---|
| `sogeb/settings/` | Réglages : `base.py` (communs), `dev.py` (poste), `production.py` (recette et production) |
| `apps/core/` | Paramètres du site (coordonnées, réseaux sociaux), chiffres clés, valeurs, blocs de contenu, commande `initialiser_sogeb`, tests |
| `apps/home/` | Page d'accueil |
| `apps/pages/` | Pages institutionnelles (La SOGEB, mentions légales) et pages infrastructure (Backbone, Data center) |
| `apps/services/` | Liste des services et fiches service |
| `apps/actualites/` | Liste des actualités et articles (catégories : Actualité, Communiqué, Vie de l'entreprise) |
| `apps/medias/` | Documents et médias |
| `apps/contact/` | Page contact et formulaire (avec champ anti-robot) |
| `templates/` | Gabarits HTML : `base.html`, morceaux réutilisés (`includes/`), affichage des blocs (`blocks/`) |
| `static/` | Feuille de style aux couleurs de la charte, polices Montserrat et Barlow Condensed, logo, scripts du menu mobile et des animations |
| `docker/` | Configuration Nginx (HTTPS, en-têtes de sécurité) et emplacement des certificats |
| `scripts/` | `sauvegarde.sh` (base + médias, 30 jours), `deployer.sh` (mise à jour), `generer_carte_guinee.py` (carte de l'accueil) |

### Ajouter un champ à un type de page

1. Ajouter le champ dans le `models.py` concerné et dans `content_panels`.
2. `python manage.py makemigrations` puis `python manage.py migrate`.
3. Afficher le champ dans le gabarit correspondant (`templates/<application>/<type>.html`).

## Rôles

La commande `initialiser_sogeb` crée deux groupes et un circuit de validation :

| Groupe | Droits |
|---|---|
| **Éditeurs** | Créer, modifier, valider, publier ; gérer images, documents, paramètres du site, chiffres clés, valeurs, redirections |
| **Contributeurs** | Créer et modifier des brouillons, ajouter des images ; soumettre à validation sans publier |
| Administrateur (superutilisateur) | Tout. Réservé à la maintenance technique (contributeur technique, DSSI) |

Circuit « Validation communication » : toute page soumise par un contributeur doit être approuvée par un éditeur.
Créer les comptes dans **Paramètres → Utilisateurs**, puis les ajouter au bon groupe.

## Mise en production (serveur Linux au data center, avec la DSSI)

Prérequis : Docker et Docker Compose, ports 80 et 443 ouverts, nom de domaine pointant vers le serveur.

```bash
git clone <dépôt> /opt/sogeb-site && cd /opt/sogeb-site
cp .env.example .env            # puis remplir toutes les valeurs
# Copier le certificat dans docker/certs/fullchain.pem et docker/certs/privkey.pem
docker compose up -d --build
docker compose run --rm app python manage.py migrate
docker compose run --rm app python manage.py initialiser_sogeb   # première installation uniquement
docker compose run --rm app python manage.py createsuperuser
```

Dans l'administration, **Paramètres → Sites** : remplacer `localhost` par le nom de domaine officiel.

Mises à jour ensuite : `./scripts/deployer.sh` (récupère le code, sauvegarde, reconstruit, migre, redémarre).

Sauvegarde nocturne, à ajouter dans la crontab du serveur :

```
30 2 * * * cd /opt/sogeb-site && ./scripts/sauvegarde.sh >> backups/sauvegarde.log 2>&1
```

## Avant la mise en ligne

- [ ] Coordonnées officielles saisies dans **Paramètres → Paramètres du site**
- [ ] Chiffre officiel de la longueur du réseau confirmé (4 500 km ou 4 352 km) dans **Fragments → Chiffres clés** et dans les textes
- [ ] Adresse destinataire du formulaire renseignée sur la page Contact
- [ ] Photographies réelles ajoutées (bannière d'accueil, pages Backbone et Data center)
- [ ] Mentions légales et politique de confidentialité complétées puis publiées
- [ ] Page Documents et médias publiée si des contenus validés existent
- [ ] Comptes nominatifs créés
- [ ] Double authentification des éditeurs et administrateurs (à ajouter à l'étape sécurité)
- [ ] Redirections des anciennes adresses WordPress (**Paramètres → Redirections**)
- [ ] Test de restauration d'une sauvegarde
