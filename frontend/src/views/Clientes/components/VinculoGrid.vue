<script setup>
import { ref, onMounted, watch } from 'vue';
import clientesService from '../../../services/clientes';

const props = defineProps({
    clienteId: {
        type: String,
        default: null
    }
});

const vinculos = ref([]);
const loading = ref(false);

const fetchVinculos = async () => {
    if (!props.clienteId) return;
    loading.value = true;
    try {
        const response = await clientesService.getById(props.clienteId);
        vinculos.value = response.data.vinculos || [];
    } catch (error) {
        console.error("Error fetching vinculos", error);
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    if (props.clienteId) {
        fetchVinculos();
    }
});

watch(() => props.clienteId, (newVal) => {
    if (newVal) fetchVinculos();
    else vinculos.value = [];
});

const handleDelete = async (id) => {
    if (!confirm('¿Eliminar vínculo?')) return;
    try {
        await clientesService.deleteVinculo(props.clienteId, id);
        await fetchVinculos();
    } catch (error) {
        alert('Error al eliminar');
    }
};
</script>

<template>
    <div class="p-4">
        <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-200">Agenda / Contactos</h3>
            <button class="bg-brand hover:bg-green-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                :disabled="!clienteId"
            >
                + Nuevo Contacto
            </button>
        </div>

        <div v-if="!clienteId" class="text-gray-500 italic text-center py-4">
            Guarde el cliente para gestionar contactos.
        </div>

        <div v-else-if="loading" class="text-gray-400 text-center py-4">
            Cargando...
        </div>

        <div v-else class="grid gap-4">
            <div v-for="vin in vinculos" :key="vin.id" class="bg-gray-800 p-3 rounded border border-gray-700 flex justify-between items-start">
                <div>
                    <p class="font-medium text-gray-200">{{ vin.persona?.nombre_completo || 'Desconocido' }}</p>
                    <p class="text-sm text-gray-400">{{ vin.tipo_contacto_id }}</p>
                    <p class="text-xs text-gray-500 mt-1">{{ vin.email_laboral }}</p>
                </div>
                <button @click="handleDelete(vin.id)" class="text-red-400 hover:text-red-300 text-sm">
                    Eliminar
                </button>
            </div>
             <div v-if="vinculos.length === 0" class="text-gray-500 text-center py-2">
                No hay contactos registrados.
            </div>
        </div>
    </div>
</template>
