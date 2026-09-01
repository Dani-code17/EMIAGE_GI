/* E-MIAGE-GI — Service Worker (PWA)
   Cache les coquilles statiques pour un démarrage rapide et un accès hors-ligne
   minimal. Les documents téléchargés passent par le réseau (pas de cache). */
const CACHE = 'emiage-v1';
const CORE = [
  '/',
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
  // Ignorer les demandes non-GET et les médias distants (GitHub/R2)
  if (event.request.method !== 'GET' || url.hostname.includes('githubusercontent')) {
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request)
        .then((resp) => {
          // Cache court pour les pages statiques/coquille
          if (resp.ok && url.pathname.startsWith('/static/')) {
            const copy = resp.clone();
            caches.open(CACHE).then((c) => c.put(event.request, copy));
          }
          return resp;
        })
        .catch(() => {
          // Hors-ligne : la page d'accueil est dispo
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }
        });
    })
  );
});
