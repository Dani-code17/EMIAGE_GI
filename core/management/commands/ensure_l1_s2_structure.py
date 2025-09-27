from django.core.management.base import BaseCommand
from core.models import UE, ECUE

S2_UE_ECUE = {
    # UE Name                         : (UE Code, [ECUE names])
    'UE MATHEMATIQUES 3':               ('UE MATHEMATIQUES 3', ['Géometrie', 'Calcul matriciel']),
    'UE PROBABILITES ET STATISTIQUE 1': ('UE PROBABILITES ET STATISTIQUE 1', ['Probabilité', 'Statistique', 'Langage R']),
    'UE ALGORITHMIQUE ET PROGRAMMATION': ('UE ALGORITHMIQUE ET PROGRAMMATION', ['Algorithmique', 'Programmation Java']),
    'UE Intelligence économique':        ('UE Intelligence économique', ['Intelligence économique']),
    'UE Gestion des ressources humaines':('UE Gestion des ressources humaines', ['Gestion des ressources humaines']),
    'UE Infographie(Montage vidéo,etc..)':('UE Infographie(Montage vidéo,etc..)', ['Infographie(Montage vidéo,etc..)']),
    'UE Anglais':                        ('UE Anglais', ['Anglais']),
    'UE Atelier de maintenance':         ('UE Atelier de maintenance', ['Atelier de maintenance']),
}

class Command(BaseCommand):
    help = "Ensure all L1 S2 UEs and ECUEs exist according to expected mapping used by import_documents."

    def handle(self, *args, **options):
        created_ue = 0
        created_ecue = 0
        for ue_name, (ue_code, ecue_list) in S2_UE_ECUE.items():
            # Lookup by unique (level, semester, code)
            ue, ue_created = UE.objects.get_or_create(
                level='L1',
                semester='S2',
                code=ue_code,
                defaults={
                    'name': ue_name,
                    'slug': ''
                }
            )
            if ue_created:
                created_ue += 1
                self.stdout.write(self.style.SUCCESS(f"Created UE: {ue.code} - {ue.name} (L1 S2)"))
            else:
                if ue.name != ue_name:
                    ue.name = ue_name
                    ue.save()

            for ecue_name in ecue_list:
                e, e_created = ECUE.objects.get_or_create(
                    ue=ue,
                    name=ecue_name,
                    defaults={'code': '', 'slug': ''}
                )
                if e_created:
                    created_ecue += 1
                    self.stdout.write(self.style.SUCCESS(f"  Created ECUE: {ecue_name} under {ue.code}"))
        self.stdout.write(self.style.SUCCESS(f"Done. UEs created: {created_ue}, ECUEs created: {created_ecue}"))
