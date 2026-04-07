// [IDENTIDAD] - frontend\src\views\Logistica\components\TransporteAbmModal.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

<template>
    <!-- BRIDGE TO SOBERANÍA: Replaces legacy modal with the Sovereign Canvas -->
    <TransporteCanvas 
        v-if="show"
        v-model="internalModel"
        @close="$emit('close')"
        @save="handleSaved"
    />
</template>

<script setup>
import { ref, watch } from 'vue';
import TransporteCanvas from './TransporteCanvas.vue';

const props = defineProps({
    show: Boolean,
    initialName: {
        type: String,
        default: ''
    }
});

const emit = defineEmits(['close', 'saved']);

const internalModel = ref({
    id: null,
    nombre: props.initialName,
    flags_estado: 3, // Existence + Active
    activo: true
});

watch(() => props.show, (val) => {
    if (val) {
        internalModel.value = {
            id: null,
            nombre: props.initialName || '',
            flags_estado: 3,
            activo: true
        };
    }
});

const handleSaved = () => {
    emit('saved', internalModel.value.nombre);
};
</script>
