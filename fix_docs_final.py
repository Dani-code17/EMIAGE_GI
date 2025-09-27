import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emiage_web.settings')
django.setup()

from core.models import Document, UE, ECUE

print('🔍 Vérification des ECUE créées...')
for e in ECUE.objects.filter(ue__level='L1'):
    print(f'  {e.ue.name} - {e.name} ({e.ue.semester})')

print('\n🔧 Rattachement des documents avec correspondance exacte...')

# Mapping exact des dossiers vers ECUE
folder_to_ecue_exact = {
    'Suites et Fonctions': ('UE MATHEMATIQUES 1', 'suites et fonctions'),
    'Calcul intégrale': ('UE MATHEMATIQUES 1', 'Calcul intégral'),
    'Elements de logique': ('UE MATHEMATIQUES 2', 'Elements de Logique'),
    'Structure Algébrique': ('UE MATHEMATIQUES 2', 'Structure Algébrique'),
    'Economie': ('UE ECONOMIE', 'Economie générale'),
    'Initiation a l\'informatique': ('UE Initiation à l\'informatique', 'Initiation à l\'informatique'),
    'Initiation à l\'algorithmique': ('UE Initiation à l\'algorithmique', 'Initiation à l\'algorithmique'),
    'Outil Bureautique': ('UE Outils Bureautiques 1', 'Outils Bureautiques 1'),
    'Electronique-Numérique': ('UE Electronique Numérique', 'Electronique Numérique'),
    'Géométrie': ('UE MATHEMATIQUES 3', 'Géometrie'),
    'Matrice-EspaceV': ('UE MATHEMATIQUES 3', 'Calcul matriciel'),
    'Probabilités': ('UE PROBABILITES ET STATISTIQUE 1', 'Probabilité'),
    'Statistique': ('UE PROBABILITES ET STATISTIQUE 1', 'Statistique'),
    'LangageR': ('UE PROBABILITES ET STATISTIQUE 1', 'Langage R'),
    'Algorithmique': ('UE ALGORITHMIQUE ET PROGRAMMATION', 'Algorithmique'),
    'Java': ('UE ALGORITHMIQUE ET PROGRAMMATION', 'Programmation Java'),
    'Intelligence économique': ('UE Intelligence économique', 'Intelligence économique'),
    'GRH': ('UE Gestion des ressources humaines', 'Gestion des ressources humaines'),
    'Infographie': ('UE Infographie(Montage vidéo,etc..)', 'Infographie(Montage vidéo,etc..)'),
    'Anglais': ('UE Anglais', 'Anglais'),
    'Maintenance': ('UE Atelier de maintenance', 'Atelier de maintenance'),
    'EOE': ('UE TECHNIQUE D\'EXPRESSION ET METHODOLOGIE DU TRAVAIL', 'Methodologie de travail'),
}

updated_count = 0
for doc in Document.objects.filter(level='L1'):
    file_path = doc.file.name
    
    # Trouver le dossier correspondant
    folder_name = None
    for folder in folder_to_ecue_exact.keys():
        if folder.lower() in file_path.lower():
            folder_name = folder
            break
    
    if folder_name:
        ue_name, ecue_name = folder_to_ecue_exact[folder_name]
        
        # Déterminer le semestre
        s1_folders = ['Suites et Fonctions', 'Calcul intégrale', 'Elements de logique', 'Structure Algébrique', 'Economie', 'Initiation a l\'informatique', 'Initiation à l\'algorithmique', 'Outil Bureautique', 'Electronique-Numérique']
        semester = 'S1' if folder_name in s1_folders else 'S2'
        
        # Trouver l'ECUE avec recherche plus flexible
        try:
            ecue = ECUE.objects.filter(
                ue__level='L1',
                ue__semester=semester
            ).filter(
                name__icontains=ecue_name.split()[0] if ecue_name else '',
                ue__name__icontains=ue_name.split()[1] if len(ue_name.split()) > 1 else ue_name
            ).first()
            
            if ecue:
                doc.ecue = ecue
                doc.save()
                updated_count += 1
                print(f'✅ {doc.title} -> {ecue.ue.name} - {ecue.name}')
            else:
                print(f'❌ ECUE non trouvée: {ue_name} - {ecue_name} ({semester})')
                
        except Exception as e:
            print(f'❌ Erreur: {e}')
    else:
        print(f'⚠️  Dossier non trouvé pour: {file_path}')

print(f'\n🎉 {updated_count} documents rattachés aux ECUE!')
