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
                @dblclick="openEditModal(remito)"
                class="group flex items-center justify-between p-4 mb-2 rounded-xl border transition-all relative overflow-hidden bg-[#070d24] border-blue-900/20 hover:bg-[#0a1435] hover:border-blue-500/30 shadow-md cursor-pointer"
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

      <!-- EDIT MODAL -->
      <div v-if="showEditModal" class="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-[100] p-4">
         <div class="bg-[#0f172a] border-2 border-blue-500/50 rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden">
            <header class="bg-blue-600/10 p-6 border-b border-blue-500/20 flex justify-between items-center">
                <div>
                    <h3 class="text-xl font-bold text-white">Editar Remito (Borrador)</h3>
                    <p class="text-xs text-blue-400 font-mono italic">ID: {{ editingRemito.id }}</p>
                </div>
                <button @click="closeEditModal" class="text-gray-500 hover:text-white transition-colors">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </header>

            <div class="p-8 space-y-6">
                <!-- Numero Legal & CAE -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Número Legal</label>
                        <input 
                            v-model="editForm.numero_legal" 
                            type="text" 
                            placeholder="0001-00001234"
                            class="w-full bg-slate-900 border border-blue-900/40 rounded-xl px-4 py-3 text-sm text-white focus:border-blue-500 outline-none transition-all"
                        />
                    </div>
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-blue-400 uppercase tracking-widest">CAE (AFIP)</label>
                        <input 
                            v-model="editForm.cae" 
                            type="text" 
                            placeholder="71234567890123"
                            class="w-full bg-slate-900 border border-blue-900/40 rounded-xl px-4 py-3 text-sm text-white focus:border-blue-500 outline-none transition-all"
                        />
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Vencimiento CAE</label>
                        <input 
                            v-model="editForm.vto_cae" 
                            type="date" 
                            class="w-full bg-slate-900 border border-blue-900/40 rounded-xl px-4 py-3 text-sm text-white focus:border-blue-500 outline-none transition-all"
                        />
                    </div>
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Transporte</label>
                        <select 
                            v-model="editForm.transporte_id" 
                            class="w-full bg-slate-900 border border-blue-900/40 rounded-xl px-4 py-3 text-sm text-white focus:border-blue-500 outline-none transition-all appearance-none"
                        >
                            <option v-for="t in maestrosStore.transportes" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                        </select>
                    </div>
                </div>

                <!-- Domicilio Choice -->
                <div class="space-y-1" v-if="clientAddresses.length > 0">
                    <label class="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Punto de Entrega</label>
                    <select 
                        v-model="editForm.domicilio_entrega_id" 
                        class="w-full bg-slate-900 border border-blue-900/40 rounded-xl px-4 py-3 text-sm text-white focus:border-blue-500 outline-none transition-all appearance-none"
                    >
                        <option v-for="d in clientAddresses" :key="d.id" :value="d.id">{{ d.calle }} {{ d.numero }} ({{ d.localidad }})</option>
                    </select>
                </div>
            </div>

            <footer class="bg-blue-600/5 p-6 border-t border-blue-500/20 flex justify-end gap-4">
                <button @click="closeEditModal" class="px-6 py-2 text-sm font-bold text-slate-400 hover:text-white transition-colors">Cancelar</button>
                <button 
                    @click="saveEdition" 
                    :disabled="isSaving"
                    class="px-8 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 text-white font-bold rounded-xl shadow-lg transition-all"
                >
                    <i v-if="isSaving" class="fas fa-spinner fa-spin mr-2"></i>
                    Actualizar Remito
                </button>
            </footer>
         </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useRemitosStore } from '@/stores/remitos'
import { useMaestrosStore } from '@/stores/maestros'
import { useNotificationStore } from '@/stores/notification'
import api from '@/services/api'

const router = useRouter()
const store = useRemitosStore()
const maestrosStore = useMaestrosStore()
const notification = useNotificationStore()

const searchQuery = ref('')

// Editing State
const showEditModal = ref(false)
const isSaving = ref(false)
const editingRemito = ref(null)
const clientAddresses = ref([])
const editForm = reactive({
    numero_legal: '',
    cae: '',
    vto_cae: '',
    transporte_id: null,
    domicilio_entrega_id: null
})

const refresh = async () => {
    await store.fetchAllRemitos()
}

const openEditModal = async (remito) => {
    if (remito.estado !== 'BORRADOR') {
        notification.add('Solo se pueden editar remitos en estado BORRADOR.', 'warning');
        return;
    }

    editingRemito.value = remito;
    editForm.numero_legal = remito.numero_legal || '';
    editForm.cae = remito.cae || '';
    editForm.vto_cae = remito.vto_cae ? new Date(remito.vto_cae).toISOString().split('T')[0] : '';
    editForm.transporte_id = remito.transporte_id;
    editForm.domicilio_entrega_id = remito.domicilio_entrega_id;

    // Load addresses for this client if we have client_id
    const clientId = remito.pedido?.cliente_id;
    if (clientId) {
        try {
            const res = await api.get(`/clientes/${clientId}`);
            clientAddresses.value = res.data.domicilios || [];
        } catch (e) {
            console.error("Error loading addresses", e);
        }
    }
    
    showEditModal.value = true;
}

const closeEditModal = () => {
    showEditModal.value = false;
    editingRemito.value = null;
}

const saveEdition = async () => {
    if (!editingRemito.value) return;
    
    isSaving.value = true;
    try {
        await store.updateRemito(editingRemito.value.id, { ...editForm });
        notification.add('Remito actualizado correctamente.', 'success');
        closeEditModal();
    } catch (e) {
        console.error(e);
        notification.add('Error al actualizar: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        isSaving.value = false;
    }
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
    if (maestrosStore.transportes.length === 0) maestrosStore.fetchTransportes()
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
