"""Vérifie que les fichiers référencés en base sont servis depuis emiage-media (dev only)."""
import os
import sys
import random
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emiage_web.settings')
import django  # noqa: E402

django.setup()
from core.models import Document  # noqa: E402

BASE = 'https://raw.githubusercontent.com/Dani-code17/emiage-media/main/media/'
docs = list(Document.objects.exclude(file=''))
random.seed(1)
sample = random.sample(docs, 8)

ok = 0
ko = 0
for d in sample:
    enc = urllib.parse.quote(d.file.name)
    url = BASE + enc
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=20) as resp:
            code = resp.status
    except Exception as exc:
        code = getattr(exc, 'code', 'ERR')
    status = 'OK ' if code == 200 else 'KO '
    print(f'{status} {code}  {d.file.name}')
    if code == 200:
        ok += 1
    else:
        ko += 1

print(f'\n{ok} OK / {ko} KO sur {len(sample)} testés')
