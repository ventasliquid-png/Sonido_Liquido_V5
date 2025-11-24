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
    <div class="p-4">
        <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-200">Domicilios</h3>
            <button class="bg-brand hover:bg-green-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                :disabled="!clienteId"
                title="Guarde el cliente primero"
            >
                + Nuevo Domicilio
            </button>
        </div>

        <div v-if="!clienteId" class="text-gray-500 italic text-center py-4">
            Guarde el cliente para gestionar domicilios.
        </div>

        <div v-else-if="loading" class="text-gray-400 text-center py-4">
            Cargando...
        </div>

        <div v-else class="grid gap-4">
            <div v-for="dom in domicilios" :key="dom.id" class="bg-gray-800 p-3 rounded border border-gray-700 flex justify-between items-start">
                <div>
                    <p class="font-medium text-gray-200">{{ dom.calle }} {{ dom.numero }}</p>
                    <p class="text-sm text-gray-400">{{ dom.localidad }}</p>
                    <div class="flex gap-2 mt-2">
                        <span v-if="dom.es_fiscal" class="text-xs bg-blue-900 text-blue-200 px-2 py-0.5 rounded">Fiscal</span>
                        <span v-if="dom.es_entrega" class="text-xs bg-green-900 text-green-200 px-2 py-0.5 rounded">Entrega</span>
                    </div>
                </div>
                <button @click="handleDelete(dom.id)" class="text-red-400 hover:text-red-300 text-sm">
                    Eliminar
                </button>
            </div>
            <div v-if="domicilios.length === 0" class="text-gray-500 text-center py-2">
                No hay domicilios registrados.
            </div>
        </div>
    </div>
</template>
