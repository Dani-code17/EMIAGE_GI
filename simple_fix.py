from core.models import Document, UE, ECUE

print('🔍 ECUE disponibles:')
for e in ECUE.objects.filter(ue__level='L1'):
    print(f'  {e.ue.name} - {e.name} ({e.ue.semester})')

print('\n🔧 Rattachement simple...')
updated = 0

# Rattacher les documents par nom de dossier
for doc in Document.objects.filter(level='L1'):
    file_path = doc.file.name.lower()
    
    # Correspondances simples
    if 'suites' in file_path or 'fonctions' in file_path:
        try:
            ecue = ECUE.objects.filter(ue__level='L1', ue__semester='S1', name__icontains='suites').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass
    
    elif 'calcul' in file_path and 'intégral' in file_path:
        try:
            ecue = ECUE.objects.filter(ue__level='L1', ue__semester='S1', name__icontains='calcul').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass
    
    elif 'logique' in file_path:
        try:
            ecue = ECUE.objects.filter(ue__level='L1', ue__semester='S1', name__icontains='logique').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass
    
    elif 'structure' in file_path or 'algébrique' in file_path:
        try:
            ecue = ECUE.objects.filter(ue__level='L1', ue__semester='S1', name__icontains='structure').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass
    
    elif 'economie' in file_path:
        try:
            ecue = ECUE.objects.filter(ue__level='L1', ue__semester='S1', name__icontains='economie').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass
    
    elif 'informatique' in file_path and 'initiation' in file_path:
        try:
            ecue = ECUE.objects.filter(ue__level='L1', ue__semester='S1', name__icontains='informatique').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass
    
    elif 'algorithmique' in file_path and 'initiation' in file_path:
        try:
            ecue = ECUE.objects.filter(ue__level='L1', ue__semester='S1', name__icontains='algorithmique').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass
    
    elif 'bureautique' in file_path:
        try:
            ecue = ECUE.objects.filter(ue__level='L1', ue__semester='S1', name__icontains='bureautique').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass
    
    elif 'electronique' in file_path or 'numérique' in file_path:
        try:
            ecue = ECUE.objects.filter(ue__level='L1', ue__semester='S1', name__icontains='electronique').first()
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated += 1
                print(f'✅ {doc.title} -> {ecue.name}')
        except:
            pass

print(f'\n🎉 {updated} documents rattachés!')
