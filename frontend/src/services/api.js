// [IDENTIDAD] - frontend\src\services\api.js
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

import axios from 'axios';
import { renovarSiHaceFalta, irAlLogin } from './sesion';

const api = axios.create({
  // [GY-LAN-ARCH] Use relative URL by default to leverage Vite Proxy (LAN Support)
  // This is the most robust way to handle localhost/LAN-IP and Satellite Windows.
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar reintentos en errores de conexión (Backend restart)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config } = error;
    // Error de red o conexión rechazada (Backend caido/reiniciando)
    if (!error.response || error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED') {
      config.__retryCount = config.__retryCount || 0;

      const MAX_RETRIES = 5;
      const RETRY_DELAY = 1500; // 1.5s

      if (config.__retryCount < MAX_RETRIES) {
        config.__retryCount += 1;
        console.log(`[API] Error de conexión detectado. Reintentando (${config.__retryCount}/${MAX_RETRIES}) en ${RETRY_DELAY}ms...`);

        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
        return api(config);
      }
    }
    // [Card #183, S888] Sesión vencida o inválida: el servidor responde 401 en las acciones que firman con el usuario. En vez de dejar que cada
    // pantalla muestre su «Token inválido o expirado» (y el operador no sepa qué hacer), se lleva al login UNA vez y después se vuelve a la
    // misma pantalla. El 401 del propio login (usuario o contraseña incorrectos) NO cuenta: ese lo muestra la pantalla de login.
    const url = String((config && config.url) || '');
    if (error.response && error.response.status === 401 && !url.includes('/auth/token')) {
      irAlLogin('vencida');
    }
    return Promise.reject(error);
  }
);

// Interceptor para agregar el token si existe (preparado para Auth)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      // [Card #183] Mientras se usa el sistema la sesión se renueva sola (como mucho una vez por hora; ver services/sesion.js). No espera la respuesta.
      if (!config.__sinRenovar && !String(config.url || '').startsWith('/auth/')) renovarSiHaceFalta(api);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
