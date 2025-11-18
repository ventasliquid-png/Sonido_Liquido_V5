<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

// Inicializar el store de Pinia
const authStore = useAuthStore()

// --- Refs para el formulario (Estado local del componente) ---
const username = ref('')
const email = ref('')
const password = ref('')

// --- Refs para la retroalimentación al usuario ---
const mensaje = ref('')
const esError = ref(false)

/**
 * Manejador del envío del formulario.
 * Llama a la API del backend para registrar al usuario.
 */
async function registrarUsuario() {
  // Limpiar mensajes anteriores
  mensaje.value = ''
  esError.value = false

  try {
    // 1. Llamar a la API (FastAPI backend)
    const response = await axios.post('http://127.0.0.1:8000/auth/register', {
      username: username.value,
      email: email.value,
      password: password.value,
      rol_name: "operador" // (Rol por defecto según el backend)
    })

    // 2. Éxito: Actualizar Pinia y mostrar mensaje
    
    // (NOTA: El endpoint /register devuelve datos del usuario, pero no un token.
    //  El token se obtendrá en el /login. Por ahora, solo guardamos al usuario.)
    authStore.setUser(response.data) 
    
    mensaje.value = `¡Registro exitoso! Usuario '${response.data.username}' creado.`
    esError.value = false

    // Limpiar formulario
    username.value = ''
    email.value = ''
    password.value = ''

  } catch (error) {
    // 3. Error: Mostrar el mensaje de error del backend
    if (error.response && error.response.data && error.response.data.detail) {
      mensaje.value = `Error: ${error.response.data.detail}`
    } else {
      mensaje.value = 'Error: No se pudo conectar con el servidor.'
    }
    esError.value = true
  }
}
</script>

<template>
  <div class="register-container">
    <h1>Crear Cuenta de Operador</h1>
    <p>Paso 1: Registrar un nuevo usuario (Rol: Operador)</p>

    <form @submit.prevent="registrarUsuario" class="register-form">
      <div class="form-group">
        <label for="username">Nombre de Usuario:</label>
        <input 
          id="username"
          v-model="username" 
          type="text" 
          placeholder="ej: carlos_p" 
          required 
        />
      </div>

      <div class="form-group">
        <label for="email">Email:</label>
        <input 
          id="email"
          v-model="email" 
          type="email" 
          placeholder="ej: carlos@dominio.com" 
          required 
        />
      </div>

      <div class="form-group">
        <label for="password">Contraseña:</label>
        <input 
          id="password"
          v-model="password" 
          type="password" 
          placeholder="Mínimo 8 caracteres" 
          required 
        />
      </div>

      <button type="submit" class="btn-submit">Registrar Usuario</button>
    </form>

    <!-- Zona de Retroalimentación -->
    <div v-if="mensaje" 
         class="mensaje-feedback"
         :class="{ 'mensaje-exito': !esError, 'mensaje-error': esError }">
      {{ mensaje }}
    </div>
  </div>
</template>

<style scoped lang="scss">
/* Usamos la Doctrina Cromática V1 definida en main.scss */

.register-container {
  max-width: 500px;
  margin: 40px auto;
  padding: 2rem;
  background-color: var(--color-contenedor);
  border: 1px solid var(--color-borde);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

h1 {
  color: var(--color-texto-general);
  text-align: center;
  border-bottom: 2px solid var(--color-auth-acento); /* Acento del módulo Auth */
  padding-bottom: 0.5rem;
  margin-top: 0;
}

p {
  text-align: center;
  font-size: 0.9rem;
  opacity: 0.8;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.75rem;
  background-color: var(--color-fondo);
  border: 1px solid var(--color-borde);
  color: var(--color-texto-general);
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-auth-acento);
  box-shadow: 0 0 0 2px var(--color-auth-acento);
}

.btn-submit {
  padding: 0.8rem;
  font-size: 1rem;
  font-weight: 600;
  color: #ffffff;
  background-color: var(--color-auth-acento); /* Acento del módulo Auth */
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-submit:hover {
  background-color: #0f766e; /* Un teal más oscuro */
}

/* --- Estilos para Mensajes de Feedback --- */
.mensaje-feedback {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 4px;
  text-align: center;
  font-weight: 500;
}

.mensaje-exito {
  background-color: rgba(5, 150, 105, 0.1); /* Fondo --color-exito con alfa */
  color: var(--color-exito);
  border: 1px solid var(--color-exito);
}

.mensaje-error {
  background-color: rgba(220, 38, 38, 0.1); /* Fondo --color-error con alfa */
  color: var(--color-error);
  border: 1px solid var(--color-error);
}
</style>