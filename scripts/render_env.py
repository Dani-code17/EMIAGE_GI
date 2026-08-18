"""Affiche les variables d'environnement d'un service Render (masque les secrets)."""
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
API_KEY = sys.argv[1]
SERVICE_ID = sys.argv[2]

req = urllib.request.Request(
    f'https://api.render.com/v1/services/{SERVICE_ID}/env-vars',
    headers={'Authorization': f'Bearer {API_KEY}'},
)
with urllib.request.urlopen(req) as resp:
    data = json.load(resp)

def mask(key, value):
    ku = key.upper()
    if any(s in ku for s in ('SECRET', 'PASSWORD', 'TOKEN')):
        return value[:6] + '****' if value else '(vide)'
    if 'URL' in ku and value and '://' in value:
        return re.sub(r'(://[^:]+:)[^@]+@', r'\1****@', value)
    return value

for item in data:
    key = item.get('envVarKey') or item.get('key')
    value = item.get('value') or ''
    if key:
        print(f'{key} = {mask(key, value)}')
    else:
        print('(entrée sans clé):', json.dumps(item, ensure_ascii=False)[:120])
