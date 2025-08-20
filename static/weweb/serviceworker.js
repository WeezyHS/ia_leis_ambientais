const version = 1;
self.addEventListener('install', event => {
    // eslint-disable-next-line no-console
    console.log(`Service worker v${version} installed`);
});
self.addEventListener('activate', event => {
    // eslint-disable-next-line no-console
    console.log(`Service worker v${version} activated`);
});
self.addEventListener('fetch', event => {
    //No cache in service worker
    if (event.request.method === 'POST' || event.request.method === 'PUT' || event.request.method === 'DELETE') {
        return;
    }

    // Permitir redirecionamentos para rotas de autenticação e dashboard
    const url = new URL(event.request.url);
    const authRoutes = ['/dashboard', '/login', '/api/auth'];
    
    if (authRoutes.some(route => url.pathname.startsWith(route))) {
        return; // Não interceptar essas rotas
    }

    event.respondWith(fetch(event.request));
});
