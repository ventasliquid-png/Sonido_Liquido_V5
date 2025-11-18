/**
 * Instancia de Axios configurada con interceptor para autenticación JWT.
 * Todas las peticiones HTTP deben usar esta instancia en lugar de axios directamente.
 */
import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

// Crear instancia de axios con configuración base
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor de request: Inyecta el token JWT automáticamente
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.authToken
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor de response: Maneja errores de autenticación
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido o expirado
      const authStore = useAuthStore()
      authStore.logout()
      // Opcional: Redirigir a login
      // router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default api

