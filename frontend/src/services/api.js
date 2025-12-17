import axios from 'axios';

const api = axios.create({
  // [DEBUG-LAN] Hardcoded IP to ensure connectivity
  baseURL: 'http://192.168.0.34:8000',
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
