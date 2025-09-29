from django.db import migrations
import os


def _normalize(path: str) -> str:
    if not path:
        return path
    p = path.replace('\\', '/').strip()
    # Remove duplicate '/media/media/' or absolute prefixes like '/opt/.../media/'
    if '/media/' in p:
        # take substring after the first 'media/' occurrence
        parts = p.split('/media/', 1)
        p = parts[1]
    if p.startswith('media/'):
        p = p[len('media/'):]
    # Ensure documents/ prefix for our files
    if not p.startswith('documents/'):
        # Try to extract filename and place under documents/
        filename = os.path.basename(p)
        if filename:
            p = f'documents/{filename}'
    return p


def forwards(apps, schema_editor):
    Document = apps.get_model('core', 'Document')
    updated = 0
    for d in Document.objects.all():
        orig = (d.file.name or '')
        norm = _normalize(orig)
        if norm and norm != orig:
            d.file.name = norm
            d.save(update_fields=['file'])
            updated += 1
    # Optionally print, but migrations shouldn't be noisy; no output


def backwards(apps, schema_editor):
    # No-op
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_org_entreprises_data'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
