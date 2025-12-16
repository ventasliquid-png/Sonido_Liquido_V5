<template>
  <div class="flex h-screen w-full bg-[#021812] text-gray-200 overflow-hidden font-sans">
    
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative min-w-0">
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
          
          <!-- General Filters (Todos/Activos/Inactivos style) -->
          <!-- For Orders: Todos / Pendientes / Completados / Anulados -->
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

            <!-- New Order Button (Direct to Tactico) -->
            <button 
                @click="router.push('/ventas/tactico')"
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
            <!-- Header Row with Sort -->
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
                class="group flex items-center justify-between p-3 rounded-lg border border-emerald-900/10 bg-emerald-900/5 hover:bg-emerald-900/10 cursor-pointer transition-colors"
                @dblclick="openPedido(pedido)"
                @contextmenu.prevent="openPedido(pedido)"
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
                <div class="flex items-center gap-4 flex-1">
                    <div class="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-900 to-green-900 flex items-center justify-center text-white font-bold text-xs border border-emerald-500/20 shrink-0">
                         {{ getInitials(pedido.cliente?.razon_social) }}
                    </div>
                    <div class="min-w-0 flex-1">
                        <h3 class="font-bold text-emerald-100 truncate">{{ pedido.cliente?.razon_social || 'Cliente Desconocido' }}</h3>
                        <!-- Optional Note Display -->
                         <p v-if="pedido.nota" class="text-xs text-emerald-200/30 font-mono italic truncate">{{ pedido.nota }}</p>
                    </div>
                </div>

                <!-- Total -->
                <div class="w-32 text-right font-mono text-emerald-100 font-bold">
                    {{ formatCurrency(pedido.total) }}
                </div>
                
                <!-- Status Badge (Interactive) -->
                <div class="w-32 flex justify-center relative group/status">
                    <span 
                        class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide border transition-all"
                        :class="getStatusClass(pedido.estado)"
                    >
                        {{ pedido.estado }}
                    </span>
                    
                    <!-- Invisible Select Overlay -->
                    <select 
                        :value="pedido.estado"
                        @click.stop
                        @change="handleStatusChange(pedido, $event.target.value)"
                        class="absolute inset-0 opacity-0 w-full h-full cursor-pointer"
                        title="Cambiar Estado"
                    >
                        <option value="BORRADOR" class="text-gray-500 bg-white font-bold">BORRADOR</option>
                        <option value="PENDIENTE" class="text-black bg-white">PENDIENTE</option>
                        <option value="CUMPLIDO" class="text-black bg-white">CUMPLIDO</option>
                        <option value="ANULADO" class="text-black bg-white">ANULADO</option>
                        <option value="PRESUPUESTO" class="text-black bg-white">PRESUPUESTO</option>
                    </select>
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
      <!-- Inspector Slide-over -->
      <Transition
        enter-active-class="transform transition ease-in-out duration-300"
        enter-from-class="translate-x-full"
        enter-to-class="translate-x-0"
        leave-active-class="transform transition ease-in-out duration-300"
        leave-from-class="translate-x-0"
        leave-to-class="translate-x-full"
      >
        <div v-if="selectedPedido" class="absolute inset-y-0 right-0 z-30 w-full max-w-md shadow-2xl">
            <PedidoInspector 
                :model-value="selectedPedido"
                @close="selectedPedido = null"
                @update-status="handleStatusChange"
                @clone="handleClone"
                @delete-item="handleDeleteItem"
            />
        </div>
      </Transition>

      <!-- Backdrop -->
      <Transition
        enter-active-class="transition-opacity ease-linear duration-300"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity ease-linear duration-300"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div 
            v-if="selectedPedido" 
            @click="selectedPedido = null"
            class="absolute inset-0 bg-black/50 z-20 backdrop-blur-sm"
        ></div>
      </Transition>

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

// Sort State
const sortKey = ref('fecha')
const sortOrder = ref('desc') // asc or desc

const filters = computed(() => {
    // Calculate counts from local list (which might be filtered by backend, but we do our best)
    // Ideally we need counts of ALL orders. If 'activeFilter' is 'all', we have all orders (up to limit).
    // If we only have a subset, counts will be subset counts.
    // For TACTICAL board, we assume we want counts of loaded.
    
    const counts = {
        all: store.pedidos.length,
        PENDIENTE: store.pedidos.filter(p => p.estado === 'PENDIENTE').length,
        BORRADOR: store.pedidos.filter(p => p.estado === 'BORRADOR' || p.estado === 'CLONADO').length,
        CUMPLIDO: store.pedidos.filter(p => p.estado === 'CUMPLIDO').length,
        PRESUPUESTO: store.pedidos.filter(p => p.estado === 'PRESUPUESTO' || p.estado === 'INTERNO').length,
        ANULADO: store.pedidos.filter(p => p.estado === 'ANULADO').length
    }

    return [
        { key: 'all', label: `Todos (${counts.all})`, activeClass: 'bg-emerald-600/70 text-white shadow-md ring-1 ring-emerald-500' },
        { key: 'PENDIENTE', label: `Pendientes (${counts.PENDIENTE})`, activeClass: 'bg-white/90 text-emerald-950 font-bold shadow-md ring-1 ring-white' },
        { key: 'BORRADOR', label: `Borradores (${counts.BORRADOR})`, activeClass: 'bg-gray-500 text-white font-bold shadow-md ring-1 ring-gray-400' },
        { key: 'CUMPLIDO', label: `Completados (${counts.CUMPLIDO})`, activeClass: 'bg-yellow-500/80 text-black font-bold shadow-md ring-1 ring-yellow-400' },
        { key: 'PRESUPUESTO', label: `Presupuesto (${counts.PRESUPUESTO})`, activeClass: 'bg-purple-600/70 text-white shadow-md ring-1 ring-purple-500' },
        { key: 'ANULADO', label: `Anulados (${counts.ANULADO})`, activeClass: 'bg-red-600/70 text-white shadow-md ring-1 ring-red-500' }
    ]
})

const refresh = async () => {
    // Fetch ALL for dashboard to get accurate counts if limit allows
    const params = { limit: 100 }
    // We don't filter by backend params here anymore if we want correct counts for other tabs!
    // If we filter backend by 'PENDIENTE', we won't know how many 'ANULADO' exist.
    // Strategy: Fetch ALL (Tactical Limit) then filter client side for tabs.
    // This supports "Tablero Táctico" concept of seeing everything.
    await store.fetchPedidos(params)
}

const setFilter = (key) => {
    activeFilter.value = key
}

const sortedAndFilteredPedidos = computed(() => {
    // 1. Filter by Status (Client Side for Counters Logic)
    let result = store.pedidos
    
    if (activeFilter.value !== 'all') {
        if (activeFilter.value === 'BORRADOR') {
            result = result.filter(p => p.estado === 'BORRADOR' || p.estado === 'CLONADO')
        } else if (activeFilter.value === 'PRESUPUESTO') {
            result = result.filter(p => p.estado === 'PRESUPUESTO' || p.estado === 'INTERNO')
        } else {
            result = result.filter(p => p.estado === activeFilter.value)
        }
    }

    // 2. Filter by Search Query
    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(p => {
             const idMatch = String(p.id).includes(query)
            const clientMatch = p.cliente?.razon_social?.toLowerCase().includes(query)
            return idMatch || clientMatch
        })
    }

    // 3. Sort
    result.sort((a, b) => {
        let valA, valB
        // ... (sort logic same as before)
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
        case 'PENDIENTE': return 'bg-white/10 text-white border-white/20 font-bold'
        case 'BORRADOR': return 'bg-gray-500/20 text-gray-400 border-gray-500/30 font-bold'
        case 'CLONADO': return 'bg-pink-500/20 text-pink-400 border-pink-500/30 font-bold' // Legacy
        case 'CUMPLIDO': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20 font-bold'
        case 'ANULADO': return 'bg-red-500/10 text-red-400 border-red-500/20 font-bold'
        case 'PRESUPUESTO': return 'bg-purple-600/40 text-purple-300 border-purple-500/50 font-bold' 
        case 'INTERNO': return 'bg-purple-600/40 text-purple-300 border-purple-500/50 font-bold' // Legacy
        default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20 font-bold'
    }
}

const openPedido = (pedido) => {
    selectedPedido.value = pedido
}

const handleStatusChange = async (pedido, newStatus) => {
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
    
    // Confirmation Dialog
    if (!confirm(`¿Estás seguro de CLONAR el Pedido #${selectedPedido.value.id}?\nSe creará una copia nueva en estado PENDIENTE.`)) {
        return
    }

    try {
        const newOrder = await store.clonePedido(selectedPedido.value.id)
        notificationStore.add(`Pedido clonado con éxito (ID: ${newOrder.id})`, 'success')
        selectedPedido.value = null 
        
        // Scroll to top to see new order
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
        router.push('/ventas/tactico')
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
        sortOrder.value = 'asc' // Default new sort to asc generally
        if (key === 'fecha' || key === 'id') sortOrder.value = 'desc' // Exception for date/id preference
    }
}
</script>
