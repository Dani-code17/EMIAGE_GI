from django.core.management.base import BaseCommand
from django.db.models import Q
from core.models import UE, ECUE, Document

class Command(BaseCommand):
    help = (
        "Normalize documents: move 'EOE' documents to ECUE 'Organisation des entreprises', "
        "and ensure 'Initiation à l\'informatique' documents are under their correct ECUE."
    )

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not persist changes, only show what would change')
        parser.add_argument('--level', default=None, help="Optional level filter, e.g., L1 or L2")
        parser.add_argument('--semester', default=None, help="Optional semester filter, e.g., S1 or S2")
        parser.add_argument('--verbose', action='store_true', help='More output')

    def handle(self, *args, **options):
        dry = options['dry_run']
        level = options['level']
        semester = options['semester']
        verbose = options['verbose']

        level_q = Q()
        if level:
            level_q &= Q(level=level)
        if semester:
            level_q &= Q(semester=semester)

        total_moved = 0
        total_fixed_init = 0

        # 1) Map EOE -> Organisation des entreprises
        # Find target ECUE by name icontains, across any UE that matches same level/semester if provided
        target_org_e_cue = ECUE.objects.filter(name__iexact='Organisation des entreprises')
        if level or semester:
            target_org_e_cue = target_org_e_cue.filter(ue__level=level if level else ECUE.objects.values('ue__level'),
                                                       ue__semester=semester if semester else ECUE.objects.values('ue__semester'))
        target_org_e_cue = target_org_e_cue.first()
        if not target_org_e_cue:
            # try contains ignoring accents / case
            target_org_e_cue = ECUE.objects.filter(name__icontains='organisation', ue__name__icontains='organisation').first()
        if not target_org_e_cue:
            self.stderr.write("ECUE 'Organisation des entreprises' not found. Skipping EOE mapping.")
        else:
            # Documents considered EOE: by ECUE name or by file path hints or title
            eoe_docs = Document.objects.filter(level_q).filter(
                Q(ecue__name__iexact='EOE') |
                Q(ecue__name__icontains='eoe') |
                Q(file__icontains='/EOE/') |
                Q(title__icontains='eoe')
            )
            if verbose:
                self.stdout.write(f"Found {eoe_docs.count()} EOE-like documents to reassign to '{target_org_e_cue.name}'.")
            if not dry:
                moved = eoe_docs.update(ecue=target_org_e_cue)
                total_moved += moved
            else:
                total_moved += eoe_docs.count()

        # 2) Fix Initiation à l'informatique vs Initiation à l'algorithmique
        # Locate ECUEs
        # Find ECUE targets with exact then fuzzy matching using Q combinations
        ecue_init_info = ECUE.objects.filter(name__iexact="Initiation à l'informatique").first()
        if not ecue_init_info:
            ecue_init_info = ECUE.objects.filter(Q(name__icontains='initiation') & Q(name__icontains='informatique')).first()

        ecue_init_algo = ECUE.objects.filter(name__iexact="Initiation à l'algorithmique").first()
        if not ecue_init_algo:
            ecue_init_algo = ECUE.objects.filter(Q(name__icontains='initiation') & Q(name__icontains='algorithmique')).first()

        if not ecue_init_info:
            self.stderr.write("ECUE 'Initiation à l'informatique' not found.")
        if not ecue_init_algo:
            self.stderr.write("ECUE 'Initiation à l'algorithmique' not found.")

        if ecue_init_info and ecue_init_algo:
            # Any documents assigned to algorithmique that look like 'informatique'
            q_source = Document.objects.filter(level_q, ecue=ecue_init_algo).filter(
                Q(title__icontains='informatique') |
                Q(file__icontains='Initiation a l\'informatique') |
                Q(file__icontains='Initiation à l\'informatique') |
                Q(file__icontains='Initiation%20a%20l\'informatique')
            )
            if verbose:
                self.stdout.write(f"Found {q_source.count()} documents to move from algo -> informatique")
            if not dry:
                total_fixed_init += q_source.update(ecue=ecue_init_info)
            else:
                total_fixed_init += q_source.count()

        self.stdout.write(self.style.SUCCESS(
            f"Done. Moved EOE->Organisation: {total_moved}, Fixed Initiation: {total_fixed_init}"
        ))
