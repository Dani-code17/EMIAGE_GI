"""Crée un compte « éditeur JI » : accès admin limité à la Journée d'Intégration.

Ce compte est *staff* (il peut se connecter à /admin/) mais n'a **aucune**
permission globale : uniquement les droits sur les modèles de la JI
(JIEdition, JIPayment, JIPhoto). Il ne peut donc rien voir d'autre
(étudiants, documents, quiz, prix…), ni accéder à l'admin personnalisé
(/admin-espace/) qui utilise d'autres identifiants.

Usage :
    python manage.py create_ji_editor --username comite_ji --password "MotDePasseFort"
    python manage.py create_ji_editor --username comite_ji --password "..." --email x@y.z
    python manage.py create_ji_editor --username comite_ji --revoke   # retire les droits
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError

JI_MODELS = ['jiedition', 'jipayment', 'jiphoto']
JI_ACTIONS = ['view', 'add', 'change', 'delete']


class Command(BaseCommand):
    help = "Crée (ou met à jour) un compte admin limité à la gestion de la JI."

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help="Nom d'utilisateur du comité")
        parser.add_argument('--password', help='Mot de passe (requis à la création)')
        parser.add_argument('--email', default='', help='Email (optionnel)')
        parser.add_argument('--revoke', action='store_true',
                            help='Retire tous les droits JI de ce compte (le désactive comme éditeur)')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']
        email = options['email']

        perms = list(Permission.objects.filter(
            content_type__app_label='core',
            content_type__model__in=JI_MODELS,
            codename__in=[f'{action}_{model}' for model in JI_MODELS for action in JI_ACTIONS],
        ))

        user = User.objects.filter(username=username).first()
        if user is None:
            if not password:
                raise CommandError("--password est obligatoire pour créer le compte.")
            user = User(username=username, email=email)
            user.set_password(password)
            self.stdout.write(f'Compte créé : {username}')
        else:
            if password:
                user.set_password(password)
            if email:
                user.email = email
            self.stdout.write(f'Compte existant mis à jour : {username}')

        # Staff (accès /admin/) mais JAMAIS superutilisateur
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.save()

        # On repart de zéro : aucune permission, puis uniquement celles de la JI
        user.user_permissions.clear()
        if options['revoke']:
            user.is_staff = False
            user.save(update_fields=['is_staff'])
            self.stdout.write(self.style.WARNING(
                f'Droits retirés : {username} n\'a plus accès à l\'admin.'))
            return

        user.user_permissions.add(*perms)
        self.stdout.write(self.style.SUCCESS(
            f'{len(perms)} permissions accordées (JIEdition, JIPayment, JIPhoto uniquement) :'
        ))
        for perm in sorted(perms, key=lambda p: p.codename):
            self.stdout.write(f'  · {perm.codename}')
        self.stdout.write(self.style.SUCCESS(
            f'\nOK — {username} peut se connecter sur /admin/ et ne verra QUE la section JI.'
        ))
