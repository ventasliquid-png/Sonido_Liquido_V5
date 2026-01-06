<template>
  <div class="flex h-screen w-full bg-[#021812] text-gray-200 overflow-hidden font-sans">
    
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-row relative min-w-0">
      
      <!-- List Section -->
      <div class="flex-1 flex flex-col min-w-0 border-r border-emerald-900/10">
        <!-- Top Bar -->
        <header class="relative z-20 flex h-16 items-center justify-between border-b border-emerald-900/20 bg-[#052e1e]/50 px-6 backdrop-blur-sm shrink-0">
          <!-- Title -->
          <div>
              <h1 class="font-outfit text-xl font-semibold text-white">
                  Gestión de Pedidos
              </h1>
              <p class="text-xs text-emerald-400/50 font-medium uppercase tracking-wider">Tablero Táctico</p>
          </div>

          <!-- Search & Tools -->
          <div class="flex items-center gap-4">
            <div class="relative">
              <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-emerald-500/50"></i>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar cliente o ID..."
                class="h-9 w-64 rounded-full border border-emerald-900/30 bg-[#020f0a] pl-10 pr-4 text-sm text-emerald-100 placeholder-emerald-900/50 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
            </div>
            <div class="h-6 w-px bg-emerald-900/20"></div>
            
            <!-- General Filters -->
            <div class="flex bg-emerald-900/10 rounded-lg p-1 border border-emerald-900/20">
              <button 
                  v-for="f in filters"
                  :key="f.key"
                  @click="setFilter(f.key)"
                  class="px-3 py-1 text-xs font-bold rounded-md transition-all whitespace-nowrap"
                  :class="activeFilter === f.key ? f.activeClass : 'text-emerald-100/40 hover:text-emerald-100 hover:bg-emerald-500/10'"
              >
                  {{ f.label }}
              </button>
            </div>

            <div class="h-6 w-px bg-emerald-900/20"></div>

            <button 
              @click="refresh"
              class="p-2 text-emerald-500 hover:text-emerald-300 transition-colors"
              title="Recargar"
            >
              <i class="fas fa-sync-alt" :class="{ 'animate-spin': store.isLoading }"></i>
            </button>

              <!-- New Order Button -->
              <button 
                  @click="router.push('/hawe/tactico')"
                  class="ml-2 flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-1.5 text-sm font-bold text-white shadow-lg shadow-emerald-500/20 transition-all hover:bg-emerald-500 hover:shadow-emerald-500/40"
                  title="Nuevo Pedido (F4)"
              >
                  <i class="fas fa-plus"></i>
                  <span class="hidden sm:inline">Nuevo</span>
              </button>
          </div>
        </header>

        <!-- Content List -->
        <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-emerald-900/10 scrollbar-thumb-emerald-900/30">
          
          <!-- List View -->
          <div class="flex flex-col gap-2">
              <!-- Header Row -->
               <div class="flex items-center justify-between px-4 py-2 text-xs font-bold text-emerald-900/50 uppercase tracking-wider select-none">
                  <div @click="toggleSort('id')" class="w-20 cursor-pointer hover:text-emerald-500 flex items-center gap-1">
                      ID
                      <i v-if="sortKey === 'id'" :class="sortOrder === 'asc' ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                  </div>
                  <div @click="toggleSort('fecha')" class="w-32 cursor-pointer hover:text-emerald-500 flex items-center gap-1">
                      Fecha
                      <i v-if="sortKey === 'fecha'" :class="sortOrder === 'asc' ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                  </div>
                  <div @click="toggleSort('cliente')" class="flex-1 cursor-pointer hover:text-emerald-500 flex items-center gap-1">
                      Cliente
                      <i v-if="sortKey === 'cliente'" :class="sortOrder === 'asc' ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                  </div>
                  <div @click="toggleSort('total')" class="w-32 text-right cursor-pointer hover:text-emerald-500 flex items-center justify-end gap-1">
                      Total
                      <i v-if="sortKey === 'total'" :class="sortOrder === 'asc' ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                  </div>
                  <div @click="toggleSort('estado')" class="w-32 text-center cursor-pointer hover:text-emerald-500 flex items-center justify-center gap-1">
                      Estado
                      <i v-if="sortKey === 'estado'" :class="sortOrder === 'asc' ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                  </div>
                  <div class="w-10"></div>
              </div>

              <div 
                  v-for="pedido in sortedAndFilteredPedidos" 
                  :key="pedido.id"
                  class="group flex items-center justify-between p-3 rounded-lg border transition-all"
                  :class="[
                    selectedPedido?.id === pedido.id 
                    ? 'border-emerald-500 bg-emerald-500/10 ring-1 ring-emerald-500/20 shadow-lg shadow-emerald-500/5' 
                    : 'border-emerald-900/10 bg-emerald-900/5 hover:bg-emerald-900/10'
                  ]"
                  @click="openPedido(pedido)"
                  @dblclick="editInTactical(pedido)"
                  @contextmenu.prevent="handleContextMenu($event, pedido)"
              >
                  <!-- ID -->
                  <div class="w-20 font-mono text-emerald-500">
                      #{{ pedido.id }}
                  </div>

                  <!-- Fecha -->
                  <div class="w-32 text-sm text-emerald-200/70 flex flex-col leading-tight">
                      <span>{{ formatDate(pedido.fecha).split(' ')[0] }}</span>
                      <span class="text-[10px] text-emerald-200/40">{{ formatDate(pedido.fecha).split(' ')[1] }}</span>
                  </div>

                  <!-- Cliente -->
                  <div class="flex items-center gap-4 flex-1 min-w-0">
                      <div class="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-900 to-green-900 flex items-center justify-center text-white font-bold text-xs border border-emerald-500/20 shrink-0">
                           {{ getInitials(pedido.cliente?.razon_social) }}
                      </div>
                      <div class="min-w-0 flex-1">
                          <h3 class="font-bold text-emerald-100 truncate">{{ pedido.cliente?.razon_social || 'Cliente Desconocido' }}</h3>
                           <p v-if="pedido.nota" class="text-xs text-emerald-200/30 font-mono italic truncate">{{ pedido.nota }}</p>
                      </div>
                  </div>

                  <!-- Total -->
                  <div class="w-32 text-right font-mono text-emerald-100 font-bold">
                      {{ formatCurrency(pedido.total) }}
                  </div>
                  
                  <!-- Status Badge (Interactive Custom Dropdown) -->
                  <div class="w-32 flex justify-center relative group/status">
                      <div class="relative">
                          <button 
                              class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide border transition-all flex items-center gap-1.5"
                              :class="getStatusClass(pedido.estado)"
                              @click.stop="toggleStatusMenu(pedido)"
                          >
                              {{ pedido.estado }}
                              <i class="fas fa-caret-down text-[8px] opacity-50"></i>
                          </button>
                          
                          <!-- Custom Colorful Dropdown Menu -->
                          <div 
                              v-if="statusMenuOpen === pedido.id" 
                              class="absolute top-full left-1/2 -translate-x-1/2 mt-1 z-50 bg-[#020f0a] border border-emerald-500/30 rounded-lg shadow-2xl py-1 min-w-[120px] backdrop-blur-md animate-in fade-in zoom-in-95 duration-150"
                              v-click-outside="() => statusMenuOpen = null"
                          >
                              <button 
                                  v-for="status in availableStatuses" 
                                  :key="status"
                                  @click.stop="handleStatusChange(pedido, status)"
                                  class="w-full px-3 py-1.5 text-left text-[10px] font-bold uppercase tracking-wider hover:bg-white/5 transition-colors flex items-center gap-2"
                                  :class="getStatusColorOnly(status)"
                              >
                                  <div class="w-1.5 h-1.5 rounded-full" :class="getStatusBgOnly(status)"></div>
                                  {{ status }}
                              </button>
                          </div>
                      </div>
                  </div>

                   <div class="w-10 flex justify-end">
                      <i class="fas fa-chevron-right text-emerald-900/30 group-hover:text-emerald-500/50 transition-colors"></i>
                  </div>
              </div>

              <!-- Empty State -->
              <div v-if="sortedAndFilteredPedidos.length === 0 && !store.isLoading" class="flex flex-col items-center justify-center py-20 text-emerald-900/40">
                  <i class="fas fa-box-open text-4xl mb-4"></i>
                  <p>No se encontraron pedidos</p>
              </div>
              
               <!-- Loading State -->
              <div v-if="store.isLoading" class="flex flex-col items-center justify-center py-20 text-emerald-500">
                  <i class="fas fa-spinner fa-spin text-4xl mb-4"></i>
                  <p>Cargando...</p>
              </div>
          </div>
        </div>
      </div>

      <!-- Static Inspector Panel -->
      <aside class="w-[400px] bg-[#02110c] border-l border-emerald-900/20 shrink-0">
          <PedidoInspector 
              :model-value="selectedPedido"
              @close="selectedPedido = null"
              @update-status="handleStatusChange"
              @clone="handleClone"
              @delete-item="handleDeleteItem"
          />
      </aside>

      <!-- Context Menu -->
      <Teleport to="body">
          <div 
              v-if="contextMenu.visible"
              class="fixed z-[9999] bg-[#05211a] border border-emerald-500/30 rounded-lg shadow-2xl py-1 min-w-[160px] backdrop-blur-md animate-in fade-in zoom-in-95 duration-100"
              :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
              v-click-outside="closeContextMenu"
          >
              <button 
                  @click="executeContextMenuAction('edit')"
                  class="w-full px-4 py-2 text-left text-xs font-bold text-emerald-100 hover:bg-emerald-500/20 flex items-center gap-2 transition-colors border-b border-emerald-900/10"
              >
                  <i class="fas fa-edit text-emerald-400"></i>
                  Abrir edición en Grilla
              </button>
              <button 
                  @click="executeContextMenuAction('inspector')"
                  class="w-full px-4 py-2 text-left text-xs font-bold text-emerald-100 hover:bg-emerald-500/20 flex items-center gap-2 transition-colors border-b border-emerald-900/10"
              >
                  <i class="fas fa-search text-emerald-400"></i>
                  Ver en Inspector
              </button>
              <button 
                  @click="executeContextMenuAction('clone')"
                  class="w-full px-4 py-2 text-left text-xs font-bold text-emerald-100 hover:bg-emerald-500/20 flex items-center gap-2 transition-colors"
              >
                  <i class="fas fa-copy text-emerald-400"></i>
                  Clonar Pedido
              </button>
          </div>
      </Teleport>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePedidosStore } from '@/stores/pedidos' 
import { useNotificationStore } from '../../stores/notification'
import PedidoInspector from './PedidoInspector.vue'

const router = useRouter()
const notificationStore = useNotificationStore()
const store = usePedidosStore()

const searchQuery = ref('')
const activeFilter = ref('all') 
const selectedPedido = ref(null)
const statusMenuOpen = ref(null)
const contextMenu = ref({ visible: false, x: 0, y: 0, pedido: null })

// Sort State
const sortKey = ref('fecha')
const sortOrder = ref('desc')

const availableStatuses = ['PENDIENTE', 'CUMPLIDO', 'ANULADO', 'PRESUPUESTO', 'INTERNO']

// Directive for clicking outside
const vClickOutside = {
    mounted(el, binding) {
        el.clickOutsideEvent = (event) => {
            if (!(el === event.target || el.contains(event.target))) {
                binding.value(event)
            }
        }
        document.addEventListener('click', el.clickOutsideEvent)
    },
    unmounted(el) {
        document.removeEventListener('click', el.clickOutsideEvent)
    }
}

const filters = computed(() => {
    const counts = {
        all: store.pedidos.length,
        PENDIENTE: store.pedidos.filter(p => p.estado === 'PENDIENTE').length,
        CUMPLIDO: store.pedidos.filter(p => p.estado === 'CUMPLIDO').length,
        PRESUPUESTO: store.pedidos.filter(p => p.estado === 'PRESUPUESTO' || p.estado === 'INTERNO' || p.estado === 'BORRADOR').length,
        ANULADO: store.pedidos.filter(p => p.estado === 'ANULADO').length
    }

    return [
        { key: 'all', label: `Todos (${counts.all})`, activeClass: 'bg-emerald-600/70 text-white shadow-md ring-1 ring-emerald-500' },
        { key: 'PENDIENTE', label: `Pendientes (${counts.PENDIENTE})`, activeClass: 'bg-emerald-500 text-white font-bold shadow-md ring-1 ring-emerald-400' },
        { key: 'CUMPLIDO', label: `Cumplidos (${counts.CUMPLIDO})`, activeClass: 'bg-yellow-500 text-black font-bold shadow-md ring-1 ring-yellow-400' },
        { key: 'PRESUPUESTO', label: `Presupuesto (${counts.PRESUPUESTO})`, activeClass: 'bg-purple-600 text-white shadow-md ring-1 ring-purple-500' },
        { key: 'ANULADO', label: `Anulados (${counts.ANULADO})`, activeClass: 'bg-red-600 text-white shadow-md ring-1 ring-red-500' }
    ]
})

const refresh = async () => {
    const params = { limit: 100 }
    await store.fetchPedidos(params)
}

const setFilter = (key) => {
    activeFilter.value = key
}

const sortedAndFilteredPedidos = computed(() => {
    let result = store.pedidos
    
    if (activeFilter.value !== 'all') {
        if (activeFilter.value === 'PRESUPUESTO') {
            result = result.filter(p => p.estado === 'PRESUPUESTO' || p.estado === 'INTERNO' || p.estado === 'BORRADOR')
        } else {
            result = result.filter(p => p.estado === activeFilter.value)
        }
    }

    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(p => {
             const idMatch = String(p.id).includes(query)
            const clientMatch = p.cliente?.razon_social?.toLowerCase().includes(query)
            return idMatch || clientMatch
        })
    }

    result.sort((a, b) => {
        let valA, valB
        switch (sortKey.value) {
             case 'id': valA = a.id; valB = b.id; break;
             case 'fecha': valA = new Date(a.fecha); valB = b.fecha ? new Date(b.fecha) : new Date(0); break;
             case 'cliente': valA = (a.cliente?.razon_social || '').toLowerCase(); valB = (b.cliente?.razon_social || '').toLowerCase(); break;
             case 'total': valA = a.total; valB = b.total; break;
             case 'estado': valA = (a.estado || '').toLowerCase(); valB = (b.estado || '').toLowerCase(); break;
             default: valA = a.id; valB = b.id;
        }

        if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1
        if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1
        return 0
    })

    return result
})

const getStatusClass = (status) => {
    switch (status) {
        case 'PENDIENTE': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50'
        case 'BORRADOR': return 'bg-purple-600/20 text-purple-400/50 border-purple-500/20'
        case 'CUMPLIDO': return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/50'
        case 'ANULADO': return 'bg-red-500/20 text-red-500 border-red-500/50'
        case 'PRESUPUESTO': return 'bg-purple-600/40 text-purple-300 border-purple-500/50' 
        case 'INTERNO': return 'bg-cyan-600/40 text-cyan-300 border-cyan-500/50'
        default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
    }
}

const getStatusColorOnly = (status) => {
    switch (status) {
        case 'PENDIENTE': return 'text-emerald-400'
        case 'BORRADOR': return 'text-purple-400/50'
        case 'CUMPLIDO': return 'text-yellow-500'
        case 'ANULADO': return 'text-red-500'
        case 'PRESUPUESTO': return 'text-purple-300' 
        case 'INTERNO': return 'text-cyan-300'
        default: return 'text-gray-400'
    }
}

const getStatusBgOnly = (status) => {
    switch (status) {
        case 'PENDIENTE': return 'bg-emerald-500'
        case 'BORRADOR': return 'bg-purple-500'
        case 'CUMPLIDO': return 'bg-yellow-500'
        case 'ANULADO': return 'bg-red-500'
        case 'PRESUPUESTO': return 'bg-purple-500' 
        case 'INTERNO': return 'bg-cyan-500'
        default: return 'bg-gray-500'
    }
}

const toggleStatusMenu = (pedido) => {
    if (statusMenuOpen.value === pedido.id) statusMenuOpen.value = null
    else statusMenuOpen.value = pedido.id
}

const openPedido = (pedido) => {
    selectedPedido.value = pedido
}

const editInTactical = (pedido) => {
    router.push(`/hawe/tactico?edit=${pedido.id}`)
}

const handleContextMenu = (e, pedido) => {
    contextMenu.value = {
        visible: true,
        x: e.clientX,
        y: e.clientY,
        pedido
    }
}

const closeContextMenu = () => {
    contextMenu.value.visible = false
}

const executeContextMenuAction = (action) => {
    const pedido = contextMenu.value.pedido
    closeContextMenu()
    
    if (!pedido) return
    
    if (action === 'edit') {
        editInTactical(pedido)
    } else if (action === 'inspector') {
        openPedido(pedido)
    } else if (action === 'clone') {
        selectedPedido.value = pedido
        handleClone()
    }
}

const handleStatusChange = async (pedido, newStatus) => {
    statusMenuOpen.value = null
    if (pedido.estado === newStatus) return
    
    try {
        await store.updatePedido(pedido.id, { estado: newStatus })
        notificationStore.add(`Pedido #${pedido.id} actualizado a ${newStatus}`, 'success')
        
        const updated = store.pedidos.find(p => p.id === pedido.id)
        if (updated && selectedPedido.value && selectedPedido.value.id === pedido.id) {
            selectedPedido.value = updated
        }
    } catch (e) {
        notificationStore.add('Error actualizando estado', 'error')
    }
}

const handleClone = async () => {
    if (!selectedPedido.value) return
    
    if (!confirm(`¿Estás seguro de CLONAR el Pedido #${selectedPedido.value.id}?\nSe creará una copia nueva en estado PENDIENTE.`)) {
        return
    }

    try {
        const newOrder = await store.clonePedido(selectedPedido.value.id)
        notificationStore.add(`Pedido clonado con éxito (ID: ${newOrder.id})`, 'success')
        selectedPedido.value = newOrder
        
        const listContainer = document.querySelector('.overflow-y-auto')
        if (listContainer) listContainer.scrollTop = 0
        
    } catch (e) {
        notificationStore.add('Error clonando pedido', 'error')
    }
}

const handleDeleteItem = async (itemId) => {
    if (!selectedPedido.value) return
    if (!confirm('¿Seguro que deseas eliminar este item?')) return

    try {
        await store.deletePedidoItem(selectedPedido.value.id, itemId)
        notificationStore.add('Item eliminado', 'success')
    } catch (e) {
        notificationStore.add('Error eliminando item', 'error')
    }
}

onMounted(() => {
    refresh()
    window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeydown)
})

const handleGlobalKeydown = (e) => {
    if (e.key === 'F4') {
        e.preventDefault()
        router.push('/hawe/tactico')
    }
}

const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('es-AR', {
        day: '2-digit',
        month: '2-digit',
        year: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value)
}

const getInitials = (name) => {
    if (!name) return '?'
    return name.substring(0, 1).toUpperCase()
}

const toggleSort = (key) => {
    if (sortKey.value === key) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
        sortKey.value = key
        sortOrder.value = 'asc'
        if (key === 'fecha' || key === 'id') sortOrder.value = 'desc'
    }
}
</script>
