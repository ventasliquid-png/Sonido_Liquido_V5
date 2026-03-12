<template>
  <div class="min-h-screen bg-slate-900 text-white p-6 font-sans">
    <!-- HEADER -->
    <header class="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
      <div>
        <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          <i class="fas fa-boxes-stacked mr-2"></i> Logística Táctica
        </h1>
        <p v-if="localPedido" class="text-slate-400 mt-1">
          Distribución para Pedido #{{ localPedido.id }} - {{ localPedido.cliente?.razon_social }}
        </p>
      </div>
      <div class="flex gap-4">
        <button @click="$router.back()" class="px-4 py-2 hover:bg-slate-800 rounded text-slate-400 transition">
          <i class="fas fa-arrow-left"></i> Volver al Pedido
        </button>
        <div v-if="loading" class="animate-spin h-6 w-6 border-2 border-blue-500 rounded-full border-t-transparent"></div>
      </div>
    </header>

    <!-- ERROR -->
    <div v-if="error" class="bg-red-500/10 border-l-4 border-red-500 p-4 mb-6 text-red-400">
      <p class="font-bold">Error Operativo</p>
      <p>{{ error }}</p>
    </div>
    
    <!-- [GATEKEEPER] SECURITY BANNER -->
    <div v-if="localPedido && !localPedido.liberado_despacho" class="bg-amber-500/10 border-l-4 border-amber-500 p-4 mb-6 text-amber-500 flex justify-between items-center">
      <div>
          <p class="font-bold uppercase tracking-wider text-xs"><i class="fas fa-lock"></i> Bloqueo Financiero Activo</p>
          <p class="text-sm">Este pedido no tiene la marca "Aprobado para Despacho". Los remitos nacerán bloqueados por defecto.</p>
      </div>
      <button class="text-xs bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 px-3 py-1.5 rounded border border-amber-500/30 uppercase font-bold transition">
          <i class="fas fa-shield-alt"></i> Ver Semáforo
      </button>
    </div>

    <div class="grid grid-cols-12 gap-8" v-if="localPedido">
      
      <!-- LEFT PANEL: POOL DE PENDIENTES -->
      <div class="col-span-4 bg-slate-800/50 rounded-xl p-4 border border-slate-700 flex flex-col h-[calc(100vh-200px)]">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold text-amber-400">
            <i class="fas fa-cubes"></i> Pool de Pendientes
          </h2>
          <span class="text-xs bg-amber-500/20 text-amber-300 px-2 py-1 rounded-full">
            {{ itemsPendientes.length }} Ítems
          </span>
        </div>

        <div class="flex-1 overflow-y-auto space-y-3 pr-2">
          <div v-for="item in itemsPendientes" :key="item.id" 
             draggable="true"
             @dragstart="onDragStart($event, item)"
             class="bg-slate-800 p-3 rounded-lg border border-slate-600 hover:border-amber-500/50 cursor-grab active:cursor-grabbing transition group select-none">
            
            <div class="flex justify-between items-start">
              <div>
                <p class="font-bold text-white">{{ item.producto?.nombre }}</p>
                <p class="text-xs text-slate-400">SKU: {{ item.producto?.sku }}</p>
              </div>
              <div class="text-right">
                <p class="text-amber-400 font-bold text-lg">{{ item.cantidad_pendiente }}</p>
                <p class="text-[10px] text-slate-500 uppercase">Pendiente</p>
              </div>
            </div>

            <!-- Progres Bar -->
            <div class="mt-2 h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
               <div class="h-full bg-amber-500 transition-all duration-500" 
                    :style="{ width: (item.cantidad_remitida / item.cantidad_original * 100) + '%' }"></div>
            </div>
            <div class="flex justify-between text-[10px] text-slate-500 mt-1">
               <span>Total: {{ item.cantidad_original }}</span>
               <span>En Viaje: {{ item.cantidad_remitida }}</span>
            </div>
          </div>

          <div v-if="itemsPendientes.length === 0" class="text-center py-10 text-slate-500 bg-slate-800/30 rounded-lg border-2 border-dashed border-slate-700">
             <i class="fas fa-check-circle text-4xl mb-2 text-green-500/50"></i>
             <p>Todo Asignado</p>
          </div>
        </div>
      </div>

      <!-- RIGHT PANEL: REMITOS ACTIVOS (CANVAS) -->
      <div class="col-span-8 space-y-6 overflow-y-auto h-[calc(100vh-200px)] pr-2">
        
        <!-- ACTION BAR -->
        <div class="flex justify-between items-end">
           <h2 class="text-xl font-semibold text-blue-400">Viajes Activos (Remitos)</h2>
           <button @click="showNewRemitoModal = true" 
             class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg hover:shadow-blue-500/20 transition flex items-center gap-2">
             <i class="fas fa-plus"></i> Nuevo Remito
           </button>
        </div>

        <!-- REMITOS LIST -->
        <div v-if="remitos.length === 0" class="text-center py-20 bg-slate-800/50 rounded-xl border border-dashed border-slate-700">
           <p class="text-slate-500">No hay remitos creados para este pedido.</p>
           <p class="text-sm text-slate-600">Cree uno nuevo para comenzar la distribución.</p>
        </div>

        <div v-for="remito in remitos" :key="remito.id" 
             @dragover.prevent @drop="onDrop($event, remito)"
             :class="{'opacity-75 grayscale': remito.estado === 'EN_CAMINO'}"
             class="bg-slate-800 rounded-xl border border-slate-700 p-4 transition-all duration-300 hover:shadow-xl hover:border-slate-600">
          
          <!-- HEADER REMITO -->
          <div class="flex justify-between items-start mb-4 pb-4 border-b border-slate-700/50">
             <div class="flex items-center gap-4">
                <div class="bg-blue-500/10 p-3 rounded-lg text-blue-400">
                   <i class="fas fa-truck text-xl"></i>
                </div>
                <div>
                   <h3 class="font-bold text-lg text-white">
                      Remito #{{ remito.numero_legal || 'BORRADOR' }}
                      <span v-if="!remito.aprobado_para_despacho" class="ml-2 text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded border border-red-500/30">
                         <i class="fas fa-lock"></i> Bloqueado
                      </span>
                   </h3>
                   <div class="flex gap-4 text-sm text-slate-400 mt-1">
                      <p><i class="fas fa-map-marker-alt"></i> {{ getAddressLabel(remito.domicilio_entrega_id) }}</p>
                      <p><i class="fas fa-building"></i> {{ getTransportLabel(remito.transporte_id) }}</p>
                   </div>
                </div>
             </div>

             <div class="text-right">
                <div class="inline-flex items-center gap-2 mb-2">
                   <span :class="getStatusClass(remito.estado)" class="px-3 py-1 rounded-full text-xs font-bold border">
                      {{ remito.estado }}
                   </span>
                </div>
                <div class="flex flex-col items-end gap-1">
                    <div v-if="remito.estado === 'BORRADOR' && remito.aprobado_para_despacho">
                       <button @click="tryDespachar(remito)" class="text-xs bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded transition w-full">
                          <i class="fas fa-paper-plane mr-1"></i> Despachar
                       </button>
                    </div>
                    <!-- PDF LEGAL BUTTON -->
                    <button @click="downloadLegalPDF(remito)" class="text-xs bg-slate-600 hover:bg-slate-500 text-white px-3 py-1 rounded transition w-full mt-1 border border-slate-500">
                        <i class="fas fa-file-pdf mr-1"></i> PDF Legal
                    </button>
                    <button @click="openPrint(remito)" class="text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-1 rounded transition w-full">
                        <i class="fas fa-print mr-1"></i> Imprimir
                    </button>
                </div>
             </div>
          </div>

          <!-- ITEMS REMITO -->
          <div class="bg-slate-900/50 rounded-lg p-3 min-h-[80px] border border-slate-700/50 mb-2">
             <p v-if="remito.items.length === 0" class="text-center text-slate-600 text-sm py-4 italic">
                Arrastre ítems aquí para asignarlos a este viaje
             </p>
             <div v-else class="space-y-2">
                <div v-for="rItem in remito.items" :key="rItem.id" class="flex justify-between items-center text-sm bg-slate-800 p-2 rounded border border-slate-700">
                   <span class="text-slate-300">
                      {{ getProductName(rItem.pedido_item_id) }}
                   </span>
                   <span class="font-mono font-bold text-blue-300">
                      {{ rItem.cantidad }} un.
                   </span>
                </div>
             </div>
          </div>
        </div>

      </div>
    </div>

    <!-- MODAL NEW REMITO -->
    <div v-if="showNewRemitoModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
       <div class="bg-slate-800 p-6 rounded-2xl w-full max-w-md shadow-2xl border border-slate-700">
          <h3 class="text-xl font-bold text-white mb-4">Nuevo Viaje (Remito)</h3>
          
          <div class="space-y-4">
             <!-- [V7] Manual Remito Support -->
             <div class="bg-slate-900/50 p-3 rounded border border-slate-700/50">
                 <p class="text-xs text-blue-400 font-bold mb-2 uppercase">Identificación Oficial (Opcional)</p>
                 <div class="grid grid-cols-2 gap-3">
                     <div>
                        <label class="text-[10px] text-slate-500 uppercase">Número Legal</label>
                        <input v-model="newRemitoForm.numero_legal" placeholder="0001-00001234" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm">
                     </div>
                     <div>
                        <label class="text-[10px] text-slate-500 uppercase">CAE (AFIP)</label>
                        <input v-model="newRemitoForm.cae" placeholder="71234567890123" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm">
                     </div>
                 </div>
                 <div v-if="newRemitoForm.cae" class="mt-2">
                    <label class="text-[10px] text-slate-500 uppercase">Vencimiento CAE</label>
                    <input type="date" v-model="newRemitoForm.vto_cae" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm">
                 </div>
             </div>

             <div>
                <label class="text-xs text-slate-400 uppercase font-bold">Dirección de Entrega</label>
                <select v-model="newRemitoForm.domicilio_entrega_id" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white mt-1">
                   <option v-for="d in clientDomicilios" :key="d.id" :value="d.id">{{ d.direccion }} - {{ d.localidad }}</option>
                </select>
             </div>
             
             <div>
                <label class="text-xs text-slate-400 uppercase font-bold">Transporte</label>
                <select v-model="newRemitoForm.transporte_id" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white mt-1">
                   <option v-for="t in logisticaStore.transportOptions" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                </select>
             </div>

             <div class="flex items-center gap-2 pt-2">
                <input type="checkbox" v-model="newRemitoForm.aprobado_para_despacho" id="approve" class="rounded bg-slate-900 border-slate-700 text-blue-600">
                <label for="approve" class="text-sm text-slate-300">Aprobar para despacho inmediato (Gatekeeper Bypass)</label>
             </div>
          </div>

          <div class="flex justify-end gap-3 mt-6">
             <button @click="showNewRemitoModal = false" class="text-slate-400 hover:text-white px-4 py-2">Cancelar</button>
             <button @click="saveNewRemito" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-bold flex items-center gap-2">
                <i v-if="newRemitoForm.cae" class="fas fa-check-circle"></i>
                {{ newRemitoForm.cae ? 'Registrar Oficial' : 'Crear Borrador' }}
             </button>
          </div>
       </div>
    </div>

    <!-- MODAL ADD ITEM -->
    <div v-if="showAddItemModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
       <div class="bg-slate-800 p-6 rounded-2xl w-full max-w-sm shadow-2xl border border-slate-700">
          <h3 class="text-lg font-bold text-white mb-4">Asignar Cantidad</h3>
          <p class="text-sm text-slate-400 mb-2">Producto: <span class="text-white">{{ dragItem?.producto?.nombre }}</span></p>
          <p class="text-sm text-slate-400 mb-4">Pendiente: {{ dragItem?.cantidad_pendiente }}</p>
          
          <input type="number" v-model.number="addItemAmount" :max="dragItem?.cantidad_pendiente" min="0.1" 
                 class="w-full bg-slate-900 border border-slate-700 rounded p-3 text-2xl text-center text-white font-mono focus:border-blue-500 outline-none">
          
          <div class="flex justify-end gap-3 mt-6">
             <button @click="cancelDrop" class="text-slate-400 hover:text-white px-4 py-2">Cancelar</button>
             <button @click="confirmDrop" class="bg-amber-600 hover:bg-amber-500 text-white px-6 py-2 rounded-lg font-bold">
                Asignar
             </button>
          </div>
       </div>
    </div>

    <!-- REMITO PRINT MDOAL -->
    <RemitoTemplate 
        v-if="printRemitoData" 
        :propRemito="printRemitoData"
        :pedido="localPedido"
        :logisticaStore="logisticaStore"
        :clientDomicilios="clientDomicilios"
        :pedidoItems="localPedido.items"
        @close="printRemitoData = null"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useRemitosStore } from '@/stores/remitos';
import { useLogisticaStore } from '@/stores/logistica';
import { usePedidosStore } from '@/stores/pedidos'; // Assuming this exists to fetch full pedido details
// If not, we might need to fetch manually. Assuming it exists.
import api from '@/services/api';
import RemitoTemplate from './components/RemitoTemplate.vue';

const route = useRoute();
const remitosStore = useRemitosStore();
const logisticaStore = useLogisticaStore();
// const pedidosStore = usePedidosStore(); // Let's try to just fetch manually or use store if robust

const localPedido = ref(null);
const loading = ref(true);
const error = ref(null);
const clientDomicilios = ref([]);

// Modals
const showNewRemitoModal = ref(false);
const showAddItemModal = ref(false);

// Forms
const newRemitoForm = ref({
    domicilio_entrega_id: null,
    transporte_id: null,
    aprobado_para_despacho: true,
    numero_legal: '',
    cae: '',
    vto_cae: ''
});

// Drag & Drop
const dragItem = ref(null);
const targetRemito = ref(null);
const addItemAmount = ref(0);
const printRemitoData = ref(null);

// --- Computed ---
const itemsPendientes = computed(() => remitosStore.itemsPendientes);
const remitos = computed(() => remitosStore.remitos);

// --- Methods ---

onMounted(async () => {
    const id = route.params.id;
    if (!id) {
        error.value = "ID de Pedido no especificado";
        return;
    }
    
    await loadData(id);
});

async function loadData(id) {
    loading.value = true;
    try {
        // 1. Load Pedido Full
        const resPedido = await api.get(`/pedidos/${id}`);
        localPedido.value = resPedido.data;
        remitosStore.currentPedido = resPedido.data;

        // 2. Load Remitos
        await remitosStore.fetchRemitos(id);
        
        // 3. Load Logistica Data
        await logisticaStore.fetchEmpresas();
        await logisticaStore.fetchAllNodos(); 
        
        // 4. Client Domicilios
        if (localPedido.value.cliente_id) {
             const resClient = await api.get(`/clientes/${localPedido.value.cliente_id}`);
             clientDomicilios.value = resClient.data.domicilios || [];
             
             // Defaults for new form
             newRemitoForm.value.domicilio_entrega_id = localPedido.value.domicilio_entrega_id;
             newRemitoForm.value.transporte_id = localPedido.value.transporte_id;
        }

    } catch (e) {
        error.value = e.message;
    } finally {
        loading.value = false;
    }
}

// Helpers
const getAddressLabel = (id) => {
   const dom = clientDomicilios.value.find(d => d.id === id);
   return dom ? `${dom.direccion} (${dom.localidad})` : 'Dirección Desconocida';
};

const getTransportLabel = (id) => {
   const opt = logisticaStore.transportOptions.find(t => t.id === id);
   // If not found (maybe raw ID?), try to find name manually or shorten UUID
   return opt ? opt.nombre : 'Transporte...';
};

const getProductName = (pedidoItemId) => {
   const item = localPedido.value?.items.find(i => i.id === pedidoItemId);
   return item?.producto?.nombre || 'Producto Desconocido';
};

const getStatusClass = (status) => {
   switch(status) {
      case 'BORRADOR': return 'bg-slate-700 text-slate-300 border-slate-600';
      case 'EN_CAMINO': return 'bg-blue-900/50 text-blue-300 border-blue-500/50';
      case 'ENTREGADO': return 'bg-green-900/50 text-green-300 border-green-500/50';
      default: return 'bg-slate-800 text-slate-400';
   }
};

// Remito Actions
const saveNewRemito = async () => {
   if (!newRemitoForm.value.domicilio_entrega_id) return alert("Seleccione dirección");
   if (!newRemitoForm.value.transporte_id) return alert("Seleccione transporte");
   
   // [GATEKEEPER SECURITY V7]
   // Validar si la OC está aprobada para logística
   if (!localPedido.value.liberado_despacho) {
       // Si no está liberado, forzar bloqueo a menos que tenga permisos de override (Gatekeeper Bypass Checkbox)
       // El checkbox 'aprobado_para_despacho' en el form permite el override si el usuario tiene rol.
       // Por ahora solo advertimos visualmente en el UI, pero si el usuario desmarca el check, nace bloqueado.
       // La lógica de negocio real del Gatekeeper: Si PedidoNO Liberado -> Remito Nace Bloqueado (False)
       if (!newRemitoForm.value.aprobado_para_despacho) {
           // OK, nace bloqueado.
       } else {
           // Usuario intenta "Forzar" aprobación.
           if (!confirm("⚠️ ALERTA DE SEGURIDAD\n\nEl pedido NO está liberado para despacho (Semáforo Financiero).\n¿Confirma forzar la aprobación de este remito?")) {
               return;
           }
       }
   }
   
   await remitosStore.createRemito({
      pedido_id: localPedido.value.id,
      items: [],
      ...newRemitoForm.value
   });
   showNewRemitoModal.value = false;
};

const tryDespachar = async (remito) => {
   if (!confirm("¿Confirmar salida física de mercadería? Esto descontará stock.")) return;
   await remitosStore.despacharRemito(remito.id);
};

const openPrint = (remito) => {
    printRemitoData.value = remito;
};

// Drag & Drop Logic
const onDragStart = (evt, item) => {
   dragItem.value = item;
   evt.dataTransfer.effectAllowed = 'move';
};

const onDrop = (evt, remito) => {
   if (remito.estado !== 'BORRADOR') return; // Bloquear drops en remitos cerrados
   targetRemito.value = remito;
   addItemAmount.value = dragItem.value.cantidad_pendiente;
   showAddItemModal.value = true;
};

const confirmDrop = async () => {
   if(!dragItem.value || !targetRemito.value) return;
   
   loading.value = true;
   try {
      await api.post(`/remitos/${targetRemito.value.id}/items`, {
         pedido_item_id: dragItem.value.id,
         cantidad: addItemAmount.value
      });
      // Refresh
      await remitosStore.fetchRemitos(localPedido.value.id); // Assuming localPedido.value.id is available
      showAddItemModal.value = false;
      addItemAmount.value = 0;
   } catch (e) {
      console.error(e);
      error.value = "Error al agregar ítem";
   } finally {
      loading.value = false;
      dragItem.value = null;
      targetRemito.value = null;
   }
};

const cancelDrop = () => {
    showAddItemModal.value = false;
    dragItem.value = null;
    targetRemito.value = null;
};

// [V5] Download Legal PDF
const downloadLegalPDF = async (remito) => {
    try {
        const response = await api.get(`/remitos/${remito.id}/pdf`, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `remito_legal_${remito.numero_legal || remito.id}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    } catch (e) {
        console.error("Error downloading PDF", e);
        alert("Error generando PDF Legal: " + (e.response?.data?.detail || e.message));
    }
};

const printRemito = (remitoData) => {
    printRemitoData.value = remitoData;
};

</script>

<style scoped>
/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #1e293b; 
}
::-webkit-scrollbar-thumb {
  background: #475569; 
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #64748b; 
}
</style>
