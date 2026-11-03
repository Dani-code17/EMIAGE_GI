# E-MIAGE-GI — Plateforme de ressources pédagogiques MIAGE

> Plateforme web qui centralise les cours, TD/TP, anciens sujets et maquettes de la filière
> **MIAGE** (L1 → M2), avec un espace étudiant, un quiz de révision et l'organisation de la
> Journée d'Intégration.

**🇫🇷 Français** · [🇬🇧 English](#-english)

- **Site en ligne :** https://emiage-gi.onrender.com
- **Stack :** Django 5.2 · PostgreSQL · Cloudflare R2 · Render

---

## Ce que la plateforme résout

Les ressources d'une filière se perdent dans des groupes WhatsApp et des dossiers Drive
éparpillés. **E-MIAGE-GI** les rend **cherchables, filtrables et pérennes** :

- **Bibliothèque structurée** par **niveau** (L1 → M2), **semestre** (S1 → S10),
  **UE / ECUE** et **catégorie** (`Cours`, `TD/TP`, `Anciens sujets`, `Maquettes`).
- **Comptes étudiants** générés à partir du nom + date de naissance : identifiant unique et
  permanent (IP) du type `YEOD2608040001`, sans formulaire à remplir.
- **Quiz de révision** (choix de niveau → questions → score) pour s'auto-évaluer.
- **Journée d'Intégration** : édition, moyens de paiement et galerie photo gérés depuis
  l'admin — délégués à un compte éditeur restreint au comité d'organisation.
- **Statistiques d'usage** : visites par jour et temps passé sur le site, mesurés côté serveur.
- **SEO & PWA** : `sitemap.xml`, `robots.txt`, `manifest.json` et service worker générés par Django.

## Stack technique

| Couche | Choix | Pourquoi |
|---|---|---|
| Backend | Django 5.2 (Python) | Admin puissant, migrations, ORM |
| Base de données | PostgreSQL (**Aiven**, plan gratuit) via `dj-database-url` | SQLite en local, aucune ligne de code à changer |
| Fichiers (médias) | **Cloudflare R2** (S3-compatible, `django-storages` + `boto3`) | Le disque de Render est limité à 512 Mo en gratuit |
| Frontend | Templates Django + Tailwind CSS | Pas de SPA à maintenir pour un site de contenu |
| Serveur | Gunicorn + WhiteNoise | Statiques servis sans serveur web dédié |
| Déploiement | Render (`render.yaml`) | CI/CD par le dépôt, plan gratuit |

## Architecture

```
emiage_web/                 Configuration Django (settings, urls, wsgi/asgi)
core/
  models.py                 Document, UE, ECUE, Student, StudentStat, JIEdition, JIPayment, JIPhoto
  views.py                  Vues publiques, espace étudiant, quiz, admin-espace, sitemap/robots/sw
  middleware.py             StudentActivityMiddleware : visites + temps passé
  urls.py                   Routes de l'application
  templates/core/           base, home, niveau/*, includes/*
  management/commands/      Import de documents, seed UE/ECUE, création d'éditeur JI, upload R2
scripts/                    Migration SQLite → PostgreSQL, scripts Render (déploiement, logs)
render.yaml                 Blueprint Render
```

## Démarrage rapide

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver        # http://127.0.0.1:8000
```

- Sans `DATABASE_URL`, le projet utilise `db.sqlite3`.
- Back-office : `/admin/` (superutilisateur via `python manage.py createsuperuser`).
- Espace d'administration métier personnalisé : `/admin-espace/`.

### Variables d'environnement (toutes optionnelles en local)

| Variable | Défaut | Rôle |
|---|---|---|
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Connexion PostgreSQL en production |
| `DJANGO_SECRET_KEY` | clé de dev | **À définir en production** |
| `DJANGO_DEBUG` | `True` | `False` en production |
| `DJANGO_ALLOWED_HOSTS` | hôtes de dev + Render | Séparés par des virgules |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://emiage-gi.onrender.com` | Origines HTTPS autorisées |
| `USE_S3` | `False` | `True` : médias servis depuis Cloudflare R2 |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | — | Token API R2 |
| `AWS_STORAGE_BUCKET_NAME` | — | Bucket R2 |
| `AWS_S3_ENDPOINT_URL` | — | `https://<account_id>.r2.cloudflarestorage.com` |
| `AWS_S3_CUSTOM_DOMAIN` | — | Domaine public du bucket |
| `ADMIN_LOGIN` / `ADMIN_PASSWORD` | valeurs de dev | Accès à `/admin-espace/` |

## Importer des documents

`import_documents` lit un arborescence de dossiers, rattache chaque matière à son UE/ECUE
et classe les fichiers en `COURS` / `TD_TP` / `EXAMS` d'après leur nom.

```bash
python manage.py import_documents --dry-run          # simulation, rien n'est créé
python manage.py import_documents --level L1         # import réel du niveau L1
python manage.py import_documents --folder "Anglais" # un seul dossier de matière
```

> Les UE/ECUE doivent exister avant l'import (`seed_ue_ecue` ou l'admin). L'import les
> recherche par nom normalisé, il ne les crée pas.

## Gestion des accès

Le site distingue **trois niveaux de droits** :

1. **Superutilisateur Django** — accès total (`/admin/` + `/admin-espace/`).
2. **Éditeur JI (comité d'organisation)** — `is_staff` mais **non** superutilisateur, avec
   uniquement les 12 permissions des modèles `JIEdition`, `JIPayment`, `JIPhoto` :

   ```bash
   python manage.py create_ji_editor --username comite_ji --password "MotDePasseFort"
   python manage.py create_ji_editor --username comite_ji --password "Nouveau" --email x@y.z
   python manage.py create_ji_editor --username comite_ji --revoke
   ```

   En dehors de la section « Journée d'Intégration », l'admin renvoie une **403**.

3. **Étudiants** — identifiant permanent + mot de passe, accès limité à leur espace, au
   téléchargement et au quiz.

## Tests

```bash
python manage.py test core
```

## Déploiement

Architecture en production : **Render** (Django) + **Aiven** (PostgreSQL) + **Cloudflare R2** (fichiers).

1. **Aiven** : créer un service PostgreSQL gratuit et copier le *Service URI*.
2. **Cloudflare R2** : créer un bucket public + token API *(Object Read & Write)*.
3. **Render** : **New → Blueprint** (le `render.yaml` du dépôt) puis renseigner
   `DATABASE_URL`, `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`,
   `USE_S3=True` et les variables `AWS_*`.
4. Build : `pip install`, `collectstatic`, `migrate`.
5. **Une seule fois** : migrer les données et pousser les fichiers

   ```bash
   DATABASE_URL="<URI Aiven>" bash scripts/migrate_sqlite_to_postgres.sh import
   python manage.py upload_media_to_s3          # --dry-run / --check disponibles
   ```

---

## 🇬🇧 English

**E-MIAGE-GI** is a Django 5.2 web platform that centralises course material (lectures, labs,
past exams, curriculum templates) for the **MIAGE** programme, from first year to Master's.

- **Structured library** browsable by year (L1→M2), semester (S1→S10), course unit (UE/ECUE)
  and category (lectures, tutorials/labs, past exams, templates).
- **Student accounts** provisioned from name + birth date into a stable permanent ID,
  no sign-up form required.
- **Self-assessment quizzes** per level, with instant scoring.
- **Integration Day module** (edition, payment methods, photo gallery) delegated to a
  restricted editor account for the organising committee — every other admin model returns 403.
- **Usage analytics** (daily visits, time on site) tracked server-side by a middleware.
- **SEO + PWA ready**: sitemap, robots.txt, web manifest and service worker served by Django.

**Tech:** Django 5.2 · PostgreSQL (Aiven) · Cloudflare R2 via django-storages · Gunicorn +
WhiteNoise · deployed on Render. SQLite for local development.

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
python manage.py test core
```

**Author:** Yeo Daniel — [github.com/Dani-code17](https://github.com/Dani-code17)
