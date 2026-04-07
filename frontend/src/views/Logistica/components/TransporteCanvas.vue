// [IDENTIDAD] - frontend\src\views\Logistica\components\TransporteCanvas.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
    <div class="bg-[#0f172a] w-full max-w-[95vw] h-[90vh] rounded-xl border border-amber-500/30 shadow-[0_0_50px_rgba(245,158,11,0.1)] flex flex-col overflow-hidden relative">
        

        <!-- EXPLICIT TITLE BAR -->
        <div class="bg-amber-500/10 border-b border-amber-500/20 py-2 px-6 flex justify-between items-center shrink-0">
            <div class="flex items-center gap-3">
                 <i class="fas fa-truck-front text-amber-500 text-lg"></i>
                 <h1 class="text-xs font-black uppercase tracking-[0.2em] text-amber-500">
                    FICHA SOBERANA DE TRANSPORTE (V5.4)
                 </h1>
            </div>
            <div class="flex items-center gap-4">
                 <span class="text-[10px] text-white/30 font-mono" v-if="!isNew">ID: {{ modelValue.id }}</span>
                 <button @click="$emit('close')" class="text-white/30 hover:text-white transition-colors">
                    <i class="fas fa-times text-lg"></i>
                 </button>
            </div>
        </div>

        <!-- MAIN BODY: Scrollable -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-amber-900/50 scrollbar-track-black/20">
            
            <!-- RECTANGLE 1: IDENTITY & MASTER DATA (Address Hub Integration) -->
            <section class="bg-black/40 border border-white/10 rounded-2xl p-5 space-y-5 backdrop-blur-md relative group overflow-hidden">
                <div class="absolute top-0 left-0 w-1 h-full bg-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.8)]"></div>
                
                <div class="grid grid-cols-12 gap-6 items-start">
                    <!-- Left Column: Identity -->
                    <div class="col-span-12 lg:col-span-5 space-y-5 border-r border-white/5 pr-6">
                        <div class="group">
                            <label class="block text-[10px] font-black text-amber-500/60 uppercase mb-2 tracking-[0.2em]">Razón Social <span class="text-red-500">*</span></label>
                            <input 
                                ref="nameInput"
                                v-model="localModel.nombre" 
                                class="w-full bg-black/40 border border-amber-500/20 rounded-xl px-4 py-3 text-xl font-black text-white focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500/50 transition-all placeholder-white/10" 
                                placeholder="NOMBRE DEL TRANSPORTE" 
                            />
                        </div>

                        <div class="grid grid-cols-2 gap-4">
                            <div class="group">
                                <label class="block text-[9px] font-bold text-white/30 uppercase mb-1 tracking-widest">CUIT <span class="text-red-500">*</span></label>
                                <input v-model="localModel.cuit" class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-sm font-mono text-amber-200 focus:outline-none focus:border-amber-500/50 transition-all" placeholder="XX-XXXXXXXX-X" />
                            </div>
                            <div class="group">
                                <label class="block text-[9px] font-bold text-white/30 uppercase mb-1 tracking-widest">Condición IVA</label>
                                <select v-model="localModel.condicion_iva_id" class="w-full bg-black/20 border border-white/10 rounded-lg px-2 py-2 text-xs text-white/70 focus:outline-none">
                                    <option :value="null">Seleccionar...</option>
                                    <option v-for="ci in condicionesIva" :key="ci.id" :value="ci.id">{{ ci.nombre }}</option>
                                </select>
                            </div>
                        </div>

                        <!-- 64-BIT STATUS FLAGS (The New Genoma) -->
                        <div class="pt-4 border-t border-white/5 space-y-3">
                            <label class="block text-[9px] font-black text-white/20 uppercase tracking-[0.2em] mb-2">Capacidades Operativas</label>
                            
                            <div class="grid grid-cols-1 gap-2">
                                <!-- Bit 2: PICKUP -->
                                <div class="flex items-center justify-between p-2 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors group cursor-pointer" @click="toggleFlag(4)">
                                    <div class="flex items-center gap-3">
                                        <div class="h-6 w-6 rounded flex items-center justify-center bg-green-500/10 border border-green-500/20">
                                            <i class="fas fa-truck-loading text-green-400 text-[10px]"></i>
                                        </div>
                                        <span class="text-[10px] font-bold text-white/70 uppercase">Servicio de Retiro (Pickup)</span>
                                    </div>
                                    <button class="relative inline-flex h-4 w-8 items-center rounded-full transition-colors bg-white/10" :class="hasFlag(4) ? 'bg-green-500/50' : 'bg-white/10'">
                                        <span class="inline-block h-3 w-3 transform rounded-full bg-white transition-transform" :class="hasFlag(4) ? 'translate-x-4' : 'translate-x-1'" />
                                    </button>
                                </div>

                                <!-- Bit 5: WEB_REQUIRED -->
                                <div class="flex items-center justify-between p-2 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors group cursor-pointer" @click="toggleFlag(32)">
                                    <div class="flex items-center gap-3">
                                        <div class="h-6 w-6 rounded flex items-center justify-center bg-purple-500/10 border border-purple-500/20">
                                            <i class="fas fa-globe text-purple-400 text-[10px]"></i>
                                        </div>
                                        <span class="text-[10px] font-bold text-white/70 uppercase">Pre-carga Web Obligatoria</span>
                                    </div>
                                    <button class="relative inline-flex h-4 w-8 items-center rounded-full transition-colors bg-white/10" :class="hasFlag(32) ? 'bg-purple-500/50' : 'bg-white/10'">
                                        <span class="inline-block h-3 w-3 transform rounded-full bg-white transition-transform" :class="hasFlag(32) ? 'translate-x-4' : 'translate-x-1'" />
                                    </button>
                                </div>

                                <!-- Bit 3: RECOMMENDED -->
                                <div class="flex items-center justify-between p-2 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors group cursor-pointer" @click="toggleFlag(8)">
                                    <div class="flex items-center gap-3">
                                        <div class="h-6 w-6 rounded flex items-center justify-center bg-yellow-500/10 border border-yellow-500/20">
                                            <i class="fas fa-award text-yellow-400 text-[10px]"></i>
                                        </div>
                                        <span class="text-[10px] font-bold text-white/70 uppercase">Transporte Recomendado (ORO)</span>
                                    </div>
                                    <button class="relative inline-flex h-4 w-8 items-center rounded-full transition-colors bg-white/10" :class="hasFlag(8) ? 'bg-yellow-500/50' : 'bg-white/10'">
                                        <span class="inline-block h-3 w-3 transform rounded-full bg-white transition-transform" :class="hasFlag(8) ? 'translate-x-4' : 'translate-x-1'" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Right Column: Address Hub -->
                    <div class="col-span-12 lg:col-span-7 space-y-4">
                        <!-- Fiscal Address Summary (Static-ish) -->
                        <div 
                         @click="openFiscalEditor"
                         class="bg-amber-950/10 border border-amber-500/20 rounded-xl p-4 cursor-pointer hover:bg-amber-950/20 transition-all flex justify-between items-center group"
                        >
                            <div class="flex items-center gap-4">
                                <div class="h-10 w-10 rounded-full bg-amber-500/10 flex items-center justify-center border border-amber-500/20 shadow-[0_0_15px_rgba(245,158,11,0.2)]">
                                    <i class="fas fa-building text-amber-500"></i>
                                </div>
                                <div>
                                    <p class="text-[9px] font-black text-amber-500/60 uppercase tracking-widest">Ubicación Administrativa (Fiscal)</p>
                                    <p class="text-sm font-bold text-white">{{ computedFiscalAddress.full }}</p>
                                    <p class="text-[10px] text-white/30 font-mono">{{ computedFiscalAddress.details }}</p>
                                </div>
                            </div>
                            <i class="fas fa-pencil-alt text-white/10 group-hover:text-amber-500 transition-colors"></i>
                        </div>

                        <!-- Address Hub Selector for Operative Depots -->
                        <div class="pt-2">
                             <AddressSelector 
                              v-model:domicilios="domicilios"
                              :transportes="[]"
                              @edit="openDomicilioTab"
                              @delete="handleDomicilioDelete"
                              @restore="handleDomicilioRestore"
                              @add="openNewDomicilio"
                              @sync-fiscal="handleSyncFiscal"
                            />
                        </div>
                    </div>
                </div>
            </section>

            <!-- RECTANGLE 2: CONTACT & WEB -->
            <section class="bg-black/20 border border-white/5 rounded-2xl p-5 shadow-inner">
                <div class="grid grid-cols-12 gap-6 items-end">
                    <div class="col-span-12 lg:col-span-3">
                        <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Teléfonos Reclamos</label>
                        <input v-model="localModel.telefono_reclamos" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-xs text-white focus:border-amber-500/50 outline-none" placeholder="0810 / 0800..." />
                    </div>
                    <div class="col-span-12 lg:col-span-3">
                        <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">WhatsApp Operativo</label>
                        <input v-model="localModel.whatsapp" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-xs text-white focus:border-amber-500/50 outline-none" placeholder="+54 9..." />
                    </div>
                    <div class="col-span-12 lg:col-span-3">
                        <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Email Administración</label>
                        <input v-model="localModel.email" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-xs text-white focus:border-amber-500/50 outline-none" placeholder="adm@..." />
                    </div>
                    <div class="col-span-12 lg:col-span-3">
                        <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Web Tracking</label>
                        <input v-model="localModel.web_tracking" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-xs text-white focus:border-amber-500/50 outline-none" placeholder="https://..." />
                    </div>
                </div>
            </section>

            <!-- RECTANGLE 3: BRANCHES / NODES (Independent Governance) -->
            <section class="bg-black/20 border border-white/5 rounded-2xl p-5 shadow-inner">
                <div class="flex justify-between items-center mb-4">
                    <div class="flex items-center gap-3">
                        <i class="fas fa-map-marked-alt text-emerald-500"></i>
                        <h3 class="text-sm font-black text-emerald-500 uppercase tracking-[0.2em]">SUCURSALES Y DESTINOS</h3>
                    </div>
                    <div class="text-[10px] text-white/20 uppercase font-bold tracking-[0.3em]" v-if="isNew">Configure el transporte para habilitar nodos</div>
                </div>
                
                <div v-if="!isNew">
                    <TransporteBranches :transport-id="localModel.id" />
                </div>
            </section>

            <!-- RECTANGLE 4: NOTES -->
            <section class="bg-black/20 border border-white/5 rounded-2xl p-5">
                <div class="flex items-center gap-2 mb-3">
                    <i class="fas fa-comment-alt text-amber-500/50"></i>
                    <label class="text-xs font-black text-amber-500/70 uppercase tracking-widest leading-none">Observaciones Internas</label>
                </div>
                <textarea 
                    v-model="localModel.observaciones" 
                    rows="3" 
                    class="w-full bg-black/40 border border-white/10 rounded-xl p-4 text-white focus:border-amber-500/50 outline-none transition-all resize-none text-sm placeholder-white/5 shadow-inner"
                    placeholder="NOTAS DE OPERACIÓN, REQUISITOS DE EMBALAJE..."
                ></textarea>
            </section>

        </div>

        <!-- FOOTER: Actions -->
        <div class="h-16 border-t border-white/10 bg-black/40 flex items-center justify-between px-6 shrink-0 z-20 backdrop-blur-md">
             <div class="text-[10px] text-white/20 font-mono">
                 <span v-if="localModel.updated_at">Actualizado: {{ formatDate(localModel.updated_at) }}</span>
             </div>
             <div class="flex gap-4">
                  <button @click="$emit('close')" class="px-6 py-2 rounded border border-white/10 text-white/40 hover:text-white hover:bg-white/5 transition-colors font-bold text-xs uppercase tracking-wider">
                      Cancelar
                  </button>
                  <button @click="save" class="px-8 py-2 rounded bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-500 hover:to-yellow-500 text-white font-bold shadow-lg shadow-amber-900/40 transition-all flex items-center gap-2 text-xs uppercase tracking-wide">
                      <span v-if="saving"><i class="fas fa-spinner fa-spin"></i> Procesando...</span>
                      <span v-else><i class="fas fa-save"></i> Guardar Ficha</span>
                  </button>
             </div>
        </div>

        <!-- MODAL LAYER (Independent Contexts) -->
        <DomicilioSplitCanvas 
            v-if="activeTab === 'DOMICILIO'" 
            :show="true" 
            :domicilio="selectedDomicilio" 
            @close="activeTab = 'TRANSPORTE'" 
            @saved="handleDomicilioSaved" 
        />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed, nextTick } from 'vue';
import { useLogisticaStore } from '../../../stores/logistica';
import { useMaestrosStore } from '../../../stores/maestros';
import { useNotificationStore } from '../../../stores/notification';

// NOTE: These components must exist in the same directory or be importable
import TransporteBranches from './TransporteBranches.vue'; 
import AddressSelector from '../../Hawe/components/AddressSelector.vue';
import DomicilioSplitCanvas from '../../Hawe/components/DomicilioSplitCanvas.vue';

const props = defineProps({
    modelValue: {
        type: Object,
        default: () => ({})
    }
});

const emit = defineEmits(['update:modelValue', 'close', 'save']);

// Stores
const logisticaStore = useLogisticaStore();
const maestrosStore = useMaestrosStore();
const notification = useNotificationStore();

// Local State
const localModel = ref({ ...props.modelValue });
const domicilios = ref([]);
const activeTab = ref('TRANSPORTE'); // 'TRANSPORTE', 'DOMICILIO'
const selectedDomicilio = ref(null);
const saving = ref(false);
const nameInput = ref(null);

const isNew = computed(() => !localModel.value.id);
const provincias = computed(() => maestrosStore.provincias);
const condicionesIva = computed(() => maestrosStore.condicionesIva);

// --- 64-BIT FLAG LOGIC ---
const toggleFlag = (bit) => {
    if (!localModel.value.flags_estado) localModel.value.flags_estado = 3;
    localModel.value.flags_estado ^= bit;
};
const hasFlag = (bit) => {
    return !!(localModel.value.flags_estado & bit);
};

// --- ADDRESS HUB MAPPING ---
const mapVinculosToDomicilios = () => {
    if (localModel.value.vinculos_geograficos) {
        domicilios.value = localModel.value.vinculos_geograficos.map(vg => ({
            ...vg.domicilio,
            flags: vg.flags_relacion, 
            is_mirror: !!(localModel.value.flags_estado & 2097152) && vg.flags_relacion === 1
        }));
    } else {
        domicilios.value = [];
    }
};

const computedFiscalAddress = computed(() => {
    const fiscal = domicilios.value.find(d => !!(d.flags & 1) || d.es_fiscal);
    if (!fiscal) return { full: 'Sin Dirección Fiscal', details: 'Haga clic para configurar' };
    
    const prov = provincias.value.find(p => p.id === fiscal.provincia_id)?.nombre || fiscal.provincia_id || '';
    return {
        full: `${fiscal.calle} ${fiscal.numero || ''}`.trim(),
        details: `${fiscal.localidad || ''} ${prov ? ', ' + prov : ''}`.trim()
    };
});

// --- HUB EVENTS ---
const openFiscalEditor = () => {
    const fiscal = domicilios.value.find(d => !!(d.flags & 1) || d.es_fiscal);
    if (fiscal) openDomicilioTab(fiscal);
    else openNewDomicilio();
};

const openDomicilioTab = (dom) => {
    selectedDomicilio.value = dom;
    activeTab.value = 'DOMICILIO';
};

const openNewDomicilio = () => {
    selectedDomicilio.value = {
        id: null,
        local_id: Date.now(),
        calle: '',
        localidad: '',
        provincia_id: null,
        activo: true
    };
    activeTab.value = 'DOMICILIO';
};

const handleDomicilioSaved = (savedDom) => {
    const index = domicilios.value.findIndex(d => (d.id && d.id === savedDom.id) || (d.local_id && d.local_id === savedDom.local_id));
    if (index !== -1) domicilios.value[index] = savedDom;
    else domicilios.value.push(savedDom);
    
    // In V5.4, we don't sync back to flat fields because they are GONE.
    // We only need to ensure the hub knows about it.
    activeTab.value = 'TRANSPORTE';
};

const handleSyncFiscal = (dom) => {
    localModel.value.flags_estado |= 2097152; // Active MIRROR
    notification.add('Mirror Fiscal activado', 'success');
};

const handleDomicilioDelete = (dom) => {
    domicilios.value = domicilios.value.filter(d => d !== dom);
};

const handleDomicilioRestore = (dom) => {
    dom.activo = true;
};

// Watchers
watch(() => props.modelValue, (val) => {
    localModel.value = { ...val };
    mapVinculosToDomicilios();
}, { deep: true, immediate: true });

// Methods
const save = async () => {
    if (!localModel.value.nombre) {
        notification.add('Razón Social obligatoria', 'error');
        return;
    }

    saving.value = true;
    try {
        const payload = { ...localModel.value };
        
        // No more legacy booleans. Backend only expects flags_estado.

        if (isNew.value) {
            await logisticaStore.createEmpresa(payload);
        } else {
            await logisticaStore.updateEmpresa(payload.id, payload);
        }
        
        notification.add('Transporte guardado con éxito', 'success');
        emit('save');
        emit('close');
    } catch (e) {
        console.error(e);
        notification.add(e.response?.data?.detail || 'Error al guardar', 'error');
    } finally {
        saving.value = false;
    }
};

const formatDate = (date) => {
    if (!date) return '';
    return new Date(date).toLocaleDateString();
};

onMounted(async () => {
    if (maestrosStore.provincias.length === 0) await maestrosStore.fetchProvincias();
    if (maestrosStore.condicionesIva.length === 0) await maestrosStore.fetchCondicionesIva();
    mapVinculosToDomicilios();
    
    nextTick(() => {
        if (nameInput.value) nameInput.value.focus();
    });

    window.addEventListener('keydown', handleKeydown);
});

import { onUnmounted } from 'vue';

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});

const handleKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault();
        save();
    }
    if (e.key === 'Escape') {
        e.preventDefault();
        emit('close');
    }
};
</script>

<style scoped>
.animate-fade-in-down {
    animation: fadeInDown 0.3s ease-out;
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
