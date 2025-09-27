#!/usr/bin/env python
"""
Script d'import automatique des documents L1
Analyse les noms de dossiers et fichiers pour mapper vers UE/ECUE
"""
import os
import re
import unicodedata
from django.core.management.base import BaseCommand
from core.models import Document, UE, ECUE

class Command(BaseCommand):
    help = 'Importe automatiquement les documents L1 depuis media/documents'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simulation sans créer de documents')
        parser.add_argument('--only-semester', default=None, help='Limiter l\'import à un semestre précis (ex: S1 ou S2)')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        only_semester = options['only_semester']
        media_path = 'media/documents'
        
        # Mapping des dossiers vers UE/ECUE
        folder_mapping = {
            # S1
            'Suites et Fonctions': ('UE MATHEMATIQUES 1', 'suites et fonctions'),
            'Calcul intégrale': ('UE MATHEMATIQUES 1', 'Calcul intégral'),
            'Elements de logique': ('UE MATHEMATIQUES 2', 'Elements de Logique'),
            'Structure Algébrique': ('UE MATHEMATIQUES 2', 'Structure Algébrique'),
            'Economie': ('UE ECONOMIE', 'Economie générale'),
            'EOE': ('UE Organisations des Entreprises', 'Organisations des Entreprises'),
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
        }
        
        # Détection du semestre basée sur le contenu
        s1_keywords = ['Suites et Fonctions', 'Calcul intégrale', 'Elements de logique', 'Structure Algébrique', 'Economie', 'EOE', 'Initiation a l\'informatique', 'Initiation à l\'algorithmique', 'Outil Bureautique', 'Electronique-Numérique']
        s2_keywords = ['Géométrie', 'Matrice-EspaceV', 'Probabilités', 'Statistique', 'LangageR', 'Algorithmique', 'Java', 'Intelligence économique', 'GRH', 'Infographie', 'Anglais', 'Maintenance']
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
                self.stdout.write(f"[WARN] Semestre indéterminé pour: {folder_name}")
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
                self.stdout.write(f"[WARN] UE non trouvée pour: {folder_name}")
                continue
            
            # Si un semestre précis est demandé, ignorer les dossiers d\'un autre semestre
            if only_semester and semester != only_semester:
                continue

            # Trouver l'ECUE en base
            def normalize(s: str) -> str:
                if not isinstance(s, str):
                    return ''
                s = unicodedata.normalize('NFKD', s)
                s = ''.join(ch for ch in s if not unicodedata.combining(ch))
                return re.sub(r"\s+", " ", s).strip().lower()

            try:
                ecue_obj = ECUE.objects.get(
                    name__iexact=ecue_name,
                    ue__name__iexact=ue_name,
                    ue__level='L1',
                    ue__semester=semester
                )
            except ECUE.DoesNotExist:
                # Fallback: recherche tolérante aux accents/espaces
                target_ue_norm = normalize(ue_name)
                target_ecue_norm = normalize(ecue_name)
                candidates = ECUE.objects.filter(
                    ue__level='L1', ue__semester=semester
                ).select_related('ue')
                best = None
                for e in candidates:
                    if normalize(e.ue.name) == target_ue_norm and normalize(e.name) == target_ecue_norm:
                        best = e
                        break
                if not best:
                    # Essayer un contains large si égalité stricte échoue
                    for e in candidates:
                        if target_ue_norm in normalize(e.ue.name) and target_ecue_norm in normalize(e.name):
                            best = e
                            break
                if not best:
                    self.stdout.write(f"[ERR] ECUE non trouvée: {ue_name} - {ecue_name} ({semester})")
                    continue
                ecue_obj = best
            except ECUE.MultipleObjectsReturned:
                ecue_obj = ECUE.objects.filter(
                    name__iexact=ecue_name,
                    ue__name__iexact=ue_name,
                    ue__level='L1',
                    ue__semester=semester
                ).first()
                self.stdout.write(f"[WARN] Plusieurs ECUE trouvées, utilisation de la première: {ecue_obj}")
            
            # Analyser les fichiers du dossier
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    # Déterminer la catégorie
                    category = self.detect_category(filename)
                    
                    # Générer un titre
                    title = self.generate_title(filename, folder_name)
                    
                    # Éviter les doublons exacts (même titre, niveau, semestre, ECUE)
                    existing = Document.objects.filter(
                        title=title,
                        level='L1',
                        semester=semester,
                        ecue=ecue_obj
                    ).first()
                    if existing:
                        self.stdout.write(f"[SKIP] Déjà présent: {title} -> {ue_name} - {ecue_name}")
                        continue

                    if dry_run:
                        self.stdout.write(f"[DRY-RUN] {title} -> {ue_name} - {ecue_name} ({category})")
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
                            self.stdout.write(f"[OK] Importé: {title}")
                        except Exception as e:
                            error_msg = f"[ERR] Erreur import {filename}: {str(e)}"
                            errors.append(error_msg)
                            self.stdout.write(error_msg)
        
        # Résumé
        self.stdout.write(f"\n[SUMMARY]")
        self.stdout.write(f"[OK] Documents importés: {imported_count}")
        if errors:
            self.stdout.write(f"[ERR] Erreurs: {len(errors)}")
            for error in errors:
                self.stdout.write(f"   {error}")
    
    def detect_category(self, filename):
        """Détecte la catégorie basée sur le nom du fichier"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ['examen', 'exam', 'sujet', 'session', 'devoir']):
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
