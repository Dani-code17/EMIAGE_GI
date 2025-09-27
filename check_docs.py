import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emiage_web.settings')
django.setup()

from core.models import Document, UE, ECUE

print('🔍 Vérification des documents par UE/ECUE...')

# Vérifier les documents sans ECUE
docs_without_ecue = Document.objects.filter(ecue__isnull=True)
print(f'Documents sans ECUE: {docs_without_ecue.count()}')

# Vérifier les UE avec une seule ECUE
ues_with_one_ecue = []
for ue in UE.objects.filter(level='L1'):
    ecue_count = ue.ecues.count()
    if ecue_count == 1:
        ues_with_one_ecue.append(ue)
        print(f'UE avec 1 ECUE: {ue.name} -> {ue.ecues.first().name}')

print(f'\nTotal UE avec 1 ECUE: {len(ues_with_one_ecue)}')

# Vérifier quelques documents spécifiques
print('\n📄 Exemples de documents:')
for doc in Document.objects.filter(level='L1')[:5]:
    ecue_name = doc.ecue.name if doc.ecue else "AUCUNE"
    print(f'  {doc.title} -> ECUE: {ecue_name}')
