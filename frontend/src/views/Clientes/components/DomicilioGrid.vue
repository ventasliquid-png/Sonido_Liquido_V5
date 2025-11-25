<script setup>
import { ref, onMounted, watch } from 'vue';
import clientesService from '../../../services/clientes';

const props = defineProps({
    clienteId: {
        type: String,
        default: null
    }
});

const domicilios = ref([]);
const loading = ref(false);

const fetchDomicilios = async () => {
    if (!props.clienteId) return;
    loading.value = true;
    try {
        // Asumimos que el cliente ya viene con domicilios o hay un endpoint específico.
        // El endpoint getById trae los domicilios.
        // Si quisieramos recargar solo domicilios, necesitariamos un endpoint especifico o re-consultar el cliente.
        // Por simplicidad, usaremos el servicio getById del padre o consultaremos aqui si es necesario.
        // PERO, el servicio clientes.js tiene createDomicilio, etc.
        // Vamos a re-consultar el cliente para tener la data fresca o emitir evento al padre.
        // Mejor: El padre le pasa la lista de domicilios? O este componente se encarga?
        // "Componente hijo DomicilioGrid. (CRUD de Domicilios)." -> Suena a que se encarga.
        const response = await clientesService.getById(props.clienteId);
        domicilios.value = response.data.domicilios || [];
    } catch (error) {
        console.error("Error fetching domicilios", error);
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    if (props.clienteId) {
        fetchDomicilios();
    }
});

watch(() => props.clienteId, (newVal) => {
    if (newVal) fetchDomicilios();
    else domicilios.value = [];
});

const handleDelete = async (id) => {
    if (!confirm('¿Eliminar domicilio?')) return;
    try {
        await clientesService.deleteDomicilio(props.clienteId, id);
        await fetchDomicilios();
    } catch (error) {
        alert('Error al eliminar');
    }
};

// TODO: Implementar Modal de Creación/Edición de Domicilio real.
// Por ahora, solo listado y borrado para cumplir Fase 1.
</script>

<template>
    <div class="h-full flex flex-col">
        <div class="flex justify-between items-center mb-4 px-1">
            <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider">Domicilios Registrados</h3>
            <button class="bg-[#54cb9b] hover:bg-[#45b085] text-white px-3 py-1.5 rounded text-xs font-bold shadow-sm transition-colors flex items-center gap-1"
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
                <button @click="handleDelete(dom.id)" class="text-gray-300 hover:text-red-500 transition-colors p-1" title="Eliminar">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </div>
            <div v-if="domicilios.length === 0" class="text-gray-400 text-center py-8 text-sm bg-gray-50 rounded-lg border border-gray-100">
                No hay domicilios registrados.
            </div>
        </div>
    </div>
</template>
