{% load static %}
const CACHE_NAME = 'au-it-dept-v1';
const DYNAMIC_CACHE = 'au-it-dept-dynamic-v1';
const ASSETS_TO_CACHE = [
    "{% static 'imgs/annamalai.png' %}",
    "{% static 'css/student_style.css' %}",
    "/offline/"
];

// Install event: Cache core assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Activate event: Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME && cache !== DYNAMIC_CACHE) {
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Fetch event: Network First, then Cache, then Offline Page
self.addEventListener('fetch', (event) => {
    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) return;

    event.respondWith(
        fetch(event.request)
            .then((fetchRes) => {
                // Cache successful GET requests
                if (!fetchRes || fetchRes.status !== 200 || fetchRes.type !== 'basic') {
                    return fetchRes;
                }
                // Clone response to cache it
                const responseToCache = fetchRes.clone();
                if (event.request.method === 'GET') {
                    caches.open(DYNAMIC_CACHE).then((cache) => {
                        cache.put(event.request, responseToCache);
                    });
                }
                return fetchRes;
            })
            .catch(() => {
                // If network fails, try cache
                return caches.match(event.request).then((cachedRes) => {
                    if (cachedRes) return cachedRes;
                    // If not in cache and it's a page navigation, show offline page
                    if (event.request.headers.get('accept').includes('text/html')) {
                        return caches.match('/offline/');
                    }
                });
            })
    );
});
// ... existing code ...

// ==========================================
// WEB PUSH NOTIFICATIONS
// ==========================================

self.addEventListener('push', function (event) {
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body,
            icon: data.icon || '/static/imgs/annamalai.png',
            badge: data.badge || '/static/imgs/annamalai.png',
            vibrate: [100, 50, 100],
            data: {
                url: data.url || '/'
            }
        };
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
