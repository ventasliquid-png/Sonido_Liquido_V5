// [IDENTIDAD] - frontend\src\services\sesion.js
// [Card #183, S888] La sesión (token JWT) vista desde la pantalla.
//
// Reglas acordadas con Carlos (19/10/2026): el operador nunca debería tener que cerrar sesión para poder hacer un cambio.
//  - La sesión dura 7 días SIN USO (backend/core/config.py). Mientras se usa el sistema se renueva sola (POST /auth/refresh),
//    como mucho una vez por hora: quien trabaja todos los días nunca la ve vencer.
//  - Si de verdad vence (7 días sin tocar, o un token viejo de antes de este cambio), la pantalla lleva sola al login UNA vez
//    y, al volver a entrar, devuelve a la misma pantalla. Antes la pantalla dejaba seguir con un token vencido (el guard solo miraba
//    que existiera) y fallaban en silencio las acciones que firman con el usuario: no comercial, liberar despacho, conciliar facturas...
//  - En los últimos minutos aparece el cartel «¿Querés seguir?» (components/ui/AvisoSesion.vue).
//
// Este módulo NO importa api.js (api.js lo importa a él): las funciones que llaman al servidor reciben `api` como parámetro.

const CLAVE = 'token';
export const RENOVAR_CADA_MS = 60 * 60 * 1000;   // renueva la sesión si el token tiene más de 1 hora
export const AVISO_ANTES_MS = 5 * 60 * 1000;     // el cartel «¿Querés seguir?» aparece en los últimos 5 minutos

export function leerToken() {
    try { return localStorage.getItem(CLAVE); } catch { return null; }
}

export function guardarToken(token) {
    try { localStorage.setItem(CLAVE, token); } catch { /* sin almacenamiento: la sesión dura lo que la pestaña */ }
}

// Datos del token (exp, iat, sub) leídos de su parte central, SIN verificar la firma: solo sirven para saber cuándo vence.
// La firma la verifica siempre el servidor. Un token mal formado devuelve null (y se trata como vencido).
export function datosDelToken(token) {
    try {
        const parte = String(token || '').split('.')[1];
        if (!parte) return null;
        const b64 = parte.replace(/-/g, '+').replace(/_/g, '/');
        const datos = JSON.parse(atob(b64.padEnd(Math.ceil(b64.length / 4) * 4, '=')));
        return datos && typeof datos.exp === 'number' ? datos : null;
    } catch {
        return null;
    }
}

export function msHastaVencer(token, ahora = Date.now()) {
    const datos = datosDelToken(token);
    return datos ? datos.exp * 1000 - ahora : -Infinity;
}

export function tokenVencido(token, ahora = Date.now()) {
    return msHastaVencer(token, ahora) <= 0;
}

// ¿Conviene renovar ya? Si el token tiene más de una hora (o es de antes de este cambio y no trae iat) y todavía no venció.
export function debeRenovar(token, ahora = Date.now()) {
    const datos = datosDelToken(token);
    if (!datos || datos.exp * 1000 <= ahora) return false;
    if (typeof datos.iat !== 'number') return true;
    return ahora - datos.iat * 1000 >= RENOVAR_CADA_MS;
}

let renovando = null;

// Renueva la sesión ahora (cartel «Sí, seguir»). Devuelve true si el servidor dio un token nuevo.
export function renovarAhora(api) {
    if (renovando) return renovando;
    renovando = api.post('/auth/refresh', null, { __sinRenovar: true })
        .then((r) => {
            const nuevo = r && r.data && r.data.access_token;
            if (nuevo) guardarToken(nuevo);
            return Boolean(nuevo);
        })
        .catch(() => false)
        .finally(() => { renovando = null; });
    return renovando;
}

// Renovación silenciosa mientras se usa el sistema: la llama el interceptor de api.js antes de cada pedido al servidor.
export function renovarSiHaceFalta(api) {
    const token = leerToken();
    if (!token || !debeRenovar(token)) return null;
    return renovarAhora(api);
}

let yendoAlLogin = false;

// La sesión venció (o la cerró el operador): limpia y lleva al login UNA sola vez, recordando la pantalla para volver.
// Usa window.location (no el router) porque la llaman api.js y el cartel, que no tienen el router a mano.
export function irAlLogin(motivo = 'vencida') {
    if (yendoAlLogin) return;
    yendoAlLogin = true;
    try { localStorage.removeItem(CLAVE); localStorage.removeItem('usuario'); } catch { /* nada */ }
    const actual = window.location.pathname + window.location.search;
    const volver = actual.startsWith('/login') ? '/' : actual;
    window.location.assign(`/login?motivo=${encodeURIComponent(motivo)}&volver=${encodeURIComponent(volver)}`);
}

// Destino seguro después del login: solo rutas internas de la propia aplicación (nunca otro sitio).
export function destinoSeguro(volver) {
    const v = String(volver || '');
    return v.startsWith('/') && !v.startsWith('//') && !v.startsWith('/login') ? v : '/';
}

// Botón «Cerrar Sesión» de la barra lateral (antes emitía un evento que nadie escuchaba y no pasaba nada).
export function cerrarSesion(router) {
    if (!window.confirm('¿Cerrar la sesión?')) return;
    try { localStorage.removeItem(CLAVE); localStorage.removeItem('usuario'); } catch { /* nada */ }
    router.push('/login');
}
