"""Déclenche un déploiement Render sur le commit courant (dev/ops)."""
import json
import os
import sys
import urllib.request

API_KEY = os.environ.get('RENDER_API_KEY', 'rnd_RO1R6D8iiT2Mp7yXjYZrlBWQhPOX')
SERVICE = 'srv-d33u9tumcj7s73amvrl0'

req = urllib.request.Request(
    f'https://api.render.com/v1/services/{SERVICE}/deploys',
    data=json.dumps({'clearCache': 'do_not_clear'}).encode(),
    headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
    method='POST',
)
with urllib.request.urlopen(req, timeout=60) as resp:
    d = json.load(resp)
print('deploy:', d.get('id'), '|', d.get('status'), '| commit:', str(d.get('commit', {}).get('id'))[:7])
