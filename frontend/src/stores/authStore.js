import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * Gestor de Estado para la Autenticación (AuthStore).
 * Utiliza Pinia y la Composition API (setup-style).
 */
export const useAuthStore = defineStore('auth', () => {

  // --- 1. ESTADO (State) ---
  // Usamos ref() para definir las propiedades reactivas del estado
  const token = ref(null)
  const isAuthenticated = ref(false)
  const usuario = ref(null) // Para guardar info del usuario (ej. username, rol)

  // --- 2. GETTERS (Computed) ---
  // Propiedades computadas que leen el estado
  const isUserLoggedIn = computed(() => isAuthenticated.value)
  const authToken = computed(() => token.value)

  // --- 3. ACCIONES (Actions) ---
  // Funciones que modifican el estado

  /**
   * Almacena el token y marca al usuario como autenticado.
   * @param {string} newToken - El token JWT recibido del backend.
   */
  function setToken(newToken) {
    token.value = newToken
    isAuthenticated.value = true
    localStorage.setItem('token', newToken)
  }

  /**
   * Almacena los datos del usuario autenticado.
   * @param {object} dataUsuario - Datos del usuario (ej. username, email, rol_id).
   */
  function setUser(dataUsuario) {
    usuario.value = dataUsuario
    localStorage.setItem('usuario', JSON.stringify(dataUsuario))
  }

  /**
   * Limpia el estado de autenticación.
   */
  function logout() {
    token.value = null
    isAuthenticated.value = false
    usuario.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('usuario')
  }

  // Exponemos el estado, getters y acciones
  return {
    token,
    isAuthenticated,
    usuario,
    isUserLoggedIn,
    authToken,
    setToken,
    setUser,
    logout
  }
})
