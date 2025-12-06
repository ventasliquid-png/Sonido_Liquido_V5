<template>
  <div class="flex h-screen w-full bg-[#081c26] text-gray-200 overflow-hidden font-sans">
    <!-- Left Sidebar (Navigation) -->
    <!-- Left Sidebar (Navigation) is now in HaweLayout -->

    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative">
      <!-- Top Bar -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-white/10 bg-black/10 px-6 backdrop-blur-sm">
        <!-- Breadcrumbs / Title -->
        <h1 class="font-outfit text-xl font-semibold text-white">
            Explorador de Clientes
            <span v-if="selectedSegmento" class="ml-2 text-sm font-normal text-gray-500">
                / {{ getSegmentoName(selectedSegmento) }}
            </span>
        </h1>

        <!-- Search & Tools -->
        <div class="flex items-center gap-4">
          <div class="relative">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar..."
              class="h-9 w-64 rounded-full border border-gray-700 bg-gray-800 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
            />
          </div>
          <div class="h-6 w-px bg-white/10"></div>
          
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

          <!-- Sort Menu -->
          <div class="relative">
            <button 
                @click="showSortMenu = !showSortMenu" 
                class="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white hover:bg-white/10 transition-colors" 
                title="Ordenar"
            >
                <i class="fas fa-sort-amount-down"></i>
                <span v-if="sortBy === 'usage'">POPULARIDAD</span>
                <span v-else-if="sortBy === 'alpha_asc'">A-Z</span>
                <span v-else-if="sortBy === 'alpha_desc'">Z-A</span>
                <span v-else-if="sortBy === 'id_asc'">ANTIGUOS</span>
                <span v-else-if="sortBy === 'id_desc'">RECIENTES</span>
            </button>
            
            <!-- Dropdown -->
            <div v-if="showSortMenu" class="absolute right-0 mt-2 w-48 bg-[#0a253a] border border-white/10 rounded-lg shadow-xl z-50 overflow-hidden">
                <div class="fixed inset-0 z-40" @click="showSortMenu = false"></div>
                <div class="relative z-50 py-1">
                    <button @click="sortBy = 'usage'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'usage' }">Más Usados</button>
                    <button @click="sortBy = 'alpha_asc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_asc' }">A-Z Alfabético</button>
                    <button @click="sortBy = 'alpha_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_desc' }">Z-A Alfabético</button>
                    <button @click="sortBy = 'id_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'id_desc' }">Más Recientes</button>
                </div>
            </div>
          </div>

          <div class="h-6 w-px bg-white/10"></div>

          <!-- View Toggle -->
          <div class="flex bg-white/5 rounded-lg p-1 border border-white/10">
            <button 
                @click="viewMode = 'grid'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'grid' ? 'bg-cyan-600 text-white shadow-sm' : 'text-white/50 hover:text-white'"
                title="Vista Cuadrícula"
            >
                <i class="fas fa-border-all"></i>
            </button>
            <button 
                @click="viewMode = 'list'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'list' ? 'bg-cyan-600 text-white shadow-sm' : 'text-white/50 hover:text-white'"
                title="Vista Lista"
            >
                <i class="fas fa-list"></i>
            </button>
          </div>

          <div class="h-6 w-px bg-white/10"></div>

          <button 
            @click="openNewCliente"
            class="flex items-center gap-2 rounded-lg bg-cyan-600 px-3 py-1.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/20 transition-all hover:bg-cyan-500 hover:shadow-cyan-500/40"
          >
            <i class="fas fa-plus"></i>
            <span class="hidden sm:inline">Nuevo</span>
          </button>

        </div>
      </header>

      <!-- Content List -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-gray-900 scrollbar-thumb-gray-700">
        
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
          <div v-for="cliente in filteredClientes" :key="cliente.id" class="relative w-full min-h-[140px]">
            <FichaCard
                class="w-full"
                :title="cliente.razon_social"
                :subtitle="cliente.cuit"
                :status="cliente.activo ? 'active' : 'inactive'"
                :selected="selectedId === cliente.id"
                @click="selectCliente(cliente)"
                @contextmenu.prevent="handleClientContextMenu($event, cliente)"
            >
                <template #icon>
                    <i class="fas fa-user"></i>
                </template>
                <template #actions>
                    <!-- Toggle Switch -->
                    <button 
                        @click.stop="toggleClienteStatus(cliente)"
                        v-if="cliente.activo"
                        class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 ml-2 bg-green-500/50"
                        title="Desactivar"
                    >
                        <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm translate-x-3.5" />
                    </button>
                     <button 
                        @click.stop="toggleClienteStatus(cliente)"
                        v-else
                        class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 ml-2 bg-red-500/50"
                        title="Activar"
                    >
                        <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm translate-x-1" />
                    </button>
                </template>
            </FichaCard>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="flex flex-col gap-2">
            <div 
                v-for="cliente in filteredClientes" 
                :key="cliente.id"
                @click="selectCliente(cliente)"
                @contextmenu.prevent="handleClientContextMenu($event, cliente)"
                class="group flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-colors"
                :class="{ 'ring-1 ring-cyan-500 bg-cyan-500/10': selectedId === cliente.id }"
            >
                <div class="flex items-center gap-4">
                    <div class="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                        {{ cliente.razon_social.substring(0,1).toUpperCase() }}
                    </div>
                    <div>
                        <h3 class="font-bold text-white">{{ cliente.razon_social }}</h3>
                        <p class="text-xs text-white/50 font-mono">{{ cliente.cuit }}</p>
                    </div>
                </div>
                
                <div class="flex items-center gap-4">
                    <span class="text-xs text-white/50">{{ getSegmentoName(cliente.segmento_id) }}</span>
                    <!-- List Toggle Switch -->
                    <button 
                        @click.stop="toggleClienteStatus(cliente)"
                        v-if="cliente.activo"
                        class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 ml-2 bg-green-500/50"
                        title="Desactivar"
                    >
                        <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm translate-x-3.5" />
                    </button>
                    <button 
                        @click.stop="toggleClienteStatus(cliente)"
                        v-else
                        class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 ml-2 bg-red-500/50"
                        title="Activar"
                    >
                        <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm translate-x-1" />
                    </button>
                    <i class="fas fa-chevron-right text-white/20 group-hover:text-white/50 transition-colors"></i>
                </div>
            </div>
        </div>

      </div>
    </main>

    <!-- Right Inspector Panel -->
    <ClienteInspector 
        :modelValue="selectedCliente" 
        :isNew="selectedId === 'new'"
        @close="closeInspector"
        @save="handleInspectorSave"
        @delete="handleInspectorDelete"
        @manage-segmentos="handleManageSegmentos"
        @switch-client="handleSwitchClient"
    />

    <!-- Modals & Context Menu -->
    <SegmentoForm 
        :show="showSegmentoModal" 
        :id="editingSegmentoId" 
        @close="closeSegmentoModal" 
        @saved="handleSegmentoSaved"
    />

    <SegmentoList 
        v-if="showSegmentoList"
        :isStacked="true"
        class="fixed inset-0 z-[60] bg-white m-4 rounded-lg shadow-2xl overflow-hidden"
        @close="showSegmentoList = false"
    />
    
    <!-- Transportes Modal (Triggered by Sidebar/CommandPalette) -->
    <div v-if="showTransporteManager" class="fixed inset-0 z-[70] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-[#0f172a] w-full max-w-6xl h-[85vh] rounded-2xl shadow-2xl overflow-hidden border border-white/10 flex flex-col">
            <TransporteManager :isModal="true" @close="showTransporteManager = false" />
        </div>
    </div>

    <ContextMenu 
        v-model="contextMenu.show" 
        :x="contextMenu.x" 
        :y="contextMenu.y" 
        :actions="contextMenu.actions"
        @close="contextMenu.show = false"
    />

    <!-- Global Command Palette -->
    <CommandPalette :show="showCommandPalette" @close="showCommandPalette = false" @navigate="handleSidebarNavigation" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import FichaCard from '../components/hawe/FichaCard.vue'
import ClienteInspector from './Hawe/components/ClienteInspector.vue'
import CommandPalette from '../components/common/CommandPalette.vue'
import TransporteManager from './Hawe/components/TransporteManager.vue'
import { useClientesStore } from '../stores/clientes'
import { useMaestrosStore } from '../stores/maestros'
import ContextMenu from '../components/common/ContextMenu.vue'
import SegmentoForm from './Maestros/SegmentoForm.vue'
import SegmentoList from './Maestros/SegmentoList.vue'
import { useNotificationStore } from '../stores/notification'

const clienteStore = useClientesStore()
const maestrosStore = useMaestrosStore()
const notificationStore = useNotificationStore()
const router = useRouter()

const clientes = computed(() => clienteStore.clientes)
const segmentos = ref([])
const selectedId = ref(null)
const selectedCliente = ref(null)
const selectedSegmento = ref(null)
const searchQuery = ref('')
const filterStatus = ref('active') // Default to active
const sortBy = ref('usage') // Default to usage (Popularity)
const viewMode = ref('grid')
const showSortMenu = ref(false)
const showCommandPalette = ref(false)
const showTransporteManager = ref(false)

// Segmento ABM Logic
const showSegmentoModal = ref(false)
const showSegmentoList = ref(false)
const editingSegmentoId = ref(null)
const contextMenu = reactive({
    show: false,
    x: 0,
    y: 0,
    actions: []
})

const handleSidebarNavigation = (payload) => {
    if (payload.name === 'Transportes') {
        router.push({ name: 'Transportes' })
    } else if (payload.name === 'Segmentos') {
        showSegmentoList.value = true
    } else if (payload.name === 'Logout') {
        logout()
    } else {
        // Fallback to router if it's a route name
        router.push(payload)
    }
}

const openSegmentoModal = (segmento = null) => {
    editingSegmentoId.value = segmento ? segmento.id : null
    showSegmentoModal.value = true
}

const closeSegmentoModal = () => {
    showSegmentoModal.value = false
    editingSegmentoId.value = null
}

const handleSegmentoSaved = async () => {
    await maestrosStore.fetchSegmentos('all')
    segmentos.value = maestrosStore.segmentos
}

const handleDeleteSegmento = async (segmento) => {
    if (!confirm(`¿Está seguro de dar de baja a ${segmento.nombre}?`)) return
    try {
        await maestrosStore.updateSegmento(segmento.id, { ...segmento, activo: false })
        await maestrosStore.fetchSegmentos('all')
        segmentos.value = maestrosStore.segmentos
    } catch (error) {
        alert('Error al dar de baja.')
        console.error(error)
    }
}

const handleContextMenu = (e, segmento) => {
    contextMenu.show = true
    contextMenu.x = e.clientX
    contextMenu.y = e.clientY
    contextMenu.actions = [
        {
            label: 'Editar',
            icon: '✏️',
            handler: () => openSegmentoModal(segmento)
        },
        {
            label: 'Dar de Baja',
            icon: '🗑️',
            handler: () => handleDeleteSegmento(segmento)
        }
    ]
}

const handleHeaderContextMenu = (e) => {
    contextMenu.show = true
    contextMenu.x = e.clientX
    contextMenu.y = e.clientY
    contextMenu.actions = [
        {
            label: 'Nuevo Segmento',
            icon: '➕',
            handler: () => openSegmentoModal()
        },
        {
            label: 'Administrar Segmentos',
            icon: '📋',
            handler: () => { showSegmentoList.value = true }
        }
    ]
}

onMounted(async () => {
  console.log('HaweView mounted')
  window.addEventListener('keydown', handleKeydown)
  try {
      await Promise.all([
          clienteStore.fetchClientes(),
          maestrosStore.fetchSegmentos()
      ])
      // clientes.value = clienteStore.clientes // Computed now
      segmentos.value = maestrosStore.segmentos
  } catch (e) {
      console.error('Error loading HaweView data:', e)
  }
})

const normalizeText = (text) => {
    return text ? text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase() : ''
}

const filteredClientes = computed(() => {
    let result = clientes.value.filter(cliente => {
        // Filter by Status
        if (filterStatus.value === 'active' && !cliente.activo) return false
        if (filterStatus.value === 'inactive' && cliente.activo) return false

        // Filter by Segment
        if (selectedSegmento.value && cliente.segmento_id !== selectedSegmento.value) {
            return false
        }
        // Filter by Search
        if (searchQuery.value) {
            const query = normalizeText(searchQuery.value)
            return normalizeText(cliente.razon_social).includes(query) || 
                   cliente.cuit.includes(query)
        }
        return true
    })

    // Sorting
    return result.sort((a, b) => {
        switch (sortBy.value) {
            case 'alpha_asc':
                return a.razon_social.localeCompare(b.razon_social)
            case 'alpha_desc':
                return b.razon_social.localeCompare(a.razon_social)
            case 'id_asc':
                return String(a.id).localeCompare(String(b.id))
            case 'id_desc':
                return String(b.id).localeCompare(String(a.id))
            case 'usage':
                return (b.contador_uso || 0) - (a.contador_uso || 0)
            default:
                return 0
        }
    })
})

const getSegmentoName = (id) => {
    const seg = segmentos.value.find(s => s.id === id)
    return seg ? seg.nombre : ''
}

const selectCliente = async (cliente) => {
    selectedId.value = cliente.id
    // Fetch full details (including domicilios) because list view might exclude them
    try {
        const fullCliente = await clienteStore.fetchClienteById(cliente.id)
        selectedCliente.value = { ...fullCliente }
    } catch (e) {
        console.error("Error fetching full client details", e)
        selectedCliente.value = { ...cliente } // Fallback
    }
}

const openNewCliente = () => {
    selectedId.value = 'new'
    selectedCliente.value = {
        razon_social: '',
        cuit: '',
        activo: true,
        condicion_iva_id: null, // Should match model
        segmento_id: null,
        domicilios: [],
        vinculos: []
    }
}

const closeInspector = () => {
    selectedId.value = null
    selectedCliente.value = null
}

const handleInspectorSave = async (clienteData) => {
    try {
        if (selectedId.value === 'new') {
            await clienteStore.createCliente(clienteData)
            notificationStore.add('Cliente creado', 'success')
        } else {
            await clienteStore.updateCliente(clienteData.id, clienteData)
            notificationStore.add('Cliente actualizado', 'success')
        }
        closeInspector()
    } catch (error) {
        console.error(error)
        notificationStore.add('Error al guardar cliente', 'error')
    }
}

const handleInspectorDelete = async (clienteData) => {
    try {
        await clienteStore.updateCliente(clienteData.id, { ...clienteData, activo: false })
        notificationStore.add('Cliente dado de baja', 'success')
        closeInspector()
    } catch (error) {
        console.error(error)
        notificationStore.add('Error al dar de baja', 'error')
    }
}

const toggleClienteStatus = async (cliente) => {
    const newStatus = !cliente.activo
    
    // Logic: Active -> Inactive requires confirmation
    if (cliente.activo && !newStatus) {
        if (!confirm(`¿Está seguro de desactivar al cliente ${cliente.razon_social}?`)) {
            return
        }
    }
    
    try {
        await clienteStore.updateCliente(cliente.id, { ...cliente, activo: newStatus })
        notificationStore.add(newStatus ? 'Cliente reactivado' : 'Cliente desactivado', 'success')
    } catch (error) {
        console.error(error)
        notificationStore.add('Error al cambiar estado', 'error')
    }
}

const handleKeydown = (e) => {
    // Command Palette Shortcut (Ctrl+K)
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault()
        showCommandPalette.value = !showCommandPalette.value
        return
    }

    if ((e.code === 'Space' || e.code === 'Enter') && selectedCliente.value && !showCommandPalette.value && !showTransporteManager.value) {
        // e.preventDefault()
        // openCanvas(selectedCliente.value) // No longer needed
    }
}

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

const handleManageSegmentos = () => {
    showSegmentoList.value = true
}

const handleSwitchClient = async (clientId) => {
    selectedId.value = clientId
    try {
        const fullCliente = await clienteStore.fetchClienteById(clientId)
        selectedCliente.value = { ...fullCliente }
    } catch (e) {
        console.error("Error switching client", e)
    }
}

const handleClientContextMenu = (e, client) => {
    contextMenu.show = true
    contextMenu.x = e.clientX
    contextMenu.y = e.clientY
    contextMenu.actions = [
        {
            label: 'Nuevo Cliente',
            icon: '➕',
            handler: () => openNewCliente()
        },
        {
            label: '----------------',
            disabled: true
        },
        {
            label: `Editar ${client.razon_social}`,
            icon: '✏️',
            handler: () => selectCliente(client)
        },
        {
            label: 'Dar de Baja',
            icon: '🗑️',
            handler: () => {
                if(confirm(`¿Está seguro de dar de baja a ${client.razon_social}?`)) {
                    handleInspectorDelete(client)
                }
            }
        }
    ]
}

const logout = () => {
    if(confirm('¿Desea cerrar sesión?')) {
        localStorage.removeItem('token')
        router.push('/login')
    }
}
</script>

<style>
/* Global overrides for this view to ensure full dark mode feel */
body {
    background-color: #0a0a0a;
}
</style>
