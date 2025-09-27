import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emiage_web.settings')
django.setup()

from core.models import Document, UE, ECUE

print('🔧 Rattachement COMPLET de tous les documents L1...')

# Créer toutes les UE et ECUE manquantes
ues_data = [
    # S1
    ('UE Outils Bureautiques 1', 'Outils Bureautiques 1', 'L1', 'S1', ['Outils Bureautiques 1']),
    ('UE Electronique Numérique', 'Electronique Numérique', 'L1', 'S1', ['Electronique Numérique']),
    ('UE Initiation à l\'informatique', 'Initiation à l\'informatique', 'L1', 'S1', ['Initiation à l\'informatique']),
    ('UE Initiation à l\'algorithmique', 'Initiation à l\'algorithmique', 'L1', 'S1', ['Initiation à l\'algorithmique']),
    ('UE ECONOMIE', 'ECONOMIE', 'L1', 'S1', ['Economie générale']),
    ('UE MATHEMATIQUES 1', 'MATHEMATIQUES 1', 'L1', 'S1', ['suites et fonctions', 'Calcul intégral']),
    ('UE MATHEMATIQUES 2', 'MATHEMATIQUES 2', 'L1', 'S1', ['Elements de Logique', 'Structure Algébrique']),
    ('UE Organisations des Entreprises', 'Organisations des Entreprises', 'L1', 'S1', ['Organisations des Entreprises']),
    # S2
    ('UE Anglais', 'Anglais', 'L1', 'S2', ['Anglais']),
    ('UE Intelligence économique', 'Intelligence économique', 'L1', 'S2', ['Intelligence économique']),
    ('UE Gestion des ressources humaines', 'Gestion des ressources humaines', 'L1', 'S2', ['Gestion des ressources humaines']),
    ('UE Infographie(Montage vidéo,etc..)', 'Infographie(Montage vidéo,etc..)', 'L1', 'S2', ['Infographie(Montage vidéo,etc..)']),
    ('UE Atelier de maintenance', 'Atelier de maintenance', 'L1', 'S2', ['Atelier de maintenance']),
    ('UE MATHEMATIQUES 3', 'MATHEMATIQUES 3', 'L1', 'S2', ['Géometrie', 'Calcul matriciel', 'Espaces vectoriels']),
    ('UE PROBABILITES ET STATISTIQUE 1', 'PROBABILITES ET STATISTIQUE 1', 'L1', 'S2', ['Probabilité', 'Statistique', 'Langage R']),
    ('UE ALGORITHMIQUE ET PROGRAMMATION', 'ALGORITHMIQUE ET PROGRAMMATION', 'L1', 'S2', ['Programmation Java', 'Algorithmique']),
    ('UE TECHNIQUE D\'EXPRESSION ET METHODOLOGIE DU TRAVAIL', 'TECHNIQUE D\'EXPRESSION ET METHODOLOGIE DU TRAVAIL', 'L1', 'S2', ['Methodologie de travail', 'Technique d\'expression']),
    ('UE Outils Bureautiques 2', 'Outils Bureautiques 2', 'L1', 'S2', ['Outils Bureautiques 2']),
]

print('📚 Création des UE/ECUE...')
for code, name, level, semester, ecues in ues_data:
    ue, created = UE.objects.get_or_create(code=code, name=name, level=level, semester=semester)
    if created:
        print(f'✅ UE créée: {name}')
    for ecue_name in ecues:
        ecue, created = ECUE.objects.get_or_create(name=ecue_name, ue=ue)
        if created:
            print(f'✅ ECUE créée: {ecue_name}')

# Mapping détaillé des dossiers vers ECUE
folder_to_ecue = {
    # S1
    'Suites et Fonctions': ('UE MATHEMATIQUES 1', 'suites et fonctions'),
    'Calcul intégrale': ('UE MATHEMATIQUES 1', 'Calcul intégral'),
    'Elements de logique': ('UE MATHEMATIQUES 2', 'Elements de Logique'),
    'Structure Algébrique': ('UE MATHEMATIQUES 2', 'Structure Algébrique'),
    'Economie': ('UE ECONOMIE', 'Economie générale'),
    'Initiation a l\'informatique': ('UE Initiation à l\'informatique', 'Initiation à l\'informatique'),
    'Initiation à l\'algorithmique': ('UE Initiation à l\'algorithmique', 'Initiation à l\'algorithmique'),
    'Outil Bureautique': ('UE Outils Bureautiques 1', 'Outils Bureautiques 1'),
    'Electronique-Numérique': ('UE Electronique Numérique', 'Electronique Numérique'),
    'Organisations des Entreprises': ('UE Organisations des Entreprises', 'Organisations des Entreprises'),
    
    # S2
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

print('\n🔗 Rattachement des documents...')
updated_count = 0
total_docs = Document.objects.filter(level='L1').count()

for doc in Document.objects.filter(level='L1'):
    file_path = doc.file.name.lower()
    
    # Trouver le dossier correspondant
    folder_name = None
    for folder in folder_to_ecue.keys():
        if folder.lower() in file_path:
            folder_name = folder
            break
    
    if folder_name:
        ue_name, ecue_name = folder_to_ecue[folder_name]
        
        # Déterminer le semestre
        s1_folders = ['Suites et Fonctions', 'Calcul intégrale', 'Elements de logique', 'Structure Algébrique', 'Economie', 'Initiation a l\'informatique', 'Initiation à l\'algorithmique', 'Outil Bureautique', 'Electronique-Numérique', 'Organisations des Entreprises']
        semester = 'S1' if folder_name in s1_folders else 'S2'
        
        # Trouver l'ECUE
        try:
            ecue = ECUE.objects.get(
                name__iexact=ecue_name,
                ue__name__iexact=ue_name,
                ue__level='L1',
                ue__semester=semester
            )
            doc.ecue = ecue
            doc.save()
            updated_count += 1
            print(f'✅ {doc.title} -> {ue_name} - {ecue_name}')
        except ECUE.DoesNotExist:
            print(f'❌ ECUE non trouvée: {ue_name} - {ecue_name} ({semester})')
    else:
        print(f'⚠️  Dossier non trouvé pour: {file_path}')

print(f'\n🎉 {updated_count}/{total_docs} documents rattachés aux ECUE!')

# Vérifier les UE avec une seule ECUE (pour l'auto-sélection)
print('\n🔍 UE avec une seule ECUE (auto-sélection):')
for ue in UE.objects.filter(level='L1'):
    ecue_count = ue.ecues.count()
    if ecue_count == 1:
        print(f'✅ {ue.name} -> {ue.ecues.first().name} ({ue.semester})')
    elif ecue_count > 1:
        print(f'📚 {ue.name} -> {ecue_count} ECUEs ({ue.semester})')
    else:
        print(f'❌ {ue.name} -> Aucune ECUE ({ue.semester})')
