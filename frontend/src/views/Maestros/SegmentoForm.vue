<script setup>
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue';
import { useMaestrosStore } from '../../stores/maestros';

const props = defineProps({
    show: Boolean,
    id: {
        type: [String, Number],
        default: null
    }
});

const emit = defineEmits(['close', 'saved']);

const store = useMaestrosStore();
const isEditing = ref(false);

const form = reactive({
    nombre: '',
    descripcion: '',
    activo: true
});

watch(() => props.show, (newVal) => {
    if (newVal) {
        if (props.id) {
            isEditing.value = true;
            const segmento = store.segmentos.find(s => s.id === props.id);
            if (segmento) {
                form.nombre = segmento.nombre;
                form.descripcion = segmento.descripcion;
                form.activo = segmento.activo;
            }
        } else {
            isEditing.value = false;
            form.nombre = '';
            form.descripcion = '';
            form.activo = true;
        }
    }
});

const handleSave = async () => {
    try {
        let result;
        if (isEditing.value) {
            result = await store.updateSegmento(props.id, form);
        } else {
            result = await store.createSegmento(form);
        }
        emit('saved', result);
        emit('close');
    } catch (error) {
        alert('Error al guardar el segmento.');
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
    <div v-if="show" class="fixed inset-0 z-[70] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" @click.self="close">
        <div class="relative w-full max-w-md bg-[#0a253a] border border-cyan-500/30 shadow-2xl shadow-cyan-900/40 rounded-lg overflow-hidden animate-scale-in">
            
            <!-- Header -->
            <div class="px-6 py-4 border-b border-cyan-900/30 flex justify-between items-center bg-[#05151f]/50">
                <h3 class="text-lg font-bold text-cyan-100 leading-6 font-outfit">
                    {{ isEditing ? 'Editar Segmento' : 'Nuevo Segmento' }}
                </h3>
                <button @click="close" class="text-cyan-900/50 hover:text-cyan-100 transition-colors">
                    <i class="fas fa-times"></i>
                </button>
            </div>

            <!-- Body -->
            <div class="p-6">
                <form @submit.prevent="handleSave">
                    <div class="mb-5">
                        <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Nombre <span class="text-red-400">*</span></label>
                        <input 
                            v-model="form.nombre" 
                            type="text" 
                            required 
                            placeholder="Ej: Mayoristas"
                            class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors placeholder-cyan-900/30"
                        >
                    </div>
                    
                    <div class="mb-5">
                        <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Descripción</label>
                        <textarea 
                            v-model="form.descripcion" 
                            rows="2"
                            placeholder="Breve descripción del segmento..."
                            class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors placeholder-cyan-900/30 resize-none"
                        ></textarea>
                    </div>

                    <div class="mb-6 flex items-center justify-between bg-cyan-900/10 p-3 rounded-lg border border-cyan-900/20">
                        <span class="text-sm font-bold text-cyan-100">Estado Activo</span>
                        <div class="flex items-center gap-2">
                             <span class="text-[10px] font-bold uppercase transition-colors" :class="form.activo ? 'text-green-400' : 'text-red-400'">
                                {{ form.activo ? 'ACTIVO' : 'INACTIVO' }}
                            </span>
                            <input 
                                v-model="form.activo" 
                                type="checkbox" 
                                class="hidden" 
                                id="statusToggle"
                            >
                            <label 
                                for="statusToggle"
                                class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors cursor-pointer"
                                :class="form.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                            >
                                <span 
                                    class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm" 
                                    :class="form.activo ? 'translate-x-3.5' : 'translate-x-1'"
                                />
                            </label>
                        </div>
                    </div>

                    <div class="flex justify-end gap-3 pt-2">
                        <button 
                            type="button" 
                            @click="close" 
                            class="px-4 py-2 bg-transparent text-cyan-900/50 hover:text-cyan-100 font-bold uppercase text-xs border border-transparent hover:border-cyan-900/30 rounded transition-all"
                        >
                            Cancelar (ESC)
                        </button>
                        <button 
                            type="submit" 
                            class="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold uppercase text-xs rounded shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 transition-all flex items-center gap-2"
                        >
                            <i class="fas fa-save"></i> Guardar (F10)
                        </button>
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
