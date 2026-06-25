// [IDENTIDAD] - frontend\src\views\Logistica\ManualRemitoView.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

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

            <!-- Pedido Selector (NUEVO) -->
            <transition name="fade">
              <div v-if="form.cliente_id" class="mt-4 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl p-4 animate-in slide-in-from-top-2">
                 <div class="flex justify-between items-end mb-2">
                   <label class="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Pedido Asociado (Opcional)</label>
                   <button @click="openNewPedidoModal" class="text-[10px] bg-orange-500/20 text-orange-400 hover:bg-orange-500/40 px-2 py-1 rounded font-bold uppercase tracking-widest transition-colors flex items-center gap-1">
                      <i class="fas fa-plus"></i> Crear Nuevo
                   </button>
                 </div>
                 <select 
                   v-model="form.pedido_id"
                   @change="onPedidoSelected"
                   class="w-full bg-[#0a0f1d] border border-indigo-500/30 rounded-xl px-4 py-3 text-sm text-white focus:border-indigo-500 focus:outline-none transition-all appearance-none"
                 >
                   <option :value="null">--- Sin Pedido Asociado (Remito Directo) ---</option>
                   <option v-for="ped in pendingOrders" :key="ped.id" :value="ped.id">
                     Pedido #{{ ped.id }} - {{ ped.fecha.split('T')[0] }} - Total: ${{ ped.total }}
                   </option>
                 </select>
                 <div v-if="pendingOrders.length === 0" class="mt-2 text-xs text-orange-400 opacity-80">
                     <i class="fas fa-info-circle"></i> El cliente no tiene pedidos pendientes.
                 </div>
              </div>
            </transition>

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

          <!-- Aviso de bloqueo cuando hay pedido seleccionado -->
          <div v-if="form.pedido_id" class="flex items-center justify-between bg-amber-500/10 border border-amber-500/20 rounded-xl px-4 py-3">
            <div class="flex items-center gap-2 text-xs text-amber-300">
              <i class="fas fa-lock text-amber-400"></i>
              <span>Los ítems provienen del pedido. Solo podés ajustar la cantidad a entregar.</span>
            </div>
            <button @click="openEditPedidoModal" class="text-[10px] font-black text-amber-400 hover:text-amber-200 bg-amber-500/20 hover:bg-amber-500/30 px-3 py-1.5 rounded-lg uppercase tracking-widest transition-all flex items-center gap-1.5 shrink-0 ml-4">
              <i class="fas fa-pen-to-square"></i> Editar Pedido
            </button>
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
                  <!-- Descripción editable solo en remito directo (sin pedido) -->
                  <input
                    v-if="!form.pedido_id"
                    v-model="item.descripcion"
                    type="text"
                    placeholder="Escriba la descripción..."
                    class="w-full bg-transparent border-none text-white text-sm focus:outline-none placeholder-gray-800"
                    @keydown.enter="focusQty(index)"
                  />
                  <span v-else class="text-sm text-white select-none">{{ item.descripcion }}</span>
                </div>
                <div class="col-span-2 flex items-center justify-end gap-4">
                  <input
                    :ref="el => qtyRefs[index] = el"
                    v-model.number="item.cantidad"
                    type="number"
                    :min="1"
                    :max="item._original_cantidad ? (item._original_cantidad - (item._entregada || 0)) : undefined"
                    class="w-20 bg-indigo-500/10 border border-indigo-500/20 rounded-lg px-2 py-1 text-right text-indigo-400 font-bold focus:outline-none focus:border-indigo-500"
                    @keydown.enter="!form.pedido_id && addItem(index)"
                  />
                  <!-- Quitar ítem solo en remito directo -->
                  <button v-if="!form.pedido_id" @click="removeItem(index)" class="text-gray-700 hover:text-red-500 transition-colors">
                    <i class="fas fa-times"></i>
                  </button>
                  <span v-else class="w-4"></span>
                </div>
              </div>

              <!-- Add Row: solo en remito directo -->
               <div v-if="!form.pedido_id" class="p-4 flex justify-center bg-indigo-500/5">
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
           <span class="text-[10px] font-bold uppercase tracking-widest">{{ ultimoNumeroLegal ? 'Último emitido: ' + ultimoNumeroLegal : 'Serie 0015 — automático' }}</span>
        </div>
        
        <div class="flex gap-4">
            <button
                @click="mostrarPreview"
                :disabled="isSaving || !isValid"
                class="group relative px-10 py-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:cursor-not-allowed text-white font-black uppercase tracking-[0.1em] rounded-2xl shadow-[0_10px_30px_-10px_rgba(79,70,229,0.5)] transition-all hover:-translate-y-1 active:translate-y-0"
            >
                <div class="flex items-center gap-3">
                    <i class="fas fa-eye"></i>
                    <span>Vista Previa</span>
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

      <!-- MODAL: PEDIDO NUEVO -->
      <Teleport to="body">
        <div v-if="showNewPedidoModal" class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-md flex items-center justify-center p-8 animate-in fade-in duration-300">
             <div class="w-full max-w-6xl h-full max-h-[95vh] bg-[#0f172a] rounded-3xl shadow-2xl border border-emerald-500/30 overflow-hidden relative">
                 <PedidoCanvas
                    :isModal="true"
                    :preselectedClienteId="form.cliente_id"
                    @close="showNewPedidoModal = false"
                    @save="onNewPedidoSaved"
                 />
             </div>
        </div>
      </Teleport>

      <!-- MODAL: EDITAR PEDIDO EXISTENTE -->
      <Teleport to="body">
        <div v-if="showEditPedidoModal" class="fixed inset-0 z-[150] bg-black/80 backdrop-blur-md flex items-center justify-center p-8 animate-in fade-in duration-300">
             <div class="w-full max-w-6xl h-full max-h-[95vh] bg-[#0f172a] rounded-3xl shadow-2xl border border-amber-500/30 overflow-hidden relative">
                 <PedidoCanvas
                    :isModal="true"
                    :editPedidoId="form.pedido_id"
                    @close="showEditPedidoModal = false"
                    @save="onEditPedidoSaved"
                 />
             </div>
        </div>
      </Teleport>

      <!-- MODAL: PREVIEW ANTES DE EMITIR -->
      <Teleport to="body">
        <div v-show="showPreview" class="fixed inset-0 z-[200] bg-black/90 backdrop-blur-md flex items-center justify-center p-8 animate-in fade-in duration-300">
          <div class="w-full max-w-3xl max-h-[90vh] bg-[#0f172a] rounded-3xl shadow-2xl border border-indigo-500/30 overflow-hidden flex flex-col">

            <!-- Preview Header -->
            <div class="shrink-0 bg-indigo-950/40 border-b border-indigo-500/20 px-8 py-5 flex justify-between items-center">
              <div class="flex items-center gap-4">
                <div class="w-9 h-9 bg-orange-500/20 rounded-xl flex items-center justify-center border border-orange-500/30">
                  <i class="fas fa-file-alt text-orange-400"></i>
                </div>
                <div>
                  <h2 class="text-base font-black text-white uppercase tracking-widest">Pre-Visualización de Remito</h2>
                  <p class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest">Revise antes de emitir</p>
                </div>
              </div>
              <button @click="showPreview = false" class="text-gray-600 hover:text-white transition-colors text-lg">
                <i class="fas fa-times"></i>
              </button>
            </div>

            <!-- Warning banner for partial delivery -->
            <div v-if="hasPartialItems" class="shrink-0 mx-6 mt-5 bg-orange-500/10 border border-orange-500/30 rounded-xl px-5 py-3 flex items-center gap-3">
              <i class="fas fa-exclamation-triangle text-orange-400 text-sm"></i>
              <span class="text-xs font-bold text-orange-300 uppercase tracking-widest">Atención — Este remito contiene entregas parciales. Los renglones destacados se entregan en cantidad menor al pedido.</span>
            </div>

            <!-- Preview Body -->
            <div class="flex-1 overflow-y-auto px-8 py-6 space-y-6 custom-scrollbar">

              <!-- Client + Date -->
              <div class="grid grid-cols-2 gap-6">
                <div class="space-y-1">
                  <p class="text-[10px] font-bold text-indigo-400/60 uppercase tracking-widest">Cliente</p>
                  <p class="text-sm font-bold text-white">{{ selectedClient?.razon_social || '—' }}</p>
                  <p class="text-xs text-indigo-400/70 font-mono">{{ selectedClient?.cuit || '' }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-[10px] font-bold text-indigo-400/60 uppercase tracking-widest">Pedido Ref.</p>
                  <p class="text-sm font-bold text-white">{{ form.pedido_id ? `#${form.pedido_id}` : '— Remito Directo —' }}</p>
                  <p class="text-xs text-indigo-400/70">{{ new Date().toLocaleDateString('es-AR') }}</p>
                </div>
              </div>

              <!-- Items Table -->
              <div class="bg-black/30 rounded-2xl border border-white/5 overflow-hidden">
                <div class="grid grid-cols-12 bg-white/5 px-5 py-2 text-[9px] font-black uppercase tracking-[0.2em] text-gray-500 border-b border-white/5">
                  <div class="col-span-1">#</div>
                  <div class="col-span-7">Descripción</div>
                  <div class="col-span-2 text-right">Pedido</div>
                  <div class="col-span-2 text-right">A Entregar</div>
                </div>
                <div class="divide-y divide-white/5">
                  <div
                    v-for="(item, idx) in form.items"
                    :key="idx"
                    :class="[
                      'grid grid-cols-12 px-5 py-3 gap-2 items-center',
                      isItemPartial(item) ? 'bg-orange-500/8 border-l-2 border-orange-500/60' : ''
                    ]"
                  >
                    <div class="col-span-1 font-mono text-xs text-indigo-500/50">{{ idx + 1 }}</div>
                    <div class="col-span-7">
                      <div class="flex items-center gap-2">
                        <span class="text-sm text-white">{{ item.descripcion }}</span>
                        <span v-if="isItemPartial(item)" class="text-[9px] font-black text-orange-400 bg-orange-500/15 px-2 py-0.5 rounded-full uppercase tracking-widest">Parcial</span>
                      </div>
                      <p v-if="item._entregada > 0" class="text-[10px] text-indigo-400/60 mt-0.5">Ya entregado anteriormente: {{ item._entregada }}</p>
                    </div>
                    <div class="col-span-2 text-right">
                      <span class="text-xs text-gray-500">{{ item._original_cantidad ?? '—' }}</span>
                    </div>
                    <div class="col-span-2 text-right">
                      <span :class="['text-sm font-bold', isItemPartial(item) ? 'text-orange-400' : 'text-emerald-400']">
                        {{ item.cantidad }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Logistics summary -->
              <div class="grid grid-cols-3 gap-4 text-xs">
                <div class="space-y-1">
                  <p class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Bultos</p>
                  <p class="text-white font-bold">{{ form.bultos }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Valor Decl.</p>
                  <p class="text-white font-bold">${{ form.valor_declarado }}</p>
                </div>
                <div v-if="form.observaciones" class="space-y-1">
                  <p class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Obs.</p>
                  <p class="text-white/70 text-xs">{{ form.observaciones }}</p>
                </div>
              </div>

            </div>

            <!-- Preview Footer -->
            <div class="shrink-0 border-t border-indigo-500/20 px-8 py-5 flex justify-between items-center bg-indigo-950/20">
              <button @click="showPreview = false" class="px-6 py-3 text-xs font-bold text-gray-400 hover:text-white border border-white/10 hover:border-white/30 rounded-xl transition-all uppercase tracking-widest">
                <i class="fas fa-arrow-left mr-2"></i>Volver a editar
              </button>
              <button
                @click="confirmarYEmitir"
                :disabled="isSaving"
                class="px-10 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 text-white font-black uppercase tracking-widest rounded-xl shadow-lg transition-all hover:-translate-y-0.5 flex items-center gap-3"
              >
                <i v-if="isSaving" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-rocket"></i>
                {{ isSaving ? 'Procesando...' : 'Confirmar y Emitir' }}
              </button>
            </div>

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
import PedidoCanvas from '../Ventas/PedidoCanvas.vue';
import api from '@/services/api';

const clientesStore = useClientesStore();
const maestrosStore = useMaestrosStore();
const notificationStore = useNotificationStore();

// --- STATE ---
const isSaving = ref(false);
const ultimoNumeroLegal = ref(null);
const showNewClientModal = ref(false);
const showNewPedidoModal = ref(false);
const showEditPedidoModal = ref(false);
const showPreview = ref(false);
const qtyRefs = ref([]);

const form = reactive({
  pedido_id: null,
  cliente_id: null,
  cliente_nuevo: null,
  domicilio_entrega_id: null,
  transporte_id: null,
  items: [
    { descripcion: '', cantidad: 1, codigo_visual: null }
  ],
  observaciones: '',
  bultos: 1,
  valor_declarado: 0
});

const availableAddresses = ref([]);
const loadingAddresses = ref(false);
const pendingOrders = ref([]);
const loadingOrders = ref(false);

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

// Reactive trigger for client addresses & orders
watch(() => form.cliente_id, async (newVal) => {
    if (!newVal) {
        availableAddresses.value = [];
        pendingOrders.value = [];
        form.pedido_id = null;
        return;
    }
    
    loadingAddresses.value = true;
    loadingOrders.value = true;
    try {
        const fullClient = await clientesStore.fetchClienteById(newVal);
        availableAddresses.value = fullClient.domicilios || [];
        
        // Fetch pending orders
        const ordersRes = await api.get('/pedidos/', { params: { estado: 'PENDIENTE', cliente_id: newVal } });
        pendingOrders.value = ordersRes.data || [];
        
        // Auto-select first address if none selected
        if (availableAddresses.value.length > 0 && !form.domicilio_entrega_id) {
            const targetDom = availableAddresses.value.find(d => d.es_fiscal) || availableAddresses.value[0];
            form.domicilio_entrega_id = targetDom.id;
        }
    } catch (e) {
        console.error("Error loading client addresses or orders", e);
    } finally {
        loadingAddresses.value = false;
        loadingOrders.value = false;
    }
}, { immediate: true });

const onClientSelected = async (val) => {
    if (!val) return;
    form.cliente_nuevo = null;
    form.domicilio_entrega_id = null;
    form.pedido_id = null;
};

const onPedidoSelected = () => {
    if (!form.pedido_id) {
        form.items = [{ descripcion: '', cantidad: 1, codigo_visual: null }];
        return;
    }
    const ped = pendingOrders.value.find(p => p.id === form.pedido_id);
    if (!ped) return;

    // Autocompletar datos logísticos del pedido
    if (ped.domicilio_entrega_id) form.domicilio_entrega_id = ped.domicilio_entrega_id;
    if (ped.transporte_id) form.transporte_id = ped.transporte_id;
    
    // Mapear items con lógica de cantidad parcial
    if (ped.items && ped.items.length > 0) {
        form.items = ped.items
            .map(i => {
                const entregada = i.cantidad_entregada || 0;
                const falta = i.cantidad - entregada;
                return {
                    descripcion: i.producto ? i.producto.nombre : (i.nota || 'Ítem de Pedido'),
                    cantidad: falta > 0 ? falta : 0,
                    codigo_visual: i.producto ? i.producto.codigo_visual : null,
                    _original_cantidad: i.cantidad,
                    _entregada: entregada
                };
            })
            .filter(i => i.cantidad > 0); // Omitimos los que ya fueron 100% entregados
            
        if (form.items.length === 0) {
            notificationStore.add("Este pedido ya fue entregado en su totalidad.", "warning");
        }
    }
};

const openNewClientModal = () => {
    showNewClientModal.value = true;
};

const onNewClientSaved = (client) => {
    showNewClientModal.value = false;
    if (client) {
        clientesStore.fetchClientes();
        form.cliente_id = client.id;
        onClientSelected(client.id);
        notificationStore.add('Cliente creado y seleccionado.', 'success');
    }
};

const openNewPedidoModal = () => {
    showNewPedidoModal.value = true;
};

const openEditPedidoModal = () => {
    showEditPedidoModal.value = true;
};

const onEditPedidoSaved = async () => {
    showEditPedidoModal.value = false;
    if (form.pedido_id && form.cliente_id) {
        const ordersRes = await api.get('/pedidos/', { params: { estado: 'PENDIENTE', cliente_id: form.cliente_id } });
        pendingOrders.value = ordersRes.data || [];
        onPedidoSelected();
        notificationStore.add('Pedido actualizado — ítems del remito sincronizados.', 'success');
    }
};

const onNewPedidoSaved = async (pedido) => {
    showNewPedidoModal.value = false;
    if (pedido) {
        notificationStore.add('Pedido creado con éxito.', 'success');
        // Refresh orders for this client
        if (form.cliente_id) {
            const ordersRes = await api.get('/pedidos/', { params: { estado: 'PENDIENTE', cliente_id: form.cliente_id } });
            pendingOrders.value = ordersRes.data || [];
            
            // Auto select new order
            form.pedido_id = pedido.id;
            onPedidoSelected();
        }
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
        pedido_id: null,
        cliente_id: null,
        cliente_nuevo: null,
        domicilio_entrega_id: null,
        transporte_id: null,
        items: [{ descripcion: '', cantidad: 1, codigo_visual: null }],
        observaciones: '',
        bultos: 1,
        valor_declarado: 0
    });
};

const isItemPartial = (item) => {
    if (!item._original_cantidad) return false;
    const totalAfter = (item._entregada || 0) + item.cantidad;
    return totalAfter < item._original_cantidad;
};

const hasPartialItems = computed(() => form.items.some(i => isItemPartial(i)));

const mostrarPreview = () => {
    if (!isValid.value) return;
    showPreview.value = true;
};

const confirmarYEmitir = () => {
    showPreview.value = false;
    emitirRemito();
};

const emitirRemito = async () => {
    if (!isValid.value) return;
    
    isSaving.value = true;
    try {
        const payload = { ...form };
        const res = await api.post('/remitos/manual', payload);
        const remito = res.data;
        ultimoNumeroLegal.value = remito.numero_legal;
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
