import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emiage_web.settings')
django.setup()

from core.models import Document

print('🔍 Vérification des maquettes...')

# Vérifier les documents qui pourraient être des maquettes
maquette_docs = Document.objects.filter(
    level='L1',
    file__icontains='maquette'
)

print(f'Documents avec "maquette" dans le nom: {maquette_docs.count()}')
for doc in maquette_docs:
    print(f'  {doc.title} - {doc.category} - {doc.file.name}')

# Corriger la catégorie des maquettes
print('\n🔧 Correction des catégories des maquettes...')
updated = 0
for doc in maquette_docs:
    if doc.category != 'MAQUETTES':
        doc.category = 'MAQUETTES'
        doc.save()
        updated += 1
        print(f'✅ {doc.title} -> MAQUETTES')

print(f'\n🎉 {updated} maquettes corrigées!')

# Vérifier les anciens sujets
print('\n🔍 Vérification des anciens sujets...')
anciens_sujets = Document.objects.filter(
    level='L1',
    category='EXAMS'
)
print(f'Anciens sujets (EXAMS): {anciens_sujets.count()}')

# Vérifier les documents avec des mots-clés d'examens
exam_keywords = ['examen', 'devoir', 'interro', 'sujet']
for keyword in exam_keywords:
    docs = Document.objects.filter(
        level='L1',
        file__icontains=keyword
    ).exclude(category='EXAMS')
    
    if docs.exists():
        print(f'\nDocuments avec "{keyword}" non classés en EXAMS:')
        for doc in docs[:5]:  # Limiter à 5 pour éviter trop d'output
            print(f'  {doc.title} - {doc.category} - {doc.file.name}')
