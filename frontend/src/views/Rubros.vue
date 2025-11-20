<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as rubrosApi from '../services/rubrosApi'

// --- ESTADO REACTIVO ---
const rubros = ref([])
const loading = ref(false)
const error = ref(null)

// Filtros y búsqueda
const searchQuery = ref('')
const filtroEstado = ref('todos') // 'activos', 'inactivos', 'todos'

// Modal de Alta/Edición
const mostrarVentanaAlta = ref(false)
const modoEdicion = ref(false)
const rubroEditando = ref(null)
const formData = ref({
  codigo: '',
  descripcion: '',
  padre_id: null
})

// Protocolo Lázaro
const showLazaroDialog = ref(false)
const lazaroRubroId = ref(null)

// Referencias para atajos de teclado
const searchInputRef = ref(null)
const inputCodigoRef = ref(null)

function resetRubro() {
  modoEdicion.value = false
  rubroEditando.value = null
  formData.value = {
    codigo: '',
    descripcion: '',
    padre_id: null
  }
}

function focusSearchInput() {
  if (searchInputRef.value) {
    searchInputRef.value.focus()
  }
}

function focusCodigoInput() {
  if (inputCodigoRef.value) {
    inputCodigoRef.value.focus()
  }
}

function puedeGuardar() {
  return Boolean(
    formData.value.codigo &&
    formData.value.descripcion &&
    formData.value.codigo.length <= 3
  )
}

// --- COMPUTED ---
const rubrosFiltrados = computed(() => {
  if (!rubros.value) return []
  
  const activo = filtroActivo.value
  if (activo === null) return rubros.value
  
  return rubros.value.filter(r => r.activo === activo)
})

const filtroActivo = computed(() => {
  if (filtroEstado.value === 'activos') return true
  if (filtroEstado.value === 'inactivos') return false
  return null
})

// --- MÉTODOS DE API ---
async function cargarRubros() {
  loading.value = true
  error.value = null
  try {
    const activo = filtroActivo.value
    rubros.value = await rubrosApi.listRubros(searchQuery.value, activo)
  } catch (err) {
    error.value = err.message
    console.error('Error al cargar rubros:', err)
  } finally {
    loading.value = false
  }
}

async function guardarRubro() {
  if (!formData.value.codigo || !formData.value.descripcion) {
    error.value = 'Código y descripción son obligatorios'
    return
  }

  if (formData.value.codigo.length > 3) {
    error.value = 'El código no puede tener más de 3 caracteres'
    return
  }

  loading.value = true
  error.value = null

  try {
    if (modoEdicion.value && rubroEditando.value) {
      // Actualizar
      await rubrosApi.updateRubro(rubroEditando.value.id, {
        descripcion: formData.value.descripcion,
        padre_id: formData.value.padre_id
      })
    } else {
      // Crear (con Protocolo Lázaro)
      const resultado = await rubrosApi.createRubro({
        codigo: formData.value.codigo,
        descripcion: formData.value.descripcion,
        padre_id: formData.value.padre_id
      })

      if (!resultado.success && resultado.lazaro) {
        // Protocolo Lázaro: Mostrar diálogo de reactivación
        lazaroRubroId.value = resultado.rubroId
        showLazaroDialog.value = true
        return
      }
    }

    // Éxito: Cerrar modal y recargar
    cerrarModal()
    await cargarRubros()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function reactivarRubroLazaro() {
  if (!lazaroRubroId.value) return

  loading.value = true
  try {
    await rubrosApi.reactivateRubro(lazaroRubroId.value, {
      descripcion: formData.value.descripcion,
      padre_id: formData.value.padre_id
    })
    showLazaroDialog.value = false
    cerrarModal()
    await cargarRubros()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function eliminarRubro(rubro) {
  if (!confirm(`¿Está seguro de eliminar el rubro "${rubro.codigo}"?`)) {
    return
  }

  loading.value = true
  try {
    await rubrosApi.deleteRubro(rubro.id, false) // Baja lógica
    await cargarRubros()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function editarRubro(rubro) {
  modoEdicion.value = true
  rubroEditando.value = rubro
  formData.value = {
    codigo: rubro.codigo,
    descripcion: rubro.descripcion,
    padre_id: rubro.padre_id
  }
  mostrarVentanaAlta.value = true
  nextTick(focusCodigoInput)
}

function clonarRubro(rubro) {
  modoEdicion.value = false
  rubroEditando.value = null
  formData.value = {
    codigo: '', // Limpiar código para obligar a definir uno nuevo
    descripcion: rubro.descripcion,
    padre_id: rubro.padre_id
  }
  mostrarVentanaAlta.value = true
  nextTick(focusCodigoInput)
}

function abrirModalAlta() {
  resetRubro()
  mostrarVentanaAlta.value = true
  nextTick(focusCodigoInput)
}

function cerrarModal() {
  mostrarVentanaAlta.value = false
  showLazaroDialog.value = false
  resetRubro()
  error.value = null
}

// --- ATAJOS DE TECLADO (DEOU) ---
function handleKeydown(event) {
  // F3: Foco en Buscador
  if (event.key === 'F3') {
    event.preventDefault()
    focusSearchInput()
  }
  
  // F4: Abrir Modal o Guardar
  if (event.key === 'F4') {
    event.preventDefault()
    if (!mostrarVentanaAlta.value) {
      abrirModalAlta()
    } else if (puedeGuardar()) {
      guardarRubro()
    }
  }
  
  // F7: Clonar (solo en edición)
  if (event.key === 'F7' && mostrarVentanaAlta.value && modoEdicion.value && rubroEditando.value) {
    event.preventDefault()
    clonarRubro(rubroEditando.value)
  }
  
  // F10: Guardar
  if (event.key === 'F10' && mostrarVentanaAlta.value) {
    event.preventDefault()
    guardarRubro()
  }
  
  // ESC: Cerrar modal
  if (event.key === 'Escape' && mostrarVentanaAlta.value) {
    event.preventDefault()
    cerrarModal()
  }
}

// --- WATCHERS ---
let searchTimeout = null
watch(searchQuery, () => {
  // Debounce: Esperar 300ms después de que el usuario deje de tipear
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    cargarRubros()
  }, 300)
})

watch(filtroEstado, () => {
  cargarRubros()
})

watch(mostrarVentanaAlta, (isOpen) => {
  if (isOpen) {
    nextTick(focusCodigoInput)
  }
})

// --- LIFECYCLE ---
onMounted(() => {
  cargarRubros()
  window.addEventListener('keydown', handleKeydown)
  nextTick(focusSearchInput)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

// --- VALIDACIÓN Y FORMATO ---
function onCodigoInput(event) {
  // Auto-uppercase y limitar a 3 caracteres
  let value = event.target.value.toUpperCase().slice(0, 3)
  formData.value.codigo = value
  event.target.value = value
}
</script>

<template>
  <div class="rubros-master-layout">
    <!-- ZONA SUPERIOR (ESPACIO DE TRABAJO) -->
    <div class="workspace-zone">
      <div class="rubros-header">
        <h1>Gestión de Rubros</h1>
        <p class="subtitulo">Módulo de administración de rubros y subrubros</p>
      </div>

      <div class="rubros-toolbar">
        <div class="search-container">
          <label for="search-input">Buscador:</label>
          <input
            id="search-input"
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por código o descripción..."
            class="search-input"
          />
          <span class="shortcut-hint">[F3]</span>
        </div>
        <button @click="abrirModalAlta" class="btn-primary btn-nuevo">
          ➕ Nuevo Rubro
          <span class="shortcut-hint">[F4]</span>
        </button>
      </div>

      <div v-if="error" class="mensaje-error">
        {{ error }}
      </div>
    </div>

    <!-- EL DIVISOR (LA LÍNEA AZUL) -->
    <div class="layout-divider"></div>

    <!-- ZONA INFERIOR (GRILLA Y FILTROS) -->
    <div class="data-zone">
      <!-- Izquierda (La Grilla) -->
      <div class="grid-container">
        <table class="rubros-table" v-if="!loading && rubros.length > 0">
          <thead>
            <tr>
              <th>Código</th>
              <th>Descripción</th>
              <th>Estado</th>
              <th>Padre</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rubro in rubrosFiltrados" :key="rubro.id">
              <td><strong>{{ rubro.codigo }}</strong></td>
              <td>{{ rubro.descripcion }}</td>
              <td>
                <span :class="rubro.activo ? 'badge-activo' : 'badge-inactivo'">
                  {{ rubro.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td>{{ rubro.padre_id || '-' }}</td>
              <td class="acciones">
                <button @click="editarRubro(rubro)" class="btn-small btn-edit">✏️ Editar</button>
                <button @click="clonarRubro(rubro)" class="btn-small btn-clone">📋 Clonar [F7]</button>
                <button @click="eliminarRubro(rubro)" class="btn-small btn-delete">🗑️ Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="loading" class="loading">Cargando...</div>
        <div v-if="!loading && rubros.length === 0" class="empty-state">
          No se encontraron rubros.
        </div>
      </div>

      <!-- Derecha (Los Filtros) -->
      <div class="filters-sidebar">
        <h3>Estado</h3>
        <div class="radio-group-vertical">
          <label class="radio-item" :class="{ 'selected': filtroEstado === 'todos' }">
            <input type="radio" v-model="filtroEstado" value="todos" />
            <span>Todos</span>
          </label>
          <label class="radio-item" :class="{ 'selected': filtroEstado === 'activos' }">
            <input type="radio" v-model="filtroEstado" value="activos" />
            <span>Activos</span>
          </label>
          <label class="radio-item" :class="{ 'selected': filtroEstado === 'inactivos' }">
            <input type="radio" v-model="filtroEstado" value="inactivos" />
            <span>Inactivos</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Modal de Alta/Edición -->
    <div v-if="mostrarVentanaAlta" class="modal-backdrop" @click.self="cerrarModal">
      <div class="modal-dialog">
        <div class="modal-card">
          <div class="modal-header">
            <h2>{{ modoEdicion ? 'Editar Rubro' : 'Nuevo Rubro' }}</h2>
            <button @click="cerrarModal" class="btn-close">✕</button>
          </div>

          <form @submit.prevent="guardarRubro" class="modal-form">
            <div class="form-group">
              <label for="codigo">Código (3 caracteres, mayúsculas):</label>
              <input
                id="codigo"
                ref="inputCodigoRef"
                :value="formData.codigo"
                @input="onCodigoInput"
                type="text"
                maxlength="3"
                :disabled="modoEdicion"
                required
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="descripcion">Descripción (máx. 30 caracteres):</label>
              <input
                id="descripcion"
                v-model="formData.descripcion"
                type="text"
                maxlength="30"
                required
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="padre_id">Rubro Padre (opcional):</label>
              <input
                id="padre_id"
                v-model.number="formData.padre_id"
                type="number"
                placeholder="ID del rubro padre"
                class="form-input"
              />
            </div>

            <div class="modal-actions">
              <button type="button" @click="cerrarModal" class="btn-secondary">Cancelar</button>
              <button type="submit" :disabled="loading" class="btn-primary">
                {{ loading ? 'Guardando...' : 'Guardar [F10]' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Diálogo Protocolo Lázaro -->
    <div v-if="showLazaroDialog" class="modal-backdrop" @click.self="showLazaroDialog = false">
      <div class="modal-dialog">
        <div class="modal-card lazaro-dialog">
          <div class="modal-header">
            <h2>⚠️ Código Inactivo Encontrado</h2>
          </div>
          <div class="lazaro-content">
            <p>El código <strong>{{ formData.codigo }}</strong> ya existe pero está inactivo.</p>
            <p>¿Desea reactivarlo con los datos ingresados?</p>
          </div>
          <div class="modal-actions">
            <button @click="showLazaroDialog = false" class="btn-secondary">Cancelar</button>
            <button @click="reactivarRubroLazaro" :disabled="loading" class="btn-primary">
              {{ loading ? 'Reactivando...' : 'Sí, Reactivar' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
/* ESTRUCTURA GLOBAL */
.rubros-master-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Evita scroll en el body */
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  color: #1e293b;
}

/* ZONA SUPERIOR (ESPACIO DE TRABAJO) */
.workspace-zone {
  flex: 1; /* Ocupa el espacio restante (aprox 60-70%) */
  padding: 2rem;
  display: flex;
  flex-direction: column;
  /* Centrado opcional o distribución */
  justify-content: flex-start; 
}

.rubros-header {
  margin-bottom: 2rem;
  
  h1 {
    color: #0c4a6e;
    font-size: 2rem;
    margin: 0 0 0.5rem 0;
  }
  
  .subtitulo {
    background: #0ea5e9;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 6px;
    display: inline-block;
    font-weight: 500;
  }
}

.rubros-toolbar {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.search-container {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  
  label {
    font-weight: 600;
    color: #334155;
  }
}

.search-input {
  padding: 0.75rem;
  border: 2px solid #cbd5e1;
  border-radius: 6px;
  width: 300px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #0ea5e9;
  }
}

.shortcut-hint {
  font-size: 0.75rem;
  color: #64748b;
  margin-left: 0.5rem;
}

.btn-primary {
  background: #0ea5e9;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    background: #0284c7;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.btn-nuevo {
  background: #16a34a;
  justify-content: center;

  &:hover {
    background: #15803d;
  }
}

.mensaje-error {
  background: #fee2e2;
  color: #991b1b;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border: 1px solid #fca5a5;
}

/* EL DIVISOR */
.layout-divider {
  border-bottom: 2px solid #0000ff; /* Azul institucional fuerte */
  width: 100%;
}

/* ZONA INFERIOR (GRILLA Y FILTROS) */
.data-zone {
  height: 35vh; /* Altura fija solicitada */
  display: flex;
  flex-direction: row;
  background: white;
}

/* Izquierda: Grilla */
.grid-container {
  flex: 1; /* Ocupa todo el ancho disponible */
  overflow-y: auto; /* Scroll interno */
  padding: 1rem;
  border-right: 1px solid #e2e8f0;
}

.rubros-table {
  width: 100%;
  border-collapse: collapse;
  
  thead {
    background: #0ea5e9;
    color: white;
    position: sticky;
    top: 0;
    z-index: 10;
    
    th {
      padding: 1rem;
      text-align: left;
      font-weight: 600;
    }
  }
  
  tbody {
    tr {
      border-bottom: 1px solid #e2e8f0;
      
      &:hover {
        background: #f1f5f9;
      }
      
      td {
        padding: 1rem;
      }
    }
  }
}

/* Derecha: Filtros */
.filters-sidebar {
  width: 200px; /* Ancho fijo para la barra lateral */
  padding: 1rem;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  
  h3 {
    margin: 0;
    font-size: 1.1rem;
    color: #334155;
    border-bottom: 2px solid #cbd5e1;
    padding-bottom: 0.5rem;
  }
}

.radio-group-vertical {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
  
  &:hover {
    background: #e2e8f0;
  }
  
  &.selected {
    background: #e0f2fe;
    color: #0284c7;
    font-weight: 600;
  }
}

/* Badges y Botones Pequeños */
.badge-activo {
  background: #d1fae5;
  color: #065f46;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.badge-inactivo {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.acciones {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-small {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  
  &.btn-edit {
    background: #3b82f6;
    color: white;
    
    &:hover {
      background: #2563eb;
    }
  }
  
  &.btn-clone {
    background: #8b5cf6;
    color: white;
    
    &:hover {
      background: #7c3aed;
    }
  }
  
  &.btn-delete {
    background: #ef4444;
    color: white;
    
    &:hover {
      background: #dc2626;
    }
  }
}

.loading, .empty-state {
  padding: 3rem;
  text-align: center;
  color: #64748b;
}

/* Modal Styles (Reused) */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-dialog {
  width: 90%;
  max-width: 520px;
}

.modal-card {
  background: white;
  border-radius: 8px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  
  h2 {
    margin: 0;
    color: #0c4a6e;
  }
  
  .btn-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #64748b;
    
    &:hover {
      color: #334155;
    }
  }
}

.modal-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #334155;
  }
  
  .form-input {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #cbd5e1;
    border-radius: 6px;
    font-size: 1rem;
    transition: border-color 0.2s;
    
    &:focus {
      outline: none;
      border-color: #0ea5e9;
      box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
    }
    
    &:disabled {
      background: #f1f5f9;
      cursor: not-allowed;
    }
  }
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #e2e8f0;
  color: #334155;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: #cbd5e1;
  }
}

.lazaro-dialog {
  .lazaro-content {
    padding: 1.5rem;
    
    p {
      margin: 0.5rem 0;
      color: #334155;
    }
  }
}
</style>
