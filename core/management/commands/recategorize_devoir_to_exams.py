from django.core.management.base import BaseCommand
from django.db.models import Q
from core.models import Document, ECUE

class Command(BaseCommand):
    help = "Recategorize 'Devoir' documents to EXAMS for a target ECUE (default: Organisations des Entreprises L1 S1)"

    def add_arguments(self, parser):
        parser.add_argument('--ecue-contains', default='organis', help='Substring to find target ECUE (default: organis)')
        parser.add_argument('--level', default='L1', help='Level (default: L1)')
        parser.add_argument('--semester', default='S1', help='Semester (default: S1)')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **opts):
        needle = opts['ecue_contains']
        level = opts['level']
        semester = opts['semester']
        dry = opts['dry_run']

        target = ECUE.objects.filter(ue__level=level, ue__semester=semester, name__icontains=needle).first()
        if not target:
            self.stderr.write('Target ECUE not found.')
            return

        q = Document.objects.filter(ecue=target).filter(
            Q(title__icontains='devoir') | Q(file__icontains='Devoir') | Q(file__icontains='devoir')
        ).exclude(category='EXAMS')
        count = q.count()
        if dry:
            self.stdout.write(f"[DRY-RUN] Would recategorize {count} documents to EXAMS")
            return
        updated = q.update(category='EXAMS')
        self.stdout.write(f"Updated {updated} documents to EXAMS for ECUE '{target.name}'")
