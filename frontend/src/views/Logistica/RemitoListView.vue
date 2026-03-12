<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans tokyo-bg neon-blue rounded-2xl border-2 border-blue-500 shadow-[0_0_30px_rgba(59,130,246,0.4)] p-6">
    
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative min-w-0">
      
      <!-- Top Bar -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-blue-900/20 bg-black/20 px-6 backdrop-blur-sm shrink-0">
        <!-- Title -->
        <div>
            <h1 class="font-outfit text-xl font-semibold text-white">
                Logística: Remitos Emitidos
            </h1>
            <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider">Control de Despachos</p>
        </div>

        <!-- Search & Tools -->
        <div class="flex items-center gap-4">
          <div class="relative">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-blue-500/50"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar por número o cliente..."
              class="h-9 w-64 rounded-full border border-blue-900/30 bg-[#02050f] pl-10 pr-4 text-sm text-blue-100 placeholder-blue-900/50 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          
          <button 
            @click="refresh"
            class="p-2 text-blue-500 hover:text-blue-300 transition-colors"
            title="Recargar"
          >
            <i class="fas fa-sync-alt" :class="{ 'animate-spin': store.loading }"></i>
          </button>
        </div>
      </header>

      <!-- Content List -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-blue-900/10 scrollbar-thumb-blue-900/30">
        
        <!-- List View -->
        <div class="flex flex-col gap-2">
            <!-- Header Row -->
             <div class="flex items-center justify-between px-4 py-2 text-xs font-bold text-blue-900/50 uppercase tracking-wider select-none">
                <div class="w-32">Número</div>
                <div class="w-28 text-center">Fecha</div>
                <div class="flex-1 px-4">Cliente</div>
                <div class="w-32 text-center">CAE</div>
                <div class="w-32 text-center">Estado</div>
                <div class="w-20 text-right">Items</div>
                <div class="w-16"></div>
            </div>

            <div 
                v-for="remito in filteredRemitos" 
                :key="remito.id"
                class="group flex items-center justify-between p-4 mb-2 rounded-xl border transition-all relative overflow-hidden bg-[#070d24] border-blue-900/20 hover:bg-[#0a1435] hover:border-blue-500/30 shadow-md"
            >
                <!-- Numero -->
                <div class="w-32 font-mono text-blue-400 font-bold text-sm">
                    {{ remito.numero_legal || 'BORRADOR' }}
                </div>

                <!-- Fecha -->
                <div class="w-28 text-center flex flex-col leading-tight">
                    <span class="text-xs text-blue-100 font-bold">{{ formatDate(remito.fecha_creacion).split(' ')[0] }}</span>
                </div>

                <!-- Cliente -->
                <div class="flex items-center gap-3 flex-1 min-w-0 px-4">
                    <div class="min-w-0 flex-1">
                        <h3 class="font-bold text-blue-50 text-sm truncate group-hover:text-blue-300 transition-colors">{{ remito.pedido?.cliente?.razon_social || 'Desconocido' }}</h3>
                        <p class="text-[10px] text-blue-200/30 font-mono italic">Pedido #{{ remito.pedido_id }}</p>
                    </div>
                </div>

                <!-- CAE -->
                <div class="w-32 text-center font-mono text-[11px] text-blue-200/60">
                    {{ remito.cae || '-' }}
                </div>
                
                <!-- Status Badge -->
                <div class="w-32 flex justify-center">
                    <span 
                        class="px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider border transition-all"
                        :class="getStatusClass(remito.estado)"
                    >
                        {{ remito.estado }}
                    </span>
                </div>

                <!-- Items Count -->
                <div class="w-20 text-right font-mono text-blue-100 font-bold">
                    {{ remito.items?.length || 0 }}
                </div>

                <!-- Actions -->
                <div class="w-16 flex justify-end gap-2">
                    <button 
                        @click="viewPedido(remito.pedido_id)" 
                        class="p-2 text-blue-500/50 hover:text-blue-400 transition-colors"
                        title="Ver Pedido"
                    >
                        <i class="fas fa-external-link-alt"></i>
                    </button>
                </div>
            </div>

            <!-- Empty State -->
            <div v-if="filteredRemitos.length === 0 && !store.loading" class="flex flex-col items-center justify-center py-20 text-blue-900/40">
                <i class="fas fa-truck-loading text-4xl mb-4"></i>
                <p>No se encontraron remitos</p>
            </div>
            
             <!-- Loading State -->
            <div v-if="store.loading" class="flex flex-col items-center justify-center py-20 text-blue-500">
                <i class="fas fa-spinner fa-spin text-4xl mb-4"></i>
                <p>Cargando remitos...</p>
            </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRemitosStore } from '@/stores/remitos'

const router = useRouter()
const store = useRemitosStore()
const searchQuery = ref('')

const refresh = async () => {
    await store.fetchAllRemitos()
}

const filteredRemitos = computed(() => {
    if (!searchQuery.value) return store.remitos
    const query = searchQuery.value.toLowerCase()
    return store.remitos.filter(r => {
        const numMatch = (r.numero_legal || '').toLowerCase().includes(query)
        const clientMatch = (r.pedido?.cliente?.razon_social || '').toLowerCase().includes(query)
        return numMatch || clientMatch
    })
})

const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('es-AR', {
        day: '2-digit',
        month: '2-digit',
        year: '2-digit'
    })
}

const getStatusClass = (status) => {
    switch (status) {
        case 'BORRADOR': return 'bg-slate-500/20 text-slate-400 border-slate-500/50'
        case 'EN_CAMINO': return 'bg-blue-500/20 text-blue-400 border-blue-500/50'
        case 'ENTREGADO': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50'
        case 'ANULADO': return 'bg-red-500/20 text-red-400 border-red-500/50'
        default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
    }
}

const viewPedido = (id) => {
    router.push({ name: 'PedidoLogistica', params: { id } })
}

onMounted(() => {
    refresh()
})
</script>

<style scoped>
.tokyo-bg {
    background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.05), transparent),
                radial-gradient(circle at bottom left, rgba(37, 99, 235, 0.05), transparent);
}
.neon-blue {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.1), inset 0 0 20px rgba(59, 130, 246, 0.05);
}
</style>
