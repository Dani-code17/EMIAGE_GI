from django.core.management.base import BaseCommand
from core.models import UE, ECUE, Document

class Command(BaseCommand):
    help = (
        "Migrate L1 S1 economy structure: delete UE 'UE-ECON' and its ECUEs, "
        "add ECUE 'Économie 2' under existing UE 'ECONOMIE', and move documents from old 'Économie 2' if present."
    )

    def add_arguments(self, parser):
        parser.add_argument('--target-ue-code', default='ECONOMIE', help="Target UE code for ÉCONOMIE (default: ECONOMIE)")

    def handle(self, *args, **options):
        # Identify target UE (must exist). Try by code, then fallback to name icontains.
        target_code = options['target_ue_code']
        target_ue = UE.objects.filter(code=target_code, level='L1', semester='S1').first()
        if not target_ue:
            # Fallback: search by name icontains 'econ' to catch 'Économie'/'Economie'
            candidates = UE.objects.filter(level='L1', semester='S1', name__icontains='econ')
            if candidates.count() == 1:
                target_ue = candidates.first()
                self.stdout.write(self.style.WARNING(
                    f"Target UE code '{target_code}' not found. Falling back to name match: {target_ue.code} - {target_ue.name}"
                ))
            elif candidates.exists():
                self.stderr.write(
                    "Multiple UE candidates found by name icontains 'econ' for L1 S1. "
                    "Specify --target-ue-code explicitly. Candidates: " + ", ".join([f"{u.code} - {u.name}" for u in candidates])
                )
                return
            else:
                self.stderr.write(
                    f"Target UE with code '{target_code}' not found and no name candidates matching 'econ' for L1 S1. Aborting."
                )
                return
        self.stdout.write(self.style.SUCCESS(f"Target UE found: {target_ue.code} - {target_ue.name}"))

        # Ensure new ECUE 'Économie 2' under target UE
        new_ecue, created_new = ECUE.objects.get_or_create(
            ue=target_ue,
            name='Économie 2',
            defaults={'code': '', 'slug': ''}
        )
        self.stdout.write(self.style.SUCCESS(
            f"ECUE under target UE: {'created' if created_new else 'ensured'} -> {new_ecue.name}"
        ))

        # Find old UE
        old_ue = UE.objects.filter(code='UE-ECON', level='L1', semester='S1').first()
        if not old_ue:
            self.stdout.write("Old UE 'UE-ECON' (L1 S1) not found. Nothing to delete.")
            return

        self.stdout.write(self.style.WARNING(f"Old UE found and will be removed: {old_ue.code} - {old_ue.name}"))

        # Migrate documents from ECUE named 'Économie 2' under old UE, if exists
        old_ecue_econ2 = ECUE.objects.filter(ue=old_ue, name='Économie 2').first()
        moved_docs = 0
        if old_ecue_econ2:
            moved_docs = Document.objects.filter(ecue=old_ecue_econ2).update(ecue=new_ecue)
            self.stdout.write(self.style.SUCCESS(f"Moved {moved_docs} documents from old ECUE 'Économie 2' to new ECUE."))

        # Delete all ECUEs under old UE (which should now be doc-less for 'Économie 2')
        old_ecue_count = old_ue.ecues.count()
        old_ue.ecues.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {old_ecue_count} ECUE(s) under old UE."))

        # Delete old UE
        old_ue.delete()
        self.stdout.write(self.style.SUCCESS("Deleted old UE 'UE-ECON'. Migration complete."))
