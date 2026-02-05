<script setup>
import { ref, reactive, watch, onMounted, onUnmounted, computed } from 'vue';
import { useMaestrosStore } from '../../../stores/maestros';
import { useLogisticaStore } from '../../../stores/logistica';
import SmartSelect from '@/components/ui/SmartSelect.vue';
import TransporteCanvas from './TransporteCanvas.vue';

const props = defineProps({
    show: Boolean,
    domicilio: {
        type: Object,
        default: null
    },
    defaultTransportId: {
        type: [String, Number],
        default: null
    },
    hasFiscal: {
        type: Boolean,
        default: false
    },
    fiscalDomicilio: {
        type: Object,
        default: null
    },
    primaryDelivery: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['close', 'saved']);

const store = useMaestrosStore();
const logisticaStore = useLogisticaStore();
const isEditing = computed(() => !!props.domicilio);

const form = reactive({
    // Identifiers
    alias: '',
    
    // FISCAL (Left Side)
    calle: '',
    numero: '',
    cp: '',
    localidad: '',
    provincia_id: null,
    es_fiscal: false,

    // LOGISTICA (Right Side)
    es_entrega: true,
    activo: true,
    piso: '',           // [V7]
    depto: '',          // [V7]
    maps_link: '',      // [V7]
    notas_logistica: '',// [V7]
    observaciones: '',  // [V7.1]
    contacto_id: null,  // [V7]
    
    // Logistics Strategy
    metodo_entrega: 'TRANSPORTE',
    transporte_id: null,
    modalidad_envio: 'A_DOMICILIO',
    origen_logistico: 'DESPACHO_NUESTRO',
    
    // Internal
    linked_delivery_id: null
});

// Sync Logic: Copy Fiscal -> Delivery if not explicitly edited (Dirty)
const dirtyFields = reactive({
    calle: false,
    numero: false,
    piso: false,
    depto: false,
    localidad: false,
    provincia: false,
    cp: false
});

// Watch Prop Changes
watch(() => props.domicilio, (newVal) => {
    if (newVal) {
        
        // HYBRID LOGIC: If editing Fiscal, and we have a separate Primary Delivery
        let sourceDelivery = newVal;
        let linkedId = null;
        
        if (newVal.es_fiscal && props.primaryDelivery && String(props.primaryDelivery.id) !== String(newVal.id)) {
             sourceDelivery = props.primaryDelivery;
             linkedId = sourceDelivery.id;
        }

        Object.assign(form, {
            alias: newVal.alias || '',
            calle: newVal.calle || '',
            numero: newVal.numero || '',
            cp: newVal.cp || '',
            localidad: newVal.localidad || '',
            provincia_id: newVal.provincia_id || null,
            es_fiscal: newVal.es_fiscal || false,
            
            // Load Entrega Fields (From Source: either Self or Primary)
            // Note: For Delivery Nodes, 'calle' is often the main address. 'calle_entrega' might be empty.
            // We favor 'calle' if 'calle_entrega' is empty for the source.
            calle_entrega: sourceDelivery.calle || '', // [V7.FIX] Use physical address as default delivery
            numero_entrega: sourceDelivery.numero || '',
            piso_entrega: sourceDelivery.piso || '',
            depto_entrega: sourceDelivery.depto || '',
            cp_entrega: sourceDelivery.cp || '',
            localidad_entrega: sourceDelivery.localidad || '',
            provincia_entrega_id: sourceDelivery.provincia_id || null,
            
            es_entrega: newVal.es_entrega !== undefined ? newVal.es_entrega : true,
            activo: newVal.activo !== undefined ? newVal.activo : true,
            
            piso: newVal.piso || '',
            depto: newVal.depto || '',
            maps_link: newVal.maps_link || '',
            notas_logistica: newVal.notas_logistica || '',
            observaciones: newVal.observaciones || '', 
            contacto_id: newVal.contacto_id || null,
            
            metodo_entrega: sourceDelivery.metodo_entrega || 'TRANSPORTE',
            transporte_id: sourceDelivery.transporte_id || null,
            modalidad_envio: sourceDelivery.modalidad_envio || 'A_DOMICILIO',
            origen_logistico: sourceDelivery.origen_logistico || 'DESPACHO_NUESTRO',
            
            linked_delivery_id: linkedId
        });
        
        // Overwrite if specific delivery attributes exist (legacy support)
        if (sourceDelivery.calle_entrega) form.calle_entrega = sourceDelivery.calle_entrega;
        if (sourceDelivery.numero_entrega) form.numero_entrega = sourceDelivery.numero_entrega;
        // ... (can add more precision if needed, but 'calle' fallback is robust for delivery nodes)
        
    } else {
        // Reset or Defaults
        Object.assign(form, {
            alias: '',
            calle: '',
            numero: '',
            cp: '',
            localidad: '',
            provincia_id: null,
            es_fiscal: !props.hasFiscal,
            
            // LOGISTICA (Right Side) - Decoupled
            calle_entrega: '',
            numero_entrega: '',
            piso_entrega: '',
            depto_entrega: '',
            cp_entrega: '',
            localidad_entrega: '',
            provincia_entrega_id: null,
            
            es_entrega: true,
            activo: true,
            piso: '',
            depto: '',
            maps_link: '',
            notas_logistica: '',
            observaciones: '',
            contacto_id: null,
            
            metodo_entrega: 'TRANSPORTE',
            transporte_id: props.defaultTransportId || null,
            modalidad_envio: 'A_DOMICILIO',
            origen_logistico: 'DESPACHO_NUESTRO'
        });
        // Reset dirty flags for new/reset form
        Object.keys(dirtyFields).forEach(k => dirtyFields[k] = false);
    }
}, { immediate: true });



// Watchers for Auto-Sync
watch(() => form.calle, (val) => { if (!dirtyFields.calle) form.calle_entrega = val; });
watch(() => form.numero, (val) => { if (!dirtyFields.numero) form.numero_entrega = val; });
watch(() => form.piso, (val) => { if (!dirtyFields.piso) form.piso_entrega = val; });
watch(() => form.depto, (val) => { if (!dirtyFields.depto) form.depto_entrega = val; });
watch(() => form.localidad, (val) => { if (!dirtyFields.localidad) form.localidad_entrega = val; });
watch(() => form.cp, (val) => { if (!dirtyFields.cp) form.cp_entrega = val; });
watch(() => form.provincia_id, (val) => { if (!dirtyFields.provincia) form.provincia_entrega_id = val; });

const markDirty = (field) => {
    dirtyFields[field] = true;
};

const toggleFiscal = () => {
    // Si ya es fiscal, NO permitir desactivarlo manualmente.
    // La unicidad del domicilio fiscal se garantiza al activar otro.
    if (form.es_fiscal) {
        // Podríamos mostrar un toast/notificación aquí
        return;
    }
    
    // Si no es fiscal y existe otro fiscal (props.hasFiscal), advertimos del cambio/reemplazo
    if (props.hasFiscal) {
        if (!confirm('¿Establecer como nuevo Domicilio Fiscal?\nEsto reemplazará al actual domicilio fiscal.')) {
            return;
        }
    }
    
    form.es_fiscal = true;
};

const handleSave = () => {
    // [GY-FIX] Critical Data Mapping
    // If NOT fiscal, the 'calle_entrega' (Right Panel) IS the physical address of this node.
    // We must copy it to the core 'calle' fields so it saves to the DB correctly.
    if (!form.es_fiscal) {
         form.calle = form.calle_entrega;
         form.numero = form.numero_entrega;
         form.piso = form.piso_entrega;
         form.depto = form.depto_entrega;
         form.cp = form.cp_entrega;
         form.localidad = form.localidad_entrega;
         form.provincia_id = form.provincia_entrega_id;
    }
    
    emit('saved', { ...props.domicilio, ...form });
    emit('close');
};

const handleKeydown = (e) => {
    if (e.key === 'Escape') emit('close');
    if (e.key === 'F10') {
        e.preventDefault();
        handleSave();
    }
};

// Transport Creation Logic
const showTransporteCanvas = ref(false);
const selectedTransporte = ref(null);
const openNewTransporte = (name) => {
    selectedTransporte.value = { nombre: name, activo: true }; // Simplified init
    showTransporteCanvas.value = true;
};
const handleTransporteCanvasCreate = async (id) => {
    await logisticaStore.fetchEmpresas();
    if(id) form.transporte_id = id;
    showTransporteCanvas.value = false;
};

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
    if (store.provincias.length === 0) store.fetchProvincias();
    logisticaStore.fetchEmpresas();
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
    <div class="flex flex-col bg-[#0f172a] w-full max-w-7xl h-[85vh] rounded-xl shadow-2xl border border-white/10 overflow-hidden animate-fade-in relative z-50">
        
        <!-- HEADER -->
        <div class="h-14 px-6 py-3 flex items-center justify-between border-b border-white/5 bg-white/5 shrink-0">
            <h2 class="font-outfit text-lg font-bold text-white flex items-center gap-2">
                <i class="fa-solid fa-map-location-dot text-cyan-400"></i>
                {{ isEditing ? 'Editar Domicilio (Split View)' : 'Nuevo Domicilio' }}
            </h2>
            <div class="flex gap-2">
                <button @click="$emit('close')" class="px-3 py-1.5 rounded-lg text-white/50 hover:text-white text-xs font-bold transition-colors">
                    CANCELAR (ESC)
                </button>
                <button @click="handleSave" class="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold shadow-lg shadow-cyan-500/20 transition-all flex items-center gap-2">
                    <i class="fa-solid fa-save"></i>
                    GUARDAR
                </button>
            </div>
        </div>

        <!-- SPLIT VIEW BODY -->
        <div class="flex-1 flex min-h-0">
            
            <!-- LEFT PANEL: UBICACIÓN (Physical & Legal) -->
            <div class="w-1/2 border-r border-white/10 flex flex-col bg-fuchsia-900/10">
                
                <!-- HEADER LEFT -->
                <div class="p-3 border-b flex justify-between items-center bg-fuchsia-900/20 border-fuchsia-500/30 h-[53px]">
                    
                    <label class="text-[10px] font-bold uppercase tracking-widest text-fuchsia-300">
                        <i class="fas fa-map-marker-alt mr-1"></i> Ubicación
                    </label>
                    <button 
                        @click="toggleFiscal"
                        class="text-[9px] px-2 py-0.5 rounded border transition-all font-bold uppercase hover:shadow-[0_0_10px_rgba(232,121,249,0.4)]"
                        :class="form.es_fiscal ? 'bg-fuchsia-600 text-white border-fuchsia-400 shadow-[0_0_10px_rgba(232,121,249,0.2)]' : 'bg-transparent text-white/20 border-white/10 hover:border-white/30 hover:text-white/50'"
                    >
                        {{ form.es_fiscal ? 'ES FISCAL' : 'NO ES FISCAL' }}
                    </button>
                </div>

                <div class="p-6 space-y-4 overflow-y-auto custom-scrollbar h-full flex flex-col">
                    

                    <!-- ROW 1: CALLE / NUM / PISO / DEPTO -->
                    <div class="grid grid-cols-12 gap-2">
                        <!-- Calle (5 cols) -->
                        <div class="col-span-12 lg:col-span-5">
                            <label class="block text-[10px] font-bold uppercase mb-1 text-fuchsia-200/50">Calle <span v-if="form.es_fiscal" class="text-fuchsia-400">*</span></label>
                            <input 
                                :value="form.es_fiscal ? form.calle : (props.fiscalDomicilio?.calle || '')"
                                @input="e => form.es_fiscal ? form.calle = e.target.value : null"
                                :readonly="!form.es_fiscal"
                                :class="!form.es_fiscal ? 'opacity-50 cursor-not-allowed' : ''"
                                type="text" class="w-full bg-black/40 border rounded px-2 py-2 text-white outline-none text-xs placeholder-white/10 transition-colors border-fuchsia-500/30 focus:border-fuchsia-500" 
                                placeholder="Ej: Av. Corrientes">
                        </div>
                        <!-- Numero (2 cols) -->
                         <div class="col-span-12 lg:col-span-3">
                            <label class="block text-[10px] font-bold uppercase mb-1 text-fuchsia-200/50">Número <span v-if="form.es_fiscal" class="text-fuchsia-400">*</span></label>
                            <input 
                                :value="form.es_fiscal ? form.numero : (props.fiscalDomicilio?.numero || '')"
                                @input="e => form.es_fiscal ? form.numero = e.target.value : null"
                                :readonly="!form.es_fiscal"
                                :class="!form.es_fiscal ? 'opacity-50 cursor-not-allowed' : ''"
                                type="text" class="w-full bg-black/40 border rounded px-2 py-2 text-white outline-none text-xs transition-colors border-fuchsia-500/30 focus:border-fuchsia-500">
                        </div>
                        <!-- Piso (2 cols) -->
                        <div class="col-span-6 lg:col-span-2">
                            <label class="block text-[10px] font-bold uppercase mb-1 text-fuchsia-200/50">Piso</label>
                            <input 
                                :value="form.es_fiscal ? form.piso : (props.fiscalDomicilio?.piso || '')"
                                @input="e => form.es_fiscal ? form.piso = e.target.value : null"
                                :readonly="!form.es_fiscal"
                                :class="!form.es_fiscal ? 'opacity-50 cursor-not-allowed' : ''"
                                type="text" class="w-full bg-black/40 border rounded px-2 py-2 text-white outline-none text-xs transition-colors border-fuchsia-500/30 focus:border-fuchsia-500"
                             placeholder="Ej: PB">
                        </div>
                        <!-- Depto (2 cols) -->
                        <div class="col-span-6 lg:col-span-2">
                            <label class="block text-[10px] font-bold uppercase mb-1 text-fuchsia-200/50">Depto</label>
                            <input 
                                :value="form.es_fiscal ? form.depto : (props.fiscalDomicilio?.depto || '')"
                                @input="e => form.es_fiscal ? form.depto = e.target.value : null"
                                :readonly="!form.es_fiscal"
                                :class="!form.es_fiscal ? 'opacity-50 cursor-not-allowed' : ''"
                                type="text" class="w-full bg-black/40 border rounded px-2 py-2 text-white outline-none text-xs transition-colors border-fuchsia-500/30 focus:border-fuchsia-500"
                             placeholder="Ej: 4B">
                        </div>
                    </div>

                    <!-- ROW 2: LOCALIDAD / PROVINCIA / CP -->
                    <div class="grid grid-cols-12 gap-2">
                        <div class="col-span-12 lg:col-span-5">
                            <label class="block text-[10px] font-bold uppercase mb-1 text-fuchsia-200/50">Localidad <span v-if="form.es_fiscal" class="text-fuchsia-400">*</span></label>
                            <input 
                                :value="form.es_fiscal ? form.localidad : (props.fiscalDomicilio?.localidad || '')"
                                @input="e => form.es_fiscal ? form.localidad = e.target.value : null"
                                :readonly="!form.es_fiscal"
                                :class="!form.es_fiscal ? 'opacity-50 cursor-not-allowed' : ''"
                                type="text" class="w-full bg-black/40 border rounded px-2 py-2 text-white outline-none text-xs transition-colors border-fuchsia-500/30 focus:border-fuchsia-500">
                        </div>
                        <div class="col-span-12 lg:col-span-5">
                            <label class="block text-[10px] font-bold uppercase mb-1 text-fuchsia-200/50">Provincia <span v-if="form.es_fiscal" class="text-fuchsia-400">*</span></label>
                            <select 
                                :value="form.es_fiscal ? form.provincia_id : (props.fiscalDomicilio?.provincia_id || null)"
                                @change="e => form.es_fiscal ? form.provincia_id = e.target.value : null"
                                :disabled="!form.es_fiscal"
                                :class="!form.es_fiscal ? 'opacity-50 cursor-not-allowed' : ''"
                                class="w-full bg-black/40 border rounded px-2 py-2 text-white outline-none text-xs appearance-none transition-colors border-fuchsia-500/30 focus:border-fuchsia-500">
                                <option :value="null">Seleccionar...</option>
                                <option v-for="prov in store.provincias" :key="prov.id" :value="prov.id">{{ prov.nombre }}</option>
                            </select>
                        </div>
                         <div class="col-span-12 lg:col-span-2">
                            <label class="block text-[10px] font-bold uppercase mb-1 text-fuchsia-200/50">CP</label>
                            <input 
                                :value="form.es_fiscal ? form.cp : (props.fiscalDomicilio?.cp || '')"
                                @input="e => form.es_fiscal ? form.cp = e.target.value : null"
                                :readonly="!form.es_fiscal"
                                :class="!form.es_fiscal ? 'opacity-50 cursor-not-allowed' : ''"
                                type="text" class="w-full bg-black/40 border rounded px-2 py-2 text-white outline-none text-xs transition-colors border-fuchsia-500/30 focus:border-fuchsia-500">
                        </div>
                    </div>

                    <!-- ALIAS (Optional) -->
                    <div class="pt-2 border-t border-white/5">
                        <label class="block text-[10px] font-bold text-white/30 uppercase mb-1">Alias (Opcional)</label>
                        <input v-model="form.alias" type="text" class="w-full bg-transparent border border-white/5 rounded px-3 py-2 text-white/70 focus:border-cyan-500/50 outline-none text-xs" placeholder="Ej: Casa Central">
                    </div>

                    <!-- OBSERVACIONES (New Box) -->
                    <div class="flex-1 min-h-0 flex flex-col pt-2">
                        <label class="block text-[10px] font-bold uppercase mb-1 text-fuchsia-200/50">Observaciones del Domicilio</label>
                        <textarea v-model="form.observaciones" class="w-full flex-1 bg-fuchsia-900/10 border rounded px-3 py-2 text-white/80 outline-none text-xs resize-none placeholder-white/10 transition-colors border-fuchsia-500/20 focus:border-fuchsia-500"
                        placeholder="Instrucciones específicas (horarios admin, referencias, etc...)"></textarea>
                    </div>

                </div>
            </div>

            <!-- RIGHT PANEL: LOGISTICS (Operational) -->
            <div class="w-1/2 flex flex-col bg-[#0f172a]">
                <!-- HEADER RIGHT -->
                <div class="p-3 bg-emerald-900/10 border-b border-emerald-500/10 flex justify-between items-center h-[53px]">
                    <div class="flex items-center gap-2 flex-1 mr-4">
                         <label class="text-[10px] font-bold text-emerald-400 uppercase tracking-widest whitespace-nowrap">
                            <i class="fas fa-truck-fast mr-1"></i> Logística (Real)
                        </label>
                        
                        <!-- MAPS LINK IN HEADER -->
                        <div class="relative flex-1 max-w-[250px] group">
                            <i class="fas fa-map-marker-alt absolute left-2 top-1.5 text-emerald-500/50 text-[10px]"></i>
                            <input v-model="form.maps_link" type="text" class="w-full bg-black/20 border border-emerald-500/10 rounded-full pl-6 pr-2 py-1 text-emerald-100 focus:border-emerald-500 outline-none text-[10px] placeholder-emerald-500/30 transition-all opacity-50 group-hover:opacity-100 focus:opacity-100" placeholder="Pegar Link Google Maps...">
                        </div>
                    </div>

                    <div class="flex items-center gap-2">
                        <label class="text-[9px] text-white/40 uppercase font-bold mr-1">Activo</label>
                        <button 
                            @click="form.activo = !form.activo"
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none"
                            :class="form.activo ? 'bg-emerald-500' : 'bg-gray-700'"
                        >
                            <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm" :class="form.activo ? 'translate-x-3.5' : 'translate-x-1'"/>
                        </button>
                    </div>
                </div>

                <div class="p-6 space-y-4 overflow-y-auto custom-scrollbar h-full flex flex-col">
                    
                    <!-- ADDRESS BLOCK (DUPLICATED FOR LOGISTICS CONTEXT) -->
                    <!-- ROW 1: CALLE / NUM / PISO / DEPTO -->
                    <div class="grid grid-cols-12 gap-2">
                        <!-- Calle (5 cols) -->
                        <div class="col-span-12 lg:col-span-5">
                            <label class="block text-[10px] font-bold text-emerald-200/50 uppercase mb-1">Calle (Entrega)</label>
                            <input v-model="form.calle_entrega" @input="markDirty('calle')" type="text" class="w-full bg-black/40 border border-emerald-500/10 focus:border-emerald-500 rounded px-2 py-2 text-white outline-none text-xs placeholder-white/10 transition-colors" placeholder="Ej: Av. Corrientes">
                        </div>
                        <!-- Numero (2 cols) -->
                         <div class="col-span-12 lg:col-span-3">
                            <label class="block text-[10px] font-bold text-emerald-200/50 uppercase mb-1">Número</label>
                            <input v-model="form.numero_entrega" @input="markDirty('numero')" type="text" class="w-full bg-black/40 border border-emerald-500/10 focus:border-emerald-500 rounded px-2 py-2 text-white outline-none text-xs transition-colors">
                        </div>
                        <!-- Piso (2 cols) -->
                        <div class="col-span-6 lg:col-span-2">
                            <label class="block text-[10px] font-bold text-emerald-200/50 uppercase mb-1">Piso</label>
                            <input v-model="form.piso_entrega" @input="markDirty('piso')" type="text" class="w-full bg-black/40 border border-emerald-500/10 focus:border-emerald-500 rounded px-2 py-2 text-white outline-none text-xs transition-colors" placeholder="Ej: PB">
                        </div>
                        <!-- Depto (2 cols) -->
                        <div class="col-span-6 lg:col-span-2">
                            <label class="block text-[10px] font-bold text-emerald-200/50 uppercase mb-1">Depto</label>
                            <input v-model="form.depto_entrega" @input="markDirty('depto')" type="text" class="w-full bg-black/40 border border-emerald-500/10 focus:border-emerald-500 rounded px-2 py-2 text-white outline-none text-xs transition-colors" placeholder="Ej: 4B">
                        </div>
                    </div>

                    <!-- ROW 2: LOCALIDAD / PROVINCIA / CP -->
                    <div class="grid grid-cols-12 gap-2">
                         <div class="col-span-12 lg:col-span-5">
                            <label class="block text-[10px] font-bold text-emerald-200/50 uppercase mb-1">Localidad</label>
                            <input v-model="form.localidad_entrega" @input="markDirty('localidad')" type="text" class="w-full bg-black/40 border border-emerald-500/10 focus:border-emerald-500 rounded px-2 py-2 text-white outline-none text-xs transition-colors">
                        </div>
                        <div class="col-span-12 lg:col-span-5">
                            <label class="block text-[10px] font-bold text-emerald-200/50 uppercase mb-1">Provincia</label>
                            <select v-model="form.provincia_entrega_id" @change="markDirty('provincia')" class="w-full bg-black/40 border border-emerald-500/10 focus:border-emerald-500 rounded px-2 py-2 text-white outline-none text-xs appearance-none transition-colors">
                                <option :value="null">Seleccionar...</option>
                                <option v-for="prov in store.provincias" :key="prov.id" :value="prov.id">{{ prov.nombre }}</option>
                            </select>
                        </div>
                        <div class="col-span-12 lg:col-span-2">
                            <label class="block text-[10px] font-bold text-emerald-200/50 uppercase mb-1">CP</label>
                            <input v-model="form.cp_entrega" @input="markDirty('cp')" type="text" class="w-full bg-black/40 border border-emerald-500/10 focus:border-emerald-500 rounded px-2 py-2 text-white outline-none text-xs transition-colors">
                        </div>
                    </div>

                     <!-- ALIAS (Optional) -->
                    <div class="pt-2 border-t border-emerald-500/10 pb-2">
                        <label class="block text-[10px] font-bold text-emerald-200/30 uppercase mb-1">Alias (Opcional)</label>
                        <input v-model="form.alias" type="text" class="w-full bg-transparent border border-emerald-500/10 rounded px-3 py-2 text-emerald-100 focus:border-emerald-500/50 outline-none text-xs" placeholder="Ej: Depósito Norte">
                    </div>


                    <!-- TRANSPORT & METHOD -->
                    <div class="space-y-3 pt-2 border-t border-emerald-500/10">
                         <div class="flex items-center gap-2 mb-2">
                            <label class="text-[10px] font-bold text-emerald-200/50 uppercase flex-1">Método de Entrega</label>
                         </div>
                         <div class="flex gap-2">
                            <button v-for="method in ['TRANSPORTE', 'RETIRO_LOCAL', 'FLETE_MOTO']" :key="method"
                                @click="form.metodo_entrega = method"
                                class="flex-1 py-2 rounded-lg border text-[10px] font-bold uppercase transition-colors"
                                :class="form.metodo_entrega === method ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300' : 'bg-white/5 border-transparent text-white/30 hover:bg-white/10'">
                                {{ method === 'RETIRO_LOCAL' ? 'RETIRA CLIENTE' : method.replace('_', ' ') }}
                            </button>
                         </div>

                         <!-- Selector Transporte -->
                         <div v-if="form.metodo_entrega === 'TRANSPORTE'" class="pt-2">
                             <label class="block text-[10px] font-bold text-emerald-200/50 uppercase mb-1">Empresa de Transporte</label>
                             <SmartSelect
                                v-model="form.transporte_id"
                                :options="logisticaStore.empresas"
                                placeholder="Elegir Transporte..."
                                :allow-create="true"
                                @create-new="openNewTransporte"
                                class="dark-smart-select h-10 text-sm"
                             />
                         </div>
                    </div>

                    <!-- NOTAS LOGISTICA -->
                    <div class="flex-1 min-h-0 flex flex-col pt-2">
                        <label class="block text-[10px] font-bold text-emerald-200/50 uppercase mb-1">Notas Logísticas / Instrucciones</label>
                        <textarea v-model="form.notas_logistica" class="w-full flex-1 bg-emerald-900/10 border border-emerald-500/20 rounded-lg px-3 py-2 text-emerald-100 focus:border-emerald-500 outline-none text-xs resize-none placeholder-emerald-900/40" placeholder="Ej: Portón verde, horario de tarde..."></textarea>
                    </div>

                </div>
            </div>

        </div>

        <!-- QuickAdd Transport Modal -->
        <Teleport to="body">
            <Transition name="fade">
                <TransporteCanvas 
                    v-if="showTransporteCanvas" 
                    v-model="selectedTransporte"
                    @close="showTransporteCanvas = false"
                    @save="handleTransporteCanvasCreate"
                />
            </Transition>
        </Teleport>

    </div>
</template>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
