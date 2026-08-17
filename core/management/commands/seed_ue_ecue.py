#!/usr/bin/env python
"""
Seed de la structure UE/ECUE (idempotent).

Peuple les UE et leurs ECUE pour les niveaux/semestres renseignés dans
STRUCTURE ci-dessous. Les slugs sont générés explicitement (les modèles
historiques / commandes ne dépendent pas du save() custom).

Usage :
    python manage.py seed_ue_ecue --dry-run     # simulation
    python manage.py seed_ue_ecue --level L2    # un niveau seulement
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import UE, ECUE

# Structure (niveau, semestre) -> {nom UE: [noms ECUE]}
# L3 / M1 / M2 : à compléter quand les maquettes seront fournies.
STRUCTURE = {
    # ------------------------------- L1 S1 ----------------------------------
    ('L1', 'S1'): {
        'UE ECONOMIE': ['Economie générale', 'Économie 2'],
        'UE Electronique Numérique': ['Electronique Numérique'],
        "UE Initiation à l'algorithmique": ["Initiation à l'algorithmique"],
        "UE Initiation à l'informatique": ["Initiation à l'informatique"],
        'UE MATHEMATIQUES 1': ['Calcul intégral', 'suites et fonctions'],
        'UE MATHEMATIQUES 2': ['Elements de Logique', 'Structure Algébrique'],
        'UE Organisations des Entreprises': ['Organisations des Entreprises'],
        'UE Outils Bureautiques 1': ['Outils Bureautiques 1'],
    },
    # ------------------------------- L1 S2 ----------------------------------
    ('L1', 'S2'): {
        'UE ALGORITHMIQUE ET PROGRAMMATION': ['Algorithmique', 'Programmation Java'],
        'UE Anglais': ['Anglais'],
        'UE Atelier de maintenance': ['Atelier de maintenance'],
        'UE Gestion des ressources humaines': ['Gestion des ressources humaines'],
        'UE Infographie(Montage vidéo,etc..)': ['Infographie(Montage vidéo,etc..)'],
        'UE Intelligence économique': ['Intelligence économique'],
        'UE MATHEMATIQUES 3': ['Calcul matriciel', 'Espaces vectoriels', 'Géometrie'],
        'UE Outils Bureautiques 2': ['Outils Bureautiques 2'],
        'UE PROBABILITES ET STATISTIQUE 1': ['Langage R', 'Probabilité', 'Statistique'],
        "UE TECHNIQUE D'EXPRESSION ET METHODOLOGIE DU TRAVAIL": [
            "Technique d'expression", 'Methodologie de travail',
        ],
    },
    # ------------------------------- L2 S3 ----------------------------------
    # Source : EXECUTION.Maquettes_MIAGE-L2_25-26.xlsx (feuille Feuil1)
    ('L2', 'S3'): {
        'Programmation orientée objet': [
            'Fondements de la POO', 'POO en Java', 'outils formels pour l\'informatique',
        ],
        'Mathématiques 4': ['Analyse 3', 'Algèbre'],
        'Probabilités et statistique 2': [
            'Probabilités 2', 'Statistique 2', 'Analyse de données',
        ],
        'Comptabilité generale': [
            'Modèle comptable', 'Opérations comptables', 'Opérations d\'inventaires',
        ],
        'Anglais': ['Anglais'],
    },
    # ------------------------------- L2 S4 ----------------------------------
    ('L2', 'S4'): {
        'Mathématiques 5': ['Arithmétique'],
        'Données semi-structurées et bases de données': [
            'Base de données relationnelles', 'Données semi-structurées',
            'base de données et applications',
        ],
        'Programmation web': ['Programmation web'],
        'Génie logiciel': ['Initiation au Langage SCALA', 'Atelier de Génie Logiciel'],
        'Programmation sous windows': ['Programmation VBA', 'Programmation C#'],
        'Contrôle budgétaire': ['Contrôle budgétaire'],
        'Initiation Python': ['Application à la cryptographie'],
        'Projet': ['Projet'],
    },
}


class Command(BaseCommand):
    help = 'Seed (idempotent) de la structure UE/ECUE pour les niveaux renseignés'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simulation sans écrire en base')
        parser.add_argument('--level', default=None, choices=['L1', 'L2', 'L3', 'M1', 'M2'],
                            help='Ne seed que ce niveau')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        only_level = options['level']

        ue_created = ecue_created = 0
        for (level, semester), ues in STRUCTURE.items():
            if only_level and level != only_level:
                continue
            for ue_name, ecue_names in ues.items():
                ue = UE.objects.filter(level=level, semester=semester, code=ue_name).first()
                ue_new = ue is None
                if ue_new:
                    ue_created += 1
                if dry_run:
                    if ue_new:
                        self.stdout.write(f"[DRY-RUN] UE à créer: {level} {semester} {ue_name}")
                else:
                    ue, _ = UE.objects.get_or_create(
                        level=level, semester=semester, code=ue_name,
                        defaults={
                            'name': ue_name,
                            'slug': slugify(f'{level}-{semester}-{ue_name}-{ue_name}'),
                        },
                    )
                    if ue.name != ue_name:
                        ue.name = ue_name
                        ue.save()

                for ecue_name in ecue_names:
                    exists = not dry_run and ECUE.objects.filter(ue=ue, name=ecue_name).exists()
                    if dry_run:
                        exists = ECUE.objects.filter(ue__level=level, ue__semester=semester,
                                                     ue__code=ue_name, name=ecue_name).exists()
                    if not exists:
                        ecue_created += 1
                    if dry_run and not exists:
                        self.stdout.write(
                            f"[DRY-RUN] ECUE à créer: {level} {semester} {ue_name} -> {ecue_name}"
                        )
                    elif not dry_run and not exists:
                        ECUE.objects.get_or_create(
                            ue=ue, name=ecue_name,
                            defaults={
                                'slug': slugify(f'{level}-{semester}-{ue_name}-{ecue_name}'),
                            },
                        )

        self.stdout.write(self.style.SUCCESS(
            f"[SUMMARY] UE créées: {ue_created} (total {UE.objects.count()}), "
            f"ECUE créées: {ecue_created} (total {ECUE.objects.count()})"
        ))
        if dry_run:
            self.stdout.write("(mode simulation — rien n'a été écrit)")
