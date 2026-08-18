"""Récupère les logs d'un service Render."""
import json
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
API_KEY, OWNER_ID, RESOURCE_ID = sys.argv[1], sys.argv[2], sys.argv[3]

query = urllib.parse.urlencode({
    'ownerId': OWNER_ID,
    'resource': RESOURCE_ID,
    'limit': 150,
    'direction': 'backward',
})
req = urllib.request.Request(
    f'https://api.render.com/v1/logs?{query}',
    headers={'Authorization': f'Bearer {API_KEY}'},
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
except urllib.error.HTTPError as exc:
    print('HTTP', exc.code, exc.read().decode()[:600])
    sys.exit(1)
except Exception as exc:  # noqa: BLE001
    print('ERREUR:', exc)
    sys.exit(1)

print('nb lignes:', len(data))
if isinstance(data, dict):
    logs = data.get('logs', [])
else:
    logs = data
print('logs:', len(logs))
for item in logs:
    if isinstance(item, str):
        print(item[:230])
        continue
    ts = str(item.get('timestamp', ''))[:19]
    msg = str(item.get('message', ''))
    labels = {l.get('name'): l.get('value') for l in item.get('labels', [])}
    lvl = labels.get('level', '')
    typ = labels.get('type', '')
    if msg.strip() or lvl in ('error', 'fatal'):
        print(ts, f'[{typ}/{lvl}]', msg[:250])
