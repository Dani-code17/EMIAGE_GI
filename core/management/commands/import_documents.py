#!/usr/bin/env python
"""
Script d'import automatique des documents (multi-niveaux : L1/L2/L3/M1/M2)

Analyse les dossiers de media/documents pour mapper vers UE/ECUE, puis classe
chaque fichier en COURS / TD_TP / EXAMS / MAQUETTES selon son nom.

Usage :
    python manage.py import_documents --dry-run            # simulation
    python manage.py import_documents --level L1           # un niveau
    python manage.py import_documents --folder "Anglais"   # un dossier de matière
    python manage.py import_documents --only-semester S1   # un semestre (S1..S10)
"""
import os
import re
import unicodedata
from django.core.management.base import BaseCommand
from core.models import Document, UE, ECUE

# Mapping dossier -> (niveau, semestre, nom UE, nom ECUE)
# Ajouter ici les nouvelles matières (L2, L3, M1...) au fur et à mesure.
FOLDER_MAPPING = {
    # L1 S1
    'Suites et Fonctions': ('L1', 'S1', 'UE MATHEMATIQUES 1', 'suites et fonctions'),
    'Calcul intégrale': ('L1', 'S1', 'UE MATHEMATIQUES 1', 'Calcul intégral'),
    'Elements de logique': ('L1', 'S1', 'UE MATHEMATIQUES 2', 'Elements de Logique'),
    'Structure Algébrique': ('L1', 'S1', 'UE MATHEMATIQUES 2', 'Structure Algébrique'),
    'Economie': ('L1', 'S1', 'UE ECONOMIE', 'Economie générale'),
    'EOE': ('L1', 'S1', 'UE Organisations des Entreprises', 'Organisations des Entreprises'),
    'Initiation a l\'informatique': ('L1', 'S1', 'UE Initiation à l\'informatique', 'Initiation à l\'informatique'),
    'Initiation à l\'algorithmique': ('L1', 'S1', 'UE Initiation à l\'algorithmique', 'Initiation à l\'algorithmique'),
    'Outil Bureautique': ('L1', 'S1', 'UE Outils Bureautiques 1', 'Outils Bureautiques 1'),
    'Electronique-Numérique': ('L1', 'S1', 'UE Electronique Numérique', 'Electronique Numérique'),

    # L1 S2
    'Géométrie': ('L1', 'S2', 'UE MATHEMATIQUES 3', 'Géometrie'),
    'Matrice-EspaceV': ('L1', 'S2', 'UE MATHEMATIQUES 3', 'Calcul matriciel'),
    'Probabilités': ('L1', 'S2', 'UE PROBABILITES ET STATISTIQUE 1', 'Probabilité'),
    'Statistique': ('L1', 'S2', 'UE PROBABILITES ET STATISTIQUE 1', 'Statistique'),
    'LangageR': ('L1', 'S2', 'UE PROBABILITES ET STATISTIQUE 1', 'Langage R'),
    'Algorithmique': ('L1', 'S2', 'UE ALGORITHMIQUE ET PROGRAMMATION', 'Algorithmique'),
    'Java': ('L1', 'S2', 'UE ALGORITHMIQUE ET PROGRAMMATION', 'Programmation Java'),
    'Intelligence économique': ('L1', 'S2', 'UE Intelligence économique', 'Intelligence économique'),
    'GRH': ('L1', 'S2', 'UE Gestion des ressources humaines', 'Gestion des ressources humaines'),
    'Infographie': ('L1', 'S2', 'UE Infographie(Montage vidéo,etc..)', 'Infographie(Montage vidéo,etc..)'),
    'Anglais': ('L1', 'S2', 'UE Anglais', 'Anglais'),
    'Maintenance': ('L1', 'S2', 'UE Atelier de maintenance', 'Atelier de maintenance'),
}


def normalize(s: str) -> str:
    """Normalise une chaîne : minuscules, sans accents, espaces uniques."""
    if not isinstance(s, str):
        return ''
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", s).strip().lower()


class Command(BaseCommand):
    help = 'Importe automatiquement les documents depuis media/documents (multi-niveaux)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simulation sans créer de documents')
        parser.add_argument('--level', default=None, choices=['L1', 'L2', 'L3', 'M1', 'M2'],
                            help='Limiter l\'import à un niveau')
        parser.add_argument('--only-semester', default=None,
                            help='Limiter l\'import à un semestre précis (ex: S1 ou S4)')
        parser.add_argument('--folder', default=None,
                            help='Importer un seul dossier de matière (ex: "Anglais")')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        only_level = options['level']
        only_semester = options['only_semester']
        only_folder = options['folder']
        media_path = 'media/documents'

        imported_count = 0
        skipped_count = 0
        errors = []

        # --- 1) Maquettes à la racine de media/documents -------------------
        imported_count += self.import_root_maquettes(media_path, dry_run)

        # --- 2) Dossiers de matières ----------------------------------------
        for folder_name in sorted(os.listdir(media_path)):
            folder_path = os.path.join(media_path, folder_name)
            if not os.path.isdir(folder_path):
                continue  # fichiers à la racine déjà traités

            if only_folder and normalize(folder_name) != normalize(only_folder):
                continue

            # Résoudre le mapping dossier -> UE/ECUE
            entry = None
            for pattern, mapped in FOLDER_MAPPING.items():
                if pattern.lower() in folder_name.lower():
                    entry = mapped
                    break

            if not entry:
                self.stdout.write(f"[WARN] Aucun mapping UE/ECUE pour: {folder_name}")
                continue

            level, semester, ue_name, ecue_name = entry

            # Filtres niveau / semestre
            if only_level and level != only_level:
                continue
            if only_semester and semester != only_semester:
                continue

            ecue_obj = self.find_ecue(ue_name, ecue_name, level, semester)
            if ecue_obj is None:
                errors.append(f"ECUE introuvable: {ue_name} - {ecue_name} ({level} {semester})")
                continue

            # Importer chaque fichier du dossier
            for filename in sorted(os.listdir(folder_path)):
                if not os.path.isfile(os.path.join(folder_path, filename)):
                    continue
                imported_count += self.import_file(
                    filename, folder_name, level, semester, ecue_obj, dry_run
                )

        # Résumé
        self.stdout.write(self.style.SUCCESS(
            f"\n[SUMMARY] Documents importés: {imported_count}"
        ))
        if errors:
            self.stdout.write(self.style.WARNING(f"[ERR] Erreurs: {len(errors)}"))
            for error in errors:
                self.stdout.write(f"   {error}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def import_root_maquettes(self, media_path, dry_run):
        """Importe les fichiers maquettes posés à la racine de media/documents."""
        count = 0
        for filename in sorted(os.listdir(media_path)):
            file_path = os.path.join(media_path, filename)
            if not os.path.isfile(file_path):
                continue

            # Détecter le niveau dans le nom (ex: "A-MAQUETTE L1 MIAGE.pdf",
            # "EXECUTION.Maquettes_MIAGE-L2_25-26.xlsx")
            match = re.search(r'(?i)(L[123]|M[12])(?=[^A-Za-z0-9]|$)', filename)
            if not match:
                self.stdout.write(f"[SKIP] Fichier racine sans niveau identifiable: {filename}")
                continue

            level = match.group(1).upper()
            title = self.generate_title(filename, folder_name=None)
            rel_path = f'documents/{filename}'

            # Dédoublonnage par fichier physique (les titres peuvent différer)
            existing = Document.objects.filter(
                file=rel_path, category='MAQUETTES'
            ).first()
            if existing:
                self.stdout.write(f"[SKIP] Maquette déjà présente: {title}")
                continue

            if dry_run:
                self.stdout.write(f"[DRY-RUN] Maquette {level}: {title}")
                count += 1
                continue

            Document.objects.create(
                title=title,
                description=f"Maquette {level} importée depuis la racine de media/documents",
                category='MAQUETTES',
                level=level,
                semester=self.semester_for_maquette(level),
                ecue=None,
                file=rel_path,
            )
            count += 1
            self.stdout.write(f"[OK] Maquette importée: {title} ({level})")
        return count

    def semester_for_maquette(self, level):
        """Semestre par défaut pour une maquette de niveau (premier semestre)."""
        return {
            'L1': 'S1', 'L2': 'S3', 'L3': 'S5', 'M1': 'S7', 'M2': 'S9',
        }[level]

    def find_ecue(self, ue_name, ecue_name, level, semester):
        """Trouve l'ECUE correspondante (recherche stricte puis tolérante aux accents)."""
        try:
            return ECUE.objects.get(
                name__iexact=ecue_name,
                ue__name__iexact=ue_name,
                ue__level=level,
                ue__semester=semester,
            )
        except ECUE.DoesNotExist:
            pass
        except ECUE.MultipleObjectsReturned:
            return ECUE.objects.filter(
                name__iexact=ecue_name,
                ue__name__iexact=ue_name,
                ue__level=level,
                ue__semester=semester,
            ).first()

        # Fallback : recherche normalisée (accents/espaces)
        target_ue_norm = normalize(ue_name)
        target_ecue_norm = normalize(ecue_name)
        for e in ECUE.objects.filter(
            ue__level=level, ue__semester=semester
        ).select_related('ue'):
            if normalize(e.ue.name) == target_ue_norm and normalize(e.name) == target_ecue_norm:
                return e
        return None

    def import_file(self, filename, folder_name, level, semester, ecue_obj, dry_run):
        """Importe un fichier d'un dossier de matière dans l'ECUE cible."""
        category = self.detect_category(filename)
        title = self.generate_title(filename, folder_name)
        rel_path = f'documents/{folder_name}/{filename}'

        # Éviter les doublons exacts (même titre, niveau, semestre, ECUE)
        existing = Document.objects.filter(
            title=title, level=level, semester=semester, ecue=ecue_obj
        ).first()
        if existing:
            self.stdout.write(f"[SKIP] Déjà présent: {title}")
            return 0

        if dry_run:
            self.stdout.write(f"[DRY-RUN] {title} -> {ecue_obj.ue.code} - {ecue_obj.name} ({category})")
            return 1

        try:
            Document.objects.create(
                title=title,
                description=f"Document importé depuis {folder_name}",
                category=category,
                level=level,
                semester=semester,
                ecue=ecue_obj,
                file=rel_path,
            )
            self.stdout.write(f"[OK] Importé: {title}")
            return 1
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERR] Erreur import {filename}: {str(e)}"))
            return 0

    def detect_category(self, filename):
        """Détecte la catégorie basée sur le nom du fichier."""
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
        """Génère un titre lisible à partir du nom de fichier."""
        name = os.path.splitext(filename)[0]
        name = re.sub(r'[_\-]+', ' ', name)
        words = name.split()
        title = ' '.join(word.capitalize() for word in words)
        if len(title) > 100:
            title = title[:97] + '...'
        return title
