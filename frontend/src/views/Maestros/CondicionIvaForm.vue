<script setup>
import { ref, reactive, watch, onMounted, onUnmounted, computed } from 'vue';
import { useMaestrosStore } from '../../stores/maestros';

const props = defineProps({
    show: Boolean,
});

const emit = defineEmits(['close', 'saved']);

const store = useMaestrosStore();
const view = ref('list'); // 'list' | 'form'
const isEditing = ref(false);
const editingId = ref(null);
const searchTerm = ref('');

const form = reactive({
    nombre: ''
});

const condiciones = computed(() => {
    if (!searchTerm.value) return store.condicionesIva;
    return store.condicionesIva.filter(c => 
        c.nombre.toLowerCase().includes(searchTerm.value.toLowerCase())
    );
});

// Watch show to reset
watch(() => props.show, (newVal) => {
    if (newVal) {
        view.value = 'list';
        store.fetchCondicionesIva();
    }
});

const switchToNew = () => {
    isEditing.value = false;
    editingId.value = null;
    form.nombre = '';
    view.value = 'form';
};

const switchToEdit = (item) => {
    isEditing.value = true;
    editingId.value = item.id;
    form.nombre = item.nombre;
    view.value = 'form';
};

const handleSave = async () => {
    try {
        if (isEditing.value) {
            await store.updateCondicionIva(editingId.value, form);
        } else {
            await store.createCondicionIva(form);
        }
        // Instead of closing, go back to list? Or user expects close?
        // Usually ABM stays open.
        view.value = 'list';
        emit('saved'); // Notify parent to refresh list, but stick to manager
    } catch (error) {
        alert('Error al guardar.');
        console.error(error);
    }
};

const handleDelete = async (id) => {
    if (!confirm('¿Seguro que desea eliminar esta condición?')) return;
    try {
        await store.deleteCondicionIva(id);
    } catch (error) {
        console.error(error);
        alert('Error al eliminar. Puede estar en uso.');
    }
};

const close = () => {
    if (view.value === 'form') {
        view.value = 'list';
    } else {
        emit('close');
    }
};

// Keyboard Shortcuts
const handleKeydown = (e) => {
    if (!props.show) return;
    if (e.key === 'Escape') close();
    if (e.key === 'F10' && view.value === 'form') {
        e.preventDefault();
        handleSave();
    }
    if (e.key === 'F4' && view.value === 'list') {
         e.preventDefault();
         switchToNew();
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
    <Teleport to="body">
        <div v-if="show" class="fixed inset-0 bg-gray-900/80 backdrop-blur-sm overflow-y-auto h-full w-full z-[9999] flex items-center justify-center">
            <div class="relative mx-auto border border-cyan-500/30 w-[500px] shadow-2xl rounded-lg bg-[#05151f] text-cyan-100 animate-scale-in overflow-hidden flex flex-col max-h-[80vh]">
                
                <!-- HEADER -->
                <div class="flex justify-between items-center p-4 border-b border-cyan-900/30 bg-[#0a253a]/50">
                    <h3 class="text-lg font-bold text-cyan-100">
                        {{ view === 'list' ? 'Administrar Condiciones IVA' : (isEditing ? 'Editar Condición' : 'Nueva Condición') }}
                    </h3>
                    <button @click="emit('close')" class="text-cyan-500 hover:text-cyan-300">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <!-- LIST VIEW -->
                <div v-if="view === 'list'" class="flex-1 flex flex-col overflow-hidden">
                    <div class="p-4 border-b border-cyan-900/30 flex gap-2">
                         <div class="relative flex-1">
                            <i class="fas fa-search absolute left-3 top-2.5 text-cyan-700/50 text-xs"></i>
                            <input 
                                v-model="searchTerm" 
                                class="w-full bg-cyan-900/10 border border-cyan-900/30 rounded pl-8 pr-2 py-1.5 text-sm text-cyan-100 placeholder-cyan-800 transition-colors focus:border-cyan-500/50 outline-none" 
                                placeholder="Buscar..."
                                autofocus
                            />
                        </div>
                        <button @click="switchToNew" class="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-bold transition-colors shadow-lg shadow-cyan-900/20">
                            <i class="fas fa-plus mr-1"></i> NUEVO (F4)
                        </button>
                    </div>
                    
                    <div class="flex-1 overflow-y-auto p-4 space-y-2">
                        <div v-if="condiciones.length === 0" class="text-center text-cyan-900/50 text-sm py-4">
                            No hay condiciones.
                        </div>
                        <div 
                            v-for="item in condiciones" 
                            :key="item.id"
                            class="flex justify-between items-center p-3 bg-cyan-900/5 hover:bg-cyan-900/10 border border-cyan-900/10 rounded-lg group transition-colors"
                        >
                            <span class="font-medium text-sm">{{ item.nombre }}</span>
                            <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button @click="switchToEdit(item)" class="text-cyan-500 hover:text-cyan-300" title="Editar">
                                    <i class="fas fa-pencil-alt"></i>
                                </button>
                                <button @click="handleDelete(item.id)" class="text-red-500 hover:text-red-400" title="Eliminar">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- FORM VIEW -->
                <div v-if="view === 'form'" class="p-6">
                    <form @submit.prevent="handleSave">
                        <div class="mb-6">
                            <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Nombre</label>
                            <input v-model="form.nombre" type="text" required class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors" placeholder="Ej: Responsable Inscripto" />
                        </div>
                        <div class="flex justify-end gap-3">
                            <button type="button" @click="close" class="px-4 py-2 bg-transparent hover:bg-cyan-900/20 text-cyan-500 text-sm font-bold rounded transition-colors border border-transparent hover:border-cyan-900/30">
                                Volver (ESC)
                            </button>
                            <button type="submit" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-sm font-bold shadow-lg shadow-cyan-900/20 transition-colors">
                                Guardar (F10)
                            </button>
                        </div>
                    </form>
                </div>

            </div>
        </div>
    </Teleport>
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
