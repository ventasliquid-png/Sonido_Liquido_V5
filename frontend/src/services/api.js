import axios from 'axios';

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
    return Promise.reject(error);
  }
);

// Interceptor para agregar el token si existe (preparado para Auth)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
