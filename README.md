# E-MIAGE-GI

Plateforme web de partage de ressources pédagogiques (cours, TD/TP, anciens sujets, maquettes)
pour les étudiants de la filière **MIAGE**. Développée avec **Django 5.2**.

- Site en ligne : https://emiage-gi.onrender.com
- Dépôt : https://github.com/Dani-code17/EMIAGE_GI

## Stack

| Composant | Choix |
|---|---|
| Framework | Django 5.2 (Python) |
| Base de données | PostgreSQL (Render) — SQLite en local pour le développement |
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

Le projet utilise PostgreSQL en production (Render). Les données initiales ont été
transférées depuis l'ancienne base SQLite avec le script :

```bash
# 1) Exporter depuis SQLite (ne pas définir DATABASE_URL) -> backup/data.json
bash scripts/migrate_sqlite_to_postgres.sh export

# 2) Importer dans PostgreSQL (DATABASE_URL = chaîne de connexion cible)
DATABASE_URL="postgres://utilisateur:motdepasse@hote:5432/emiage_gi" \
  bash scripts/migrate_sqlite_to_postgres.sh import
```

Le script applique les migrations, charge les données (UE, ECUE, Documents, utilisateur
admin) et réinitialise les séquences. À exécuter **une seule fois** sur une base vide.

## Déploiement (Render)

Le fichier `render.yaml` décrit le déploiement : service web + base PostgreSQL gérés.

1. Sur https://dashboard.render.com, **New → Blueprint** et connecter ce dépôt.
2. Le blueprint crée la base `emiage-gi-db` et injecte `DATABASE_URL` dans le service web.
3. `DJANGO_SECRET_KEY` est généré automatiquement ; `DJANGO_DEBUG=False` ; hosts autorisés.
4. Au build : `pip install`, `collectstatic`, `migrate`.
5. **Une seule fois**, importer les données existantes dans la base Render :
   `DATABASE_URL="<connection string Render>" bash scripts/migrate_sqlite_to_postgres.sh import`
   (la connection string Render est publique ; exécutable depuis le poste local).

> ⚠️ Les fichiers `media/` sont versionnés dans git (nécessaire sur le plan gratuit de
> Render, dont le filesystem est éphémère). Ne pas les supprimer du dépôt.
