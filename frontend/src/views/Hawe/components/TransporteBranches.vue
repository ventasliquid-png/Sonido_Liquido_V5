<template>
  <div class="space-y-3">
    <!-- List -->
    <div v-if="loading" class="text-center py-6">
        <i class="fas fa-spinner fa-spin text-cyan-500 text-xl"></i>
    </div>
    <div v-else-if="nodos.length === 0" class="text-center py-6 text-white/30 text-sm border-2 border-dashed border-white/5 rounded-lg">
        No hay sucursales cargadas.
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div 
            v-for="nodo in nodos" 
            :key="nodo.id" 
            class="bg-black/40 border border-white/10 rounded-lg p-3 hover:border-cyan-500/30 transition-colors group relative"
        >
            <div class="flex justify-between items-start mb-2">
                <h4 class="font-bold text-white text-sm truncate pr-6">{{ nodo.nombre_nodo }}</h4>
                <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity absolute top-3 right-3">
                    <button @click="$emit('edit', nodo)" class="text-white/40 hover:text-cyan-400" title="Editar"><i class="fas fa-pencil"></i></button>
                    <button @click="deleteNodo(nodo)" class="text-white/40 hover:text-red-400" title="Eliminar"><i class="fas fa-trash"></i></button>
                </div>
            </div>
            
            <p class="text-xs text-white/50 mb-1 truncate">
                 <i class="fas fa-map-marker-alt w-4 text-center"></i>
                 {{ nodo.localidad || '---' }} <span v-if="nodo.provincia_id">({{ nodo.provincia_id }})</span>
            </p>
            <p class="text-xs text-white/50 mb-2 truncate">
                 <i class="fas fa-location-arrow w-4 text-center"></i>
                 {{ nodo.direccion_completa || 'Sin dirección' }}
            </p>

            <div class="flex flex-wrap gap-1 mt-auto pt-2 border-t border-white/5">
                <span v-if="nodo.es_punto_despacho" class="text-[10px] bg-blue-900/30 text-blue-300 px-1.5 py-0.5 rounded border border-blue-500/20">Despacho</span>
                <span v-if="nodo.es_punto_retiro" class="text-[10px] bg-emerald-900/30 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-500/20">Retiro</span>
                <span v-if="!nodo.es_punto_despacho && !nodo.es_punto_retiro" class="text-[10px] bg-white/5 text-white/30 px-1.5 py-0.5 rounded">Sin Servicios</span>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useLogisticaStore } from '../../../stores/logistica';
import { useNotificationStore } from '../../../stores/notification';

const props = defineProps({
    transportId: {
        type: String,
        required: true
    }
});

const emit = defineEmits(['edit']);

const store = useLogisticaStore();
const notification = useNotificationStore();
const nodos = ref([]);
const loading = ref(false);

const loadNodos = async () => {
    if (!props.transportId) return;
    loading.value = true;
    try {
        nodos.value = await store.fetchNodos(props.transportId);
    } catch (e) {
        console.error(e);
    } finally {
        loading.value = false;
    }
};

const deleteNodo = async (nodo) => {
    if (!confirm(`¿Eliminar sucursal ${nodo.nombre_nodo}?`)) return;
    try {
        await store.deleteNodo(nodo.id);
        notification.add('Sucursal eliminada', 'success');
        nodos.value = nodos.value.filter(n => n.id !== nodo.id);
    } catch (e) {
        notification.add('Error al eliminar', 'error');
    }
};

watch(() => props.transportId, () => {
    loadNodos();
});

onMounted(() => {
    loadNodos();
});

// Expose reload for parent
defineExpose({ reload: loadNodos });
</script>
