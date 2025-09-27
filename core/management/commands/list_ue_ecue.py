from django.core.management.base import BaseCommand
from core.models import UE, ECUE

class Command(BaseCommand):
    help = "List UE/ECUE by optional name contains filter"

    def add_arguments(self, parser):
        parser.add_argument('--contains', default='', help='Substring to filter names')

    def handle(self, *args, **options):
        needle = options['contains']
        if needle:
            ues = UE.objects.filter(name__icontains=needle)
            ecues = ECUE.objects.filter(name__icontains=needle)
        else:
            ues = UE.objects.all()
            ecues = ECUE.objects.all()
        self.stdout.write('UEs:')
        for u in ues.order_by('level','semester','code','name'):
            self.stdout.write(f"- {u.level} {u.semester} | {u.code} | {u.name}")
        self.stdout.write('ECUEs:')
        for e in ecues.select_related('ue').order_by('ue__level','ue__semester','ue__code','name'):
            self.stdout.write(f"- {e.ue.level} {e.ue.semester} | {e.ue.code} | {e.ue.name} :: {e.name}")
