"""Logs Render sur une plage horaire (pour diagnostiquer un crash)."""
import json
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
API_KEY, OWNER_ID, RESOURCE_ID = sys.argv[1], sys.argv[2], sys.argv[3]
START, END = sys.argv[4], sys.argv[5]

query = urllib.parse.urlencode({
    'ownerId': OWNER_ID,
    'resource': RESOURCE_ID,
    'limit': 500,
    'startTime': START,
    'endTime': END,
})
req = urllib.request.Request(
    f'https://api.render.com/v1/logs?{query}',
    headers={'Authorization': f'Bearer {API_KEY}'},
)
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.load(resp)

logs = data.get('logs', data) if isinstance(data, dict) else data
for item in logs:
    ts = str(item.get('timestamp', ''))[:19]
    msg = str(item.get('message', ''))
    labels = {l.get('name'): l.get('value') for l in item.get('labels', [])}
    typ = labels.get('type', '?')
    lvl = labels.get('level', '?')
    print(ts, f'[{typ}/{lvl}]', msg[:260])
