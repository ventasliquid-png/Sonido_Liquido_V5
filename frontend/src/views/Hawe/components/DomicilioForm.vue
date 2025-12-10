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
    tipo: 'ENTREGA', 
    es_fiscal: false,
    es_entrega: true,
    activo: true,
    // V5.2 Logistics Strategy
    metodo_entrega: 'TRANSPORTE', // Default
    modalidad_envio: 'A_DOMICILIO',
    origen_logistico: 'DESPACHO_NUESTRO'
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
            es_fiscal: newVal.es_fiscal || false,
            es_entrega: newVal.es_entrega !== undefined ? newVal.es_entrega : true,
            activo: newVal.activo !== undefined ? newVal.activo : true,
            metodo_entrega: newVal.metodo_entrega || 'TRANSPORTE',
            modalidad_envio: newVal.modalidad_envio || 'A_DOMICILIO',
            origen_logistico: newVal.origen_logistico || 'DESPACHO_NUESTRO'
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
            transporte_id: props.defaultTransportId || null, 
            es_fiscal: false,
            es_entrega: true,
            activo: true,
            metodo_entrega: 'TRANSPORTE',
            modalidad_envio: 'A_DOMICILIO',
            origen_logistico: 'DESPACHO_NUESTRO'
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
        e.stopPropagation(); // Prevent parent from catching F10
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
                    <i class="fa-solid fa-map-marker-alt text-cyan-400"></i>
                    {{ isEditing ? 'Editar Domicilio' : 'Nuevo Domicilio' }}
                </h2>
                <p class="text-white/50 text-sm">Complete los datos de entrega o facturación.</p>
            </div>
            <div class="flex gap-3">
                <button @click="close" class="px-4 py-2 rounded-lg text-white/50 hover:text-white hover:bg-white/10 text-sm font-medium transition-colors">
                    <i class="fa-solid fa-arrow-left mr-2"></i>Volver
                </button>
                <button @click="handleSave" class="px-6 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-bold shadow-lg shadow-cyan-500/20 transition-all flex items-center gap-2">
                    <i class="fa-solid fa-save"></i>
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

                <!-- Estrategia Logística (Wizard) -->
                <div class="bg-white/5 rounded-xl border border-white/10 overflow-hidden">
                    <div class="p-4 bg-white/5 border-b border-white/5">
                         <label class="block text-xs font-bold text-cyan-400 uppercase"><i class="fa-solid fa-truck-fast mr-2"></i>Estrategia Logística</label>
                    </div>
                    
                    <div class="p-6 space-y-6">
                        <!-- 1. Método de Entrega -->
                        <div>
                            <label class="block text-[10px] font-bold text-white/40 uppercase mb-2">¿Cómo recibe el cliente?</label>
                            <div class="grid grid-cols-4 gap-3">
                                <button 
                                    type="button"
                                    @click="form.metodo_entrega = 'RETIRO_LOCAL'"
                                    class="flex flex-col items-center justify-center p-3 rounded-lg border transition-all gap-2"
                                    :class="form.metodo_entrega === 'RETIRO_LOCAL' ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300' : 'bg-black/20 border-transparent text-white/40 hover:bg-white/5'"
                                >
                                    <i class="fa-solid fa-store text-xl"></i>
                                    <span class="text-xs font-bold">Retiro Local</span>
                                </button>
                                <button 
                                    type="button"
                                    @click="form.metodo_entrega = 'TRANSPORTE'"
                                    class="flex flex-col items-center justify-center p-3 rounded-lg border transition-all gap-2"
                                    :class="form.metodo_entrega === 'TRANSPORTE' ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300' : 'bg-black/20 border-transparent text-white/40 hover:bg-white/5'"
                                >
                                    <i class="fa-solid fa-truck text-xl"></i>
                                    <span class="text-xs font-bold">Transporte</span>
                                </button>
                                <button 
                                    type="button"
                                    @click="form.metodo_entrega = 'FLETE_MOTO'"
                                    class="flex flex-col items-center justify-center p-3 rounded-lg border transition-all gap-2"
                                    :class="form.metodo_entrega === 'FLETE_MOTO' ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300' : 'bg-black/20 border-transparent text-white/40 hover:bg-white/5'"
                                >
                                    <i class="fa-solid fa-motorcycle text-xl"></i>
                                    <span class="text-xs font-bold">Moto/Flete</span>
                                </button>
                                <button 
                                    type="button"
                                    @click="form.metodo_entrega = 'PLATAFORMA'"
                                    class="flex flex-col items-center justify-center p-3 rounded-lg border transition-all gap-2"
                                    :class="form.metodo_entrega === 'PLATAFORMA' ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300' : 'bg-black/20 border-transparent text-white/40 hover:bg-white/5'"
                                >
                                    <i class="fa-solid fa-laptop text-xl"></i>
                                    <span class="text-xs font-bold">Plataforma</span>
                                </button>
                            </div>
                        </div>

                        <!-- 2. Configuración Detallada (Condicional) -->
                        <div v-if="form.metodo_entrega !== 'RETIRO_LOCAL'" class="grid grid-cols-2 gap-6 pt-4 border-t border-white/5 animate-fade-in">
                            
                            <!-- Selección de Transporte (Solo si es Transporte o Moto) -->
                            <div v-if="['TRANSPORTE', 'FLETE_MOTO'].includes(form.metodo_entrega)" class="col-span-2">
                                <label class="block text-[10px] font-bold text-white/40 uppercase mb-2">Transportista Asignado</label>
                                <select v-model="form.transporte_id" class="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-cyan-500 outline-none transition-all">
                                    <option :value="null" class="bg-gray-900">Seleccionar Empresa...</option>
                                    <option v-for="trans in store.transportes" :key="trans.id" :value="trans.id" class="bg-gray-900">
                                        {{ trans.nombre }}
                                    </option>
                                </select>
                            </div>

                            <!-- Modalidad (Domicilio vs Sucursal) -->
                             <div v-if="form.metodo_entrega === 'TRANSPORTE'">
                                <label class="block text-[10px] font-bold text-white/40 uppercase mb-2">Modalidad de Envío</label>
                                <div class="flex gap-2">
                                     <button 
                                        type="button"
                                        @click="form.modalidad_envio = 'A_DOMICILIO'"
                                        class="flex-1 py-2 px-3 rounded text-xs font-bold border transition-colors"
                                        :class="form.modalidad_envio === 'A_DOMICILIO' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'border-white/10 text-white/40 hover:bg-white/5'"
                                    >
                                        <i class="fa-solid fa-house mr-2"></i>A Domicilio
                                    </button>
                                     <button 
                                        type="button"
                                        @click="form.modalidad_envio = 'A_SUCURSAL'"
                                        class="flex-1 py-2 px-3 rounded text-xs font-bold border transition-colors"
                                        :class="form.modalidad_envio === 'A_SUCURSAL' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'border-white/10 text-white/40 hover:bg-white/5'"
                                    >
                                        <i class="fa-solid fa-building mr-2"></i>A Sucursal
                                    </button>
                                </div>
                            </div>

                            <!-- Origen Logístico (Quién despacha) -->
                             <div :class="form.metodo_entrega === 'TRANSPORTE' ? '' : 'col-span-2'">
                                <label class="block text-[10px] font-bold text-white/40 uppercase mb-2">Origen Logístico</label>
                                <div class="flex gap-2">
                                     <button 
                                        type="button"
                                        @click="form.origen_logistico = 'DESPACHO_NUESTRO'"
                                        class="flex-1 py-2 px-3 rounded text-xs font-bold border transition-colors"
                                        :class="form.origen_logistico === 'DESPACHO_NUESTRO' ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300' : 'border-white/10 text-white/40 hover:bg-white/5'"
                                    >
                                        <i class="fa-solid fa-dolly mr-2"></i>Despachamos
                                    </button>
                                     <button 
                                        type="button"
                                        @click="form.origen_logistico = 'RETIRO_EN_PLANTA'"
                                        class="flex-1 py-2 px-3 rounded text-xs font-bold border transition-colors"
                                        :class="form.origen_logistico === 'RETIRO_EN_PLANTA' ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300' : 'border-white/10 text-white/40 hover:bg-white/5'"
                                    >
                                        <i class="fa-solid fa-truck-pickup mr-2"></i>Nos Retiran
                                    </button>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
            </form>

            <div class="max-w-4xl mx-auto mt-6 space-y-6">
                 <!-- Estado (Active Toggle) -->
                 <div class="bg-white/5 p-6 rounded-xl border border-white/10 flex items-center justify-between">
                    <div>
                        <label class="block text-xs font-bold text-white/60 uppercase mb-1">Estado del Domicilio</label>
                        <p class="text-sm text-white/50">Si desactiva el domicilio, no aparecerá en las búsquedas habituales.</p>
                    </div>
                    <button 
                        @click="form.activo = !form.activo"
                        class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-[#0f172a]"
                        :class="form.activo ? 'bg-green-500' : 'bg-gray-700'"
                    >
                        <span 
                            class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                            :class="form.activo ? 'translate-x-6' : 'translate-x-1'"
                        />
                    </button>
                </div>

                <!-- Flags de Uso -->
                <div class="grid grid-cols-2 gap-6">
                    <div class="bg-white/5 p-4 rounded-xl border border-white/10 flex items-center justify-between">
                            <div>
                            <label class="block text-xs font-bold text-purple-400 uppercase mb-1">Fiscal</label>
                            <p class="text-[10px] text-white/40">Dirección legal de facturación</p>
                            </div>
                            <button 
                                @click="form.es_fiscal = !form.es_fiscal"
                                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none"
                                :class="form.es_fiscal ? 'bg-purple-600' : 'bg-gray-700'"
                            >
                                <span 
                                    class="inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform"
                                    :class="form.es_fiscal ? 'translate-x-4.5' : 'translate-x-1'"
                                />
                            </button>
                    </div>
                    <div class="bg-white/5 p-4 rounded-xl border border-white/10 flex items-center justify-between">
                            <div>
                            <label class="block text-xs font-bold text-blue-400 uppercase mb-1">Entrega</label>
                            <p class="text-[10px] text-white/40">Habilitado para envíos</p>
                            </div>
                            <button 
                                @click="form.es_entrega = !form.es_entrega"
                                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none"
                                :class="form.es_entrega ? 'bg-blue-600' : 'bg-gray-700'"
                            >
                                <span 
                                    class="inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform"
                                    :class="form.es_entrega ? 'translate-x-4.5' : 'translate-x-1'"
                                />
                            </button>
                    </div>
                </div>

                <!-- Bottom Actions -->
                <div class="flex justify-end pt-6 border-t border-white/10">
                    <button @click="handleSave" class="px-8 py-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-base font-bold shadow-lg shadow-cyan-500/20 transition-all flex items-center gap-2 transform active:scale-95">
                        <i class="fa-solid fa-save"></i>
                        GUARDAR CAMBIOS
                    </button>
                </div>
            </div>
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
