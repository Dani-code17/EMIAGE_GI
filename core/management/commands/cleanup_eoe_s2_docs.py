from django.core.management.base import BaseCommand
from django.db.models import Q
from core.models import Document

class Command(BaseCommand):
    help = "Delete L1 S2 documents incorrectly associated with EOE (by ECUE name/title/path hints)."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Only show what would be deleted')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')

    def handle(self, *args, **options):
        dry = options['dry_run']
        verbose = options['verbose']

        qs = Document.objects.filter(level='L1', semester='S2').filter(
            Q(ecue__name__iexact='EOE') |
            Q(ecue__name__icontains='eoe') |
            Q(title__icontains='eoe') |
            Q(file__icontains='/EOE/')
        )
        count = qs.count()
        if verbose:
            for d in qs:
                self.stdout.write(f"- {d.id} | {d.title} | {d.category} | {d.file}")
        if dry:
            self.stdout.write(f"[DRY-RUN] Would delete {count} documents")
        else:
            # Ensure file deletion via model delete method
            for d in qs:
                d.delete()
            self.stdout.write(f"Deleted {count} documents")
