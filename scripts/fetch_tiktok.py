"""Récupère les vidéos du compte TikTok @miage.ufhb (dev only)."""
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://www.tiktok.com/@miage.ufhb'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
}

req = urllib.request.Request(URL, headers=HEADERS)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='replace')
except Exception as exc:  # noqa: BLE001
    print('ERREUR fetch:', exc)
    sys.exit(1)

print('taille HTML:', len(html))

# IDs de vidéos
ids = re.findall(r'/(?:video|@[^/]+/video)/(\d+)', html)
uniq = list(dict.fromkeys(ids))
print('IDs vidéos:', len(uniq), uniq[:15])

# oEmbed n'est pas dispo sans l'URL complète, mais on peut construire
# https://www.tiktok.com/@miage.ufhb/video/<id>
if uniq:
    print('Exemple URL vidéo: https://www.tiktok.com/@miage.ufhb/video/' + uniq[0])

# Meta tags
for m in re.findall(r'<meta[^>]*(?:og:title|og:description|og:video)[^>]*>', html)[:8]:
    print(m[:170])

# Nom du compte
m = re.search(r'"uniqueId":\s*"([^"]+)"', html)
print('uniqueId:', m.group(1) if m else '?')
