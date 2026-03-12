<template>
    <div v-if="show" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fade-in">
        <div class="bg-[#1f1b24] border border-white/10 rounded-xl shadow-2xl w-full max-w-md overflow-hidden flex flex-col max-h-[90vh]">
            
            <!-- Header -->
            <div class="flex justify-between items-center p-4 border-b border-white/5 bg-white/5">
                <h3 class="text-lg font-bold text-white flex items-center gap-2">
                    <i class="fa-solid fa-truck text-cyan-400"></i>
                    {{ isEditing ? 'Editar Transporte' : 'Nuevo Transporte' }}
                </h3>
                <button @click="close" class="text-white/40 hover:text-white transition-colors">
                    <i class="fa-solid fa-times"></i>
                </button>
            </div>

            <!-- Body -->
            <div class="p-6 space-y-4 overflow-y-auto custom-scrollbar">
                
                <!-- Nombre -->
                <div>
                    <label class="block text-xs font-bold uppercase text-white/40 mb-1">Nombre <span class="text-red-400">*</span></label>
                    <input 
                        ref="firstInput"
                        v-model="form.nombre" 
                        class="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white focus:border-cyan-500 outline-none text-sm placeholder-white/20 transition-colors" 
                        placeholder="Ej: Via Cargo"
                        @keydown.enter.prevent="save"
                    />
                </div>

                <!-- Web Tracking -->
                <div>
                    <label class="block text-xs font-bold uppercase text-white/40 mb-1">Web Tracking</label>
                    <div class="relative">
                        <i class="fa-solid fa-globe absolute left-3 top-1/2 -translate-y-1/2 text-white/20"></i>
                        <input 
                            v-model="form.web_tracking" 
                            class="w-full bg-black/20 border border-white/10 rounded pl-9 pr-3 py-2 text-white focus:border-cyan-500 outline-none text-sm placeholder-white/20 transition-colors" 
                            placeholder="https://tracking..."
                        />
                    </div>
                </div>

                <!-- Contacto Grid -->
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold uppercase text-white/40 mb-1">Tel. Reclamos</label>
                        <input v-model="form.telefono_reclamos" class="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white focus:border-cyan-500 outline-none text-sm" placeholder="0800..." />
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase text-white/40 mb-1">WhatsApp</label>
                        <input v-model="form.whatsapp" class="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white focus:border-cyan-500 outline-none text-sm" placeholder="+54 9..." />
                    </div>
                </div>

                <!-- Checks -->
                <div class="bg-white/5 p-3 rounded border border-white/5 space-y-2">
                    <div class="flex items-center gap-2">
                        <input type="checkbox" v-model="form.requiere_carga_web" id="webCheckModal" class="accent-cyan-500 h-4 w-4 rounded cursor-pointer" />
                        <label for="webCheckModal" class="text-xs font-bold text-white/80 cursor-pointer select-none">Requiere Carga Web</label>
                    </div>
                    <div class="flex items-center gap-2">
                        <input type="checkbox" v-model="form.servicio_retiro_domicilio" id="pickupCheckModal" class="accent-cyan-500 h-4 w-4 rounded cursor-pointer" />
                        <label for="pickupCheckModal" class="text-xs text-white/60 cursor-pointer select-none">Acepta retiros por domicilio</label>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="p-4 border-t border-white/10 bg-black/20 flex gap-3">
                <button @click="close" class="flex-1 px-4 py-2 rounded-lg text-white/60 hover:text-white hover:bg-white/5 text-xs font-bold transition-colors">
                    Cancelar (Esc)
                </button>
                <button 
                    @click="save" 
                    :disabled="saving"
                    class="flex-[2] px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2"
                >
                    <span v-if="saving"><i class="fa-solid fa-spinner fa-spin"></i> Guardando...</span>
                    <span v-else><i class="fa-solid fa-save"></i> Guardar (F10)</span>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick, onMounted, onUnmounted } from 'vue';
import { useLogisticaStore } from '../../../stores/logistica';
import { useNotificationStore } from '../../../stores/notification';

const props = defineProps({
    show: Boolean,
    initialName: {
        type: String,
        default: ''
    }
});

const emit = defineEmits(['close', 'saved']);

const logisticaStore = useLogisticaStore();
const notificationStore = useNotificationStore();

const form = reactive({
    nombre: '',
    web_tracking: '',
    telefono_reclamos: '',
    whatsapp: '',
    requiere_carga_web: false,
    servicio_retiro_domicilio: false,
    activo: true
});

const saving = ref(false);
const firstInput = ref(null);
const isEditing = ref(false); // For now, only handling Create mode via F4

watch(() => props.show, (val) => {
    if (val) {
        // Reset form
        form.nombre = props.initialName || '';
        form.web_tracking = '';
        form.telefono_reclamos = '';
        form.whatsapp = '';
        form.requiere_carga_web = false;
        form.servicio_retiro_domicilio = false;
        form.activo = true;
        
        nextTick(() => {
            firstInput.value?.focus();
        });
    }
});

const close = () => {
    emit('close');
};

const save = async () => {
    if (!form.nombre.trim()) {
        notificationStore.add('El nombre es obligatorio', 'error');
        return;
    }

    saving.value = true;
    try {
        await logisticaStore.createEmpresa(form);
        notificationStore.add('Transporte creado exitosamente', 'success');
        emit('saved', form.nombre); // Return name to auto-select if needed, or trigger store refresh
        close();
    } catch (e) {
        console.error(e);
        notificationStore.add('Error al guardar transporte', 'error');
    } finally {
        saving.value = false;
    }
};

const handleKeydown = (e) => {
    if (!props.show) return;
    
    if (e.key === 'Escape') {
        e.preventDefault();
        close();
    }
    if (e.key === 'F10') {
        e.preventDefault();
        save();
    }
};

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}
</style>
