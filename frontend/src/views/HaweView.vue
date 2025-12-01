<template>
  <div class="flex h-screen w-full bg-[var(--hawe-bg-main)] text-gray-200 overflow-hidden font-sans">
    <!-- Left Sidebar (Navigation) -->
    <AppSidebar 
        @logout="logout" 
        @open-command-palette="showCommandPalette = true"
        @navigate="handleSidebarNavigation"
    />

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
          <button 
            @click="router.push({ name: 'HaweClientCanvas', params: { id: 'new' } })"
            class="flex items-center gap-2 rounded-lg bg-cyan-600 px-3 py-1.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/20 transition-all hover:bg-cyan-500 hover:shadow-cyan-500/40"
          >
            <i class="fas fa-plus"></i>
            <span class="hidden sm:inline">Nuevo</span>
          </button>
          <div class="h-6 w-px bg-white/10"></div>
          <div class="h-6 w-px bg-white/10"></div>
          
          <!-- Sort Menu -->
          <div class="relative">
            <button 
                @click="showSortMenu = !showSortMenu" 
                class="text-white/70 hover:text-white transition-colors flex items-center gap-2" 
                title="Ordenar"
            >
                <i class="fas fa-sort-amount-down"></i>
                <span class="text-xs font-mono text-cyan-400" v-if="sortBy === 'usage'">POPULARIDAD</span>
                <span class="text-xs font-mono text-cyan-400" v-else-if="sortBy === 'alpha_asc'">A-Z</span>
                <span class="text-xs font-mono text-cyan-400" v-else-if="sortBy === 'alpha_desc'">Z-A</span>
                <span class="text-xs font-mono text-cyan-400" v-else-if="sortBy === 'id_asc'">ANTIGUEDAD</span>
                <span class="text-xs font-mono text-cyan-400" v-else-if="sortBy === 'id_desc'">RECIENTES</span>
            </button>
            
            <!-- Dropdown -->
            <div v-if="showSortMenu" class="absolute right-0 mt-2 w-48 bg-[#0a253a] border border-white/10 rounded-lg shadow-xl z-50">
                <!-- Click outside overlay -->
                <div class="fixed inset-0 z-40" @click="showSortMenu = false"></div>
                
                <div class="relative z-50 py-1">
                    <button @click="sortBy = 'usage'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'usage' }">Más Usados (Popularidad)</button>
                    <div class="border-t border-white/10 my-1"></div>
                    <button @click="sortBy = 'alpha_asc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_asc' }">A-Z Alfabético</button>
                    <button @click="sortBy = 'alpha_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_desc' }">Z-A Alfabético</button>
                    <div class="border-t border-white/10 my-1"></div>
                    <button @click="sortBy = 'id_asc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'id_asc' }">Más Antiguos</button>
                    <button @click="sortBy = 'id_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'id_desc' }">Más Recientes</button>
                </div>
            </div>
          </div>
          
          <button class="text-white/70 hover:text-white"><i class="fas fa-list"></i></button>
        </div>
      </header>

      <!-- Content Grid -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-gray-900 scrollbar-thumb-gray-700">
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
          <FichaCard
            v-for="cliente in filteredClientes"
            :key="cliente.id"
            :title="cliente.razon_social"
            :subtitle="cliente.cuit"
            :status="cliente.activo ? 'active' : 'inactive'"
            :selected="selectedId === cliente.id"
            @click="selectCliente(cliente)"
            @select="selectCliente(cliente)"
            @dblclick="openCanvas(cliente)"
            @contextmenu.prevent="handleClientContextMenu($event, cliente)"
          >
            <template #icon>
                <i class="fas fa-user"></i>
            </template>
          </FichaCard>
        </div>
      </div>
    </main>

    <!-- Right Inspector Panel -->
    <aside class="w-80 border-l border-gray-800 bg-gray-900/50">
        <InspectorPanel :item="selectedCliente" @open="openCanvas(selectedCliente)" />
    </aside>

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
import InspectorPanel from '../components/canvas/InspectorPanel.vue'
import AppSidebar from '../components/layout/AppSidebar.vue'
import CommandPalette from '../components/common/CommandPalette.vue'
import TransporteManager from './Hawe/components/TransporteManager.vue'
import { useClientesStore } from '../stores/clientes'
import { useMaestrosStore } from '../stores/maestros'
import ContextMenu from '../components/common/ContextMenu.vue'
import SegmentoForm from './Maestros/SegmentoForm.vue'
import SegmentoList from './Maestros/SegmentoList.vue'

const clienteStore = useClientesStore()
const maestrosStore = useMaestrosStore()
const router = useRouter()

const clientes = ref([])
const segmentos = ref([])
const selectedId = ref(null)
const selectedCliente = ref(null)
const selectedSegmento = ref(null)
const searchQuery = ref('')
const filterStatus = ref('active') // Default to active
const sortBy = ref('usage') // Default to usage (Popularity)
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
      clientes.value = clienteStore.clientes
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

const selectCliente = (cliente) => {
    selectedId.value = cliente.id
    selectedCliente.value = cliente
}

const openCanvas = async (cliente) => {
    try {
        await clienteStore.incrementUsage(cliente.id)
    } catch (e) {
        console.error('Failed to increment usage', e)
    }
    router.push({ name: 'HaweClientCanvas', params: { id: cliente.id } })
}

const handleKeydown = (e) => {
    // Command Palette Shortcut (Ctrl+K)
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault()
        showCommandPalette.value = !showCommandPalette.value
        return
    }

    if ((e.code === 'Space' || e.code === 'Enter') && selectedCliente.value && !showCommandPalette.value && !showTransporteManager.value) {
        e.preventDefault()
        openCanvas(selectedCliente.value)
    }
}

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

const handleClientContextMenu = (e, client) => {
    contextMenu.show = true
    contextMenu.x = e.clientX
    contextMenu.y = e.clientY
    contextMenu.actions = [
        {
            label: 'Nueva Ficha',
            icon: '➕',
            handler: () => router.push({ name: 'HaweClientCanvas', params: { id: 'new' } })
        },
        {
            label: 'Administrar Fichas',
            icon: '📋',
            handler: () => router.push('/hawe') // Already here, but consistent with request
        },
        {
            label: '----------------',
            disabled: true
        },
        {
            label: `Editar ${client.razon_social}`,
            icon: '✏️',
            handler: () => openCanvas(client)
        },
        {
            label: 'Dar de Baja',
            icon: '🗑️',
            handler: () => {
                if(confirm(`¿Está seguro de dar de baja a ${client.razon_social}?`)) {
                    // store.deleteCliente(client.id) // Implement delete logic
                    console.log('Dar de baja', client.id)
                }
            }
        },
        {
            label: 'IA',
            icon: '✨',
            handler: () => alert('Funcionalidad IA próximamente')
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
