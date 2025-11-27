<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import clientesService from '../../../services/clientes';
import maestrosService from '../../../services/maestros';
import SmartSelect from '../../../components/ui/SmartSelect.vue';
import TransporteForm from '../../Logistica/TransporteForm.vue';

const props = defineProps({
    clienteId: {
        type: String,
        default: null
    }
});

const emit = defineEmits(['change']);

const domicilios = ref([]);
const loading = ref(false);
const transportes = ref([]);
const transportesHabituales = ref([]);
const showForm = ref(false);
const showTransporteForm = ref(false);
const isEditing = ref(false);
const formMode = ref(''); // 'FISCAL' | 'ENTREGA'

const formData = ref({
    id: null,
    calle: '',
    numero: '',
    piso: '',
    depto: '',
    localidad: '',
    cp: '',
    provincia: '', // ID
    transporte_id: null,
    intermediario_id: null,
    es_fiscal: false,
    es_entrega: true,
    observaciones: ''
});

const provincias = ref([]);

// Computed
const domicilioFiscal = computed(() => domicilios.value.find(d => d.es_fiscal));
const domiciliosEntrega = computed(() => domicilios.value.filter(d => d.es_entrega && !d.es_fiscal));

const getTransporteName = (id) => {
    if (!id) return 'RETIRO EN LOCAL';
    const t = transportes.value.find(t => t.id === id);
    return t ? t.nombre : 'RETIRO EN LOCAL';
};

const fetchDomicilios = async () => {
    if (!props.clienteId) return;
    loading.value = true;
    try {
        const response = await clientesService.getById(props.clienteId);
        domicilios.value = response.data.domicilios || [];
    } catch (error) {
        console.error("Error fetching domicilios", error);
    } finally {
        loading.value = false;
    }
};

const fetchMaestros = async () => {
    try {
        const [transRes, provRes] = await Promise.all([
            maestrosService.getTransportes(),
            maestrosService.getProvincias()
        ]);
        transportes.value = transRes.data;
        provincias.value = provRes.data;
    } catch (error) {
        console.error("Error loading maestros", error);
    }
};

const fetchHabituales = async () => {
    if (!props.clienteId) return;
    try {
        const res = await clientesService.getTransportesHabituales(props.clienteId);
        transportesHabituales.value = res.data;
    } catch (error) {
        console.error("Error loading habituales", error);
    }
};



watch(() => props.clienteId, (newVal) => {
    if (newVal) fetchDomicilios();
    else domicilios.value = [];
});

const openForm = async (domicilio = null, mode = 'ENTREGA') => {
    await fetchHabituales();
    formMode.value = mode;
    
    if (domicilio) {
        isEditing.value = true;
        formData.value = { 
            ...domicilio, 
            transporte_id: domicilio.transporte_habitual_nodo_id,
            provincia: domicilio.provincia_id 
        };
        // Force flags based on mode if needed, but usually we respect existing
        if (mode === 'FISCAL') formData.value.es_fiscal = true;
    } else {
        isEditing.value = false;
        
        // Pre-fill logic
        let prefill = {};
        if (mode === 'ENTREGA' && domicilioFiscal.value) {
            // Copy address from Fiscal
            const { id, es_fiscal, es_entrega, transporte_habitual_nodo_id, provincia_id, ...rest } = domicilioFiscal.value;
            prefill = { 
                ...rest, 
                provincia: provincia_id,
                transporte_id: transporte_habitual_nodo_id // Copy transport from Fiscal
            };
        }

        formData.value = {
            id: null,
            calle: '',
            numero: '',
            piso: '',
            depto: '',
            localidad: '',
            cp: '',
            provincia: '',
            transporte_id: null,
            intermediario_id: null,
            es_fiscal: mode === 'FISCAL',
            es_entrega: true,
            observaciones: '',
            ...prefill
        };

        // Default Transport (ID 1 or first available) if not prefilled
        if (!formData.value.transporte_id && transportes.value.length > 0) {
            const retiro = transportes.value.find(t => t.nombre.toLowerCase().includes('retiro'));
            formData.value.transporte_id = retiro ? retiro.id : transportes.value[0].id;
        }
    }
    showForm.value = true;
};

const closeForm = () => {
    showForm.value = false;
};

const handleSave = async () => {
    const errors = [];
    if (!formData.value.calle) errors.push('Calle');
    if (!formData.value.numero) errors.push('Número');
    if (!formData.value.localidad) errors.push('Localidad');
    
    // Auto-fill Transport if missing
    if (!formData.value.transporte_id) {
        console.log("Auto-filling transport. Available:", transportes.value.length);
        // Try to find "Retiro..." or "Local"
        let defaultTransport = transportes.value.find(t => {
            const name = (t.nombre || '').toLowerCase();
            return name.includes('retir') || name.includes('local');
        });

        // If not found, fallback to the first one in the list (better than blocking)
        if (!defaultTransport && transportes.value.length > 0) {
            console.log("No match found, using first available.");
            defaultTransport = transportes.value[0];
        }

        if (defaultTransport) {
            console.log("Selected default:", defaultTransport.nombre);
            formData.value.transporte_id = defaultTransport.id;
        } else {
            console.error("No transports available to auto-fill.");
            errors.push('Transporte (No hay transportes disponibles)');
        }
    }

    if (errors.length > 0) {
        alert(`Faltan datos obligatorios: ${errors.join(', ')}`);
        return;
    }

    try {
        if (isEditing.value) {
            await clientesService.updateDomicilio(props.clienteId, formData.value.id, formData.value);
        } else {
            await clientesService.createDomicilio(props.clienteId, formData.value);
        }
        await fetchDomicilios();
        emit('change');
        closeForm();
    } catch (error) {
        console.error("Error saving domicilio", error);
        alert('Error al guardar domicilio. Verifique los datos e intente nuevamente.');
    }
};

const handleDelete = async (id) => {
    if (!confirm('¿Eliminar domicilio?')) return;
    try {
        await clientesService.deleteDomicilio(props.clienteId, id);
        await fetchDomicilios();
        emit('change');
    } catch (error) {
        alert('Error al eliminar');
    }
};

const handleCreateTransporte = () => {
    showTransporteForm.value = true;
};

const onTransporteSaved = async (newTransporte) => {
    const res = await maestrosService.getTransportes();
    transportes.value = res.data;
    // Ensure the list is updated before setting the value so SmartSelect can find it
    setTimeout(() => {
        formData.value.transporte_id = newTransporte.id;
    }, 100);
    showTransporteForm.value = false;
};

const isFormOpen = computed(() => showForm.value);

const handleKeydown = (e) => {
    if (!showForm.value) return;
    if (e.key === 'F10') {
        e.preventDefault();
        e.stopImmediatePropagation();
        handleSave();
    }
    if (e.key === 'Escape') {
        e.preventDefault();
        e.stopImmediatePropagation();
        closeForm();
    }
};

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
    if (props.clienteId) {
        fetchDomicilios();
    }
    fetchMaestros();
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});

// Expose openForm and state for parent component
defineExpose({ openForm, isFormOpen });
</script>

<template>
    <div class="h-full flex flex-col relative bg-gray-50/50">
        
        <div v-if="loading" class="flex-1 flex items-center justify-center text-gray-400 text-sm">
            <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-[#54cb9b] mr-2"></div> Cargando...
        </div>

        <div v-else class="flex-1 overflow-y-auto p-4 space-y-6">
            
            <!-- SECTION 1: FISCAL ADDRESS -->
            <div class="bg-white rounded-lg border border-blue-100 shadow-sm overflow-hidden">
                <div class="bg-blue-50 px-4 py-2 border-b border-blue-100 flex justify-between items-center">
                    <h3 class="text-xs font-bold text-blue-800 uppercase tracking-wider flex items-center gap-2">
                        <span>🏛️</span> Domicilio Fiscal (Obligatorio)
                    </h3>
                    <button 
                        v-if="!domicilioFiscal"
                        @click="openForm(null, 'FISCAL')"
                        class="text-[10px] bg-blue-600 text-white px-2 py-1 rounded font-bold hover:bg-blue-700 transition-colors"
                    >
                        + AGREGAR
                    </button>
                </div>
                
                <div class="p-4">
                    <div v-if="domicilioFiscal" class="flex justify-between items-start">
                        <div>
                            <p class="font-bold text-gray-800 text-sm">{{ domicilioFiscal.calle }} {{ domicilioFiscal.numero }}</p>
                            <p class="text-xs text-gray-500">{{ domicilioFiscal.localidad }} <span v-if="domicilioFiscal.cp">({{ domicilioFiscal.cp }})</span></p>
                            <p v-if="domicilioFiscal.piso || domicilioFiscal.depto" class="text-xs text-gray-400 mt-0.5">
                                Piso: {{ domicilioFiscal.piso || '-' }} | Dpto: {{ domicilioFiscal.depto || '-' }}
                            </p>
                            <p class="text-[10px] text-gray-400 mt-2">Provincia: {{ provincias.find(p => p.id === domicilioFiscal.provincia_id)?.nombre || 'No definida' }}</p>
                        </div>
                        <button 
                            @click="openForm(domicilioFiscal, 'FISCAL')"
                            class="text-gray-400 hover:text-blue-600 transition-colors p-1 bg-gray-50 rounded hover:bg-blue-50"
                            title="Editar Domicilio Fiscal"
                        >
                            ✏️ EDITAR
                        </button>
                    </div>
                    <div v-else class="text-center py-6 border-2 border-dashed border-blue-100 rounded bg-blue-50/30">
                        <p class="text-sm font-bold text-blue-300">No hay Domicilio Fiscal definido</p>
                        <p class="text-xs text-gray-400">Es necesario para la facturación.</p>
                    </div>
                </div>
            </div>

            <!-- SECTION 2: DELIVERY ADDRESSES -->
            <div class="bg-white rounded-lg border border-green-100 shadow-sm overflow-hidden">
                <div class="bg-green-50 px-4 py-2 border-b border-green-100 flex justify-between items-center">
                    <h3 class="text-xs font-bold text-green-800 uppercase tracking-wider flex items-center gap-2">
                        <span>🚚</span> Domicilios de Entrega
                    </h3>
                    <button 
                        @click="openForm(null, 'ENTREGA')"
                        class="text-[10px] bg-green-600 text-white px-2 py-1 rounded font-bold hover:bg-green-700 transition-colors"
                    >
                        + NUEVO DESTINO
                    </button>
                </div>

                <div class="divide-y divide-gray-100">
                    <div v-for="dom in domiciliosEntrega" :key="dom.id" class="p-4 hover:bg-gray-50 transition-colors flex justify-between items-start group">
                        <div>
                            <div class="flex items-center gap-2">
                                <span class="font-bold text-gray-800 text-sm">{{ dom.calle }} {{ dom.numero }}</span>
                                <span v-if="dom.es_fiscal" class="text-[10px] bg-gray-100 text-gray-500 px-1.5 rounded border border-gray-200">FISCAL</span>
                            </div>
                            <p class="text-xs text-gray-500">{{ dom.localidad }} <span v-if="dom.cp">({{ dom.cp }})</span></p>
                            <div class="mt-2 flex items-center gap-2">
                                <span class="text-[10px] text-gray-400 uppercase tracking-wide">Transporte:</span>
                                <span class="text-[10px] font-bold bg-green-50 text-green-700 px-2 py-0.5 rounded border border-green-100">
                                    {{ getTransporteName(dom.transporte_id) }}
                                </span>
                            </div>
                        </div>
                        <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button @click="openForm(dom, 'ENTREGA')" class="text-gray-400 hover:text-blue-600 transition-colors p-1" title="Editar">
                                ✏️
                            </button>
                            <button @click="handleDelete(dom.id)" class="text-gray-400 hover:text-red-500 transition-colors p-1" title="Eliminar">
                                🗑️
                            </button>
                        </div>
                    </div>
                    
                    <div v-if="domiciliosEntrega.length === 0" class="text-center py-8 text-gray-400 text-sm italic">
                        No hay direcciones de entrega adicionales.
                        <br>
                        <span class="text-xs opacity-70" v-if="domicilioFiscal?.es_entrega">(Se usará el Domicilio Fiscal)</span>
                    </div>
                </div>
            </div>

        </div>

        <!-- MODAL DOMICILIO -->
        <div v-if="showForm" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div class="bg-white w-full max-w-2xl rounded-lg shadow-2xl overflow-hidden animate-scale-in">
                <div class="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
                    <h3 class="font-bold text-gray-800 flex items-center gap-2">
                        <span v-if="formMode === 'FISCAL'">🏛️ Editar Domicilio Fiscal</span>
                        <span v-else>🚚 {{ isEditing ? 'Editar Destino' : 'Nuevo Destino de Entrega' }}</span>
                    </h3>
                    <button @click="closeForm" class="text-gray-400 hover:text-gray-600">✕</button>
                </div>
                
                <div class="p-6 grid grid-cols-12 gap-4">
                    <!-- ADDRESS FIELDS -->
                    <div class="col-span-8">
                        <label class="block text-xs font-bold text-gray-600 mb-1">Calle *</label>
                        <input v-model="formData.calle" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                    </div>
                    <div class="col-span-4">
                        <label class="block text-xs font-bold text-gray-600 mb-1">Número *</label>
                        <input v-model="formData.numero" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                    </div>
                    <div class="col-span-3">
                        <label class="block text-xs font-bold text-gray-600 mb-1">Piso</label>
                        <input v-model="formData.piso" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                    </div>
                    <div class="col-span-3">
                        <label class="block text-xs font-bold text-gray-600 mb-1">Depto</label>
                        <input v-model="formData.depto" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                    </div>
                    <div class="col-span-6">
                        <label class="block text-xs font-bold text-gray-600 mb-1">CP</label>
                        <input v-model="formData.cp" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                    </div>
                    <div class="col-span-6">
                        <label class="block text-xs font-bold text-gray-600 mb-1">Localidad *</label>
                        <input v-model="formData.localidad" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                    </div>
                    <div class="col-span-6">
                        <label class="block text-xs font-bold text-gray-600 mb-1">Provincia</label>
                        <select v-model="formData.provincia" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none bg-white">
                            <option value="">Seleccionar...</option>
                            <option v-for="p in provincias" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                        </select>
                    </div>

                    <!-- TRANSPORT FIELDS -->
                    <div class="col-span-12 pt-4 border-t border-gray-100">
                        <SmartSelect 
                            label="Transporte Habitual"
                            v-model="formData.transporte_id"
                            :options="transportes"
                            :priorityIds="transportesHabituales"
                            @create-new="handleCreateTransporte"
                        />
                    </div>
                    <div class="col-span-12">
                        <SmartSelect 
                            label="Intermediario / Redespacho (Opcional)"
                            v-model="formData.intermediario_id"
                            :options="transportes"
                            @create-new="handleCreateTransporte"
                        />
                    </div>

                    <!-- FLAGS (HIDDEN/READONLY based on mode) -->
                    <div class="col-span-12 flex gap-4 mt-2 bg-gray-50 p-3 rounded border border-gray-100" v-if="false"> 
                        <!-- Hidden as per user request to simplify, logic handles it -->
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input v-model="formData.es_entrega" type="checkbox" class="form-checkbox h-4 w-4 text-[#54cb9b] rounded border-gray-300 focus:ring-[#54cb9b]">
                            <span class="text-sm text-gray-700">Es punto de entrega</span>
                        </label>
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input v-model="formData.es_fiscal" type="checkbox" class="form-checkbox h-4 w-4 text-blue-500 rounded border-gray-300 focus:ring-blue-500">
                            <span class="text-sm text-gray-700">Es domicilio fiscal</span>
                        </label>
                    </div>
                </div>
                <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end gap-3">
                    <button @click="closeForm" class="px-4 py-2 text-gray-600 font-bold text-sm hover:bg-gray-200 rounded transition-colors">Cancelar</button>
                    <button @click="handleSave" class="px-4 py-2 bg-[#54cb9b] text-white font-bold text-sm hover:bg-[#45b085] rounded shadow-sm transition-colors">
                        {{ isEditing ? 'Guardar Cambios' : 'Crear Domicilio' }}
                    </button>
                </div>
            </div>
        </div>

        <TransporteForm 
            :show="showTransporteForm" 
            @close="showTransporteForm = false" 
            @saved="onTransporteSaved"
        />
    </div>
</template>
