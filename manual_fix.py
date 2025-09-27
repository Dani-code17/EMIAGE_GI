import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emiage_web.settings')
django.setup()

from core.models import Document, UE, ECUE

print('🔍 Vérification des documents...')
docs = Document.objects.filter(level='L1')
print(f'Total documents L1: {docs.count()}')

if docs.exists():
    print('Exemples de chemins:')
    for doc in docs[:5]:
        print(f'  {doc.file.name}')
    
    print('\n🔧 Rattachement manuel...')
    
    # Rattacher quelques documents de test
    updated = 0
    
    # Documents Outils Bureautiques
    for doc in docs.filter(file__icontains='bureautique'):
        try:
            ecue = ECUE.objects.filter(name__icontains='bureautique').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass
    
    # Documents Electronique
    for doc in docs.filter(file__icontains='electronique'):
        try:
            ecue = ECUE.objects.filter(name__icontains='electronique').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass
    
    print(f'\n🎉 {updated} documents rattachés!')
else:
    print('Aucun document L1 trouvé!')
