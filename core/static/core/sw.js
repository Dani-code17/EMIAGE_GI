/* E-MIAGE-GI — Service Worker (PWA)
   Stratégie :
   - Pages HTML : RÉSEAU D'ABORD (pour toujours voir la dernière version),
     le cache ne sert qu'en secours hors-ligne.
   - Fichiers statiques (/static/, ../logo) : cache d'abord (rapides, immuables).
   - Les documents (médias) ne sont pas mis en cache.
*/
const CACHE = 'emiage-v2';   // v2 : purge l'ancien cache qui figeait la page d'accueil
const CORE = [
  '/static/core/logo/favicon.png',
  '/static/core/logo/icon-192.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(CORE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // On ne gère que le GET de notre propre origine (les médias GitHub/R2 passent direct)
  if (event.request.method !== 'GET' || url.origin !== self.location.origin) {
    return;
  }
  // Le service worker lui-même et le manifest ne sont jamais mis en cache
  if (url.pathname === '/sw.js' || url.pathname.startsWith('/manifest')) {
    return;
  }

  // Fichiers statiques : cache d'abord (rapide)
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(event.request).then((cached) =>
        cached || fetch(event.request).then((resp) => {
          if (resp.ok) {
            const copy = resp.clone();
            caches.open(CACHE).then((c) => c.put(event.request, copy));
          }
          return resp;
        })
      )
    );
    return;
  }

  // Pages et données : RÉSEAU D'ABORD, cache en secours si hors-ligne
  event.respondWith(
    fetch(event.request)
      .then((resp) => {
        // On ne garde en secours que les navigations réussies
        if (resp.ok && event.request.mode === 'navigate') {
          const copy = resp.clone();
          caches.open(CACHE).then((c) => c.put(event.request, copy));
        }
        return resp;
      })
      .catch(() => caches.match(event.request).then((cached) => cached || caches.match('/')))
  );
});
