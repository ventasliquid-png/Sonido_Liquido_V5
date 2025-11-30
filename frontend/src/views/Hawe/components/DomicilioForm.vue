<script setup>
import { ref, reactive, watch, onMounted, onUnmounted, computed } from 'vue';
import { useMaestrosStore } from '../../../stores/maestros';

const props = defineProps({
    show: Boolean,
    domicilio: {
        type: Object,
        default: null
    },
    defaultTransportId: {
        type: [String, Number],
        default: null
    }
});

const emit = defineEmits(['close', 'saved']);

const store = useMaestrosStore();
const isEditing = computed(() => !!props.domicilio);

const form = reactive({
    calle: '',
    numero: '',
    piso: '',
    depto: '',
    cp: '',
    localidad: '',
    provincia_id: null,
    transporte_id: null,
    tipo: 'ENTREGA' // Default type
});

// Load masters on mount if empty
onMounted(() => {
    if (store.provincias.length === 0) store.fetchProvincias();
    if (store.transportes.length === 0) store.fetchTransportes();
});

// Initialize form when domicile changes or on mount
watch(() => props.domicilio, (newVal) => {
    if (newVal) {
        // Edit mode
        Object.assign(form, {
            calle: newVal.calle || '',
            numero: newVal.numero || '',
            piso: newVal.piso || '',
            depto: newVal.depto || '',
            cp: newVal.cp || '',
            localidad: newVal.localidad || '',
            provincia_id: newVal.provincia_id || null,
            transporte_id: newVal.transporte_id || null,
            tipo: newVal.tipo || 'ENTREGA'
        });
    } else {
        // Create mode
        Object.assign(form, {
            calle: '',
            numero: '',
            piso: '',
            depto: '',
            cp: '',
            localidad: '',
            provincia_id: null,
            transporte_id: props.defaultTransportId || null, // Auto-fill transport
            tipo: 'ENTREGA'
        });
    }
}, { immediate: true });

const handleSave = () => {
    // Basic validation
    if (!form.calle) {
        alert('La calle es obligatoria');
        return;
    }
    
    emit('saved', { ...form, id: props.domicilio?.id });
    emit('close');
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
    <div class="h-full flex flex-col bg-[#0f172a] animate-fade-in">
        <!-- Header -->
        <div class="h-32 px-8 py-6 flex items-start justify-between border-b border-white/5 bg-white/5 shrink-0">
            <div>
                <h2 class="font-outfit text-2xl font-bold text-white mb-1 flex items-center gap-3">
                    <i class="fas fa-map-marker-alt text-cyan-400"></i>
                    {{ isEditing ? 'Editar Domicilio' : 'Nuevo Domicilio' }}
                </h2>
                <p class="text-white/50 text-sm">Complete los datos de entrega o facturación.</p>
            </div>
            <div class="flex gap-3">
                <button @click="close" class="px-4 py-2 rounded-lg text-white/50 hover:text-white hover:bg-white/10 text-sm font-medium transition-colors">
                    <i class="fas fa-arrow-left mr-2"></i>Volver
                </button>
                <button @click="handleSave" class="px-6 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-bold shadow-lg shadow-cyan-500/20 transition-all flex items-center gap-2">
                    <i class="fas fa-save"></i>
                    Guardar (F10)
                </button>
            </div>
        </div>

        <!-- Form Body -->
        <div class="flex-1 overflow-y-auto p-8">
            <form @submit.prevent="handleSave" class="max-w-4xl mx-auto space-y-6">
                <!-- Calle y Número -->
                <div class="grid grid-cols-12 gap-6">
                    <div class="col-span-8">
                        <label class="block text-xs font-bold text-cyan-400 uppercase mb-1">Calle <span class="text-red-400">*</span></label>
                        <input v-model="form.calle" type="text" ref="firstInput" required class="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all placeholder-white/20 text-lg" placeholder="Ej: Av. Corrientes">
                    </div>
                    <div class="col-span-4">
                        <label class="block text-xs font-bold text-cyan-400 uppercase mb-1">Número</label>
                        <input v-model="form.numero" type="text" class="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all placeholder-white/20 text-lg" placeholder="1234">
                    </div>
                </div>

                <!-- Piso, Depto, CP -->
                <div class="grid grid-cols-3 gap-6">
                    <div>
                        <label class="block text-xs font-bold text-white/60 uppercase mb-1">Piso</label>
                        <input v-model="form.piso" type="text" class="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-white/60 uppercase mb-1">Depto</label>
                        <input v-model="form.depto" type="text" class="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-white/60 uppercase mb-1">CP</label>
                        <input v-model="form.cp" type="text" class="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all">
                    </div>
                </div>

                <!-- Localidad y Provincia -->
                <div class="grid grid-cols-2 gap-6">
                    <div>
                        <label class="block text-xs font-bold text-cyan-400 uppercase mb-1">Localidad</label>
                        <input v-model="form.localidad" type="text" class="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-cyan-400 uppercase mb-1">Provincia</label>
                        <select v-model="form.provincia_id" class="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all appearance-none">
                            <option :value="null" class="bg-gray-900">Seleccionar...</option>
                            <option v-for="prov in store.provincias" :key="prov.id" :value="prov.id" class="bg-gray-900">
                                {{ prov.nombre }}
                            </option>
                        </select>
                    </div>
                </div>

                <!-- Transporte -->
                <div class="bg-white/5 p-6 rounded-xl border border-white/10">
                    <label class="block text-xs font-bold text-cyan-400 uppercase mb-2"><i class="fas fa-truck mr-2"></i>Transporte Sugerido</label>
                    <select v-model="form.transporte_id" class="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all appearance-none text-lg">
                        <option :value="null" class="bg-gray-900">Seleccionar...</option>
                        <option v-for="trans in store.transportes" :key="trans.id" :value="trans.id" class="bg-gray-900">
                            {{ trans.nombre }}
                        </option>
                    </select>
                    <p class="text-xs text-white/40 mt-2">Este transporte se sugerirá automáticamente en los pedidos para este domicilio.</p>
                </div>
            </form>
        </div>
    </div>
</template>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
