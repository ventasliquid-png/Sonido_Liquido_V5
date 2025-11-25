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
    <div class="h-full flex flex-col">
        <div class="flex justify-between items-center mb-4 px-1">
            <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider">Agenda / Contactos</h3>
            <button class="bg-[#54cb9b] hover:bg-[#45b085] text-white px-3 py-1.5 rounded text-xs font-bold shadow-sm transition-colors flex items-center gap-1"
                :disabled="!clienteId"
            >
                <span>+</span> Nuevo Contacto
            </button>
        </div>

        <div v-if="!clienteId" class="flex-1 flex items-center justify-center text-gray-400 italic text-sm border-2 border-dashed border-gray-200 rounded-lg bg-gray-50">
            Guarde el cliente para gestionar contactos.
        </div>

        <div v-else-if="loading" class="flex-1 flex items-center justify-center text-gray-400 text-sm">
            <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-[#54cb9b] mr-2"></div> Cargando...
        </div>

        <div v-else class="grid gap-3 overflow-y-auto pr-1">
            <div v-for="vin in vinculos" :key="vin.id" class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex justify-between items-start hover:border-[#54cb9b]/50 transition-colors group">
                <div class="flex items-start gap-3">
                    <div class="bg-gray-100 p-2 rounded-full text-gray-400 group-hover:text-[#54cb9b] group-hover:bg-green-50 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                    </div>
                    <div>
                        <p class="font-bold text-gray-800 text-sm">{{ vin.persona?.nombre_completo || 'Desconocido' }}</p>
                        <p class="text-xs font-bold text-[#54cb9b] uppercase tracking-wide mb-1">{{ vin.tipo_contacto_id }}</p>
                        <p class="text-xs text-gray-500 flex items-center gap-1">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                            {{ vin.email_laboral || 'Sin email' }}
                        </p>
                    </div>
                </div>
                <button @click="handleDelete(vin.id)" class="text-gray-300 hover:text-red-500 transition-colors p-1" title="Eliminar">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </div>
             <div v-if="vinculos.length === 0" class="text-gray-400 text-center py-8 text-sm bg-gray-50 rounded-lg border border-gray-100">
                No hay contactos registrados.
            </div>
        </div>
    </div>
</template>
