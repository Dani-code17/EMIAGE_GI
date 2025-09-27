from django.core.management.base import BaseCommand
from core.models import UE, ECUE, Document

class Command(BaseCommand):
    help = "Add or ensure UE 'Économie' (L1 S1) and ECUE 'Économie 2' exist."

    def add_arguments(self, parser):
        parser.add_argument('--ue-code', default='UE-ECON', help='UE code to use for Économie (default: UE-ECON)')
        parser.add_argument('--ue-name', default='Économie', help='UE name (default: Économie)')
        parser.add_argument('--ecue-name', default='Économie 2', help='ECUE name (default: Économie 2)')

    def handle(self, *args, **options):
        ue_code = options['ue_code']
        ue_name = options['ue_name']
        ecue_name = options['ecue_name']

        # Ensure UE exists for L1 S1
        ue, created_ue = UE.objects.get_or_create(
            code=ue_code,
            level='L1',
            semester='S1',
            defaults={'name': ue_name, 'slug': ''}
        )
        if not created_ue:
            # If the UE exists but name differs, sync the name
            if ue.name != ue_name:
                ue.name = ue_name
                ue.save()

        self.stdout.write(self.style.SUCCESS(f"UE ensured: {ue.code} - {ue.name} ({ue.level} {ue.semester})"))

        # Ensure ECUE exists under that UE
        ecue, created_ecue = ECUE.objects.get_or_create(
            ue=ue,
            name=ecue_name,
            defaults={'code': '', 'slug': ''}
        )
        action = 'created' if created_ecue else 'ensured'
        self.stdout.write(self.style.SUCCESS(f"ECUE {action}: {ecue.name} under UE {ue.code}"))

        # Optional: Give a short report of documents attached to this ECUE (if any)
        docs_count = Document.objects.filter(ecue=ecue).count()
        self.stdout.write(f"Documents linked to ECUE '{ecue.name}': {docs_count}")

        self.stdout.write(self.style.SUCCESS('Done.'))
