#!/usr/bin/env python
"""
Script d'import automatique des documents L1
Analyse les noms de dossiers et fichiers pour mapper vers UE/ECUE
"""
import os
import re
from django.core.management.base import BaseCommand
from core.models import Document, UE, ECUE

class Command(BaseCommand):
    help = 'Importe automatiquement les documents L1 depuis media/documents'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simulation sans créer de documents')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        media_path = 'media/documents'
        
        # Mapping des dossiers vers UE/ECUE
        folder_mapping = {
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
        
        # Détection du semestre basée sur le contenu
        s1_keywords = ['Suites et Fonctions', 'Calcul intégrale', 'Elements de logique', 'Structure Algébrique', 'Economie', 'Initiation a l\'informatique', 'Initiation à l\'algorithmique', 'Outil Bureautique', 'Electronique-Numérique']
        s2_keywords = ['Géométrie', 'Matrice-EspaceV', 'Probabilités', 'Statistique', 'LangageR', 'Algorithmique', 'Java', 'Intelligence économique', 'GRH', 'Infographie', 'Anglais', 'Maintenance', 'EOE']
        
        imported_count = 0
        errors = []
        
        for folder_name in os.listdir(media_path):
            folder_path = os.path.join(media_path, folder_name)
            if not os.path.isdir(folder_path):
                continue
                
            # Déterminer le semestre
            if any(kw.lower() in folder_name.lower() for kw in s1_keywords):
                semester = 'S1'
            elif any(kw.lower() in folder_name.lower() for kw in s2_keywords):
                semester = 'S2'
            else:
                self.stdout.write(f"⚠️  Semestre indéterminé pour: {folder_name}")
                continue
            
            # Trouver la UE/ECUE correspondante
            ue_name = None
            ecue_name = None
            
            for pattern, (ue, ecue) in folder_mapping.items():
                if pattern.lower() in folder_name.lower():
                    ue_name = ue
                    ecue_name = ecue
                    break
            
            if not ue_name:
                self.stdout.write(f"⚠️  UE non trouvée pour: {folder_name}")
                continue
            
            # Trouver l'ECUE en base
            try:
                ecue_obj = ECUE.objects.get(
                    name__iexact=ecue_name,
                    ue__name__iexact=ue_name,
                    ue__level='L1',
                    ue__semester=semester
                )
            except ECUE.DoesNotExist:
                self.stdout.write(f"❌ ECUE non trouvée: {ue_name} - {ecue_name} ({semester})")
                continue
            except ECUE.MultipleObjectsReturned:
                ecue_obj = ECUE.objects.filter(
                    name__iexact=ecue_name,
                    ue__name__iexact=ue_name,
                    ue__level='L1',
                    ue__semester=semester
                ).first()
                self.stdout.write(f"⚠️  Plusieurs ECUE trouvées, utilisation de la première: {ecue_obj}")
            
            # Analyser les fichiers du dossier
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    # Déterminer la catégorie
                    category = self.detect_category(filename)
                    
                    # Générer un titre
                    title = self.generate_title(filename, folder_name)
                    
                    if dry_run:
                        self.stdout.write(f"📄 [DRY-RUN] {title} -> {ue_name} - {ecue_name} ({category})")
                    else:
                        try:
                            # Créer le document
                            doc = Document.objects.create(
                                title=title,
                                description=f"Document importé depuis {folder_name}",
                                category=category,
                                level='L1',
                                semester=semester,
                                ecue=ecue_obj,
                                file=file_path
                            )
                            imported_count += 1
                            self.stdout.write(f"✅ Importé: {title}")
                        except Exception as e:
                            error_msg = f"❌ Erreur import {filename}: {str(e)}"
                            errors.append(error_msg)
                            self.stdout.write(error_msg)
        
        # Résumé
        self.stdout.write(f"\n📊 Résumé:")
        self.stdout.write(f"✅ Documents importés: {imported_count}")
        if errors:
            self.stdout.write(f"❌ Erreurs: {len(errors)}")
            for error in errors:
                self.stdout.write(f"   {error}")
    
    def detect_category(self, filename):
        """Détecte la catégorie basée sur le nom du fichier"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ['examen', 'exam', 'sujet', 'session']):
            return 'EXAMS'
        elif any(word in filename_lower for word in ['td', 'tp', 'travaux', 'exercice', 'correction']):
            return 'TD_TP'
        elif any(word in filename_lower for word in ['cours', 'cm', 'chapitre', 'chap', 'support']):
            return 'COURS'
        elif any(word in filename_lower for word in ['maquette', 'planning', 'programme']):
            return 'MAQUETTES'
        else:
            return 'COURS'  # Par défaut
    
    def generate_title(self, filename, folder_name):
        """Génère un titre lisible à partir du nom de fichier"""
        # Enlever l'extension
        name = os.path.splitext(filename)[0]
        
        # Remplacer les underscores et tirets par des espaces
        name = re.sub(r'[_\-]+', ' ', name)
        
        # Capitaliser les mots
        words = name.split()
        title = ' '.join(word.capitalize() for word in words)
        
        # Limiter la longueur
        if len(title) > 100:
            title = title[:97] + '...'
        
        return title
