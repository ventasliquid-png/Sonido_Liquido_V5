// [IDENTIDAD] - frontend\src\views\Logistica\components\TransporteBranches.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

<template>
  <div class="space-y-3">
    <!-- List -->
    <div v-if="loading" class="text-center py-6">
        <i class="fas fa-spinner fa-spin text-emerald-500 text-xl"></i>
    </div>
    <div v-else-if="nodos.length === 0" class="text-center py-6 text-white/30 text-[10px] uppercase font-bold tracking-widest border border-dashed border-white/5 rounded-xl bg-white/2">
        No hay sucursales o destinos configurados.
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div 
            v-for="nodo in nodos" 
            :key="nodo.id" 
            class="bg-black/40 border border-white/10 rounded-xl p-4 hover:border-emerald-500/30 transition-all group relative overflow-hidden"
        >
            <div class="absolute top-0 right-0 w-16 h-16 bg-emerald-500/5 rounded-bl-full -mr-8 -mt-8 group-hover:bg-emerald-500/10 transition-colors"></div>
            
            <div class="flex justify-between items-start mb-2 relative z-10">
                <h4 class="font-bold text-white text-xs uppercase tracking-wider truncate pr-8">{{ nodo.nombre_nodo }}</h4>
                <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity absolute top-0 right-0">
                    <button @click="$emit('edit', nodo)" class="text-white/40 hover:text-emerald-400" title="Editar"><i class="fas fa-pencil-alt text-[10px]"></i></button>
                    <button @click="deleteNodo(nodo)" class="text-white/40 hover:text-red-400" title="Eliminar"><i class="fas fa-trash text-[10px]"></i></button>
                </div>
            </div>
            
            <div class="space-y-1 relative z-10">
                <p class="text-[10px] text-white/40 font-mono truncate">
                     <i class="fas fa-map-marker-alt mr-2 text-emerald-500/50"></i>
                     {{ nodo.localidad || '---' }} <span v-if="nodo.provincia_id" class="text-emerald-500/30">[{{ nodo.provincia_id }}]</span>
                </p>
                <p class="text-[10px] text-white/40 truncate">
                     <i class="fas fa-location-arrow mr-2 text-emerald-500/50"></i>
                     {{ nodo.direccion_completa || 'Sin dirección' }}
                </p>
            </div>

            <div class="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-white/5 relative z-10">
                <span v-if="nodo.es_punto_despacho" class="text-[9px] font-black bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded border border-blue-500/20 uppercase">Envío</span>
                <span v-if="nodo.es_punto_retiro" class="text-[9px] font-black bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 uppercase">Retiro</span>
                <span v-if="!nodo.es_punto_despacho && !nodo.es_punto_retiro" class="text-[9px] font-black bg-white/5 text-white/20 px-2 py-0.5 rounded uppercase">Inactivo</span>
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

defineExpose({ reload: loadNodos });
</script>
