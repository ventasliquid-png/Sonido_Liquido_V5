<template>
  <div class="min-h-screen w-full bg-[#0f172a] p-4 flex justify-center items-start font-sans">
    <div class="w-full max-w-6xl bg-[#0f172a] rounded-3xl border-2 border-indigo-500/30 shadow-[0_0_50px_-12px_rgba(99,102,241,0.3)] overflow-hidden flex flex-col h-[90vh]">
      
      <!-- HEADER -->
      <header class="shrink-0 bg-indigo-950/20 border-b border-indigo-500/20 py-4 px-8 flex justify-between items-center backdrop-blur-md">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 bg-indigo-500 rounded-xl flex items-center justify-center shadow-[0_0_15px_rgba(99,102,241,0.5)]">
            <i class="fas fa-file-invoice text-white text-lg"></i>
          </div>
          <div>
            <h1 class="text-xl font-bold text-white tracking-tight uppercase">Nuevo Remito Manual</h1>
            <p class="text-[10px] text-indigo-400 font-bold tracking-widest uppercase">Protocolo Rosa/Blanco • V15.1.4</p>
          </div>
        </div>
        
        <div class="flex gap-4">
          <button @click="$router.push({ name: 'RemitoList' })" class="px-4 py-2 text-xs font-bold text-indigo-300 hover:text-white transition-colors flex items-center gap-2">
            <i class="fas fa-list"></i> Ver Listado
          </button>
          <button @click="resetForm" class="px-4 py-2 text-xs font-bold text-gray-500 hover:text-indigo-400 transition-colors flex items-center gap-2">
            <i class="fas fa-redo"></i> Reset
          </button>
        </div>
      </header>

      <!-- BODY -->
      <div v-if="!clientesStore.loading" class="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
        
        <!-- SECTION 1: CLIENT & LOGISTICS -->
        <div class="grid grid-cols-12 gap-8">
          
          <!-- Client Selector -->
          <div class="col-span-12 lg:col-span-7 space-y-4">
            <div class="flex justify-between items-end">
              <label class="text-[10px] font-bold text-indigo-400/60 uppercase tracking-widest">Selección de Cliente</label>
              <button @click="openNewClientModal" class="text-[10px] font-bold text-emerald-400 hover:text-emerald-300 transition-colors uppercase tracking-widest flex items-center gap-1">
                <i class="fas fa-plus-circle"></i> Nuevo Cliente (F4)
              </button>
            </div>
            
            <div class="relative group">
              <SmartSelect
                v-model="form.cliente_id"
                :options="clientesOptions"
                placeholder="Busque por Razón Social o CUIT..."
                canteraType="clientes"
                @create-new="openNewClientModal"
                @update:modelValue="onClientSelected"
              />
            </div>

            <!-- Client Info Card (Static) -->
            <transition name="fade">
              <div v-if="selectedClient" class="bg-indigo-500/5 border border-indigo-500/20 rounded-2xl p-4 flex gap-4 items-start animate-in slide-in-from-top-2">
                <div class="w-12 h-12 rounded-full bg-indigo-500/10 flex items-center justify-center shrink-0 border border-indigo-500/20">
                    <i class="fas fa-user text-indigo-400"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <h3 class="text-white font-bold truncate">{{ selectedClient.razon_social }}</h3>
                    <div class="flex gap-4 mt-1">
                        <span class="text-[11px] font-mono text-indigo-400/70">CUIT: {{ selectedClient.cuit }}</span>
                        <span class="text-[11px] font-bold text-indigo-400/70 uppercase">Condición: {{ selectedClient.condicion_iva?.nombre || 'S/D' }}</span>
                    </div>
                </div>
              </div>
            </transition>
          </div>

          <!-- Logistics -->
          <div class="col-span-12 lg:col-span-5 space-y-6 bg-black/20 rounded-2xl p-6 border border-white/5">
            <div class="space-y-2">
              <label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Punto de Entrega</label>
              <select 
                v-model="form.domicilio_entrega_id"
                class="w-full bg-[#0a0f1d] border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:border-indigo-500 focus:outline-none transition-all appearance-none"
                :disabled="!selectedClient"
              >
                <option :value="null">--- {{ selectedClient ? 'Seleccione dirección' : 'Seleccione cliente primero' }} ---</option>
                <option v-for="dom in clientAddresses" :key="dom.id" :value="dom.id">
                  {{ dom.calle }} {{ dom.numero }} ({{ dom.localidad }})
                </option>
              </select>
            </div>

            <div class="space-y-2">
              <label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Transporte / Expreso</label>
              <select 
                v-model="form.transporte_id"
                class="w-full bg-[#0a0f1d] border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:border-indigo-500 focus:outline-none transition-all appearance-none"
              >
                <option :value="null">--- Seleccione Transporte ---</option>
                <option v-for="t in transportes" :key="t.id" :value="t.id">
                  {{ t.nombre }}
                </option>
              </select>
            </div>
          </div>

        </div>

        <!-- SECTION 2: ITEMS GRID -->
        <div class="space-y-4">
          <div class="flex justify-between items-center">
             <label class="text-[10px] font-bold text-indigo-400/60 uppercase tracking-widest">Detalle de Mercadería</label>
             <span class="text-[10px] text-gray-600 font-mono">{{ form.items.length }} ítems cargados</span>
          </div>

          <div class="bg-black/40 rounded-3xl border border-white/5 overflow-hidden">
            <!-- Table Header -->
            <div class="grid grid-cols-12 bg-white/5 px-6 py-3 text-[9px] font-black uppercase tracking-[0.2em] text-gray-500 border-b border-white/5">
              <div class="col-span-1">#</div>
              <div class="col-span-9">Descripción del ítem</div>
              <div class="col-span-2 text-right">Cantidad</div>
            </div>

            <!-- Items -->
            <div class="divide-y divide-white/5">
              <div v-for="(item, index) in form.items" :key="index" class="grid grid-cols-12 px-6 py-4 gap-4 items-center group hover:bg-white/[0.02] transition-colors">
                <div class="col-span-1 font-mono text-xs text-indigo-500/50">{{ index + 1 }}</div>
                <div class="col-span-9">
                  <input 
                    v-model="item.descripcion"
                    type="text"
                    placeholder="Escriba la descripción..."
                    class="w-full bg-transparent border-none text-white text-sm focus:outline-none placeholder-gray-800"
                    @keydown.enter="focusQty(index)"
                  />
                </div>
                <div class="col-span-2 flex items-center justify-end gap-4">
                  <input 
                    :ref="el => qtyRefs[index] = el"
                    v-model.number="item.cantidad"
                    type="number"
                    class="w-20 bg-indigo-500/10 border border-indigo-500/20 rounded-lg px-2 py-1 text-right text-indigo-400 font-bold focus:outline-none focus:border-indigo-500"
                    @keydown.enter="addItem(index)"
                  />
                  <button @click="removeItem(index)" class="text-gray-700 hover:text-red-500 transition-colors">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>

              <!-- Add Row Trigger -->
               <div class="p-4 flex justify-center bg-indigo-500/5">
                  <button @click="addItem" class="text-[10px] font-bold text-indigo-400 hover:text-indigo-300 transition-all uppercase tracking-widest flex items-center gap-2">
                    <i class="fas fa-plus"></i> Agregar Línea
                  </button>
               </div>
            </div>
          </div>
        </div>

        <!-- SECTION 3: OBSERVATIONS -->
        <div class="grid grid-cols-12 gap-8">
            <div class="col-span-12 lg:col-span-8 space-y-2">
                <label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Observaciones / Notas de Entrega</label>
                <textarea 
                    v-model="form.observaciones"
                    class="w-full h-24 bg-black/20 border border-white/10 rounded-2xl p-4 text-sm text-white focus:border-indigo-500 focus:outline-none resize-none placeholder-gray-800"
                    placeholder="Instrucciones especiales para el transporte..."
                ></textarea>
            </div>
            <div class="col-span-12 lg:col-span-4 grid grid-cols-2 gap-4">
                 <div class="space-y-2">
                    <label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Bultos</label>
                    <input type="number" v-model.number="form.bultos" class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-sm text-white text-center" />
                </div>
                <div class="space-y-2">
                    <label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Valor Decl.</label>
                    <input type="number" v-model.number="form.valor_declarado" class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-sm text-white text-center" />
                </div>
            </div>
        </div>

      </div>

      <!-- FOOTER / ACTIONS -->
      <footer class="shrink-0 bg-indigo-950/20 border-t border-indigo-500/20 p-6 flex justify-between items-center px-12">
        <div class="flex items-center gap-2 text-indigo-400/50">
           <i class="fas fa-info-circle"></i>
           <span class="text-[10px] font-bold uppercase tracking-widest">Serie automática 0015-00003010+</span>
        </div>
        
        <div class="flex gap-4">
            <button 
                @click="emitirRemito"
                :disabled="isSaving || !isValid"
                class="group relative px-10 py-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:cursor-not-allowed text-white font-black uppercase tracking-[0.1em] rounded-2xl shadow-[0_10px_30px_-10px_rgba(79,70,229,0.5)] transition-all hover:-translate-y-1 active:translate-y-0"
            >
                <div class="flex items-center gap-3">
                    <i v-if="isSaving" class="fas fa-spinner fa-spin"></i>
                    <i v-else class="fas fa-rocket"></i>
                    <span>{{ isSaving ? 'Procesando...' : 'Emitir y Descargar' }}</span>
                </div>
            </button>
        </div>
      </footer>

      <!-- MODAL: CLIENTE NUEVO -->
      <Teleport to="body">
        <div v-if="showNewClientModal" class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-md flex items-center justify-center p-8 animate-in fade-in duration-300">
             <div class="w-full max-w-5xl h-full max-h-[90vh] bg-[#0f172a] rounded-3xl shadow-2xl border border-indigo-500/30 overflow-hidden relative">
                 <ClientCanvas 
                    id="new"
                    :isModal="true"
                    @close="showNewClientModal = false"
                    @save="onNewClientSaved"
                 />
             </div>
        </div>
      </Teleport>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue';
import { useClientesStore } from '@/stores/clientes';
import { useMaestrosStore } from '@/stores/maestros';
import { useNotificationStore } from '@/stores/notification';
import SmartSelect from '@/components/ui/SmartSelect.vue';
import ClientCanvas from '../Hawe/ClientCanvas.vue';
import api from '@/services/api';

const clientesStore = useClientesStore();
const maestrosStore = useMaestrosStore();
const notificationStore = useNotificationStore();

// --- STATE ---
const isSaving = ref(false);
const showNewClientModal = ref(false);
const qtyRefs = ref([]);

const form = reactive({
  cliente_id: null,
  cliente_nuevo: null,
  domicilio_entrega_id: null,
  transporte_id: null,
  items: [
    { descripcion: '', cantidad: 1 }
  ],
  observaciones: '',
  bultos: 1,
  valor_declarado: 0
});

const availableAddresses = ref([]);
const loadingAddresses = ref(false);

// --- COMPUTED ---
const clientesOptions = computed(() => {
  return clientesStore.clientes.map(c => ({
    id: c.id,
    nombre: c.razon_social,
    razon_social: c.razon_social,
    cuit: c.cuit
  }));
});

const selectedClient = computed(() => {
  if (!form.cliente_id) return null;
  return clientesStore.clientes.find(c => c.id === form.cliente_id);
});

const clientAddresses = computed(() => {
  if (form.cliente_nuevo) return form.cliente_nuevo.domicilios || [];
  return availableAddresses.value;
});

const transportes = computed(() => maestrosStore.transportes);

const isValid = computed(() => {
  return (form.cliente_id || form.cliente_nuevo) && 
         form.items.length > 0 && 
         form.items.every(i => i.descripcion.trim() && i.cantidad > 0);
});

// --- ACTIONS ---
onMounted(async () => {
  if (clientesStore.clientes.length === 0) await clientesStore.fetchClientes();
  if (maestrosStore.transportes.length === 0) await maestrosStore.fetchTransportes();
});

// Reactive trigger for client addresses
watch(() => form.cliente_id, async (newVal) => {
    if (!newVal) {
        availableAddresses.value = [];
        return;
    }
    
    loadingAddresses.value = true;
    try {
        const fullClient = await clientesStore.fetchClienteById(newVal);
        availableAddresses.value = fullClient.domicilios || [];
        
        // Auto-select first address if none selected
        if (availableAddresses.value.length > 0 && !form.domicilio_entrega_id) {
            const targetDom = availableAddresses.value.find(d => d.es_fiscal) || availableAddresses.value[0];
            form.domicilio_entrega_id = targetDom.id;
        }
    } catch (e) {
        console.error("Error loading client addresses", e);
    } finally {
        loadingAddresses.value = false;
    }
}, { immediate: true });

const onClientSelected = async (val) => {
    if (!val) return;
    form.cliente_nuevo = null;
    // Clearing current selection to force re-fetch or re-assignment
    form.domicilio_entrega_id = null;
};

const openNewClientModal = () => {
    showNewClientModal.value = true;
};

const onNewClientSaved = (client) => {
    showNewClientModal.value = false;
    if (client) {
        // Since it's a new client, it might not be in store yet or we can just use the ID
        // Refresh store
        clientesStore.fetchClientes();
        form.cliente_id = client.id;
        onClientSelected(client.id);
        notificationStore.add('Cliente creado y seleccionado.', 'success');
    }
};

const addItem = (index) => {
    // If enter pressed on last item, add new
    if (index !== undefined && index < form.items.length - 1) return;
    
    form.items.push({ descripcion: '', cantidad: 1 });
    // Focus new desc input? We'll let the user click for now or add clever refs
};

const removeItem = (index) => {
    if (form.items.length > 1) {
        form.items.splice(index, 1);
    } else {
        form.items[0] = { descripcion: '', cantidad: 1 };
    }
};

const focusQty = (index) => {
    nextTick(() => {
        if (qtyRefs.value[index]) qtyRefs.value[index].focus();
    });
};

const resetForm = () => {
    Object.assign(form, {
        cliente_id: null,
        cliente_nuevo: null,
        domicilio_entrega_id: null,
        transporte_id: null,
        items: [{ descripcion: '', cantidad: 1 }],
        observaciones: '',
        bultos: 1,
        valor_declarado: 0
    });
};

const emitirRemito = async () => {
    if (!isValid.value) return;
    
    isSaving.value = true;
    try {
        const payload = { ...form };
        const res = await api.post('/remitos/manual', payload);
        const remito = res.data;
        
        notificationStore.add(`Remito ${remito.numero_legal} emitido con éxito.`, 'success');
        
        // [GY-FIX] Robust PDF URL resolution
        // Use relative path to leverage Vite Proxy which we know is working for other API calls
        const pdfUrl = `/remitos/${remito.id}/pdf`;
        window.open(pdfUrl, '_blank');
        
        // Ask if want to reset? For now just reset
        resetForm();
    } catch (e) {
        console.error(e);
        notificationStore.add('Error al emitir remito: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        isSaving.value = false;
    }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.2);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.4);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
