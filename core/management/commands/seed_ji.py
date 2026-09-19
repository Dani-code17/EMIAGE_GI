"""Seed d'une édition de la Journée d'Intégration (idempotent).

Usage : python manage.py seed_ji
"""
from django.core.management.base import BaseCommand
from core.models import JIEdition, JIPayment, JIPhoto


class Command(BaseCommand):
    help = 'Crée une édition de la JI (exemple à compléter depuis l\'admin).'

    def handle(self, *args, **options):
        ed, created = JIEdition.objects.get_or_create(
            year='2026',
            defaults={
                'title': "Journée d'Intégration MIAGE 2026",
                'subtitle': "L'intégration : la meilleure addition à ta vie étudiante !",
                'status': 'inscriptions',
                'is_featured': True,
                'order': 100,
                'location': 'Amphi IRMA, Abidjan · Groupe Cestia 2EP',
                'description': (
                    "🚀 Panel, conférences, débats, MIAGE Project, activités sportives et culturelles…\n"
                    "La Journée d'Intégration réunit toute la communauté MIAGE de l'UFHB :\n\n"
                    "• Accueil et présentation de la filière\n"
                    "• Panel et conférences avec des professionnels\n"
                    "• MIAGE Project (présentation des projets étudiants)\n"
                    "• Moments de partage, photos et surprises\n\n"
                    "Renseigne ici la date, l'heure et les détails pratiques depuis l'administration."
                ),
                'price': 'À définir',
            },
        )
        if created:
            self.stdout.write(f'[OK] Édition créée : {ed}')
        else:
            self.stdout.write(f'[SKIP] Édition déjà présente : {ed}')

        # Moyens de paiement d'exemple (numéros à remplacer par le comité)
        if not ed.payments.exists():
            JIPayment.objects.create(
                edition=ed, label='Orange Money', number='À renseigner', holder='Comité JI-MIAGE',
                instructions="Après le paiement, envoie la capture d'écran au comité.",
                is_active=True, order=1,
            )
            JIPayment.objects.create(
                edition=ed, label='Wave', number='À renseigner', holder='Comité JI-MIAGE',
                instructions="Mentionne « JI 2026 + ton nom » dans le motif.",
                is_active=True, order=2,
            )
            self.stdout.write('[OK] Moyens de paiement d\'exemple créés (numéros à compléter)')
        else:
            self.stdout.write('[SKIP] Moyens de paiement déjà présents')

        self.stdout.write(self.style.SUCCESS(
            f"[SUMMARY] Éditions: {JIEdition.objects.count()} | "
            f"Paiements: {JIPayment.objects.count()} | Photos: {JIPhoto.objects.count()}"
        ))
