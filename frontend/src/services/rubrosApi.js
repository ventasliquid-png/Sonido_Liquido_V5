/**
 * Servicio API para Rubros.
 * Maneja todas las peticiones HTTP al backend con autenticación JWT.
 * 
 * NOTA: Usa la instancia de axios configurada con interceptor (api.js)
 * que inyecta automáticamente el token Bearer en cada petición.
 */
import api from './api'
import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = '/rubros'

/**
 * Lista rubros con búsqueda y filtros.
 * @param {string} query - Búsqueda por código o descripción
 * @param {boolean|null} activo - Filtro de estado (true=activos, false=inactivos, null=todos)
 */
export async function listRubros(query = '', activo = null) {
  try {
    const params = new URLSearchParams()
    if (query) params.append('q', query)
    if (activo !== null) params.append('activo', activo)
    
    const response = await api.get(`${API_BASE_URL}/?${params.toString()}`)
    return response.data
  } catch (error) {
    throw handleApiError(error)
  }
}

/**
 * Obtiene un rubro por su ID.
 */
export async function getRubroById(id) {
  try {
    const response = await api.get(`${API_BASE_URL}/${id}`)
    return response.data
  } catch (error) {
    throw handleApiError(error)
  }
}

/**
 * Crea un nuevo rubro.
 * Retorna el rubro creado o lanza error especial para Protocolo Lázaro.
 */
export async function createRubro(rubroData) {
  try {
    const authStore = useAuthStore()
    const rawToken = authStore?.authToken
    const token = typeof rawToken === 'string' ? rawToken : rawToken?.value
    const headers = token ? { Authorization: `Bearer ${token}` } : {}

    const response = await api.post(`${API_BASE_URL}/`, rubroData, { headers })
    return { success: true, data: response.data }
  } catch (error) {
    // Protocolo Lázaro: Si el código está inactivo, retornamos info especial
    if (error.response?.status === 409 && 
        error.response?.headers['x-lazaro-inactive'] === 'true') {
      const rubroId = error.response?.headers['x-rubro-id']
      return {
        success: false,
        lazaro: true,
        rubroId: rubroId ? parseInt(rubroId) : null,
        message: error.response?.data?.detail || 'Código inactivo existente'
      }
    }
    throw handleApiError(error)
  }
}

/**
 * Actualiza un rubro existente.
 */
export async function updateRubro(id, rubroData) {
  try {
    const response = await api.patch(`${API_BASE_URL}/${id}/`, rubroData)
    return response.data
  } catch (error) {
    throw handleApiError(error)
  }
}

/**
 * Reactiva un rubro inactivo (Protocolo Lázaro).
 */
export async function reactivateRubro(id, rubroData = null) {
  try {
    const response = await api.patch(`${API_BASE_URL}/${id}/reactivate/`, rubroData || {})
    return response.data
  } catch (error) {
    throw handleApiError(error)
  }
}

/**
 * Elimina un rubro (baja lógica por defecto, física con force_physical=true).
 */
export async function deleteRubro(id, forcePhysical = false) {
  try {
    const params = forcePhysical ? '?force_physical=true' : ''
    const url = `${API_BASE_URL}/${id}/`
    await api.delete(`${url}${params}`)
    return { success: true }
  } catch (error) {
    throw handleApiError(error)
  }
}

/**
 * Maneja errores de la API y retorna mensajes amigables.
 */
function handleApiError(error) {
  if (error.response) {
    // Error del servidor
    const message = error.response.data?.detail || error.response.data?.message || 'Error del servidor'
    return new Error(message)
  } else if (error.request) {
    // Error de red
    return new Error('No se pudo conectar con el servidor. Verifica tu conexión.')
  } else {
    // Error en la configuración
    return new Error('Error al realizar la petición.')
  }
}

