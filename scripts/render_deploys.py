"""Affiche les déploiements récents d'un service Render."""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
API_KEY, SERVICE_ID = sys.argv[1], sys.argv[2]

req = urllib.request.Request(
    f'https://api.render.com/v1/services/{SERVICE_ID}/deploys?limit=3',
    headers={'Authorization': f'Bearer {API_KEY}'},
)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
except urllib.error.HTTPError as exc:
    print('HTTP', exc.code, exc.read().decode()[:500])
    sys.exit(1)

for item in data:
    d = item.get('deploy', item)
    print('---')
    for k in ('id', 'status', 'triggeredBy', 'finishedAt', 'failureReason'):
        print(f'{k}: {d.get(k)}')
    c = d.get('commit') or {}
    print('commit:', str(c.get('id'))[:7], c.get('message', '')[:80])
