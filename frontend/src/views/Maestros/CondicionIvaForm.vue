<script setup>
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue';
import { useMaestrosStore } from '../../stores/maestros';

const props = defineProps({
    show: Boolean,
    id: {
        type: [String, Number], // UUID is string in JS
        default: null
    }
});

const emit = defineEmits(['close', 'saved']);

const store = useMaestrosStore();
const isEditing = ref(false);

const form = reactive({
    nombre: ''
});

watch(() => props.show, (newVal) => {
    if (newVal) {
        if (props.id) {
            isEditing.value = true;
            const condicion = store.condicionesIva.find(c => c.id === props.id);
            if (condicion) {
                form.nombre = condicion.nombre;
            }
        } else {
            isEditing.value = false;
            form.nombre = '';
        }
    }
});

const handleSave = async () => {
    try {
        let result;
        if (isEditing.value) {
            result = await store.updateCondicionIva(props.id, form);
        } else {
            result = await store.createCondicionIva(form);
        }
        emit('saved', result);
        emit('close');
    } catch (error) {
        alert('Error al guardar la condición de IVA.');
        console.error(error);
    }
};

const close = () => {
    emit('close');
};

// Keyboard Shortcuts
const handleKeydown = (e) => {
    if (!props.show) return;
    if (e.key === 'Escape') close();
    if (e.key === 'F10') {
        e.preventDefault();
        handleSave();
    }
};

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
    <div v-if="show" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-[60] flex items-center justify-center">
        <div class="relative mx-auto p-5 border w-96 shadow-lg rounded-md bg-white animate-scale-in">
            <div class="mt-3">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">{{ isEditing ? 'Editar Condición IVA' : 'Nueva Condición IVA' }}</h3>
                <form @submit.prevent="handleSave">
                    <div class="mb-4">
                        <label class="block text-gray-700 text-sm font-bold mb-2">Nombre</label>
                        <input v-model="form.nombre" type="text" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b]">
                    </div>
                    <div class="flex justify-end gap-2 mt-4">
                        <button type="button" @click="close" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 text-sm font-bold">Cancelar (ESC)</button>
                        <button type="submit" class="px-4 py-2 bg-[#54cb9b] text-white rounded hover:bg-[#45b085] text-sm font-bold">Guardar (F10)</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<style scoped>
.animate-scale-in {
    animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}
</style>
