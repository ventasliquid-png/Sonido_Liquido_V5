import axios from 'axios';

const api = axios.create({
  // [GY-LAN-ARCH] Use relative URL by default to leverage Vite Proxy (LAN Support)
  // If VITE_API_URL is set (Production?), use it. Otherwise use proxy or fallback to backend port.
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token si existe (preparado para Auth)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      // console.log('Token attached to request:', config.url);
    } else {
      console.warn('No token found in localStorage for request:', config.url);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
