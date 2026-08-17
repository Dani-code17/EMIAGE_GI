#!/usr/bin/env python
"""
Script d'import automatique des documents (multi-niveaux : L1/L2/L3/M1/M2)

Analyse les dossiers de media/documents pour mapper vers UE/ECUE, puis classe
chaque fichier en COURS / TD_TP / EXAMS / MAQUETTES selon son nom.

Seuls les fichiers de type document sont importés (voir DOC_EXTENSIONS) ;
les images, CSS, archives, sources de projets, etc. sont ignorés.

Usage :
    python manage.py import_documents --dry-run            # simulation
    python manage.py import_documents --level L2           # un niveau
    python manage.py import_documents --folder "Anglais"   # un dossier de matière
    python manage.py import_documents --only-semester S3   # un semestre (S1..S10)
"""
import os
import re
import sys
import unicodedata
from django.core.management.base import BaseCommand
from core.models import Document, UE, ECUE

# La console Windows (cp1252) ne peut pas encoder certains caractères de noms
# de fichiers (ex: U+2560) ; sans cela, l'import s'interrompt en plein milieu.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Extensions de fichiers considérées comme des documents pédagogiques.
DOC_EXTENSIONS = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.odt', '.odp', '.ods'}

# Mapping dossier -> cible UE/ECUE.
# Valeur possible :
#   - tuple (niveau, semestre, nom UE, nom ECUE) : tous les fichiers du dossier
#   - dict {sous-dossier: (niveau, semestre, nom UE, nom ECUE)} : fichiers
#     dispatchés selon le sous-dossier (ex: Données semi-structurées...)
FOLDER_MAPPING = {
    # ============================ L1 S1 =====================================
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

    # ============================ L1 S2 =====================================
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

    # ============================ L2 S3 =====================================
    'Algèbre': ('L2', 'S3', 'Mathématiques 4', 'Algèbre'),
    'Analyse': ('L2', 'S3', 'Mathématiques 4', 'Analyse 3'),
    'Analyse de donnée': ('L2', 'S3', 'Probabilités et statistique 2', 'Analyse de données'),
    'L2-Anglais': ('L2', 'S3', 'Anglais', 'Anglais'),
    'Comptabilité': ('L2', 'S3', 'Comptabilité generale', 'Comptabilité'),
    'Fondamentaux POO': ('L2', 'S3', 'Programmation orientée objet', 'Fondements de la POO'),
    'Outils formels': ('L2', 'S3', 'Programmation orientée objet', 'outils formels pour l\'informatique'),
    'Probabilité': ('L2', 'S3', 'Probabilités et statistique 2', 'Probabilités 2'),
    'Programmation Orientée Objet Java': ('L2', 'S3', 'Programmation orientée objet', 'POO en Java'),
    'Renforcemnt Java': ('L2', 'S3', 'Programmation orientée objet', 'POO en Java'),
    'L2-Statistique': ('L2', 'S3', 'Probabilités et statistique 2', 'Statistique 2'),

    # ============================ L2 S4 =====================================
    'Arithmétique': ('L2', 'S4', 'Mathématiques 5', 'Arithmétique'),
    'Base de données relationnelles': ('L2', 'S4', 'Données semi-structurées et bases de données', 'Base de données relationnelles'),
    'Contrôle Budgétaire': ('L2', 'S4', 'Contrôle budgétaire', 'Contrôle budgétaire'),
    'Cryptographie': ('L2', 'S4', 'Initiation Python', 'Application à la cryptographie'),
    'Données semi-structurées et bases de données': {
        'Base de données et applications': ('L2', 'S4', 'Données semi-structurées et bases de données', 'base de données et applications'),
        'Base de données relationnelles': ('L2', 'S4', 'Données semi-structurées et bases de données', 'Base de données relationnelles'),
        'Données semi-structurées': ('L2', 'S4', 'Données semi-structurées et bases de données', 'Données semi-structurées'),
    },
    'Génie logiciel': ('L2', 'S4', 'Génie logiciel', 'Atelier de Génie Logiciel'),
    'Programmation Web': ('L2', 'S4', 'Programmation web', 'Programmation web'),
    'scala': ('L2', 'S4', 'Génie logiciel', 'Initiation au Langage SCALA'),

    # ============================ L3 S5 =====================================
    'ALGORITHMIQUE DES GRAPHES': ('L3', 'S5', 'ALGORITHMIQUE DES GRAPHES', 'ALGORITHMIQUE DES GRAPHES'),
    'BASE DE DONNEES AVANCEES': ('L3', 'S5', 'BASE DE DONNEES AVANCEES', 'BASE DE DONNEES AVANCEES'),
    'COMPTABILITE ANALYTIQUE': ('L3', 'S5', 'COMPTABILITE ANALYTIQUE', 'COMPTABILITE ANALYTIQUE'),
    'COURS DE PROGRAMMATION': ('L3', 'S5', 'COURS DE PROGRAMMATION', 'COURS DE PROGRAMMATION'),
    'PROGRAMMATION LINEAIRE': ('L3', 'S5', 'PROGRAMMATION LINEAIRE', 'PROGRAMMATION LINEAIRE'),
    'PROGRAMMATION WEB CLIENT': ('L3', 'S5', 'PROGRAMMATION WEB CLIENT', 'PROGRAMMATION WEB CLIENT'),
    'SYSTEME D\'EXPLOITATION': ('L3', 'S5', 'SYSTEME D\'EXPLOITATION', 'SYSTEME D\'EXPLOITATION'),
    'UNIX_C': ('L3', 'S5', 'UNIX_C', 'UNIX_C'),

    # ============================ L3 S6 =====================================
    'ANALYSE DE DONNEES': ('L3', 'S6', 'ANALYSE DE DONNEES', 'ANALYSE DE DONNEES'),
    'L3-Anglais': ('L3', 'S6', 'ANGLAIS', 'ANGLAIS'),
    'ENVIRONNEMENT JURIDIQUE': ('L3', 'S6', 'ENVIRONNEMENT JURIDIQUE', 'ENVIRONNEMENT JURIDIQUE'),
    'FILE D\'ATTENTE ET GESTION DE STOCKS': ('L3', 'S6', 'FILE D\'ATTENTE ET GESTION DE STOCKS', 'FILE D\'ATTENTE ET GESTION DE STOCKS'),
    'GEESTION FINANCIERE': ('L3', 'S6', 'GESTION FINANCIERE', 'GESTION FINANCIERE'),
    'GENIE LOGICIEL JAVA': ('L3', 'S6', 'GENIE LOGICIEL JAVA', 'GENIE LOGICIEL JAVA'),
    'INTERNET-INTRANET': ('L3', 'S6', 'INTERNET-INTRANET', 'INTERNET-INTRANET'),
    'PROGRAMMATION D\'APPLICATION': ('L3', 'S6', 'PROGRAMMATION D\'APPLICATION', 'PROGRAMMATION D\'APPLICATION'),
    'RESEAU': ('L3', 'S6', 'RESEAU', 'RESEAU'),
    'THEORIE DU LANGUAGE': ('L3', 'S6', 'THEORIE DU LANGUAGE', 'THEORIE DU LANGUAGE'),
    'UML': ('L3', 'S6', 'UML', 'UML'),
}


def normalize(s: str) -> str:
    """Normalise une chaîne : minuscules, sans accents, apostrophes unifiées."""
    if not isinstance(s, str):
        return ''
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    # Unifier les apostrophes (droite ', courbe ’, guillemet '02BC, etc.)
    s = s.replace('\u2019', "'").replace('\u2018', "'").replace('\u02bc', "'")
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
        only_folder = normalize(options['folder']) if options['folder'] else None
        media_path = 'media/documents'

        imported_count = 0
        errors = []

        # --- 1) Maquettes à la racine de media/documents -------------------
        imported_count += self.import_root_maquettes(media_path, dry_run)

        # --- 2) Dossiers de matières ----------------------------------------
        for folder_name in sorted(os.listdir(media_path)):
            folder_path = os.path.join(media_path, folder_name)
            if not os.path.isdir(folder_path):
                continue  # fichiers à la racine déjà traités

            entry = self.match_folder(folder_name)
            if entry is None:
                self.stdout.write(f"[WARN] Aucun mapping UE/ECUE pour: {folder_name}")
                continue

            if only_folder and normalize(folder_name) != only_folder:
                continue

            if isinstance(entry, dict):
                # Sous-dossiers -> ECUE distinctes
                for sub_name, sub_entry in entry.items():
                    sub_path = os.path.join(folder_path, sub_name)
                    if not os.path.isdir(sub_path):
                        self.stdout.write(f"[WARN] Sous-dossier absent: {sub_name}")
                        continue
                    level, semester, ue_name, ecue_name = sub_entry
                    if only_level and level != only_level:
                        continue
                    if only_semester and semester != only_semester:
                        continue
                    ecue_obj = self.find_ecue(ue_name, ecue_name, level, semester)
                    if ecue_obj is None:
                        errors.append(f"ECUE introuvable: {ue_name} - {ecue_name} ({level} {semester})")
                        continue
                    for rel in self.walk_docs(sub_path):
                        imported_count += self.import_file(
                            rel, folder_name, level, semester, ecue_obj, dry_run
                        )
            else:
                level, semester, ue_name, ecue_name = entry
                if only_level and level != only_level:
                    continue
                if only_semester and semester != only_semester:
                    continue
                ecue_obj = self.find_ecue(ue_name, ecue_name, level, semester)
                if ecue_obj is None:
                    errors.append(f"ECUE introuvable: {ue_name} - {ecue_name} ({level} {semester})")
                    continue
                for rel in self.walk_docs(folder_path):
                    imported_count += self.import_file(
                        rel, folder_name, level, semester, ecue_obj, dry_run
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
    def match_folder(self, folder_name):
        """Trouve l'entrée du mapping par correspondance normalisée exacte."""
        target = normalize(folder_name)
        for pattern, entry in FOLDER_MAPPING.items():
            if normalize(pattern) == target:
                return entry
        return None

    def walk_docs(self, folder_path):
        """Parcourt récursivement un dossier et renvoie les chemins relatifs
        (depuis media/documents) des fichiers de type document."""
        rels = []
        for root, dirs, files in os.walk(folder_path):
            for f in sorted(files):
                if f.startswith('~$'):
                    continue  # fichiers temporaires Word/Office
                if os.path.splitext(f)[1].lower() in DOC_EXTENSIONS:
                    abs_path = os.path.join(root, f)
                    rels.append(os.path.relpath(abs_path, 'media/documents'))
        return sorted(rels)

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

    def import_file(self, rel_path, folder_name, level, semester, ecue_obj, dry_run):
        """Importe un fichier (chemin relatif documents/...) dans l'ECUE cible."""
        filename = os.path.basename(rel_path)
        category = self.detect_category(filename)
        title = self.generate_title(filename, folder_name)
        rel_path = rel_path.replace('\\', '/')
        # Garantir le préfixe documents/
        if not rel_path.startswith('documents/'):
            rel_path = f'documents/{rel_path}'

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
