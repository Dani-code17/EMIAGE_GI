"""Envoie les fichiers de media/ vers Cloudflare R2 (compatible S3).

Usage :
    python manage.py upload_media_to_s3 [--dry-run] [--force] [--check]

- Par défaut : uploade uniquement les fichiers absents du bucket
  (les clés correspondent au chemin relatif, ex: documents/...).
- --dry-run : affiche ce qui serait envoyé sans rien transférer.
- --force : ré-envoie tout, même si la clé existe déjà.
- --check : vérifie que chaque fichier référencé par la base existe dans
  le bucket (sans rien envoyer).

Variables d'environnement requises (comme pour le serveur) :
    USE_S3=True, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME, AWS_S3_ENDPOINT_URL
"""
import os
import sys
from collections import Counter

from django.conf import settings
from django.core.management.base import BaseCommand

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class Command(BaseCommand):
    help = 'Envoie les fichiers de media/ vers Cloudflare R2 (compatible S3).'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simule sans transférer.')
        parser.add_argument('--force', action='store_true', help='Ré-envoie tout, même si présent.')
        parser.add_argument('--check', action='store_true', help='Vérifie la présence des fichiers dans le bucket.')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        check = options['check']

        if not settings.USE_S3:
            self.stderr.write('USE_S3 n\'est pas activé. Définissez USE_S3=True et les variables AWS_* '
                              'dans l\'environnement.')
            return

        import boto3
        from botocore.exceptions import ClientError

        s3 = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        if check:
            self._check(s3, bucket)
            return

        media_root = settings.MEDIA_ROOT
        total = 0
        skipped = 0
        uploaded = 0
        failed = 0

        for root, dirs, files in os.walk(media_root):
            for filename in sorted(files):
                full_path = os.path.join(root, filename)
                # Clé = chemin relatif à media/ avec des / (ex: documents/Economie/...)
                key = os.path.relpath(full_path, media_root).replace(os.sep, '/')

                if not force and not dry_run:
                    try:
                        s3.head_object(Bucket=bucket, Key=key)
                        skipped += 1
                        continue
                    except ClientError:
                        pass  # absent -> on l'envoie

                total += 1
                if dry_run:
                    self.stdout.write(f'[DRY-RUN] {key}')
                    continue

                try:
                    s3.upload_file(full_path, bucket, key)
                    uploaded += 1
                    if uploaded % 50 == 0:
                        self.stdout.write(f'  ... {uploaded} envoyés')
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    self.stderr.write(f'[ERREUR] {key}: {exc}')

        self.stdout.write(self.style.SUCCESS(
            f'[SUMMARY] {"" if dry_run else "Envoyés: "}{uploaded} | '
            f'{skipped} déjà présents | {failed} erreurs'
        ))

    def _check(self, s3, bucket):
        """Vérifie que chaque fichier référencé par la base existe dans le bucket."""
        from core.models import Document

        missing = []
        for doc in Document.objects.exclude(file='').only('file'):
            key = doc.file.name
            try:
                s3.head_object(Bucket=bucket, Key=key)
            except ClientError:
                missing.append(key)

        by_folder = Counter()
        for key in missing:
            folder = key.split('/')[1] if key.count('/') >= 1 else '(racine)'
            by_folder[folder] += 1

        if missing:
            self.stderr.write(f'{len(missing)} fichiers manquants dans le bucket:')
            for folder, n in sorted(by_folder.items()):
                self.stderr.write(f'  {folder}: {n}')
        else:
            self.stdout.write(self.style.SUCCESS('Tous les fichiers référencés sont présents dans le bucket.'))
