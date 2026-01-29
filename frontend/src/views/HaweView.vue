<template>
  <div class="flex h-screen w-full bg-[#081c26] text-gray-200 overflow-hidden font-sans">
    
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative min-w-0">
      <!-- Global Header Injection -->
      <Teleport to="#global-header-center" v-if="isMounted">
        <div class="flex items-center gap-6 animate-in fade-in duration-300">
            <h1 class="font-outfit text-xl font-bold text-white flex items-center gap-3 whitespace-nowrap">
                <i class="fas fa-users text-cyan-500"></i>
                <span class="hidden xl:inline">Explorador de </span>Clientes
            </h1>
            
            <!-- Search -->
            <div class="relative w-96 group">
                <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-cyan-500/30 group-focus-within:text-cyan-400 transition-colors"></i>
                <input 
                  v-model="searchQuery"
                  type="text" 
                  placeholder="Buscar Cliente, CUIT, Fantasía..." 
                  class="w-full h-10 rounded-xl border border-white/5 bg-black/20 py-2 pl-10 pr-4 text-sm text-white placeholder-cyan-500/30 focus:border-cyan-500/50 focus:bg-black/40 focus:outline-none transition-all shadow-inner"
                />
            </div>
        </div>
      </Teleport>

      <!-- Local Toolbar (User Order 1-9) -->
      <div class="relative z-[70] flex items-center gap-4 px-6 py-3 border-b border-cyan-900/20 bg-[#0a253a]/30 shrink-0 overflow-x-auto">
          
          <!-- 1. Checkbox Todos -->
          <div class="flex items-center gap-2 cursor-pointer group shrink-0" @click="toggleSelectAll" title="Seleccionar Todos">
              <input 
                  type="checkbox" 
                  :checked="isAllSelected"
                  class="rounded bg-[#020a0f] border-cyan-500/50 text-cyan-500 focus:ring-0 focus:ring-offset-0 cursor-pointer h-5 w-5 shadow-sm"
              />
              <span class="text-sm font-bold text-white/50 group-hover:text-white select-none">Todos</span>
          </div>

          <!-- 2. XX Seleccionados -->
          <div v-if="selectedIds.length > 0" class="shrink-0 animate-in fade-in slide-in-from-left-2 px-2">
               <span class="text-xs font-bold text-cyan-400 bg-cyan-900/30 px-3 py-1.5 rounded-full border border-cyan-500/30 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                  {{ selectedIds.length }}
                  <span class="opacity-60 text-[10px] uppercase ml-1">SELECCIONADOS</span>
              </span>
          </div>

          <!-- Divider -->
          <div class="h-6 w-px bg-white/5 shrink-0"></div>

          <!-- 3. Segmento Filter -->
          <select 
            v-model="selectedSegmento"
            class="h-9 rounded-lg border border-white/10 bg-[#0f172a] text-cyan-100/80 px-3 text-xs font-bold focus:border-cyan-500 focus:outline-none min-w-[160px]"
          >
            <option :value="null">Todos los Segmentos</option>
            <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
          </select>

          <!-- 4. Status Filter (Group) -->
          <div class="flex bg-black/20 rounded-lg p-1 border border-white/10 shrink-0">
              <button @click="filterStatus = 'all'" class="px-3 py-1 text-[10px] font-bold rounded uppercase transition-all" :class="filterStatus === 'all' ? 'bg-indigo-600 text-white shadow' : 'text-white/30 hover:text-white'">Todos</button>
              <button @click="filterStatus = 'active'" class="px-3 py-1 text-[10px] font-bold rounded uppercase transition-all" :class="filterStatus === 'active' ? 'bg-green-600 text-white shadow' : 'text-white/30 hover:text-white'">Activos</button>
              <button @click="filterStatus = 'inactive'" class="px-3 py-1 text-[10px] font-bold rounded uppercase transition-all" :class="filterStatus === 'inactive' ? 'bg-red-600 text-white shadow' : 'text-white/30 hover:text-white'">Inactivos</button>
          </div>

          <!-- 5. Sort Button -->
           <button 
                @click="showSortMenu = !showSortMenu" 
                class="flex items-center gap-2 h-9 rounded-lg border border-white/10 bg-black/20 px-3 text-xs font-bold text-cyan-100 hover:bg-white/5 transition-colors shrink-0 relative"
            >
                <i class="fas fa-sort-amount-down text-cyan-500"></i>
                <span class="max-w-[80px] truncate hidden xl:inline">
                    {{ sortBy === 'usage' ? 'Populares' : (sortBy === 'alpha_asc' ? 'A-Z' : 'Orden') }}
                </span>
                
                <!-- Dropdown -->
                <div v-if="showSortMenu" class="absolute top-full left-0 mt-2 w-48 bg-[#0a253a] border border-cyan-500/30 rounded-lg shadow-xl z-[100] overflow-hidden text-left">
                    <div class="fixed inset-0 z-40" @click.stop="showSortMenu = false"></div>
                    <div class="relative z-50 py-1">
                        <button @click="sortBy = 'usage'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-cyan-100 hover:bg-cyan-500/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'usage' }">Más Usados</button>
                        <button @click="sortBy = 'alpha_asc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-cyan-100 hover:bg-cyan-500/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_asc' }">A-Z Alfabético</button>
                        <button @click="sortBy = 'id_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-cyan-100 hover:bg-cyan-500/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'id_desc' }">Más Recientes</button>
                    </div>
                </div>
            </button>

          <!-- 6. View Toggle -->
          <div class="flex bg-white/5 rounded-lg p-1 border border-white/10 shrink-0">
            <button @click="viewMode = 'grid'" class="p-1 rounded transition-all" :class="viewMode === 'grid' ? 'bg-cyan-500/20 text-cyan-400' : 'text-white/30 hover:text-white'"><i class="fas fa-border-all text-xs"></i></button>
            <button @click="viewMode = 'list'" class="p-1 rounded transition-all" :class="viewMode === 'list' ? 'bg-cyan-500/20 text-cyan-400' : 'text-white/30 hover:text-white'"><i class="fas fa-list text-xs"></i></button>
          </div>

          <div class="flex-1"></div>

          <!-- 7. Baja (Bulk) -->
          <button 
            v-if="selectedIds.length > 0"
            @click="handleBulkAction"
            class="flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-bold text-white shadow-lg transition-transform active:scale-95 shrink-0"
            :class="filterStatus === 'inactive' ? 'bg-gradient-to-r from-red-600 to-red-500 shadow-red-500/20' : 'bg-gradient-to-r from-indigo-600 to-violet-600 shadow-indigo-500/20'"
          >
            <i :class="filterStatus === 'inactive' ? 'fas fa-trash-alt' : 'fas fa-archive'"></i>
            <span>{{ filterStatus === 'inactive' ? `Eliminar` : `Baja` }}</span>
          </button>

          <!-- 8. Modificar -->
          <button 
            v-if="selectedIds.length === 1"
            @click="handleModifySelected"
            class="flex items-center gap-2 rounded-lg bg-[#0f2430] border border-cyan-500/30 px-5 py-2 text-xs font-bold text-cyan-100 shadow-lg hover:bg-cyan-900/40 hover:text-white hover:border-cyan-400/50 transition-all shrink-0"
          >
            <i class="fas fa-pencil-alt"></i>
            <span>Modificar</span>
          </button>

           <!-- 9. Nuevo -->
          <button 
            @click="openNewCliente"
            class="flex items-center gap-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 px-6 py-2 text-xs font-black text-black uppercase tracking-wider shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:shadow-[0_0_30px_rgba(6,182,212,0.6)] transition-all active:scale-95 shrink-0"
          >
            <i class="fas fa-plus"></i>
            <span>Nuevo</span>
          </button>

      </div>

      <!-- Content List -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-cyan-900/10 scrollbar-thumb-cyan-900/30">
        

        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
          <div v-for="cliente in filteredClientes" :key="cliente.id" class="relative w-full min-h-[140px] group">
            <!-- Selection Checkbox -->
            <div class="absolute top-0 right-0 z-[60] p-3 cursor-pointer" @click.stop="toggleSelection(cliente.id)">
                <input 
                    type="checkbox" 
                    :checked="selectedIds.includes(cliente.id)" 
                    class="rounded bg-[#020a0f] border-cyan-500/50 text-cyan-500 focus:ring-0 focus:ring-offset-0 cursor-pointer h-5 w-5 shadow-lg shadow-black/50 transition-opacity"
                    :class="{ 'opacity-100': selectedIds.includes(cliente.id), 'opacity-50 group-hover:opacity-100': !selectedIds.includes(cliente.id) }"
                    @click.stop
                    @change="toggleSelection(cliente.id)"
                />
            </div>
            <FichaCard
                class="w-full"
                :title="cliente.razon_social || 'Sin Nombre'"
                :subtitle="cliente.cuit || '---'"
                :selected="selectedIds.includes(cliente.id)"
                :hasLogisticsAlert="cliente.requiere_entrega"
                :hasTransport="cliente.domicilios?.some(d => d.transporte_id)"
                :extraData="{
                    segmento: getSegmentoName(cliente.segmento_id),
                    domicilio: cliente.domicilio_fiscal_resumen,
                    contacto: cliente.contacto_principal_nombre
                }"
                @dblclick="selectCliente(cliente)"
                @contextmenu.prevent="handleClientContextMenu($event, cliente)"
            >
                <template #icon>
                    <i class="fas fa-user"></i>
                </template>
                <template #actions>
                    <div class="flex items-center gap-1 bg-black/40 rounded-full p-1 backdrop-blur-sm border border-white/5">
                        <!-- Edit Button -->
                        <button 
                            @click.stop="selectCliente(cliente)"
                            class="h-6 w-6 rounded-full flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/20 transition-colors"
                            title="Modificar"
                        >
                            <i class="fas fa-pencil-alt text-xs"></i>
                        </button>

                        <div class="w-px h-3 bg-white/20"></div>

                        <!-- Toggle Switch -->
                        <button 
                            @click.stop="toggleClienteStatus(cliente)"
                            v-if="cliente.activo"
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 bg-green-500/50 hover:bg-green-500/70"
                            title="Desactivar"
                        >
                            <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm translate-x-3.5" />
                        </button>
                        <button 
                            @click.stop="toggleClienteStatus(cliente)"
                            v-else
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 bg-red-500/50 hover:bg-red-500/70"
                            title="Activar"
                        >
                            <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm translate-x-1" />
                        </button>
                    </div>
                </template>
            </FichaCard>
          </div>
        </div>

        <!-- List View -->
        <div v-else-if="filteredClientes.length > 0" class="flex flex-col gap-2">
            <div 
                v-for="cliente in filteredClientes" 
                :key="cliente.id"
                class="group relative flex items-center justify-between gap-4 rounded-lg border border-cyan-900/10 bg-[#0a1f2e]/60 p-3 transition-all hover:bg-[#0f2d42] hover:border-cyan-500/30"
                :class="{ 'ring-1 ring-cyan-500 bg-[#0f2d42]': selectedIds.includes(cliente.id) }"
                @dblclick="selectCliente(cliente)"
            >
                <!-- Checkbox -->
                <div class="flex items-center pl-2 p-2 cursor-pointer z-20" @click.stop="toggleSelection(cliente.id)">
                     <input 
                        type="checkbox" 
                        :checked="selectedIds.includes(cliente.id)" 
                        @click.stop
                        @change="toggleSelection(cliente.id)"
                        class="rounded bg-[#020a0f] border-cyan-500/50 text-cyan-500 focus:ring-0 focus:ring-offset-0 cursor-pointer h-4 w-4"
                    />
                </div>

                <!-- Main Info -->
                <div class="flex-1 min-w-0 grid grid-cols-12 gap-4 items-center">
                    <!-- Name & ID -->
                    <div class="col-span-4 truncate">
                        <div class="flex items-center gap-2">
                            <span class="font-outfit font-bold text-white group-hover:text-cyan-400 transition-colors truncate">
                                {{ cliente.razon_social }}
                            </span>
                             <span v-if="cliente.requiere_entrega" class="text-amber-500 text-xs" title="Logística Pendiente">
                                <i class="fas fa-truck-loading"></i>
                            </span>
                        </div>
                        <div class="text-xs text-cyan-500/50 font-mono">{{ cliente.cuit }}</div>
                    </div>

                    <!-- Meta Data -->
                    <div class="col-span-3 truncate text-xs text-cyan-200/60 hidden sm:block">
                        <div class="flex items-center gap-1">
                            <i class="fas fa-layer-group text-cyan-500/40"></i>
                            <span>{{ getSegmentoName(cliente.segmento_id) }}</span>
                        </div>
                    </div>

                     <div class="col-span-3 truncate text-xs text-cyan-200/60 hidden md:block">
                        <div class="flex items-center gap-1" v-if="cliente.domicilio_fiscal_resumen">
                            <i class="fas fa-map-marker-alt text-cyan-500/40"></i>
                            <span class="truncate">{{ cliente.domicilio_fiscal_resumen }}</span>
                        </div>
                    </div>

                    <!-- Status -->
                    <div class="col-span-2 flex justify-end">
                        <div 
                            class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border"
                            :class="cliente.activo ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'"
                        >
                            {{ cliente.activo ? 'Activo' : 'Inactivo' }}
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="flex items-center gap-2 pr-2 opacity-50 group-hover:opacity-100 transition-opacity">
                     <button 
                        @click.stop="toggleClienteStatus(cliente)"
                        class="h-8 w-8 rounded-full flex items-center justify-center transition-colors hover:bg-cyan-500/20 active:scale-95"
                        :class="cliente.activo ? 'text-red-400' : 'text-green-400'"
                        :title="cliente.activo ? 'Desactivar' : 'Reactivar'"
                    >
                        <i :class="cliente.activo ? 'fas fa-toggle-on text-lg' : 'fas fa-toggle-off text-lg'"></i>
                    </button>
                    <button 
                         @click.stop="handleClientContextMenu($event, cliente)"
                         class="h-8 w-8 rounded-full flex items-center justify-center text-cyan-500/50 hover:text-cyan-400 hover:bg-cyan-500/20 transition-colors"
                    >
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                </div>
            </div>        </div>

        <!-- Empty State & Cantera Fallback -->
        <div v-if="filteredClientes.length === 0 && !selectedSegmento" class="flex flex-col items-center justify-center py-20 bg-black/20 rounded-2xl border border-white/5 mx-auto max-w-2xl px-8 text-center">
            <div class="h-20 w-20 bg-cyan-900/20 rounded-full flex items-center justify-center text-3xl text-cyan-500/50 mb-6">
                <i class="fas fa-search"></i>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">No se encontraron clientes locales</h3>
            <p class="text-cyan-200/50 mb-8">No hay registros en la base operativa que coincidan con "{{ searchQuery }}".</p>
            
            <div v-if="searchQuery" class="w-full space-y-4">
                <button 
                    @click="handleCanteraSearch"
                    :disabled="canteraLoading"
                    class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-3 active:scale-95"
                >
                    <i class="fas" :class="canteraLoading ? 'fa-spinner fa-spin' : 'fa-database'"></i>
                    {{ canteraLoading ? 'Buscando en Maestros...' : 'Buscar en Maestros de Seguridad (Cantera)' }}
                </button>
                
                <!-- Cantera Results in View -->
                <div v-if="canteraResults.length > 0" class="mt-8 grid grid-cols-1 gap-4 w-full text-left">
                    <p class="text-[10px] uppercase font-bold text-emerald-500 tracking-widest pl-2">Resultados en Cantera</p>
                    <div 
                        v-for="item in canteraResults" 
                        :key="item.id"
                        @click="importFromCantera(item)"
                        class="p-4 bg-white/5 border border-white/10 rounded-xl hover:border-emerald-500/50 hover:bg-white/10 transition-all cursor-pointer flex justify-between items-center group"
                    >
                        <div>
                            <p class="font-bold text-white group-hover:text-emerald-400 transition-colors">{{ item.razon_social }}</p>
                            <p class="text-xs text-white/40 font-mono">{{ item.cuit }}</p>
                        </div>
                        <i class="fas fa-plus-circle text-emerald-500 opacity-0 group-hover:opacity-100 transition-all transform group-hover:scale-110"></i>
                    </div>
                </div>
            </div>
        </div>
        
        <div v-if="filteredClientes.length === 0 && selectedSegmento" class="flex flex-col items-center justify-center py-20 text-center">
             <div class="h-16 w-16 bg-white/5 rounded-full flex items-center justify-center text-2xl text-white/20 mb-4">
                <i class="fas fa-filter"></i>
            </div>
            <h3 class="text-lg font-bold text-white/50">Segmento Vacío</h3>
        </div>

      </div>
       <!-- Context Menu -->
       <ContextMenu 
            v-if="contextMenuState.show" 
            v-model="contextMenuState.show"
            :x="contextMenuState.x"
            :y="contextMenuState.y"
            :actions="contextMenuProps.actions"
            @close="contextMenuState.show = false"
       />
    </main>

    <!-- Right Inspector Panel (Browsing/Editing) -->
    <!-- Right Inspector Panel (DEPRECATED: Now using Central Canvas) -->
    <!-- <aside ... > -->

    <!-- Central Modal (New Client / Alta) -->
    <div v-if="selectedId === 'new'" class="fixed inset-0 z-[60] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" @click.self="closeInspector">
        <div class="bg-[#05151f] w-full max-w-2xl h-[90vh] rounded-2xl shadow-2xl overflow-hidden border border-cyan-500/30 flex flex-col relative">
            <ClienteInspector 
                :modelValue="selectedCliente" 
                :isNew="true"
                @close="closeInspector"
                @save="handleInspectorSave"
                class="flex-1"
            />
        </div>
    </div>

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
import { ref, onMounted, onActivated, computed, onUnmounted, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
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
import canteraService from '../services/canteraService'

const clienteStore = useClientesStore()
const maestrosStore = useMaestrosStore()
const notificationStore = useNotificationStore()
const router = useRouter()
const route = useRoute()

const clientes = computed(() => clienteStore.clientes)
const segmentos = ref([])
const selectedId = ref(null)
const selectedCliente = ref(null)
const selectedSegmento = ref(null)
const searchQuery = ref('')
const filterStatus = ref(localStorage.getItem('hawe_filter_pref') || 'active') // Persisted
const sortBy = ref(localStorage.getItem('hawe_sort_pref') || 'usage')
const viewMode = ref('grid')
const selectedIds = ref([]) // IDs for bulk actions
const showSortMenu = ref(false)
const showCommandPalette = ref(false)
const showTransporteManager = ref(false)

// Cantera Integration
const canteraResults = ref([])
const canteraLoading = ref(false)

const handleCanteraSearch = async () => {
    if (!searchQuery.value) return
    canteraLoading.value = true
    try {
        const res = await canteraService.searchClientes(searchQuery.value)
        canteraResults.value = res.data
        if (canteraResults.value.length === 0) {
            notificationStore.add('No se encontraron registros ni siquiera en maestros.', 'info')
        }
    } catch (e) {
        console.error("Error searching in cantera", e)
        notificationStore.add('Error al conectar con la Cantera de maestros.', 'error')
    } finally {
        canteraLoading.value = false
    }
}

const importFromCantera = async (item) => {
    try {
        notificationStore.add('Importando cliente...', 'info')
        await canteraService.importCliente(item.id)
        notificationStore.add('Cliente importado con éxito', 'success')
        
        // Refresh local list
        await clienteStore.fetchClientes()
        
        // Auto-select the imported client
        const imported = clienteStore.clientes.find(c => c.id === item.id)
        if (imported) {
            selectCliente(imported)
        }
    } catch (e) {
        console.error("Error importing", e)
        notificationStore.add('Error al importar cliente.', 'error')
    }
}

watch(sortBy, (newVal) => {
    localStorage.setItem('hawe_sort_pref', newVal)
})

watch(filterStatus, (newVal) => {
    localStorage.setItem('hawe_filter_pref', newVal)
    selectedIds.value = [] // Clear selection on tab switch
})

const isAllSelected = computed(() => {
    if (filteredClientes.value.length === 0) return false
    return filteredClientes.value.every(c => selectedIds.value.includes(c.id))
})

const toggleSelection = (id) => {
    if (selectedIds.value.includes(id)) {
        selectedIds.value = selectedIds.value.filter(existingId => existingId !== id)
    } else {
        selectedIds.value = [...selectedIds.value, id]
    }
}

const toggleSelectAll = () => {
    if (isAllSelected.value) {
        selectedIds.value = []
    } else {
        selectedIds.value = filteredClientes.value.map(c => c.id)
    }
}

const handleBulkAction = async () => {
    if (filterStatus.value === 'inactive') {
        await handleBulkHardDelete()
    } else {
        await handleBulkSoftDelete()
    }
}

const handleBulkSoftDelete = async () => {
    if (!confirm(`¿Está seguro que desea DESACTIVAR ${selectedIds.value.length} clientes?`)) return
    
    let successCount = 0
    for (const id of selectedIds.value) {
        try {
            const client = clientes.value.find(c => c.id === id)
            if (client && client.activo) {
                 await clienteStore.updateCliente(id, { ...client, activo: false })
                 successCount++
            }
        } catch (e) {
            console.error(`Error deactivating ${id}`, e)
        }
    }
    notificationStore.add(`${successCount} clientes desactivados`, 'success')
    selectedIds.value = []
}

const handleBulkHardDelete = async () => {
    if (!confirm(`PELIGRO: ¿Está seguro que desea eliminar DEFINITIVAMENTE ${selectedIds.value.length} clientes? Esta acción NO se puede deshacer y borrará permanentemente los datos si no tienen pedidos.`)) return
    
    let successCount = 0
    let failCount = 0
    
    for (const id of selectedIds.value) {
        try {
            await clienteStore.hardDeleteCliente(id)
            successCount++
        } catch (e) {
            console.error(`Error deleting ${id}`, e)
            failCount++
        }
    }
    
    if (successCount > 0) notificationStore.add(`${successCount} clientes eliminados definitivamente`, 'success')
    if (failCount > 0) notificationStore.add(`${failCount} clientes no se pudieron eliminar (posiblemente tienen pedidos)`, 'error')
    
    selectedIds.value = [] // Clear
    
    // Refresh
    clienteStore.fetchClientes()
}

// Segmento ABM Logic
const showSegmentoModal = ref(false)
const showSegmentoList = ref(false)

// Context Menu State
const contextMenuState = ref({ show: false, x: 0, y: 0 })
const contextMenuProps = ref({ actions: [] })


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
    // Navigate to Central Canvas
    console.log("Navigating to Canvas:", cliente.razon_social)
    router.push({ name: 'HaweClientCanvas', params: { id: cliente.id } })
}

const openNewCliente = () => {
    router.push({ name: 'HaweClientCanvas', params: { id: 'new' } })
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

const isMounted = ref(false)

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
        notificationStore.add('Cliente dado de baja (Inactivo)', 'success')
        closeInspector()
    } catch (error) {
        notificationStore.add('Error al dar de baja', 'error')
    }
}

const handleHardDelete = async (clienteData) => {
    try {
        await clienteStore.hardDeleteCliente(clienteData.id)
        notificationStore.add('CLIENTE ELIMINADO DEFINITIVAMENTE', 'success')
        
        closeInspector()
    } catch (error) {
        console.error(error)
        const detail = error.response?.data?.detail || 'Error en baja física'
        notificationStore.add(detail, 'error')
    }
}

const toggleClienteStatus = async (cliente) => {
    const newStatus = !cliente.activo
    
    // [GY-UX] Deactivation Warning
    if (cliente.activo && !newStatus) {
        if (!confirm(`¿Está seguro de desactivar al cliente ${cliente.razon_social}?`)) return
    }
    
    // [GY-UX] Reactivation Validation (V14)
    if (!cliente.activo && newStatus) {
        // Check Mandatory Fields (Simple check based on available data in list)
        // Note: 'cliente' from list might be partial? Ideally we trust list data.
        // Required: Segmento, ListaPrecios, CondicionIVA
        const missingFields = []
        if (!cliente.segmento_id) missingFields.push("Segmento")
        if (!cliente.lista_precios_id) missingFields.push("Lista de Precios")
        if (!cliente.condicion_iva_id) missingFields.push("Condición IVA")
        
        if (missingFields.length > 0) {
            if (confirm(`No se puede activar el cliente porque faltan datos obligatorios:\n- ${missingFields.join('\n- ')}\n\n¿Desea abrir la ficha para completar los datos ahora?`)) {
                selectCliente(cliente)
            }
            return // Block activation
        }
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
    contextMenuState.value = {
        show: true,
        x: e.clientX,
        y: e.clientY
    }
    contextMenuProps.value.actions = [
        { 
            label: 'Editar Ficha (Doble Clic)', 
            iconClass: 'fas fa-edit', 
            handler: () => selectCliente(client)
        },
        { 
            label: 'Clonar Cliente', 
            iconClass: 'fas fa-copy', 
            handler: () => handleCloneCliente(client)
        },
        { 
            label: client.activo ? 'Dar de Baja (Desactivar)' : 'Reactivar Cliente', 
            iconClass: client.activo ? 'fas fa-ban' : 'fas fa-check-circle',
            handler: () => toggleClienteStatus(client)
        }
    ]
}

const handleCloneCliente = async (client) => {
    try {
        const fullCliente = await clienteStore.fetchClienteById(client.id)
        
        const clone = { 
            ...fullCliente, 
            id: null, 
            razon_social: `${fullCliente.razon_social} (COPIA)`,
            cuit: '', 
            domicilios: fullCliente.domicilios ? fullCliente.domicilios.map(d => ({ ...d, id: null, cliente_id: null })) : [],
            vinculos: fullCliente.vinculos ? fullCliente.vinculos.map(v => ({ ...v, id: null, cliente_id: null })) : [],
            activo: true,
            contador_uso: 0,
            fecha_ultima_compra: null
        }
        
        // Use Store Draft to pass data to ClientCanvas
        clienteStore.setDraft(clone);
        
        // Navigate to 'new' which will trigger ClientCanvas to check draft
        router.push({ name: 'HaweClientCanvas', params: { id: 'new' } })
        
    } catch (e) {
        console.error("Clone failed", e)
        notificationStore.add("Error al preparar clonado", "error")
    }
}

const handleModifySelected = () => {
    if (selectedIds.value.length === 1) {
        const client = clientes.value.find(c => c.id === selectedIds.value[0])
        if (client) {
            selectCliente(client)
        }
    }
}

const handleKeydown = (e) => {
    if (e.key === 'F10' && selectedCliente.value) {
        e.preventDefault()
    }
    if (e.key === 'Escape') {
        if(selectedCliente.value) closeInspector()
    }
    if (e.key === 'F4') {
        e.preventDefault()
        openNewCliente()
    }
}

const logout = () => {
    if(confirm('¿Desea cerrar sesión?')) {
        localStorage.removeItem('token')
        router.push('/login')
    }
}
// [GY-FIX] Robust hydration logic
const hydrateData = async () => {
    try {
        if (clienteStore.clientes.length === 0) {
            await clienteStore.fetchClientes()
        }
        
        if (maestrosStore.segmentos.length === 0) {
            await maestrosStore.fetchSegmentos()
        }
        segmentos.value = maestrosStore.segmentos
    } catch (e) {
        console.error("Hydration failed:", e)
    }
}

onMounted(async () => {
    isMounted.value = true
    window.addEventListener('keydown', handleKeydown)
    
    await hydrateData()

    // Check for Auto-Inspect (existing logic)
    if (route.query.inspectId) {
        console.log("Auto-inspecting:", route.query.inspectId)
        const client = clientes.value.find(c => c.id === route.query.inspectId)
        if (client) {
            await selectCliente(client)
        } else {
            await handleSwitchClient(route.query.inspectId)
        }
    }
})

// [GY-FIX] Handle Keep-Alive re-entry
onActivated(async () => {
    if (clienteStore.clientes.length === 0) {
        await hydrateData()
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
