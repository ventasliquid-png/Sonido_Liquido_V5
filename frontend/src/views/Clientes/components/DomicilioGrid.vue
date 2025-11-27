<script setup>
import { ref, onMounted, watch } from 'vue';
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

const domicilios = ref([]);
const loading = ref(false);
const transportes = ref([]);
const transportesHabituales = ref([]);
const showForm = ref(false);
const showTransporteForm = ref(false);
const isEditing = ref(false);

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

onMounted(() => {
    if (props.clienteId) {
        fetchDomicilios();
    }
    fetchMaestros();
});

watch(() => props.clienteId, (newVal) => {
    if (newVal) fetchDomicilios();
    else domicilios.value = [];
});

const openForm = async (domicilio = null) => {
    await fetchHabituales();
    if (domicilio) {
        isEditing.value = true;
        formData.value = { ...domicilio, transporte_id: domicilio.transporte_habitual_nodo_id };
    } else {
        isEditing.value = false;
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
            es_fiscal: false,
            es_entrega: true,
            observaciones: ''
        };
        // Default Transport (ID 1 or first available)
        if (transportes.value.length > 0) {
            // Try to find "Retiro en Local" or use first
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
    if (!formData.value.calle || !formData.value.numero || !formData.value.localidad) {
        alert('Complete los campos obligatorios (Calle, Número, Localidad)');
        return;
    }

    try {
        if (isEditing.value) {
            await clientesService.updateDomicilio(props.clienteId, formData.value.id, formData.value);
        } else {
            await clientesService.createDomicilio(props.clienteId, formData.value);
        }
        await fetchDomicilios();
        closeForm();
    } catch (error) {
        console.error("Error saving domicilio", error);
        alert('Error al guardar domicilio');
    }
};

const handleDelete = async (id) => {
    if (!confirm('¿Eliminar domicilio?')) return;
    try {
        await clientesService.deleteDomicilio(props.clienteId, id);
        await fetchDomicilios();
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
    formData.value.transporte_id = newTransporte.id;
    showTransporteForm.value = false;
};
</script>

<template>
    <div class="h-full flex flex-col relative">
        <div class="flex justify-between items-center mb-4 px-1">
            <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider">Domicilios Registrados</h3>
            <button 
                @click="openForm()"
                class="bg-[#54cb9b] hover:bg-[#45b085] text-white px-3 py-1.5 rounded text-xs font-bold shadow-sm transition-colors flex items-center gap-1"
                :disabled="!clienteId"
                title="Guarde el cliente primero"
            >
                <span>+</span> Nuevo Domicilio
            </button>
        </div>

        <div v-if="!clienteId" class="flex-1 flex items-center justify-center text-gray-400 italic text-sm border-2 border-dashed border-gray-200 rounded-lg bg-gray-50">
            Guarde el cliente para gestionar domicilios.
        </div>

        <div v-else-if="loading" class="flex-1 flex items-center justify-center text-gray-400 text-sm">
            <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-[#54cb9b] mr-2"></div> Cargando...
        </div>

        <div v-else class="grid gap-3 overflow-y-auto pr-1">
            <div v-for="dom in domicilios" :key="dom.id" class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex justify-between items-start hover:border-[#54cb9b]/50 transition-colors group">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="font-bold text-gray-800 text-sm">{{ dom.calle }} {{ dom.numero }}</span>
                        <div class="flex gap-1">
                            <span v-if="dom.es_fiscal" class="text-[10px] font-bold bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded border border-blue-200">FISCAL</span>
                            <span v-if="dom.es_entrega" class="text-[10px] font-bold bg-green-100 text-green-700 px-1.5 py-0.5 rounded border border-green-200">ENTREGA</span>
                        </div>
                    </div>
                    <p class="text-xs text-gray-500">{{ dom.localidad }} <span v-if="dom.cp">({{ dom.cp }})</span></p>
                    <p v-if="dom.piso || dom.depto" class="text-xs text-gray-400 mt-0.5">Piso: {{ dom.piso || '-' }} | Dpto: {{ dom.depto || '-' }}</p>
                </div>
                <div class="flex gap-2">
                    <button @click="openForm(dom)" class="text-gray-300 hover:text-blue-500 transition-colors p-1" title="Editar">
                        ✏️
                    </button>
                    <button @click="handleDelete(dom.id)" class="text-gray-300 hover:text-red-500 transition-colors p-1" title="Eliminar">
                        🗑️
                    </button>
                </div>
            </div>
            <div v-if="domicilios.length === 0" class="text-gray-400 text-center py-8 text-sm bg-gray-50 rounded-lg border border-gray-100">
                No hay domicilios registrados.
            </div>
        </div>

        <!-- MODAL DOMICILIO -->
        <div v-if="showForm" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div class="bg-white w-full max-w-2xl rounded-lg shadow-2xl overflow-hidden animate-scale-in">
                <div class="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
                    <h3 class="font-bold text-gray-800">{{ isEditing ? 'Editar Domicilio' : 'Nuevo Domicilio' }}</h3>
                    <button @click="closeForm" class="text-gray-400 hover:text-gray-600">✕</button>
                </div>
                <div class="p-6 grid grid-cols-12 gap-4">
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
                    <div class="col-span-12">
                        <SmartSelect 
                            label="Transporte (Obligatorio)"
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
                    <div class="col-span-12 flex gap-4 mt-2">
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
                    <button @click="handleSave" class="px-4 py-2 bg-[#54cb9b] text-white font-bold text-sm hover:bg-[#45b085] rounded shadow-sm transition-colors">Guardar Domicilio</button>
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
