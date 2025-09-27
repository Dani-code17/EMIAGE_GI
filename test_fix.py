import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emiage_web.settings')
django.setup()

from core.models import Document, UE, ECUE

# Créer quelques UE/ECUE de test pour vérifier le fonctionnement
print('🔧 Création des UE/ECUE de test...')

# UE avec une seule ECUE (pour tester l'auto-sélection)
ue_bureautique, _ = UE.objects.get_or_create(
    code='UE Outils Bureautiques 1',
    name='Outils Bureautiques 1',
    level='L1',
    semester='S1'
)

ecue_bureautique, _ = ECUE.objects.get_or_create(
    name='Outils Bureautiques 1',
    ue=ue_bureautique
)

# UE avec une seule ECUE (Electronique)
ue_electronique, _ = UE.objects.get_or_create(
    code='UE Electronique Numérique',
    name='Electronique Numérique',
    level='L1',
    semester='S1'
)

ecue_electronique, _ = ECUE.objects.get_or_create(
    name='Electronique Numérique',
    ue=ue_electronique
)

print('✅ UE/ECUE créées!')

# Rattacher quelques documents de test
print('🔧 Rattachement des documents de test...')

# Documents Outils Bureautiques
bureautique_docs = Document.objects.filter(
    level='L1',
    file__icontains='bureautique'
)
for doc in bureautique_docs:
    doc.ecue = ecue_bureautique
    doc.save()
    print(f'✅ {doc.title} -> Outils Bureautiques')

# Documents Electronique
electronique_docs = Document.objects.filter(
    level='L1',
    file__icontains='electronique'
)
for doc in electronique_docs:
    doc.ecue = ecue_electronique
    doc.save()
    print(f'✅ {doc.title} -> Electronique Numérique')

print(f'\n🎉 Documents rattachés!')
print(f'Documents Outils Bureautiques: {bureautique_docs.count()}')
print(f'Documents Electronique: {electronique_docs.count()}')
