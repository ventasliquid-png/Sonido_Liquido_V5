<template>
  <div class="flex h-screen w-full bg-[#0a0a0a] text-gray-200 overflow-hidden font-sans">
    <!-- Left Sidebar (Navigation) -->
    <aside class="flex w-64 flex-col border-r border-white/10 bg-black/20">
      <!-- Logo Area -->
      <div class="flex h-16 items-center px-6 border-b border-white/10">
        <div class="h-8 w-8 rounded bg-gradient-to-br from-cyan-400 to-blue-500 mr-3"></div>
        <span class="font-outfit text-lg font-bold tracking-tight text-white">HAWE <span class="text-cyan-400">V5</span></span>
      </div>

      <!-- Nav Links -->
      <nav class="flex-1 space-y-1 p-4 overflow-y-auto">
        <a href="#" class="flex items-center rounded-lg bg-white/10 px-4 py-3 text-sm font-medium text-white shadow-md shadow-black/10 border-l-2 border-cyan-400">
          <i class="fas fa-users w-6 text-cyan-400"></i>
          Clientes
        </a>
        
        <!-- Filters Submenu (Only for Clientes) -->
        <div class="mt-2 pl-4 space-y-1">
            <h4 class="px-2 text-xs font-semibold uppercase text-white/50 mb-2 mt-4">Segmentos</h4>
            <button 
                @click="selectedSegmento = null"
                class="w-full flex items-center rounded-md px-2 py-1.5 text-xs font-medium transition-colors"
                :class="selectedSegmento === null ? 'text-cyan-300 bg-cyan-900/40' : 'text-white/70 hover:text-white hover:bg-white/10'"
            >
                <i class="fas fa-circle w-4 text-[8px]" :class="selectedSegmento === null ? 'text-cyan-400' : 'text-white/30'"></i>
                Todos
            </button>
            <button 
                v-for="seg in segmentos" 
                :key="seg.id"
                @click="selectedSegmento = seg.id"
                class="w-full flex items-center rounded-md px-2 py-1.5 text-xs font-medium transition-colors"
                :class="selectedSegmento === seg.id ? 'text-cyan-300 bg-cyan-900/40' : 'text-white/70 hover:text-white hover:bg-white/10'"
            >
                <i class="fas fa-circle w-4 text-[8px]" :class="selectedSegmento === seg.id ? 'text-cyan-400' : 'text-white/30'"></i>
                {{ seg.nombre }}
            </button>
        </div>

        <div class="my-4 border-t border-white/10"></div>

        <a href="#" class="flex items-center rounded-lg px-4 py-3 text-sm font-medium text-white/70 transition-colors hover:bg-white/10 hover:text-white">
          <i class="fas fa-box w-6"></i>
          Productos
        </a>
        <a href="#" class="flex items-center rounded-lg px-4 py-3 text-sm font-medium text-white/70 transition-colors hover:bg-white/10 hover:text-white">
          <i class="fas fa-shopping-cart w-6"></i>
          Pedidos
        </a>
      </nav>

      <!-- User Profile -->
      <div class="border-t border-white/10 p-4">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-full bg-white/10"></div>
          <div>
            <p class="text-sm font-medium text-white">Usuario</p>
            <p class="text-xs text-white/50">Admin</p>
          </div>
        </div>
      </div>
    </aside>

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
          <div class="relative group">
            <button class="text-white/70 hover:text-white transition-colors" title="Ordenar">
                <i class="fas fa-sort-amount-down"></i>
            </button>
            <!-- Dropdown -->
            <div class="absolute right-0 mt-2 w-48 bg-[#0a253a] border border-white/10 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                <div class="py-1">
                    <button @click="sortBy = 'alpha_asc'" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_asc' }">A-Z Alfabético</button>
                    <button @click="sortBy = 'alpha_desc'" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_desc' }">Z-A Alfabético</button>
                    <div class="border-t border-white/10 my-1"></div>
                    <button @click="sortBy = 'id_asc'" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'id_asc' }">Más Antiguos</button>
                    <button @click="sortBy = 'id_desc'" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'id_desc' }">Más Recientes</button>
                    <div class="border-t border-white/10 my-1"></div>
                    <button @click="sortBy = 'usage'" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'usage' }">Más Usados</button>
                    <button @click="sortBy = 'movement_desc'" class="block w-full text-left px-4 py-2 text-sm text-white/50 cursor-not-allowed" title="Próximamente">Mayor Movimiento</button>
                    <button @click="sortBy = 'abc'" class="block w-full text-left px-4 py-2 text-sm text-white/50 cursor-not-allowed" title="Próximamente">ABC Compras</button>
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
            @dblclick="openCanvas(cliente)"
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
        <InspectorPanel :item="selectedCliente" />
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import FichaCard from '../components/hawe/FichaCard.vue'
import InspectorPanel from '../components/canvas/InspectorPanel.vue'
import { useClientesStore } from '../stores/clientes'
import { useMaestrosStore } from '../stores/maestros'

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
const sortBy = ref('alpha_asc') // Default sort

onMounted(async () => {
  console.log('HaweView mounted')
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
            case 'id_asc': // Oldest created (assuming ID correlates or we use created_at if available, using ID for now as proxy)
                return String(a.id).localeCompare(String(b.id)) // UUIDs aren't strictly time-ordered, but it's a stable sort. Ideally use created_at.
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

const openCanvas = (cliente) => {
    console.log('Opening canvas for', cliente.razon_social)
    router.push({ name: 'HaweClientCanvas', params: { id: cliente.id } })
}
</script>

<style>
/* Global overrides for this view to ensure full dark mode feel */
body {
    background-color: #0a0a0a;
}
</style>
