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
    console.log('DomicilioForm received prop:', newVal);
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
            es_fiscal: true, // Default to Fiscal to prevent "No Fiscal" errors
            es_entrega: true,
            activo: true,
            metodo_entrega: 'TRANSPORTE',
            modalidad_envio: 'A_DOMICILIO',
            origen_logistico: 'DESPACHO_NUESTRO'
        });
    }
}, { immediate: true });

const isValid = computed(() => {
    // If "Retiro por Local", address is not mandatory
    if (form.metodo_entrega === 'RETIRO_LOCAL') return true

    const basic = form.calle && form.numero && form.localidad
    // If delivery, transport is mandatory logic? (Currently defaults to 'Retira por local' so maybe not)
    return basic
})

const handleSave = () => {
    // Logic Sync: If Retiro Local, set origen_logistico to RETIRO_EN_PLANTA
    if (form.metodo_entrega === 'RETIRO_LOCAL') {
        form.origen_logistico = 'RETIRO_EN_PLANTA';
    } else {
        // If switching back to delivery, ensure we don't keep RETIRO_EN_PLANTA
        if (form.origen_logistico === 'RETIRO_EN_PLANTA') {
            form.origen_logistico = 'DESPACHO_NUESTRO';
        }
    }

    // Basic validation (Skip if Retiro Local)
    if (form.metodo_entrega !== 'RETIRO_LOCAL' && !form.calle) {
        alert('La calle es obligatoria para envíos.');
        return;
    }
    
    console.log('DomicilioForm saving:', { ...form, id: props.domicilio?.id });
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
    if (e.code === 'F10') {
        e.preventDefault();
        e.stopPropagation(); 
        handleSave();
    }
};

const firstInput = ref(null);

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
    // Auto-focus on show
    if (props.show) {
        setTimeout(() => firstInput.value?.focus(), 100);
    }
});

const modalRef = ref(null);
const isDragging = ref(false);
const dragOffset = reactive({ x: 0, y: 0 });
const modalPosition = reactive({ top: null, left: null });

const startDrag = (e) => {
    if (!modalRef.value) return;
    isDragging.value = true;
    
    const rect = modalRef.value.getBoundingClientRect();
    dragOffset.x = e.clientX - rect.left;
    dragOffset.y = e.clientY - rect.top;
    
    // Set initial absolute position matching current visual position
    modalPosition.left = rect.left;
    modalPosition.top = rect.top;
    
    window.addEventListener('mousemove', onDrag);
    window.addEventListener('mouseup', stopDrag);
};

const onDrag = (e) => {
    if (!isDragging.value) return;
    modalPosition.left = e.clientX - dragOffset.x;
    modalPosition.top = e.clientY - dragOffset.y;
};

const stopDrag = () => {
    isDragging.value = false;
    window.removeEventListener('mousemove', onDrag);
    window.removeEventListener('mouseup', stopDrag);
};

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
    window.removeEventListener('mousemove', onDrag);
    window.removeEventListener('mouseup', stopDrag);
});
</script>

<template>
    <div 
        ref="modalRef"
        class="flex flex-col bg-[#0f172a] animate-fade-in w-full max-w-4xl h-auto max-h-[90vh] rounded-xl shadow-2xl border border-white/10 overflow-hidden"
        :class="modalPosition.top === null ? 'mx-auto relative' : 'fixed margin-0'"
        :style="modalPosition.top !== null ? { top: `${modalPosition.top}px`, left: `${modalPosition.left}px`, transform: 'none' } : {}"
    >
        <!-- Header (Draggable) -->
        <div 
            @mousedown="startDrag"
            class="h-14 px-6 py-3 flex items-center justify-between border-b border-white/5 bg-white/5 shrink-0 rounded-t-xl cursor-move select-none active:cursor-grabbing"
        >
            <div>
                <h2 class="font-outfit text-lg font-bold text-white flex items-center gap-2">
                    <i class="fa-solid fa-map-marker-alt text-cyan-400"></i>
                    {{ isEditing ? 'Editar Domicilio' : 'Nuevo Domicilio' }}
                </h2>
            </div>
            <div class="flex gap-2">
                <button @click="close" class="px-3 py-1.5 rounded-lg text-white/50 hover:text-white hover:bg-white/10 text-xs font-medium transition-colors">
                    <i class="fa-solid fa-times mr-1"></i>Cancelar
                </button>
                <button @click="handleSave" class="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold shadow-lg shadow-cyan-500/20 transition-all flex items-center gap-2">
                    <i class="fa-solid fa-save"></i>
                    Guardar (F10)
                </button>
            </div>
        </div>

        <!-- Form Body -->
        <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
            <form @submit.prevent="handleSave" class="space-y-4">
                
                <!-- Status & Identification Row -->
                <div class="grid grid-cols-2 gap-4 mb-2">
                     <!-- Fiscal Flag -->
                    <div class="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-lg border border-white/10 flex-1 relative group">
                            <div class="flex-1">
                            <label class="block text-[10px] font-bold uppercase mb-0.5" :class="form.es_fiscal ? 'text-purple-400' : 'text-gray-500'">Fiscal</label>
                            </div>
                            
                            <!-- Tooltip wrapper for Disabled State -->
                            <div class="relative">
                            <button 
                                type="button"
                                @click="!isEditing || !form.es_fiscal ? (form.es_fiscal = !form.es_fiscal) : null"
                                class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0"
                                :class="form.es_fiscal ? 'bg-purple-600 cursor-not-allowed opacity-80' : 'bg-gray-700 cursor-pointer'"
                            >
                                <span 
                                    class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                    :class="form.es_fiscal ? 'translate-x-3.5' : 'translate-x-1'"
                                />
                            </button>
                            <!-- Tooltip -->
                            <div v-if="isEditing && form.es_fiscal" class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 bg-black text-white text-[10px] p-2 rounded shadow-xl border border-white/20 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 text-center">
                                Para cambiar el domicilio fiscal, active la opción en el nuevo domicilio destino.
                            </div>
                            </div>
                    </div>

                    <!-- Estado -->
                    <div class="flex items-center justify-between bg-white/5 px-4 py-2 rounded-lg border border-white/10">
                        <label class="text-[10px] font-bold text-white/60 uppercase">Estado</label>
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] font-bold uppercase" :class="form.activo ? 'text-green-400' : 'text-red-400'">{{ form.activo ? 'Activo' : 'Inactivo' }}</span>
                                <button 
                                type="button"
                                @click="!form.es_fiscal && (form.activo = !form.activo)"
                                class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0"
                                :class="[
                                    form.activo ? 'bg-green-500' : 'bg-gray-700',
                                    form.es_fiscal ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                                ]"
                            >
                                <span 
                                    class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                    :class="form.activo ? 'translate-x-3.5' : 'translate-x-1'"
                                />
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- ROW 1: Calle, Numero, Piso, Depto -->
                <div class="grid grid-cols-12 gap-3">
                    <div class="col-span-6">
                        <label class="block text-[10px] font-bold text-cyan-400 uppercase mb-0.5">Calle <span class="text-red-400">*</span></label>
                        <input v-model="form.calle" type="text" ref="firstInput" required class="w-full bg-black/20 border border-white/10 rounded px-3 py-1.5 text-white focus:border-cyan-500 outline-none text-sm placeholder-white/20" placeholder="Ej: Av. Corrientes">
                    </div>
                    <div class="col-span-2">
                        <label class="block text-[10px] font-bold text-cyan-400 uppercase mb-0.5">Número <span class="text-red-400">*</span></label>
                        <input v-model="form.numero" type="text" class="w-full bg-black/20 border border-white/10 rounded px-3 py-1.5 text-white focus:border-cyan-500 outline-none text-sm placeholder-white/20">
                    </div>
                    <div class="col-span-2">
                        <label class="block text-[10px] font-bold text-white/60 uppercase mb-0.5">Piso</label>
                        <input v-model="form.piso" type="text" class="w-full bg-black/20 border border-white/10 rounded px-3 py-1.5 text-white focus:border-cyan-500 outline-none text-sm">
                    </div>
                    <div class="col-span-2">
                        <label class="block text-[10px] font-bold text-white/60 uppercase mb-0.5">Depto</label>
                        <input v-model="form.depto" type="text" class="w-full bg-black/20 border border-white/10 rounded px-3 py-1.5 text-white focus:border-cyan-500 outline-none text-sm">
                    </div>
                </div>

                <!-- ROW 2: Localidad, Provincia, CP -->
                <div class="grid grid-cols-12 gap-3">
                    <div class="col-span-5">
                        <label class="block text-[10px] font-bold text-cyan-400 uppercase mb-0.5">Localidad <span class="text-red-400">*</span></label>
                        <input v-model="form.localidad" type="text" class="w-full bg-black/20 border border-white/10 rounded px-3 py-1.5 text-white focus:border-cyan-500 outline-none text-sm">
                    </div>
                    <div class="col-span-5">
                        <label class="block text-[10px] font-bold text-cyan-400 uppercase mb-0.5">Provincia <span class="text-red-400">*</span></label>
                        <select v-model="form.provincia_id" class="w-full bg-black/20 border border-white/10 rounded px-3 py-1.5 text-white focus:border-cyan-500 outline-none text-sm appearance-none">
                            <option :value="null" class="bg-gray-900 text-white">Seleccionar...</option>
                            <option v-for="prov in store.provincias" :key="prov.id" :value="prov.id" class="bg-gray-900 text-white">
                                {{ prov.nombre }}
                            </option>
                        </select>
                    </div>
                     <div class="col-span-2">
                        <label class="block text-[10px] font-bold text-white/60 uppercase mb-0.5">CP</label>
                        <input v-model="form.cp" type="text" class="w-full bg-black/20 border border-white/10 rounded px-3 py-1.5 text-white focus:border-cyan-500 outline-none text-sm">
                    </div>
                </div>

                <!-- LOGISTICS CONFIG (Compact Wizard) -->
                <div class="bg-white/5 rounded-lg border border-white/10 overflow-hidden mt-2">
                    <div class="px-4 py-2 bg-black/20 border-b border-white/5 flex justify-between items-center">
                         <label class="text-[10px] font-bold text-cyan-400 uppercase"><i class="fa-solid fa-truck-fast mr-1"></i>Logística</label>
                    </div>
                    
                    <div class="p-4 space-y-4">
                        <!-- Método -->
                        <div class="flex items-center gap-4">
                            <label class="text-[10px] font-bold text-white/40 uppercase w-24 shrink-0">Método de Entrega</label>
                            <div class="flex gap-2 flex-1">
                                <button v-for="method in [
                                    { id: 'RETIRO_LOCAL', icon: 'fa-store', label: 'Retiro Local' },
                                    { id: 'TRANSPORTE', icon: 'fa-truck', label: 'Transporte' },
                                    { id: 'FLETE_MOTO', icon: 'fa-motorcycle', label: 'Moto/Flete' },
                                    { id: 'PLATAFORMA', icon: 'fa-laptop', label: 'Plataforma' }
                                ]" :key="method.id"
                                type="button"
                                @click="form.metodo_entrega = method.id"
                                class="flex-1 py-1.5 px-2 rounded border transition-colors flex items-center justify-center gap-2"
                                :class="form.metodo_entrega === method.id ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300' : 'bg-black/20 border-transparent text-white/40 hover:bg-white/5'">
                                    <i class="fa-solid text-xs" :class="method.icon"></i>
                                    <span class="text-[10px] font-bold uppercase">{{ method.label }}</span>
                                </button>
                            </div>
                        </div>

                        <!-- Configs Detalladas -->
                         <div v-if="form.metodo_entrega !== 'RETIRO_LOCAL'" class="space-y-3 pt-2 border-t border-white/5">
                            
                            <!-- Transportista -->
                            <div v-if="['TRANSPORTE', 'FLETE_MOTO'].includes(form.metodo_entrega)" class="flex items-center gap-4">
                                <label class="text-[10px] font-bold text-white/40 uppercase w-24 shrink-0">Transportista</label>
                                <select v-model="form.transporte_id" class="flex-1 bg-black/20 border border-white/10 rounded px-3 py-1.5 text-white focus:border-cyan-500 outline-none text-xs">
                                    <option :value="null" class="bg-gray-900">Seleccionar Empresa...</option>
                                    <option v-for="trans in store.transportes" :key="trans.id" :value="trans.id" class="bg-gray-900">
                                        {{ trans.nombre }}
                                    </option>
                                </select>
                            </div>

                            <div class="flex gap-4">
                                <!-- Modalidad Envío -->
                                <div v-if="form.metodo_entrega === 'TRANSPORTE'" class="flex-1 flex gap-2 items-center">
                                     <label class="text-[10px] font-bold text-white/40 uppercase w-24 shrink-0">Modalidad</label>
                                     <div class="flex-1 flex gap-1">
                                        <button type="button" @click="form.modalidad_envio = 'A_DOMICILIO'" class="flex-1 py-1 px-2 rounded border text-[10px] font-bold transition-colors" :class="form.modalidad_envio === 'A_DOMICILIO' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'border-white/10 text-white/40'">Dom</button>
                                        <button type="button" @click="form.modalidad_envio = 'A_SUCURSAL'" class="flex-1 py-1 px-2 rounded border text-[10px] font-bold transition-colors" :class="form.modalidad_envio === 'A_SUCURSAL' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'border-white/10 text-white/40'">Suc</button>
                                     </div>
                                </div>
                                <!-- Origen Logístico -->
                                <div class="flex-1 flex gap-2 items-center" :class="form.metodo_entrega !== 'TRANSPORTE' ? 'col-span-2' : ''">
                                     <label class="text-[10px] font-bold text-white/40 uppercase w-24 shrink-0">Origen</label>
                                     <div class="flex-1 flex gap-1">
                                        <button type="button" @click="form.origen_logistico = 'DESPACHO_NUESTRO'" class="flex-1 py-1 px-2 rounded border text-[10px] font-bold transition-colors flex items-center justify-center gap-1" :class="form.origen_logistico === 'DESPACHO_NUESTRO' ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300' : 'border-white/10 text-white/40'">
                                            <i class="fa-solid fa-dolly"></i> Despacha
                                        </button>
                                        <button type="button" @click="form.origen_logistico = 'RETIRO_EN_PLANTA'" class="flex-1 py-1 px-2 rounded border text-[10px] font-bold transition-colors flex items-center justify-center gap-1" :class="form.origen_logistico === 'RETIRO_EN_PLANTA' ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300' : 'border-white/10 text-white/40'">
                                            <i class="fa-solid fa-truck-pickup"></i> Retira
                                        </button>
                                     </div>
                                </div>
                            </div>

                         </div>
                    </div>
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
