#!/usr/bin/env bash
# =============================================================================
# Migration des données SQLite -> PostgreSQL
# -----------------------------------------------------------------------------
# Usage (depuis la racine du projet) :
#
#   1) Export depuis SQLite (BD locale par défaut) :
#        bash scripts/migrate_sqlite_to_postgres.sh export
#      -> produit backup/data.json (UIDs préservés, données de l'app core + auth)
#
#   2) Import dans PostgreSQL (DATABASE_URL doit pointer vers la BD cible) :
#        DATABASE_URL="postgres://user:pass@host:5432/emiage_gi" \
#          bash scripts/migrate_sqlite_to_postgres.sh import
#      -> applique les migrations, charge le dump, réinitialise les séquences
#
#   Variante Render : exporter localement, puis exécuter l'import sur Render
#   (Shell) avec DATABASE_URL fourni automatiquement par Render.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

MODE="${1:-}"
FORCE="${2:-}"
DUMP_FILE="backup/data.json"
EXCLUDES=(contenttypes auth.permission admin.logentry sessions)

case "$MODE" in
  export)
    echo "[1/1] Export depuis SQLite (aucune DATABASE_URL ne doit être définie)..."
    test -z "${DATABASE_URL:-}" || { echo "ERREUR: DATABASE_URL définie ! Désactivez-la pour exporter depuis SQLite."; exit 1; }
    mkdir -p backup
    PYTHONUTF8=1 python manage.py dumpdata \
      --exclude contenttypes \
      --exclude auth.permission \
      --exclude admin.logentry \
      --exclude sessions \
      --output "$DUMP_FILE"
    echo "OK -> $DUMP_FILE"
    ;;
  import)
    echo "[1/4] Vérification de DATABASE_URL..."
    test -n "${DATABASE_URL:-}" || { echo "ERREUR: DATABASE_URL non définie (cible PostgreSQL)."; exit 1; }
    test -f "$DUMP_FILE" || { echo "ERREUR: $DUMP_FILE introuvable. Lancez d'abord: $0 export"; exit 1; }

    echo "[1b/4] Garde-fou : refus d'écraser des comptes étudiants existants..."
    # Un import complet PURGE les tables core (dont core_student) puis recharge
    # depuis le dump SQLite local. S'il existe déjà des étudiants sur la cible
    # (inscrits depuis le site en ligne), on abandonne pour ne pas les effacer.
    # Utiliser --force uniquement pour une restauration volontaire.
    if [ "$FORCE" != "--force" ]; then
      python manage.py shell -c "
from django.db import connection
with connection.cursor() as c:
    c.execute('SELECT COUNT(*) FROM core_student')
    n = c.fetchone()[0]
    if n > 0:
        raise SystemExit(
            'ABANDON: ' + str(n) + ' étudiants existent déjà sur la base cible. '
            'Un import complet les effacerait. Pour modifier les données, utilisez '
            'des commandes ciblées (seed_quiz, seed_ue_ecue, admin...) directement '
            'sur cette base, ou relancez avec --force si vous voulez vraiment écraser.'
        )
print('OK: base cible vide, import autorisé')
"
    fi

    echo "[2/4] Application des migrations sur PostgreSQL..."
    python manage.py migrate --noinput

    echo "[2b/4] Purge des données seedées par les migrations (UE/ECUE/EOE)..."
    # Les migrations 0004/0007 créent des UE/ECUE et des documents EOE qui
    # entreraient en conflit avec le dump. On vide les tables core via SQL brut
    # (ordre FK) pour ne PAS déclencher Document.delete() (qui supprimerait
    # les fichiers) et pour ne pas laisser de références orphelines.
    python manage.py shell -c "
from django.db import connection
with connection.cursor() as c:
    c.execute('DELETE FROM core_quizanswer')
    c.execute('DELETE FROM core_quizquestion')
    c.execute('DELETE FROM core_quizattempt')
    c.execute('DELETE FROM core_studentstat')
    c.execute('DELETE FROM core_prize')
    c.execute('DELETE FROM core_document')
    c.execute('DELETE FROM core_ecue')
    c.execute('DELETE FROM core_ue')
    c.execute('DELETE FROM core_student')
print('Tables core purgées')
"

    echo "[3/4] Chargement des données..."
    python manage.py loaddata "$DUMP_FILE"

    echo "[4/4] Réinitialisation des séquences..."
    python manage.py shell -c "
from django.db import connection
from django.core.management.color import no_style
from django.apps import apps
models = list(apps.get_models())
sql = connection.ops.sequence_reset_sql(no_style(), models)
with connection.cursor() as c:
    for s in sql:
        c.execute(s)
print('Séquences réinitialisées')
"

    echo "OK. Vérification rapide :"
    python manage.py shell -c \
      "from core.models import Document, UE, ECUE; print(f'Documents={Document.objects.count()} UE={UE.objects.count()} ECUE={ECUE.objects.count()}')"
    ;;
  *)
    echo "Usage: $0 {export|import}"
    exit 1
    ;;
esac
