"""Affiche les événements d'un déploiement Render."""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
API_KEY, SERVICE_ID, DEPLOY_ID = sys.argv[1], sys.argv[2], sys.argv[3]

req = urllib.request.Request(
    f'https://api.render.com/v1/services/{SERVICE_ID}/deploys/{DEPLOY_ID}/events',
    headers={'Authorization': f'Bearer {API_KEY}'},
)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
except urllib.error.HTTPError as exc:
    print('HTTP', exc.code, exc.read().decode()[:500])
    sys.exit(1)

for e in data:
    print(e.get('timestamp', ''), '|', e.get('type', ''), '|', str(e.get('description', ''))[:250])
