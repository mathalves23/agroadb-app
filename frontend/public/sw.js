const VERSION = 'agroadb-shell-v3';
const STATIC_CACHE = `${VERSION}:static`;
const API_CACHE = `${VERSION}:api`;
const APP_SHELL = ['/', '/site.webmanifest', '/pwa-192.png', '/pwa-512.png', '/apple-touch-icon.png'];
const OFFLINE_SYNC_TAG = 'agroadb-sync';

function isStaticAsset(request) {
  const url = new URL(request.url);
  return (
    url.origin === self.location.origin &&
    (url.pathname.startsWith('/assets/') ||
      url.pathname.endsWith('.js') ||
      url.pathname.endsWith('.css') ||
      url.pathname.endsWith('.png') ||
      url.pathname.endsWith('.svg') ||
      url.pathname.endsWith('.webmanifest'))
  );
}

function isCacheableApi(request) {
  const url = new URL(request.url);
  return (
    request.method === 'GET' &&
    url.pathname.startsWith('/api/v1/') &&
    (url.pathname.includes('/investigations') ||
      url.pathname.includes('/notifications') ||
      url.pathname.includes('/auth/me') ||
      url.pathname.includes('/legal/queries/summary'))
  );
}

async function networkFirst(request, cacheName, fallbackUrl) {
  const cache = await caches.open(cacheName);
  try {
    const response = await fetch(request);
    if (response && response.status === 200) {
      cache.put(request, response.clone()).catch(() => undefined);
    }
    return response;
  } catch {
    const cached = await cache.match(request);
    if (cached) return cached;
    if (fallbackUrl) {
      const fallback = await caches.match(fallbackUrl);
      if (fallback) return fallback;
    }
    return Response.error();
  }
}

async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  const networkPromise = fetch(request)
    .then((response) => {
      if (response && response.status === 200) {
        cache.put(request, response.clone()).catch(() => undefined);
      }
      return response;
    })
    .catch(() => cached || Response.error());

  return cached || networkPromise;
}

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(APP_SHELL)).catch(() => undefined)
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => ![STATIC_CACHE, API_CACHE].includes(key)).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('sync', (event) => {
  if (event.tag !== OFFLINE_SYNC_TAG) return;
  event.waitUntil(
    self.clients.matchAll({ includeUncontrolled: true, type: 'window' }).then((clients) =>
      Promise.all(clients.map((client) => client.postMessage({ type: OFFLINE_SYNC_TAG })))
    )
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request, STATIC_CACHE, '/'));
    return;
  }

  if (isStaticAsset(request)) {
    event.respondWith(staleWhileRevalidate(request, STATIC_CACHE));
    return;
  }

  if (isCacheableApi(request)) {
    event.respondWith(networkFirst(request, API_CACHE));
  }
});
