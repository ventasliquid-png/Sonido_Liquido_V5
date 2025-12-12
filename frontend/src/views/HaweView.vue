<template>
  <div class="flex h-screen w-full bg-[#081c26] text-gray-200 overflow-hidden font-sans">
    
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative min-w-0">
      <!-- Top Bar -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-cyan-900/20 bg-[#0a253a]/50 px-6 backdrop-blur-sm shrink-0">
        <!-- Breadcrumbs / Title -->
        <h1 class="font-outfit text-xl font-semibold text-white">
            Explorador de Clientes
            <span v-if="selectedSegmento" class="ml-2 text-sm font-normal text-cyan-400">
                / {{ getSegmentoName(selectedSegmento) }}
            </span>
        </h1>

        <!-- Search & Tools -->
        <div class="flex items-center gap-4">
          <div class="relative">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-cyan-500/50"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar..."
              class="h-9 w-64 rounded-full border border-cyan-900/30 bg-[#020a0f] pl-10 pr-4 text-sm text-cyan-100 placeholder-cyan-900/50 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
            />
          </div>
          <div class="h-6 w-px bg-cyan-900/20"></div>
          
          <!-- Status Filter -->
          <div class="flex bg-cyan-900/10 rounded-lg p-1 border border-cyan-900/20">
            <button 
                @click="filterStatus = 'all'"
                class="px-3 py-1 text-xs font-bold rounded-md transition-all"
                :class="filterStatus === 'all' ? 'bg-indigo-600/70 text-white shadow-md ring-1 ring-indigo-500' : 'text-cyan-100/40 hover:text-cyan-100 hover:bg-cyan-500/10'"
            >
                Todos
            </button>
            <button 
                @click="filterStatus = 'active'"
                class="px-3 py-1 text-xs font-bold rounded-md transition-all"
                :class="filterStatus === 'active' ? 'bg-green-600/70 text-white shadow-md ring-1 ring-green-500' : 'text-cyan-100/40 hover:text-cyan-100 hover:bg-cyan-500/10'"
            >
                Activos
            </button>
            <button 
                @click="filterStatus = 'inactive'"
                class="px-3 py-1 text-xs font-bold rounded-md transition-all"
                :class="filterStatus === 'inactive' ? 'bg-red-600/70 text-white shadow-md ring-1 ring-red-500' : 'text-cyan-100/40 hover:text-cyan-100 hover:bg-cyan-500/10'"
            >
                Inactivos
            </button>
          </div>

          <div class="h-6 w-px bg-cyan-900/20"></div>

          <!-- Sort Menu -->
          <div class="relative">
            <button 
                @click="showSortMenu = !showSortMenu" 
                class="flex items-center gap-2 rounded-lg border border-cyan-900/20 bg-cyan-900/10 px-3 py-1.5 text-xs font-medium text-cyan-200 hover:bg-cyan-900/20 transition-colors" 
                title="Ordenar"
            >
                <i class="fas fa-sort-amount-down"></i>
                <span v-if="sortBy === 'usage'">POPULARIDAD</span>
                <span v-else-if="sortBy === 'alpha_asc'">A-Z</span>
                <span v-else-if="sortBy === 'alpha_desc'">Z-A</span>
                <span v-else>ordenar</span>
            </button>
            
            <!-- Dropdown -->
            <div v-if="showSortMenu" class="absolute right-0 mt-2 w-48 bg-[#0a253a] border border-cyan-500/30 rounded-lg shadow-xl z-50 overflow-hidden">
                <div class="fixed inset-0 z-40" @click="showSortMenu = false"></div>
                <div class="relative z-50 py-1">
                    <button @click="sortBy = 'usage'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-cyan-100 hover:bg-cyan-500/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'usage' }">Más Usados</button>
                    <button @click="sortBy = 'alpha_asc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-cyan-100 hover:bg-cyan-500/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_asc' }">A-Z Alfabético</button>
                    <button @click="sortBy = 'alpha_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-cyan-100 hover:bg-cyan-500/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_desc' }">Z-A Alfabético</button>
                    <button @click="sortBy = 'id_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-cyan-100 hover:bg-cyan-500/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'id_desc' }">Más Recientes</button>
                </div>
            </div>
          </div>

          <div class="h-6 w-px bg-cyan-900/20"></div>

          <!-- View Toggle -->
          <div class="flex bg-cyan-900/10 rounded-lg p-1 border border-cyan-900/20">
            <button 
                @click="viewMode = 'grid'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'grid' ? 'bg-cyan-500/20 text-cyan-400' : 'text-cyan-900/50 hover:text-cyan-200'"
                title="Vista Cuadrícula"
            >
                <i class="fas fa-border-all"></i>
            </button>
            <button 
                @click="viewMode = 'list'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'list' ? 'bg-cyan-500/20 text-cyan-400' : 'text-cyan-900/50 hover:text-cyan-200'"
                title="Vista Lista"
            >
                <i class="fas fa-list"></i>
            </button>
          </div>

          <button 
            @click="openNewCliente"
            class="ml-2 flex items-center gap-2 rounded-lg bg-cyan-600 px-4 py-1.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/20 transition-all hover:bg-cyan-500 hover:shadow-cyan-500/40"
          >
            <i class="fas fa-plus"></i>
            <span class="hidden sm:inline">Nuevo</span>
          </button>

        </div>
      </header>

      <!-- Content List -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-cyan-900/10 scrollbar-thumb-cyan-900/30">
        
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
          <div v-for="cliente in filteredClientes" :key="cliente.id" class="relative w-full min-h-[140px]">
            <FichaCard
                class="w-full"
                :title="cliente.razon_social"
                :subtitle="cliente.cuit"
                :selected="selectedId === cliente.id"
                :hasLogisticsAlert="cliente.requiere_entrega"
                :extraData="{
                    segmento: getSegmentoName(cliente.segmento_id),
                    domicilio: cliente.domicilio_fiscal_resumen,
                    contacto: cliente.contacto_principal_nombre
                }"
                @click="selectCliente(cliente)"
                @dblclick="selectCliente(cliente)"
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
            <!-- Header Row -->
             <div class="flex items-center justify-between px-4 py-2 text-xs font-bold text-cyan-900/50 uppercase tracking-wider">
                <div class="flex-1">Cliente</div>
                <div class="w-1/4 hidden md:block">Segmento</div>
                <div class="w-24 text-center">Estado</div>
                <div class="w-10"></div>
            </div>

            <div 
                v-for="cliente in filteredClientes" 
                :key="cliente.id"
                @click="selectCliente(cliente)"
                @dblclick="selectCliente(cliente)"
                @contextmenu.prevent="handleClientContextMenu($event, cliente)"
                class="group flex items-center justify-between p-3 rounded-lg border border-cyan-900/10 bg-cyan-900/5 hover:bg-cyan-900/10 cursor-pointer transition-colors"
                :class="{ 'ring-1 ring-cyan-500 bg-cyan-500/10': selectedId === cliente.id }"
            >
                <div class="flex items-center gap-4 flex-1">
                    <div class="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-600 to-blue-700 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-cyan-900/20">
                        {{ cliente.razon_social.substring(0,1).toUpperCase() }}
                    </div>
                    <div class="min-w-0 flex-1">
                        <h3 class="font-bold text-cyan-100 truncate">{{ cliente.razon_social }}</h3>
                        <p class="text-xs text-cyan-200/50 font-mono">{{ cliente.cuit }}</p>
                    </div>
                </div>

                <div class="w-1/4 hidden md:block">
                     <span class="text-xs text-cyan-200/50">{{ getSegmentoName(cliente.segmento_id) }}</span>
                </div>
                
                <!-- Logistics Indicator (List) -->
                <div class="px-2 w-8 flex justify-center">
                     <div
                        v-if="cliente.requiere_entrega"
                        class="h-2 w-2 rounded-full shadow-[0_0_8px] bg-orange-500 shadow-orange-500"
                        title="Requiere Entrega (Logística)"
                    ></div>
                </div>
                
                <div class="w-24 flex justify-center">
                    <!-- List Toggle Switch -->
                    <div class="flex items-center gap-2 bg-black/20 px-2 py-1 rounded-full border border-cyan-900/10">
                        <button 
                            @click.stop="toggleClienteStatus(cliente)"
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0"
                            :class="cliente.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                            title="Click para cambiar estado"
                        >
                            <span 
                                class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                :class="cliente.activo ? 'translate-x-3.5' : 'translate-x-1'"
                            />
                        </button>
                    </div>
                </div>
                 <div class="w-10 flex justify-end">
                    <i class="fas fa-chevron-right text-cyan-900/30 group-hover:text-cyan-500/50 transition-colors"></i>
                </div>
            </div>
        </div>

      </div>
    </main>

    <!-- Right Inspector Panel (Fixed) -->
    <aside 
        class="w-96 border-l border-cyan-900/30 bg-[#05151f]/95 flex flex-col z-30 shadow-2xl overflow-hidden shrink-0"
    >
        <ClienteInspector 
            :modelValue="selectedCliente" 
            :isNew="selectedId === 'new'"
            @close="closeInspector"
            @save="handleInspectorSave"
            @delete="handleInspectorDelete"
            @manage-segmentos="handleManageSegmentos"
            @switch-client="handleSwitchClient"
        />
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
        class="fixed inset-0 z-[60] bg-[#0a1f2e] m-4 rounded-lg shadow-2xl overflow-hidden border border-cyan-500/30"
        @close="showSegmentoList = false"
    />
    
    <!-- Transportes Modal (Triggered by Sidebar/CommandPalette) -->
    <div v-if="showTransporteManager" class="fixed inset-0 z-[70] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-[#0f172a] w-full max-w-6xl h-[85vh] rounded-2xl shadow-2xl overflow-hidden border border-white/10 flex flex-col">
            <TransporteManager :isModal="true" @close="showTransporteManager = false" />
        </div>
    </div>

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
import { useRoute } from 'vue-router' // Import useRoute
const route = useRoute()

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

// Context Menu Logic
// Note: ContextMenu in template was removed as it's cleaner to handle via specialized components or global teleport if needed.
// But we kept the handler logic "handleClientContextMenu" - we probably need to keep the component if we want Right Click to work.
// Re-adding ContextMenu logic properly.

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

const getSegmentoName = (id) => {
    const seg = segmentos.value.find(s => s.id === id)
    return seg ? seg.nombre : ''
}

const selectCliente = async (cliente) => {
    // Single Click Selection
    console.log("Selecting:", cliente.razon_social)
    selectedId.value = cliente.id
    
    try {
        const fullCliente = await clienteStore.fetchClienteById(cliente.id)
        selectedCliente.value = { ...fullCliente }
    } catch (e) {
        console.error("Error fetching full client details", e)
        selectedCliente.value = { ...cliente }
    }
}

const openNewCliente = () => {
    selectedId.value = 'new'
    selectedCliente.value = {
        razon_social: '',
        cuit: '',
        activo: true,
        condicion_iva_id: null,
        segmento_id: null,
        domicilios: [],
        vinculos: []
    }
}

const closeInspector = () => {
    selectedId.value = null
    selectedCliente.value = null
    
    // Auto Return to Tactical if context exists
    if (route.query.returnUrl) {
        console.log("Returning to source:", route.query.returnUrl)
        router.push({ 
            path: route.query.returnUrl,
            query: { q: route.query.q } // Restore search context
        })
    }
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
        notificationStore.add('Error al guardar cliente', 'error')
    }
}

const handleInspectorDelete = async (clienteData) => {
    try {
        await clienteStore.updateCliente(clienteData.id, { ...clienteData, activo: false })
        notificationStore.add('Cliente dado de baja', 'success')
        closeInspector()
    } catch (error) {
        notificationStore.add('Error al dar de baja', 'error')
    }
}

const toggleClienteStatus = async (cliente) => {
    const newStatus = !cliente.activo
    if (cliente.activo && !newStatus) {
        if (!confirm(`¿Está seguro de desactivar al cliente ${cliente.razon_social}?`)) return
    }
    try {
        await clienteStore.updateCliente(cliente.id, { ...cliente, activo: newStatus })
        notificationStore.add(newStatus ? 'Cliente reactivado' : 'Cliente desactivado', 'success')
    } catch (error) {
        notificationStore.add('Error al cambiar estado', 'error')
    }
}

const normalizeText = (text) => {
    return text ? text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase() : ''
}

const filteredClientes = computed(() => {
    let result = clientes.value.filter(cliente => {
        if (filterStatus.value === 'active' && !cliente.activo) return false
        if (filterStatus.value === 'inactive' && cliente.activo) return false
        if (selectedSegmento.value && cliente.segmento_id !== selectedSegmento.value) return false
        if (searchQuery.value) {
            const query = normalizeText(searchQuery.value)
            return normalizeText(cliente.razon_social).includes(query) || cliente.cuit.includes(query)
        }
        return true
    })

    return result.sort((a, b) => {
        switch (sortBy.value) {
            case 'alpha_asc': return a.razon_social.localeCompare(b.razon_social)
            case 'alpha_desc': return b.razon_social.localeCompare(a.razon_social)
            case 'id_desc': return String(b.id).localeCompare(String(a.id))
            case 'usage': return (b.contador_uso || 0) - (a.contador_uso || 0)
            default: return 0
        }
    })
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
    // TODO: Implement Context Menu if really needed, or remove. 
    // Re-added for feature parity.
}

const handleKeydown = (e) => {
    if (e.key === 'F10' && selectedCliente.value) {
        e.preventDefault()
    }
    if (e.key === 'Escape') {
        if(selectedCliente.value) closeInspector()
    }
}

const logout = () => {
    if(confirm('¿Desea cerrar sesión?')) {
        localStorage.removeItem('token')
        router.push('/login')
    }
}

onMounted(async () => {
    window.addEventListener('keydown', handleKeydown)
    try {
        await Promise.all([
            clienteStore.fetchClientes(),
            maestrosStore.fetchSegmentos()
        ])
        segmentos.value = maestrosStore.segmentos
        
        // Check for Auto-Inspect
        if (route.query.inspectId) {
            console.log("Auto-inspecting:", route.query.inspectId)
            // Buscar el cliente en la lista cargada para tener info básica
            const client = clientes.value.find(c => c.id === route.query.inspectId)
            if (client) {
                await selectCliente(client)
            } else {
                // Si no está en la lista (inactivo?), intentar fetch directo
                await handleSwitchClient(route.query.inspectId)
            }
        }
    } catch (e) {
        console.error('Error loading HaweView data:', e)
    }
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

</script>

<style>
body {
    background-color: #0a0a0a;
}
</style>
