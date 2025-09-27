from django.db import migrations
import os
import re
from django.utils.text import slugify

def forwards(apps, schema_editor):
    UE = apps.get_model('core', 'UE')
    ECUE = apps.get_model('core', 'ECUE')
    Document = apps.get_model('core', 'Document')

    # Ensure UE/ECUE exist
    ue_code = 'UE Organisations des Entreprises'
    ue_name = 'UE Organisations des Entreprises'
    ue, _ = UE.objects.get_or_create(
        level='L1', semester='S1', code=ue_code,
        defaults={'name': ue_name, 'slug': slugify(f"L1-S1-{ue_code}-{ue_name}")}
    )
    if ue.name != ue_name:
        ue.name = ue_name
        ue.save()

    ecue_name = 'Organisations des Entreprises'
    ecue, _ = ECUE.objects.get_or_create(
        ue=ue, name=ecue_name,
        defaults={'code': '', 'slug': slugify(f"{ue.level}-{ue.semester}-{ue.code}-{ecue_name}")}
    )

    # Import files from repo path media/documents/EOE
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    media_folder = os.path.join(base_dir, 'media', 'documents', 'EOE')
    if not os.path.isdir(media_folder):
        # Nothing to import
        return

    def detect_category(filename):
        name = filename.lower()
        if any(w in name for w in ['examen', 'exam', 'sujet', 'session', 'devoir']):
            return 'EXAMS'
        if any(w in name for w in ['td', 'tp', 'travaux', 'exercice', 'correction']):
            return 'TD_TP'
        if any(w in name for w in ['maquette', 'planning', 'programme']):
            return 'MAQUETTES'
        return 'COURS'

    def generate_title(filename):
        base = os.path.splitext(os.path.basename(filename))[0]
        base = re.sub(r'[_\-]+', ' ', base)
        words = base.split()
        title = ' '.join(w.capitalize() for w in words)
        return title[:100] if len(title) > 100 else title

    for fname in os.listdir(media_folder):
        fpath = os.path.join(media_folder, fname)
        if not os.path.isfile(fpath):
            continue
        title = generate_title(fname)
        category = detect_category(fname)
        # Avoid duplicates
        if Document.objects.filter(title=title, level='L1', semester='S1', ecue=ecue).exists():
            continue
        # Store relative path from MEDIA_ROOT
        rel_path = os.path.join('documents', 'EOE', fname).replace('\\', '/')
        Document.objects.create(
            title=title,
            description=f"Importé via migration depuis media/documents/EOE",
            category=category,
            level='L1',
            semester='S1',
            ecue=ecue,
            file=rel_path,
        )


def backwards(apps, schema_editor):
    # Non destructive rollback: do nothing
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_auto_20250927_0934'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
