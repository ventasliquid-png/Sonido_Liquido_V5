<template>
  <div class="flex h-full w-full bg-[var(--hawe-bg-main)] text-gray-200 overflow-hidden font-sans relative">
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative min-w-0">
      <!-- Top Bar -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-white/10 bg-black/10 px-6 backdrop-blur-sm shrink-0">
        <div class="flex items-center gap-4">
            <button v-if="isModal" @click="$emit('close')" class="text-white/50 hover:text-white transition-colors" title="Volver">
                <i class="fa-solid fa-arrow-left text-lg"></i>
            </button>
            <h1 class="font-outfit text-xl font-semibold text-white truncate">
                Explorador de Transportes
            </h1>
        </div>

        <!-- Search & Tools -->
        <div class="flex items-center gap-4 ml-4">
          <div class="relative hidden sm:block">
            <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar transporte..."
              class="h-9 w-48 lg:w-64 rounded-full border border-gray-700 bg-gray-800 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all"
            />
          </div>
          <div class="h-6 w-px bg-white/10 hidden sm:block"></div>
          
          <!-- Status Filter -->
          <div class="flex bg-white/5 rounded-lg p-1 border border-white/10">
            <button 
                @click="filterStatus = 'all'"
                class="px-3 py-1 text-xs font-medium rounded-md transition-all"
                :class="filterStatus === 'all' ? 'bg-cyan-600 text-white shadow-sm' : 'text-white/50 hover:text-white'"
            >
                Todos
            </button>
            <button 
                @click="filterStatus = 'active'"
                class="px-3 py-1 text-xs font-medium rounded-md transition-all"
                :class="filterStatus === 'active' ? 'bg-green-600 text-white shadow-sm' : 'text-white/50 hover:text-white'"
            >
                Activos
            </button>
            <button 
                @click="filterStatus = 'inactive'"
                class="px-3 py-1 text-xs font-medium rounded-md transition-all"
                :class="filterStatus === 'inactive' ? 'bg-red-600 text-white shadow-sm' : 'text-white/50 hover:text-white'"
            >
                Inactivos
            </button>
          </div>

          <div class="h-6 w-px bg-white/10"></div>

          <!-- View Toggle -->
          <div class="flex bg-white/5 rounded-lg p-1 border border-white/10">
            <button 
                @click="viewMode = 'grid'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'grid' ? 'bg-white/10 text-cyan-400' : 'text-white/30 hover:text-white'"
                title="Vista Cuadrícula"
            >
                <i class="fa-solid fa-border-all"></i>
            </button>
            <button 
                @click="viewMode = 'list'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'list' ? 'bg-white/10 text-cyan-400' : 'text-white/30 hover:text-white'"
                title="Vista Lista"
            >
                <i class="fa-solid fa-list"></i>
            </button>
          </div>

          <button 
            @click="openNewTransporte"
            class="flex items-center gap-2 rounded-lg bg-cyan-600 px-3 py-1.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/20 transition-all hover:bg-cyan-500 hover:shadow-cyan-500/40 whitespace-nowrap ml-2"
          >
            <i class="fa-solid fa-plus"></i>
            <span class="hidden sm:inline">Nuevo</span>
          </button>
        </div>
      </header>

      <!-- Content Grid -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-gray-900 scrollbar-thumb-gray-700">
        <div v-if="loading" class="flex items-center justify-center h-full">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500"></div>
        </div>
        
        <!-- Grid View -->
        <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <div 
            v-for="transporte in filteredTransportes" 
            :key="transporte.id"
            @click="selectTransporte(transporte)"
            class="group relative flex flex-col justify-between rounded-xl border border-white/5 bg-white/5 p-4 transition-all hover:bg-white/10 hover:shadow-xl hover:shadow-cyan-900/20 cursor-pointer"
            :class="{ 'ring-2 ring-cyan-500 bg-white/10': selectedId === transporte.id }"
          >
            <div class="flex items-start justify-between">
                <div class="flex items-center gap-3 overflow-hidden">
                    <div class="h-10 w-10 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shrink-0">
                        <i class="fa-solid fa-truck"></i>
                    </div>
                    <div class="min-w-0">
                        <h3 class="font-bold text-white leading-tight group-hover:text-cyan-300 transition-colors truncate">{{ transporte.nombre }}</h3>
                        <p class="text-xs text-white/50 truncate">{{ transporte.telefono_reclamos || 'Sin teléfono' }}</p>
                    </div>
                </div>
                <!-- Inline Toggle -->
                <button 
                    @click.stop="toggleTransporteStatus(transporte)"
                    class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 ml-2"
                    :class="transporte.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                    title="Click para cambiar estado"
                >
                    <span 
                        class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                        :class="transporte.activo ? 'translate-x-3.5' : 'translate-x-1'"
                    />
                </button>
            </div>
            
            <div class="mt-4 pt-4 border-t border-white/5 flex justify-between items-center">
                <span class="text-[10px] uppercase font-bold text-white/30 tracking-wider truncate max-w-[100px]" :title="transporte.id">ID: {{ transporte.id.split('-')[0] }}...</span>
                <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click.stop="selectTransporte(transporte)" class="text-white/50 hover:text-white" title="Editar"><i class="fa-solid fa-pencil"></i></button>
                    <button v-if="transporte.activo" @click.stop="deleteTransporteItem(transporte)" class="text-red-400/50 hover:text-red-400" title="Dar de baja"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="flex flex-col gap-2">
             <div 
                v-for="transporte in filteredTransportes" 
                :key="transporte.id"
                @click="selectTransporte(transporte)"
                class="group flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-colors"
                :class="{ 'ring-1 ring-cyan-500 bg-white/10': selectedId === transporte.id }"
             >
                <div class="flex items-center gap-4 flex-1 min-w-0">
                    <div class="h-8 w-8 rounded bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white shrink-0 text-xs">
                        <i class="fa-solid fa-truck"></i>
                    </div>
                    <div class="min-w-0 flex-1 grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <h3 class="font-bold text-white truncate">{{ transporte.nombre }}</h3>
                        <p class="text-sm text-white/50 truncate hidden sm:block">{{ transporte.telefono_reclamos || '---' }}</p>
                        <p class="text-sm text-white/50 truncate hidden sm:block">{{ transporte.web_tracking || '---' }}</p>
                    </div>
                </div>
                
                <div class="flex items-center gap-4 ml-4">
                    <div class="flex items-center gap-2 bg-black/20 px-2 py-1 rounded-full border border-white/5">
                        <button 
                            @click.stop="toggleTransporteStatus(transporte)"
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0"
                            :class="transporte.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                            title="Click para cambiar estado"
                        >
                            <span 
                                class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                :class="transporte.activo ? 'translate-x-3.5' : 'translate-x-1'"
                            />
                        </button>
                        <span class="text-[10px] uppercase font-bold text-white/50 hidden sm:inline">{{ transporte.activo ? 'Activo' : 'Inactivo' }}</span>
                    </div>
                    <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity w-16 justify-end">
                        <button @click.stop="selectTransporte(transporte)" class="text-white/50 hover:text-white" title="Editar"><i class="fa-solid fa-pencil"></i></button>
                        <button v-if="transporte.activo" @click.stop="deleteTransporteItem(transporte)" class="text-red-400/50 hover:text-red-400" title="Dar de baja"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </div>
             </div>
        </div>

      </div>
    </main>

    <!-- Right Inspector Panel -->
    <aside 
        class="border-l border-gray-800 bg-gray-900/95 flex flex-col z-30 shadow-2xl transition-all duration-300 ease-in-out overflow-hidden"
        :class="selectedTransporte ? 'w-80 opacity-100' : 'w-0 opacity-0 border-none'"
    >
        <div class="p-6 flex flex-col h-full min-w-[20rem]">
            <div class="flex justify-between items-center mb-6" v-if="selectedTransporte">
                <h2 class="text-lg font-bold text-white">
                    {{ selectedId === 'new' ? 'Nuevo Transporte' : 'Editar Transporte' }}
                </h2>
                <button @click="closeInspector" class="text-white/40 hover:text-white transition-colors">
                    <i class="fa-solid fa-times"></i>
                </button>
            </div>
        
        <div class="space-y-4 flex-1 overflow-y-auto" v-if="selectedTransporte">
            <!-- Active Toggle -->
            <div class="flex items-center justify-between bg-white/5 p-3 rounded-lg border border-white/10">
                <span class="text-sm font-bold text-white">Estado</span>
                <div class="flex items-center gap-2">
                    <span class="text-[10px] font-bold uppercase" :class="selectedTransporte.activo ? 'text-green-400' : 'text-red-400'">
                        {{ selectedTransporte.activo ? 'ACTIVO' : 'INACTIVO' }}
                    </span>
                    <button 
                        @click="toggleSelectedTransporteActive"
                        class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none"
                        :class="selectedTransporte.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                    >
                        <span 
                            class="inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform shadow-sm"
                            :class="selectedTransporte.activo ? 'translate-x-4.5' : 'translate-x-1'"
                        />
                    </button>
                </div>
            </div>

            <div>
                <label class="block text-xs font-bold uppercase text-white/40 mb-1">Nombre *</label>
                <input v-model="selectedTransporte.nombre" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none transition-colors" placeholder="Ej: Via Cargo" />
            </div>
            <div>
                <label class="block text-xs font-bold uppercase text-white/40 mb-1">Teléfono Reclamos</label>
                <input v-model="selectedTransporte.telefono_reclamos" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none transition-colors" placeholder="+54 9 11..." />
            </div>
             <div>
                <label class="block text-xs font-bold uppercase text-white/40 mb-1">Web Tracking</label>
                <input v-model="selectedTransporte.web_tracking" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none transition-colors" placeholder="https://..." />
            </div>
            
            <div class="bg-white/5 p-3 rounded border border-white/5 space-y-2">
                <div class="flex items-center gap-2">
                    <input type="checkbox" v-model="selectedTransporte.requiere_carga_web" id="webCheck" class="accent-cyan-500 h-4 w-4" />
                    <label for="webCheck" class="text-sm text-white cursor-pointer select-none">Requiere Carga Web</label>
                </div>
            </div>

            <div>
                <label class="block text-xs font-bold uppercase text-white/40 mb-1">Formato Etiqueta</label>
                <select v-model="selectedTransporte.formato_etiqueta" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none transition-colors">
                    <option value="PROPIA">Propia</option>
                    <option value="EXTERNA_PDF">Externa (PDF)</option>
                </select>
            </div>
        </div>

        <div class="pt-6 mt-6 border-t border-white/10 flex gap-3" v-if="selectedTransporte">
            <button @click="saveTransporte" class="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white py-2 rounded font-bold transition-colors shadow-lg shadow-cyan-900/20">
                <span v-if="saving"><i class="fa-solid fa-spinner fa-spin mr-2"></i>Guardando...</span>
                <span v-else>Guardar (F10)</span>
            </button>
            <button v-if="selectedId !== 'new'" @click="deleteTransporte" class="px-3 bg-red-900/20 hover:bg-red-900/40 text-red-400 rounded border border-red-500/30 transition-colors" title="Dar de baja">
                <i class="fa-solid fa-trash"></i>
            </button>
        </div>
        </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useLogisticaStore } from '../../../stores/logistica'
import { useNotificationStore } from '../../../stores/notification'

const props = defineProps({
    isModal: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['close'])

const transporteStore = useLogisticaStore()
const notificationStore = useNotificationStore()

const transportes = computed(() => transporteStore.empresas)
const loading = computed(() => transporteStore.loading)
const searchQuery = ref('')
const selectedId = ref(null)
const selectedTransporte = ref(null)
const saving = ref(false)

// New State
const filterStatus = ref('active') // 'all', 'active', 'inactive'
const viewMode = ref('grid') // 'grid', 'list'

onMounted(async () => {
    await transporteStore.fetchEmpresas('all')
    window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

const filteredTransportes = computed(() => {
    let result = transportes.value

    // Filter by Status
    if (filterStatus.value === 'active') {
        result = result.filter(t => t.activo)
    } else if (filterStatus.value === 'inactive') {
        result = result.filter(t => !t.activo)
    }

    // Filter by Search
    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(t => t.nombre.toLowerCase().includes(query))
    }

    return result
})

const selectTransporte = (t) => {
    selectedId.value = t.id
    // Clone to avoid direct mutation before save
    selectedTransporte.value = { ...t }
}

const openNewTransporte = () => {
    selectedId.value = 'new'
    selectedTransporte.value = {
        id: null,
        nombre: '',
        telefono_reclamos: '',
        web_tracking: '',
        activo: true,
        requiere_carga_web: false,
        formato_etiqueta: 'PROPIA'
    }
}

const closeInspector = () => {
    selectedId.value = null
    selectedTransporte.value = null
}

const saveTransporte = async () => {
    if (!selectedTransporte.value.nombre) {
        notificationStore.add('El nombre es obligatorio', 'error')
        return
    }

    console.log('Saving transporte:', selectedTransporte.value)
    saving.value = true
    try {
        if (selectedId.value === 'new') {
            await transporteStore.createEmpresa(selectedTransporte.value)
            notificationStore.add('Transporte creado', 'success')
        } else {
            await transporteStore.updateEmpresa(selectedTransporte.value.id, selectedTransporte.value)
            notificationStore.add('Transporte actualizado', 'success')
        }
        closeInspector()
    } catch (e) {
        notificationStore.add('Error al guardar', 'error')
        console.error(e)
    } finally {
        saving.value = false
    }
}

const deleteTransporte = async () => {
    if (!confirm('¿Seguro que desea dar de baja este transporte?')) return
    try {
        // Soft delete
        await transporteStore.updateEmpresa(selectedTransporte.value.id, { ...selectedTransporte.value, activo: false })
        notificationStore.add('Transporte dado de baja', 'success')
        closeInspector()
    } catch (e) {
        notificationStore.add('Error al eliminar', 'error')
    }
}

const deleteTransporteItem = async (t) => {
    if (!confirm(`¿Seguro que desea dar de baja a ${t.nombre}?`)) return
    try {
        await transporteStore.updateEmpresa(t.id, { ...t, activo: false })
        notificationStore.add('Transporte dado de baja', 'success')
    } catch (e) {
        notificationStore.add('Error al eliminar', 'error')
    }
}

const toggleTransporteStatus = async (t) => {
    console.log('toggleTransporteStatus clicked', t.nombre, t.activo)
    if (t.activo) {
        // If active, use the delete routine (Tachito)
        console.log('Calling deleteTransporteItem')
        await deleteTransporteItem(t)
    } else {
        // If inactive, activate directly
        console.log('Activating directly')
        try {
            await transporteStore.updateEmpresa(t.id, { ...t, activo: true })
            notificationStore.add('Transporte activado', 'success')
        } catch (e) {
            notificationStore.add('Error al activar', 'error')
        }
    }
}

const toggleSelectedTransporteActive = () => {
    if (selectedTransporte.value.activo) {
        // If active, use the delete routine (Tachito) which confirms and closes
        deleteTransporte()
    } else {
        // If inactive, just toggle local state (user must save)
        selectedTransporte.value.activo = true
    }
}

const handleKeydown = (e) => {
    if (e.key === 'F10' && selectedTransporte.value) {
        e.preventDefault()
        saveTransporte()
    }
    if (e.key === 'Escape') {
        if (selectedTransporte.value) {
            e.preventDefault()
            closeInspector()
        } else if (props.isModal) {
            emit('close')
        }
    }
}
</script>
