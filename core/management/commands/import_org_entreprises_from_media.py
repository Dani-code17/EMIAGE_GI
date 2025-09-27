import os
import re
from django.core.management.base import BaseCommand
from core.models import Document, ECUE

class Command(BaseCommand):
    help = "Importe les documents du dossier media/documents/EOE vers l'ECUE 'Organisations des Entreprises' (L1 S1)"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simulation sans création de documents')
        parser.add_argument('--folder', default='media/documents/EOE', help='Dossier source (par défaut: media/documents/EOE)')

    def handle(self, *args, **options):
        dry = options['dry_run']
        folder = options['folder']

        # Trouver l'ECUE cible
        ecue = ECUE.objects.filter(
            ue__level='L1', ue__semester='S1', name__iexact='Organisations des Entreprises'
        ).select_related('ue').first()
        if not ecue:
            self.stdout.write('[ERR] ECUE Organisations des Entreprises (L1 S1) introuvable.')
            return

        if not os.path.isdir(folder):
            self.stdout.write(f"[ERR] Dossier introuvable: {folder}")
            return

        created = 0
        skipped = 0
        errors = 0

        def detect_category(filename):
            name = filename.lower()
            if any(w in name for w in ['examen', 'exam', 'sujet', 'session']):
                return 'EXAMS'
            if any(w in name for w in ['td', 'tp', 'travaux', 'exercice', 'correction']):
                return 'TD_TP'
            if any(w in name for w in ['maquette', 'planning', 'programme']):
                return 'MAQUETTES'
            return 'COURS'

        def generate_title(filename):
            base = os.path.splitext(os.path.basename(filename))[0]
            base = re.sub(r'[_\-]+', ' ', base)
            words = base.split()
            title = ' '.join(w.capitalize() for w in words)
            return title[:100] if len(title) > 100 else title

        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if not os.path.isfile(fpath):
                continue
            category = detect_category(fname)
            title = generate_title(fname)

            # éviter doublon exact
            exists = Document.objects.filter(
                title=title, level='L1', semester='S1', ecue=ecue
            ).first()
            if exists:
                skipped += 1
                continue

            if dry:
                self.stdout.write(f"[DRY-RUN] {title} -> {ecue.ue.name} - {ecue.name} ({category})")
                continue

            try:
                Document.objects.create(
                    title=title,
                    description=f"Importé depuis {folder}",
                    category=category,
                    level='L1',
                    semester='S1',
                    ecue=ecue,
                    file=fpath
                )
                created += 1
            except Exception as e:
                errors += 1
                self.stdout.write(f"[ERR] {fname}: {e}")

        self.stdout.write(f"[SUMMARY] created={created}, skipped={skipped}, errors={errors}")
