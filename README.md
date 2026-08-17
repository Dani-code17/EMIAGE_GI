# E-MIAGE-GI

Plateforme web de partage de ressources pédagogiques (cours, TD/TP, anciens sujets, maquettes)
pour les étudiants de la filière **MIAGE**. Développée avec **Django 5.2**.

- Site en ligne : https://emiage-gi.onrender.com
- Dépôt : https://github.com/Dani-code17/EMIAGE_GI

## Stack

| Composant | Choix |
|---|---|
| Framework | Django 5.2 (Python) |
| Base de données | PostgreSQL (**Aiven** free, via `DATABASE_URL`) — SQLite en local pour le développement |
| Fichiers (médias) | **Cloudflare R2** (compatible S3, via django-storages) en production — disque local en dev |
| Front | Templates Django + Tailwind CSS (CDN) |
| Serveur | Gunicorn |
| Statiques | WhiteNoise (`collectstatic` au build) |
| Hébergement | Render (plan gratuit) |

## Structure

```
emiage_web/          Configuration Django (settings, urls, wsgi)
core/                Application principale
  models.py          Document, UE, ECUE
  views.py           Pages home, /bibliotheque/l1..m2, about, sitemap…
  templates/core/    Templates (base, home, niveau/*, includes/*)
  management/commands/  Commandes d'import et de maintenance
  migrations/        Schéma + données seedées (UE/ECUE L1, documents EOE)
media/documents/     Fichiers pédagogiques (organisés par matière)
scripts/             Scripts utilitaires (migration de données)
render.yaml          Blueprint Render (web + PostgreSQL)
```

## Développement local

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

- Sans `DATABASE_URL`, le projet utilise `db.sqlite3` (déjà peuplé).
- Admin : `/admin/` (superuser créé via `python manage.py createsuperuser`).

### Variables d'environnement (optionnelles en local)

| Variable | Défaut | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///db.sqlite3` | URL de la base (PostgreSQL en prod) |
| `DJANGO_SECRET_KEY` | clé de dev | À définir en production |
| `DJANGO_DEBUG` | `True` | Mettre `False` en production |
| `DJANGO_ALLOWED_HOSTS` | hôtes de dev + Render | Séparés par des virgules |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://emiage-gi.onrender.com` | Origines HTTPS autorisées |
| `USE_S3` | `False` | `True` en production : médias servis depuis Cloudflare R2 |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | — | Identifiants API R2 (si `USE_S3=True`) |
| `AWS_STORAGE_BUCKET_NAME` | — | Nom du bucket R2 |
| `AWS_S3_ENDPOINT_URL` | — | `https://<account_id>.r2.cloudflarestorage.com` |
| `AWS_S3_CUSTOM_DOMAIN` | — | Domaine public du bucket (optionnel, sinon URL S3) |

## Tests

```bash
python manage.py test core
```

## Importer des documents (multi-niveaux)

La commande `import_documents` lit `media/documents/` et rattache chaque dossier de
matière à son UE/ECUE (via un mapping dans la commande), puis classe les fichiers en
`COURS` / `TD_TP` / `EXAMS` selon leur nom.

```bash
# Simuler l'import L1 (rien n'est créé)
python manage.py import_documents --dry-run

# Importer réellement
python manage.py import_documents --level L1

# Importer un seul dossier de matière
python manage.py import_documents --folder "Anglais"
```

> Les UE/ECUE doivent exister en base avant l'import (commande `seed_ue_ecue` ou admin).
> L'import ne crée pas les UE/ECUE manquantes — il les cherche par nom normalisé.

## Migration des données vers PostgreSQL

Le projet utilise PostgreSQL en production (hébergé chez **Aiven**). Les données initiales ont
été transférées depuis l'ancienne base SQLite avec le script :

```bash
# 1) Exporter depuis SQLite (ne pas définir DATABASE_URL) -> backup/data.json
bash scripts/migrate_sqlite_to_postgres.sh export

# 2) Importer dans PostgreSQL (DATABASE_URL = chaîne de connexion Aiven)
DATABASE_URL="postgres://utilisateur:motdepasse@hote:5432/defaultdb" \
  bash scripts/migrate_sqlite_to_postgres.sh import
```

Le script applique les migrations, charge les données (UE, ECUE, Documents, utilisateur
admin) et réinitialise les séquences. À exécuter **une seule fois** sur une base vide.

## Envoyer les fichiers vers Cloudflare R2

En production, les fichiers pédagogiques sont servis depuis Cloudflare R2 (pas depuis le
disque de Render, limité à 512 Mo sur le plan gratuit). Une fois le bucket créé :

```bash
# Variables requises
export USE_S3=True
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_STORAGE_BUCKET_NAME="emiage-documents"
export AWS_S3_ENDPOINT_URL="https://<account_id>.r2.cloudflarestorage.com"

# Simuler l'envoi (ne transfère rien)
python manage.py upload_media_to_s3 --dry-run

# Envoyer les fichiers manquants (les clés = chemins relatifs, ex: documents/...)
python manage.py upload_media_to_s3

# Vérifier que tous les fichiers référencés en base existent dans le bucket
python manage.py upload_media_to_s3 --check
```

> Le bucket doit être **public** (lecture) : les URLs des fichiers seront
> `https://<domaine-public>/documents/...` (configurer `AWS_S3_CUSTOM_DOMAIN`).

## Déploiement (Render)

Architecture en production : **Render** (application Django, plan gratuit) +
**Aiven** (PostgreSQL) + **Cloudflare R2** (fichiers).

Le fichier `render.yaml` décrit le service web (le PostgreSQL y est déclaré pour Render,
mais en pratique on branche la base Aiven via `DATABASE_URL`).

1. **Aiven** : créer une base PostgreSQL gratuite (console.aiven.io → Create service →
   PostgreSQL → plan Free). Copier la chaîne de connexion (Service URI).
2. **Cloudflare R2** : créer un bucket public + un token API (Object Read & Write).
   Récupérer l'account ID (endpoint S3) et le domaine public du bucket.
3. Sur https://dashboard.render.com, ouvrir le service (ou **New → Blueprint** avec ce dépôt)
   et définir les variables d'environnement :
   `DATABASE_URL` (Aiven), `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY`,
   `DJANGO_ALLOWED_HOSTS=emiage-gi.onrender.com`, `USE_S3=True`, les `AWS_*` (R2).
4. Au build : `pip install`, `collectstatic`, `migrate`.
5. **Une seule fois** : importer les données dans la base Aiven
   (`DATABASE_URL="<URI Aiven>" bash scripts/migrate_sqlite_to_postgres.sh import`)
   puis envoyer les fichiers (`python manage.py upload_media_to_s3`).

> Les fichiers `media/` restent versionnés dans git (source de vérité et base de dev
> locale), mais en production ils sont servis depuis R2.
