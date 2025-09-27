import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emiage_web.settings')
django.setup()

from core.models import Document, UE, ECUE

print('🔧 Recréation des UE et ECUE...')

# Supprimer les anciennes UE/ECUE
UE.objects.filter(level='L1').delete()
print('Anciennes UE/ECUE supprimées')

# Créer les UE et ECUE pour L1 S1
ues_s1 = [
    ('UE MATHEMATIQUES 1', 'MATHEMATIQUES 1', ['suites et fonctions', 'Calcul intégral']),
    ('UE MATHEMATIQUES 2', 'MATHEMATIQUES 2', ['Elements de Logique', 'Structure Algébrique']),
    ('UE ECONOMIE', 'ECONOMIE', ['Economie générale']),
    ('UE Initiation à l\'informatique', 'Initiation à l\'informatique', ['Initiation à l\'informatique']),
    ('UE Initiation à l\'algorithmique', 'Initiation à l\'algorithmique', ['Initiation à l\'algorithmique']),
    ('UE Outils Bureautiques 1', 'Outils Bureautiques 1', ['Outils Bureautiques 1']),
    ('UE Organisations des Entreprises', 'Organisations des Entreprises', ['Organisations des Entreprises']),
    ('UE Electronique Numérique', 'Electronique Numérique', ['Electronique Numérique']),
]

# Créer les UE et ECUE pour L1 S2
ues_s2 = [
    ('UE MATHEMATIQUES 3', 'MATHEMATIQUES 3', ['Géometrie', 'Calcul matriciel', 'Espaces vectoriels']),
    ('UE PROBABILITES ET STATISTIQUE 1', 'PROBABILITES ET STATISTIQUE 1', ['Probabilité', 'Statistique', 'Langage R']),
    ('UE ALGORITHMIQUE ET PROGRAMMATION', 'ALGORITHMIQUE ET PROGRAMMATION', ['Programmation Java', 'Algorithmique']),
    ('UE Intelligence économique', 'Intelligence économique', ['Intelligence économique']),
    ('UE Gestion des ressources humaines', 'Gestion des ressources humaines', ['Gestion des ressources humaines']),
    ('UE Outils Bureautiques 2', 'Outils Bureautiques 2', ['Outils Bureautiques 2']),
    ('UE Infographie(Montage vidéo,etc..)', 'Infographie(Montage vidéo,etc..)', ['Infographie(Montage vidéo,etc..)']),
    ('UE Anglais', 'Anglais', ['Anglais']),
    ('UE Atelier de maintenance', 'Atelier de maintenance', ['Atelier de maintenance']),
    ('UE TECHNIQUE D\'EXPRESSION ET METHODOLOGIE DU TRAVAIL', 'TECHNIQUE D\'EXPRESSION ET METHODOLOGIE DU TRAVAIL', ['Methodologie de travail', 'Technique d\'expression']),
]

# Créer les UE/ECUE S1
for code, name, ecues in ues_s1:
    ue, _ = UE.objects.get_or_create(code=code, name=name, level='L1', semester='S1')
    if not ecues:
        ECUE.objects.get_or_create(code='', name=name, ue=ue)
    else:
        for e in ecues:
            ECUE.objects.get_or_create(code='', name=e, ue=ue)

# Créer les UE/ECUE S2
for code, name, ecues in ues_s2:
    ue, _ = UE.objects.get_or_create(code=code, name=name, level='L1', semester='S2')
    if not ecues:
        ECUE.objects.get_or_create(code='', name=name, ue=ue)
    else:
        for e in ecues:
            ECUE.objects.get_or_create(code='', name=e, ue=ue)

print('✅ UE et ECUE créées!')

# Maintenant rattacher les documents
print('🔧 Rattachement des documents...')

folder_to_ecue = {
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
    for folder in folder_to_ecue.keys():
        if folder.lower() in file_path.lower():
            folder_name = folder
            break
    
    if folder_name:
        ue_name, ecue_name = folder_to_ecue[folder_name]
        
        # Déterminer le semestre
        s1_folders = ['Suites et Fonctions', 'Calcul intégrale', 'Elements de logique', 'Structure Algébrique', 'Economie', 'Initiation a l\'informatique', 'Initiation à l\'algorithmique', 'Outil Bureautique', 'Electronique-Numérique']
        semester = 'S1' if folder_name in s1_folders else 'S2'
        
        # Trouver l'ECUE
        try:
            ecue = ECUE.objects.get(
                name__iexact=ecue_name,
                ue__name__iexact=ue_name,
                ue__level='L1',
                ue__semester=semester
            )
            
            # Mettre à jour le document
            doc.ecue = ecue
            doc.save()
            updated_count += 1
            print(f'✅ {doc.title} -> {ue_name} - {ecue_name}')
            
        except ECUE.DoesNotExist:
            print(f'❌ ECUE non trouvée: {ue_name} - {ecue_name} ({semester})')
    else:
        print(f'⚠️  Dossier non trouvé pour: {file_path}')

print(f'\n🎉 {updated_count} documents rattachés aux ECUE!')
