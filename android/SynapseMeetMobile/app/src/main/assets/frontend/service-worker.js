/**
 * SynapseMeet - minimal service worker
 * Caches the app shell so the mobile app opens instantly on repeat visits.
 * API calls (to the Django backend) are always fetched from the network.
 */
const CACHE_NAME = 'synapsemeet-shell-v1';
const APP_SHELL = [
  'index.html',
  'register.html',
  'dashboard.html',
  'meeting-create.html',
  'meeting-room.html',
  'profile.html',
  'css/style.css',
  'css/responsive.css',
  'js/api.js',
  'js/auth.js',
  'js/dashboard.js',
  'js/meeting.js',
  'js/ai-assistant.js',
  'assets/icons/synapse-logo.svg',
  'manifest.json',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/api/')) return; // never cache API calls

  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
