<template>
  <div class="flex h-screen w-full bg-[var(--hawe-bg-main)] text-gray-200 overflow-hidden font-sans">
    <!-- Sidebar is handled by AppSidebar in the parent layout or router view structure -->
    <!-- Assuming this view is rendered inside the main layout, but if it's a top level route, we might need the sidebar here or in App.vue -->
    <!-- Based on HaweView, it seems we might need to include the sidebar if this is a standalone view -->
    
    <AppSidebar 
        theme="pink"
        @logout="logout" 
        @open-command-palette="showCommandPalette = true"
        @navigate="handleNavigation"
    />

    <main class="flex flex-1 flex-col relative min-w-0">
      <!-- Top Bar -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-white/10 bg-black/10 px-6 backdrop-blur-sm shrink-0">
        <div class="flex items-center gap-4">
            <h1 class="font-outfit text-xl font-semibold text-white truncate">
                Agenda de Contactos
            </h1>
        </div>

        <!-- Search & Tools -->
        <div class="flex items-center gap-4 ml-4">
          <div class="relative hidden sm:block">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"></i>
            <input
              v-model="searchQuery"
              @input="handleSearch"
              type="text"
              placeholder="Buscar persona..."
              class="h-9 w-48 lg:w-64 rounded-full border border-gray-700 bg-gray-800 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:border-pink-500 focus:outline-none focus:ring-1 focus:ring-pink-500 transition-all"
            />
          </div>
          <div class="h-6 w-px bg-white/10 hidden sm:block"></div>
          
          <!-- Status Filter -->
          <div class="flex bg-white/5 rounded-lg p-1 border border-white/10">
            <button 
                @click="filterStatus = 'all'"
                class="px-3 py-1 text-xs font-medium rounded-md transition-all"
                :class="filterStatus === 'all' ? 'bg-pink-600 text-white shadow-sm' : 'text-white/50 hover:text-white'"
                title="Todos"
            >
                Todos
            </button>
            <button 
                @click="filterStatus = 'active'"
                class="px-3 py-1 text-xs font-medium rounded-md transition-all"
                :class="filterStatus === 'active' ? 'bg-green-600 text-white shadow-sm' : 'text-white/50 hover:text-white'"
                title="Activos"
            >
                Activos
            </button>
            <button 
                @click="filterStatus = 'inactive'"
                class="px-3 py-1 text-xs font-medium rounded-md transition-all"
                :class="filterStatus === 'inactive' ? 'bg-red-600 text-white shadow-sm' : 'text-white/50 hover:text-white'"
                title="Inactivos"
            >
                Inactivos
            </button>
          </div>

          <div class="h-6 w-px bg-white/10"></div>

          <!-- Sort Menu -->
          <div class="relative">
            <button 
                @click="showSortMenu = !showSortMenu" 
                class="text-white/70 hover:text-white transition-colors flex items-center gap-2" 
                title="Ordenar"
            >
                <i class="fas fa-sort-amount-down"></i>
                <span class="text-xs font-mono text-pink-400" v-if="sortBy === 'usage'">POPULARIDAD</span>
                <span class="text-xs font-mono text-pink-400" v-else-if="sortBy === 'alpha_asc'">A-Z</span>
                <span class="text-xs font-mono text-pink-400" v-else-if="sortBy === 'alpha_desc'">Z-A</span>
                <span class="text-xs font-mono text-pink-400" v-else-if="sortBy === 'id_asc'">ANTIGUEDAD</span>
                <span class="text-xs font-mono text-pink-400" v-else-if="sortBy === 'id_desc'">RECIENTES</span>
            </button>
            
            <!-- Dropdown -->
            <div v-if="showSortMenu" class="absolute right-0 mt-2 w-48 bg-[#0a253a] border border-white/10 rounded-lg shadow-xl z-50">
                <!-- Click outside overlay -->
                <div class="fixed inset-0 z-40" @click="showSortMenu = false"></div>
                
                <div class="relative z-50 py-1">
                    <button @click="sortBy = 'usage'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-pink-400 font-bold': sortBy === 'usage' }">Más Usados (Popularidad)</button>
                    <div class="border-t border-white/10 my-1"></div>
                    <button @click="sortBy = 'alpha_asc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-pink-400 font-bold': sortBy === 'alpha_asc' }">A-Z Alfabético</button>
                    <button @click="sortBy = 'alpha_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-pink-400 font-bold': sortBy === 'alpha_desc' }">Z-A Alfabético</button>
                    <div class="border-t border-white/10 my-1"></div>
                    <button @click="sortBy = 'id_asc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-pink-400 font-bold': sortBy === 'id_asc' }">Más Antiguos</button>
                    <button @click="sortBy = 'id_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-pink-400 font-bold': sortBy === 'id_desc' }">Más Recientes</button>
                </div>
            </div>
          </div>

          <!-- View Toggle -->
          <div class="flex bg-white/5 rounded-lg p-1 border border-white/10">
            <button 
                @click="viewMode = 'grid'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'grid' ? 'bg-white/10 text-pink-400' : 'text-white/30 hover:text-white'"
                title="Vista Cuadrícula"
            >
                <i class="fas fa-border-all"></i>
            </button>
            <button 
                @click="viewMode = 'list'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'list' ? 'bg-white/10 text-pink-400' : 'text-white/30 hover:text-white'"
                title="Vista Lista"
            >
                <i class="fas fa-list"></i>
            </button>
          </div>

          <button 
            @click="openNewContacto"
            class="flex items-center gap-2 rounded-lg bg-pink-600 px-3 py-1.5 text-sm font-bold text-white shadow-lg shadow-pink-500/20 transition-all hover:bg-pink-500 hover:shadow-pink-500/40 whitespace-nowrap ml-2"
          >
            <i class="fas fa-plus"></i>
            <span class="hidden sm:inline">Nuevo</span>
          </button>
        </div>
      </header>

      <!-- Content List -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-gray-900 scrollbar-thumb-gray-700">
        <div v-if="loading" class="flex items-center justify-center h-full">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500"></div>
        </div>
        
        <!-- Grid View (Cards) -->
        <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 relative">
            <div 
                v-for="persona in filteredPersonas" 
                :key="persona.id"
                @click="editPersona(persona)"
                @mouseenter="handleMouseEnter(persona.id)"
                @mouseleave="handleMouseLeave"
                class="group flex flex-col justify-between rounded-xl border border-white/5 p-4 transition-all duration-300 cursor-pointer"
                :class="[
                    { 'ring-2 ring-pink-500 bg-white/10': selectedPersona?.id === persona.id },
                    hoveredCardId === persona.id 
                        ? 'absolute z-50 scale-110 bg-gray-900 shadow-2xl shadow-black/50 h-auto min-h-[160px] border-pink-500' 
                        : 'relative bg-white/5 hover:bg-white/10 hover:shadow-xl hover:shadow-pink-900/20'
                ]"
                :style="hoveredCardId === persona.id ? { width: '100%', maxWidth: '100%' } : {}"
            >
                <div class="flex items-start justify-between mb-4">
                    <div class="h-12 w-12 rounded-full bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center text-white shrink-0 font-bold text-lg shadow-lg">
                        {{ getInitials(persona.nombre_completo) }}
                    </div>
                    <!-- Inline Toggle -->
                    <div 
                        class="flex items-center gap-2 bg-black/20 px-2 py-1 rounded-full border border-white/5 cursor-pointer hover:bg-white/10 transition-colors"
                        @click.stop="togglePersonaStatus(persona)"
                        title="Click para cambiar estado"
                    >
                        <div 
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors shrink-0"
                            :class="persona.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                        >
                            <span 
                                class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                :class="persona.activo ? 'translate-x-3.5' : 'translate-x-1'"
                            />
                        </div>
                    </div>
                </div>
                
                <div class="mb-4">
                    <h3 class="font-bold text-white text-lg leading-tight group-hover:text-pink-300 transition-colors" :class="{ 'truncate': hoveredCardId !== persona.id }">{{ persona.nombre_completo }}</h3>
                    <p class="text-sm text-white/50" :class="{ 'truncate': hoveredCardId !== persona.id }">{{ persona.puesto || 'Sin puesto definido' }}</p>
                </div>

                <div class="space-y-1 mb-4">
                    <div class="flex items-center gap-2 text-xs text-white/70 truncate" v-if="persona.email_personal">
                        <i class="fas fa-envelope text-white/30 w-4"></i>
                        {{ persona.email_personal }}
                    </div>
                    <div class="flex items-center gap-2 text-xs text-white/70 truncate" v-if="persona.celular_personal">
                        <i class="fas fa-phone text-white/30 w-4"></i>
                        {{ persona.celular_personal }}
                    </div>
                    <!-- Extra details on hover -->
                    <div v-if="hoveredCardId === persona.id" class="pt-2 mt-2 border-t border-white/10 text-xs text-white/60 animate-fade-in">
                        <p v-if="persona.observaciones" class="italic mb-2">"{{ persona.observaciones }}"</p>
                        <p class="text-pink-400">Click para editar</p>
                    </div>
                </div>

                <div class="mt-auto pt-4 border-t border-white/5 flex justify-between items-center">
                    <div class="flex items-center gap-1 text-xs text-white/40">
                        <i class="fas fa-link"></i>
                        <span>{{ persona.vinculos?.length || 0 }}</span>
                    </div>
                    <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button @click.stop="editPersona(persona)" class="text-white/50 hover:text-white" title="Editar"><i class="fas fa-pencil-alt"></i></button>
                        <button v-if="persona.activo" @click.stop="deletePersona(persona)" class="text-red-400/50 hover:text-red-400" title="Dar de baja"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            </div>
        </div>

        <!-- List View -->
        <div v-else class="grid grid-cols-1 gap-4">
             <div 
                v-for="persona in filteredPersonas" 
                :key="persona.id"
                @click="editPersona(persona)"
                class="group flex items-center justify-between p-4 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-colors"
             >
                <div class="flex items-center gap-4 flex-1 min-w-0">
                    <div class="h-10 w-10 rounded-full bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center text-white shrink-0 font-bold text-sm shadow-lg">
                        {{ getInitials(persona.nombre_completo) }}
                    </div>
                    <div class="min-w-0 flex-1 grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <h3 class="font-bold text-white truncate">{{ persona.nombre_completo }}</h3>
                            <p class="text-xs text-white/40 truncate">{{ persona.puesto || 'Sin puesto definido' }}</p>
                        </div>
                        <div class="flex flex-col justify-center">
                            <div class="flex items-center gap-2 text-sm text-white/70 truncate" v-if="persona.email_personal">
                                <i class="fas fa-envelope text-white/30 w-4"></i>
                                {{ persona.email_personal }}
                            </div>
                            <div class="flex items-center gap-2 text-sm text-white/70 truncate" v-if="persona.celular_personal">
                                <i class="fas fa-phone text-white/30 w-4"></i>
                                {{ persona.celular_personal }}
                            </div>
                        </div>
                         <div class="flex items-center gap-2 text-sm text-white/50">
                            <i class="fas fa-link text-white/30"></i>
                            <span v-if="persona.vinculos && persona.vinculos.length > 0">
                                {{ persona.vinculos.length }} Vínculo{{ persona.vinculos.length !== 1 ? 's' : '' }}
                            </span>
                            <span v-else class="italic text-white/30">Sin vínculos</span>
                        </div>
                    </div>
                </div>
                
                <div class="flex items-center gap-4 ml-4">
                    <div 
                        class="flex items-center gap-2 bg-black/20 px-2 py-1 rounded-full border border-white/5 cursor-pointer hover:bg-white/10 transition-colors"
                        @click.stop="togglePersonaStatus(persona)"
                        title="Click para cambiar estado"
                    >
                        <div 
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors shrink-0"
                            :class="persona.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                        >
                            <span 
                                class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                :class="persona.activo ? 'translate-x-3.5' : 'translate-x-1'"
                            />
                        </div>
                        <span class="text-[10px] uppercase font-bold text-white/50 hidden sm:inline select-none">{{ persona.activo ? 'Activo' : 'Inactivo' }}</span>
                    </div>
                    <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity w-16 justify-end">
                        <button @click.stop="editPersona(persona)" class="text-white/50 hover:text-white" title="Editar"><i class="fas fa-pencil-alt"></i></button>
                        <button v-if="persona.activo" @click.stop="deletePersona(persona)" class="text-red-400/50 hover:text-red-400" title="Dar de baja"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
             </div>
        </div>
      </div>
    </main>

    <!-- Right Inspector Panel -->
    <aside 
        class="w-80 border-l border-gray-800 bg-gray-900/95 flex flex-col z-30 shadow-2xl overflow-hidden"
    >
        <div v-if="!selectedPersona && !showNewInspector" class="flex flex-col items-center justify-center h-full text-white/30 p-6 text-center">
            <i class="fas fa-user-tie text-4xl mb-4"></i>
            <p>Seleccione un contacto para ver sus detalles</p>
        </div>
        <ContactoInspector 
            v-else
            :persona="selectedPersona"
            @close="closeInspector"
            @saved="handleContactoSaved"
        />
    </aside>

    <!-- Modals -->
    <CommandPalette :show="showCommandPalette" @close="showCommandPalette = false" @navigate="handleNavigation" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppSidebar from '../../components/layout/AppSidebar.vue'
import CommandPalette from '../../components/common/CommandPalette.vue'
import ContactoInspector from './components/ContactoInspector.vue'
import { useAgendaStore } from '../../stores/agenda'
import { useNotificationStore } from '../../stores/notification'
import { debounce } from 'lodash'

const router = useRouter()
const agendaStore = useAgendaStore()
const notificationStore = useNotificationStore()

const personas = computed(() => agendaStore.personas)
const loading = computed(() => agendaStore.loading)

const searchQuery = ref('')
const filterStatus = ref('active')
const showCommandPalette = ref(false)
const showNewInspector = ref(false)
const selectedPersona = ref(null)

onMounted(() => {
    fetchData()
})

const fetchData = async () => {
    await agendaStore.fetchPersonas({ status: 'all' })
}

const handleSearch = debounce(async () => {
    if (searchQuery.value.length >= 3) {
        await agendaStore.searchPersonas(searchQuery.value)
    } else if (searchQuery.value.length === 0) {
        await fetchData()
    }
}, 300)

const sortBy = ref('alpha_asc')
const viewMode = ref('list')
const showSortMenu = ref(false)

// Hover Zoom Logic
const hoveredCardId = ref(null)
let hoverTimeout = null

const handleMouseEnter = (id) => {
    hoverTimeout = setTimeout(() => {
        hoveredCardId.value = id
    }, 1000)
}

const handleMouseLeave = () => {
    if (hoverTimeout) clearTimeout(hoverTimeout)
    hoveredCardId.value = null
}

const filteredPersonas = computed(() => {
    let result = personas.value
    
    // Client-side filtering for status
    if (filterStatus.value === 'active') {
        result = result.filter(p => p.activo)
    } else if (filterStatus.value === 'inactive') {
        result = result.filter(p => !p.activo)
    }

    // Sorting
    return result.sort((a, b) => {
        switch (sortBy.value) {
            case 'alpha_asc':
                return a.nombre_completo.localeCompare(b.nombre_completo)
            case 'alpha_desc':
                return b.nombre_completo.localeCompare(a.nombre_completo)
            case 'id_asc':
                return String(a.id).localeCompare(String(b.id))
            case 'id_desc':
                return String(b.id).localeCompare(String(a.id))
            case 'usage':
                // Fallback to name if usage not available
                return (b.contador_uso || 0) - (a.contador_uso || 0)
            default:
                return 0
        }
    })
})

const getInitials = (name) => {
    if (!name) return '?'
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
}

const openNewContacto = () => {
    selectedPersona.value = null
    showNewInspector.value = true
}

const editPersona = (persona) => {
    selectedPersona.value = persona
    showNewInspector.value = false // Logic handled by computed in template or just by existence of selectedPersona
}

const closeInspector = () => {
    showNewInspector.value = false
    selectedPersona.value = null
}

const handleContactoSaved = async () => {
    // await fetchData() // Removed to rely on store local update
    notificationStore.add('Contacto guardado correctamente', 'success')
    closeInspector()
}

const togglePersonaStatus = async (persona) => {
    if (persona.activo) {
        // If active, use the delete routine (Tachito) which handles confirmation and deactivation
        await deletePersona(persona)
    } else {
        // If inactive, activate directly
        try {
            // Optimistic update for activation
            persona.activo = true
            await agendaStore.updatePersona(persona.id, { activo: true })
            notificationStore.add('Contacto activado', 'success')
        } catch (e) {
            console.error(e)
            persona.activo = false // Revert
            notificationStore.add('Error al activar', 'error')
        }
    }
}

const deletePersona = async (persona) => {
    if (!confirm(`¿Seguro que desea dar de baja a ${persona.nombre_completo}?`)) return
    try {
        await agendaStore.updatePersona(persona.id, { activo: false })
        // await fetchData() // Removed to rely on store local update
        notificationStore.add('Contacto dado de baja', 'success')
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al dar de baja', 'error')
    }
}

const handleNavigation = (payload) => {
    if (payload.name === 'Logout') {
        logout()
    } else {
        router.push(payload)
    }
}

const logout = () => {
    if(confirm('¿Desea cerrar sesión?')) {
        localStorage.removeItem('token')
        router.push('/login')
    }
}
</script>

<style>
body {
    background-color: #0a0a0a;
}
</style>
