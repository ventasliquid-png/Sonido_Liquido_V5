<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useClientesStore } from '../../stores/clientes';
import { useNotificationStore } from '../../stores/notification';
import maestrosService from '../../services/maestros';
import clientesService from '../../services/clientes';
import DomicilioGrid from './components/DomicilioGrid.vue';
import VinculoGrid from './components/VinculoGrid.vue';
import SmartSelect from '../../components/ui/SmartSelect.vue';
import SegmentoForm from '../Maestros/SegmentoForm.vue';
import TransporteForm from '../Logistica/TransporteForm.vue';

const props = defineProps({
    show: Boolean,
    clienteId: {
        type: String,
        default: null
    }
});

const emit = defineEmits(['close', 'saved', 'edit-existing']);

const store = useClientesStore();
const notificationStore = useNotificationStore();
const activeTab = ref('general');
const loading = ref(false);

// State
const formData = ref({
    razon_social: '',
    nombre_fantasia: '',
    cuit: '',
    condicion_iva_id: null,
    whatsapp_empresa: '',
    web_portal_pagos: '',
    datos_acceso_pagos: '',
    activo: true,
    lista_precios_id: null,
    segmento_id: null,
    transporte_id: null,
    limite_credito: 0,
    requiere_auditoria: false,
    
    // Address Fields (Tab 1)
    calle: '',
    numero: '',
    piso: '',
    depto: '',
    localidad: '',
    cp: '',
    provincia: ''
});

const segmentos = ref([]);
const transportes = ref([]);
const condicionesIva = ref([]);
const provincias = ref([]);
const pendingReactivation = ref(false);
const showSegmentoForm = ref(false);
const showTransporteForm = ref(false);

const conflictModal = ref({
    show: false,
    type: '',
    clients: []
});

// Domicile Dashboard Logic
const domicilios = ref([]); // Store full list for dashboard

const domicilioFiscal = computed(() => {
    return domicilios.value.find(d => d.es_fiscal);
});

const domiciliosEntrega = computed(() => {
    return domicilios.value.filter(d => d.es_entrega && !d.es_fiscal);
});

const isFiscalSameAsEntrega = computed(() => {
    const fiscal = domicilioFiscal.value;
    const entregas = domiciliosEntrega.value;
    // If there are no specific delivery addresses, and fiscal is delivery, then it's same.
    if (entregas.length === 0 && fiscal?.es_entrega) return true;
    return false;
});

const handleDomicilioChange = async () => {
    if (props.clienteId) {
        const res = await clientesService.getById(props.clienteId);
        if (res.data && res.data.domicilios) {
            domicilios.value = res.data.domicilios;
        }
    }
};

// Computed
const isNew = computed(() => !props.clienteId);

// Methods
const fetchMaestros = async () => {
    try {
        const [segRes, transRes, ivaRes, provRes] = await Promise.all([
            maestrosService.getSegmentos(),
            maestrosService.getTransportes(),
            maestrosService.getCondicionesIva(),
            maestrosService.getProvincias()
        ]);
        segmentos.value = segRes.data;
        transportes.value = transRes.data;
        condicionesIva.value = ivaRes.data;
        provincias.value = provRes.data;
    } catch (error) {
        console.error('Error fetching maestros:', error);
        notificationStore.add('Error al cargar listas maestras.', 'error');
    }
};

const isValidCuit = (cuit) => {
    if (!cuit || cuit.length !== 11) return false;
    const multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
    let total = 0;
    for (let i = 0; i < 10; i++) {
        total += parseInt(cuit[i]) * multipliers[i];
    }
    const mod = total % 11;
    const digit = mod === 0 ? 0 : mod === 1 ? 9 : 11 - mod;
    return digit === parseInt(cuit[10]);
};

const handleCuitInput = (e) => {
    // Allow only numbers
    formData.value.cuit = e.target.value.replace(/\D/g, '');
};

const resolveConflict = (action, client = null) => {
    conflictModal.value.show = false;
    if (action === 'reactivate' && client) {
        emit('edit-existing', client.id);
        pendingReactivation.value = true; 
    } else if (action === 'edit' && client) {
        emit('edit-existing', client.id);
    } else if (action === 'create') {
        handleSave(true);
    }
};

const originalCuit = ref('');

const handleCuitBlur = async () => {
    if (formData.value.cuit) {
        let clean = formData.value.cuit.replace(/\D/g, '');
        if (clean.length > 11) clean = clean.slice(0, 11);
        formData.value.cuit = clean;
        
        if (clean.length === 0) return;
        if (!isNew.value && clean === originalCuit.value) return;

        if (!isValidCuit(clean)) {
            notificationStore.add('El CUIT ingresado no es válido. Verifique los dígitos.', 'error');
            return;
        }

        // Smart CUIT Check
        try {
            const response = await clientesService.checkCuit(clean, props.clienteId);
            const { status, existing_clients } = response.data;

            if (status === 'NEW') return;

            const otherClients = existing_clients.filter(c => c.id !== props.clienteId);
            
            if (otherClients.length === 0) return;

            conflictModal.value = {
                show: true,
                type: status, 
                clients: otherClients
            };

        } catch (error) {
            console.error("Error checking CUIT:", error);
        }
    }
};

watch(() => props.show, async (newVal) => {
    if (newVal) {
        activeTab.value = 'general';
        await fetchMaestros(); 
        
        if (props.clienteId) {
            loading.value = true;
            const cliente = await store.fetchClienteById(props.clienteId);
            if (cliente) {
                formData.value = { 
                    ...cliente,
                    calle: '', numero: '', piso: '', depto: '', localidad: '', cp: '', provincia: ''
                };
                originalCuit.value = cliente.cuit; 
                domicilios.value = cliente.domicilios || []; // Load for dashboard 
                
                // Extract transporte_id from default domicile
                if (cliente.domicilios && cliente.domicilios.length > 0) {
                    const defaultDom = cliente.domicilios.find(d => d.es_entrega) || cliente.domicilios.find(d => d.es_fiscal) || cliente.domicilios[0];
                    if (defaultDom) {
                        formData.value.transporte_id = defaultDom.transporte_id;
                    }
                }

                if (pendingReactivation.value) {
                    formData.value.activo = true;
                    pendingReactivation.value = false;
                    notificationStore.add(`El cliente "${cliente.razon_social}" ha sido marcado para REACTIVACIÓN.`, 'info', 5000);
                }
            }
            loading.value = false;
        } else {
            formData.value = {
                razon_social: '',
                nombre_fantasia: '',
                cuit: '',
                condicion_iva_id: null,
                whatsapp_empresa: '',
                web_portal_pagos: '',
                datos_acceso_pagos: '',
                activo: true,
                lista_precios_id: null,
                segmento_id: null,
                transporte_id: null,
                limite_credito: 0,
                requiere_auditoria: false,
                calle: '', numero: '', piso: '', depto: '', localidad: '', cp: '', provincia: ''
            };
            
            // Pre-select default transport (Retiro en Local)
            if (transportes.value.length > 0) {
                const retiro = transportes.value.find(t => t.nombre.toLowerCase().includes('retiro'));
                formData.value.transporte_id = retiro ? retiro.id : transportes.value[0].id;
            }
        }
    }
});
watch(() => props.clienteId, async (newId) => {
    if (props.show && newId) {
        loading.value = true;
        const cliente = await store.fetchClienteById(newId);
        if (cliente) {
            formData.value = { ...cliente, calle: '', numero: '', piso: '', depto: '', localidad: '', cp: '', provincia: '' };
            originalCuit.value = cliente.cuit;
            domicilios.value = cliente.domicilios || [];
            
            // Extract transporte_id from default domicile
            if (cliente.domicilios && cliente.domicilios.length > 0) {
                const defaultDom = cliente.domicilios.find(d => d.es_entrega) || cliente.domicilios.find(d => d.es_fiscal) || cliente.domicilios[0];
                if (defaultDom) {
                    formData.value.transporte_id = defaultDom.transporte_id;
                }
            }

            if (pendingReactivation.value) {
                formData.value.activo = true;
                pendingReactivation.value = false;
            }
        }
        loading.value = false;
    }
});

const handleSave = async (force = false) => {
    let cleanCuit = formData.value.cuit.replace(/\D/g, '');
    if (cleanCuit.length > 11) cleanCuit = cleanCuit.slice(0, 11);
    
    if (!isValidCuit(cleanCuit)) {
        notificationStore.add('No se puede guardar: El CUIT es inválido.', 'error');
        return;
    }

    if (!force && !props.clienteId) {
        try {
            const response = await clientesService.checkCuit(cleanCuit, props.clienteId);
            const { status, existing_clients } = response.data;

            if (status !== 'NEW') {
                const otherClients = existing_clients.filter(c => c.id !== props.clienteId);
                if (otherClients.length > 0) {
                    conflictModal.value = {
                        show: true,
                        type: status,
                        clients: otherClients
                    };
                    return; 
                }
            }
        } catch (error) {
            console.error("Error checking CUIT:", error);
        }
    }
    
    let selectedTransport = formData.value.transporte_id;
    if (!selectedTransport && transportes.value.length > 0) {
        // Default to first transport (usually Retiro en Local if seeded first)
        selectedTransport = transportes.value[0].id;
    }

    const payload = {
        razon_social: formData.value.razon_social,
        cuit: cleanCuit,
        condicion_iva_id: formData.value.condicion_iva_id,
        lista_precios_id: formData.value.lista_precios_id,
        activo: formData.value.activo,
        whatsapp_empresa: formData.value.whatsapp_empresa,
        web_portal_pagos: formData.value.web_portal_pagos,
        datos_acceso_pagos: formData.value.datos_acceso_pagos,
        segmento_id: formData.value.segmento_id,
        transporte_id: selectedTransport, 
    };

    if (isNew.value) {
        payload.domicilios = [{
            calle: formData.value.calle,
            numero: formData.value.numero,
            piso: formData.value.piso,
            depto: formData.value.depto,
            localidad: formData.value.localidad,
            cp: formData.value.cp,
            provincia: formData.value.provincia,
            es_fiscal: true,
            es_entrega: true, 
            transporte_id: selectedTransport
        }];
    }

    try {
        if (isNew.value) {
            const newCliente = await store.createCliente(payload);
            emit('saved', newCliente.id);
            emit('close');
            if (newCliente.requiere_auditoria) {
                notificationStore.add('⚠️ Cliente creado con CUIT duplicado. Se ha marcado para AUDITORÍA.', 'warning', 5000);
            } else {
                notificationStore.add('Cliente creado exitosamente.', 'success');
            }
        } else {
            await store.updateCliente(props.clienteId, payload);
            emit('saved', props.clienteId);
            emit('close');
            notificationStore.add('Cliente actualizado exitosamente.', 'success');
        }
    } catch (error) {
        console.error('Error saving cliente:', error);
        let msg = 'Error al guardar.';
        if (error.response && error.response.data) {
             msg += ' ' + JSON.stringify(error.response.data.detail || error.response.data);
        }
        notificationStore.add(msg, 'error');
    }
};

const handleDelete = async () => {
    if (!confirm('¿Está seguro de dar de BAJA a este cliente? Esta acción es lógica y no borrará historial.')) return;
    try {
        await store.deleteCliente(props.clienteId);
        emit('saved', props.clienteId); 
        emit('close');
        notificationStore.add('Cliente dado de baja exitosamente.', 'success');
    } catch (error) {
        console.error('Error deleting cliente:', error);
        notificationStore.add('Error al dar de baja al cliente.', 'error');
    }
};

const handleValidate = async () => {
    if (!confirm('¿Confirmar validación de este cliente?')) return;
    try {
        await store.approveCliente(props.clienteId);
        notificationStore.add('Cliente validado exitosamente.', 'success');
        emit('saved', props.clienteId);
    } catch (error) {
        console.error('Error validando cliente:', error);
        notificationStore.add('Error al validar cliente.', 'error');
    }
};

const handleHardDelete = async () => {
    if (!confirm('🔥 ATENCIÓN: ¿Está seguro de ELIMINAR FÍSICAMENTE este registro?\n\nEsta acción es IRREVERSIBLE y solo funcionará si el cliente NO tiene historial.')) return;
    if (!confirm('Confirme nuevamente: ¿ELIMINAR DEFINITIVAMENTE?')) return;

    try {
        await store.hardDeleteCliente(props.clienteId);
        notificationStore.add('Cliente eliminado físicamente.', 'success');
        emit('saved', props.clienteId);
        emit('close');
    } catch (error) {
        console.error('Error eliminando cliente:', error);
        if (error.response && error.response.status === 409) {
            notificationStore.add('⛔ NO SE PUEDE ELIMINAR: El cliente tiene historial.', 'error', 5000);
        } else {
            notificationStore.add('Error al eliminar cliente.', 'error');
        }
    }
};

const close = () => {
    emit('close');
};

const handleKeydown = (e) => {
    if (showTransporteForm.value || showSegmentoForm.value || conflictModal.value.show) return;
    // Check if DomicilioGrid modal is open
    if (domicileGridRef.value && domicileGridRef.value.isFormOpen) return;
    
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

const handleCreateSegmento = () => {
    showSegmentoForm.value = true;
};

const handleCreateTransporte = () => {
    showTransporteForm.value = true;
};

const onSegmentoSaved = async (newSegmento) => {
    const res = await maestrosService.getSegmentos();
    segmentos.value = res.data;
    formData.value.segmento_id = newSegmento.id;
    showSegmentoForm.value = false;
};

const onTransporteSaved = async (newTransporte) => {
    const res = await maestrosService.getTransportes();
    transportes.value = res.data;
    formData.value.transporte_id = newTransporte.id;
    showTransporteForm.value = false; 
};

const domicileGridRef = ref(null);

const handleEditDomicilio = (domicilio, createFiscal = false) => {
    activeTab.value = 'logistica';
    // Wait for v-show to make it visible (though it's always mounted now, we might need a tick)
    setTimeout(() => {
        if (domicileGridRef.value) {
            if (createFiscal) {
                domicileGridRef.value.openForm({ es_fiscal: true, es_entrega: true });
            } else if (domicilio) {
                domicileGridRef.value.openForm(domicilio);
            }
        }
    }, 100);
};

const handleWhatsappFocus = () => {
    if (!formData.value.whatsapp_empresa) {
        formData.value.whatsapp_empresa = '+54 9 ';
    }
};

const handleWhatsappBlur = () => {
    if (formData.value.whatsapp_empresa === '+54 9 ') {
        formData.value.whatsapp_empresa = '';
    }
};
</script>

<template>
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <div class="bg-white w-full max-w-5xl h-[85vh] rounded-lg shadow-2xl flex flex-col overflow-hidden animate-scale-in relative">
            
            <!-- HEADER -->
            <div class="px-6 py-3 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                <div>
                    <h2 class="text-lg font-bold text-gray-800 uppercase tracking-wide">
                        {{ isNew ? 'Nueva Ficha de Cliente' : formData.razon_social || 'Editar Cliente' }}
                    </h2>
                    <p v-if="!isNew" class="text-xs text-gray-500 font-mono">ID: {{ props.clienteId }} | CUIT: {{ formData.cuit }}</p>
                </div>
                <div class="flex gap-3">
                    <button 
                        @click="close"
                        class="px-4 py-1.5 rounded border border-gray-300 text-gray-600 font-bold text-xs hover:bg-gray-100 transition-colors flex items-center gap-2"
                    >
                        <span class="bg-gray-200 px-1 rounded text-[10px] text-gray-500">ESC</span> CERRAR
                    </button>
                    
                    <button 
                        v-if="!isNew"
                        @click="handleDelete"
                        class="px-4 py-1.5 rounded bg-red-100 text-red-700 border border-red-200 font-bold text-xs hover:bg-red-200 transition-colors flex items-center gap-2"
                        title="Baja Lógica (Recomendado)"
                    >
                        BAJA
                    </button>

                    <button 
                        v-if="!isNew"
                        @click="handleHardDelete"
                        class="px-2 py-1.5 rounded bg-white text-red-500 border border-red-200 font-bold text-xs hover:bg-red-50 transition-colors flex items-center gap-2"
                        title="Eliminar Físicamente (Solo sin historial)"
                    >
                        🗑️
                    </button>

                    <button 
                        @click="handleSave()"
                        class="px-4 py-1.5 rounded text-white font-bold text-xs shadow-sm transition-colors flex items-center gap-2"
                        :class="isNew ? 'bg-[#54cb9b] hover:bg-[#45b085]' : 'bg-violet-600 hover:bg-violet-700'"
                    >
                        <span class="bg-white/20 px-1 rounded text-[10px]">F10</span> {{ isNew ? 'GUARDAR' : 'MODIFICAR' }}
                    </button>
                </div>
            </div>

            <!-- AUDITOR MODE ALERT BAR -->
            <div v-if="formData.requiere_auditoria" class="bg-amber-100 border-b border-amber-200 px-6 py-2 flex justify-between items-center animate-pulse-slow">
                <div class="flex items-center gap-2 text-amber-800">
                    <span class="text-xl">⚠️</span>
                    <div>
                        <p class="text-xs font-bold uppercase tracking-wider">Registro en Revisión (CUIT Duplicado)</p>
                        <p class="text-[10px] opacity-80">Este cliente requiere validación por un supervisor.</p>
                    </div>
                </div>
                <div class="flex gap-2">
                    <button 
                        @click="handleHardDelete"
                        class="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-xs font-bold rounded shadow-sm flex items-center gap-1 transition-colors"
                        title="Eliminar Físicamente (Solo si no tiene historia)"
                    >
                        <span>🔥</span> ELIMINAR
                    </button>
                    <button 
                        @click="handleValidate"
                        class="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-xs font-bold rounded shadow-sm flex items-center gap-1 transition-colors"
                    >
                        <span>✅</span> VALIDAR
                    </button>
                </div>
            </div>

            <!-- TABS -->
            <div class="flex border-b border-gray-200 bg-white px-6">
                <button 
                    @click="activeTab = 'general'"
                    class="px-4 py-3 text-sm font-bold border-b-2 transition-colors flex items-center gap-2"
                    :class="activeTab === 'general' ? 'border-[#54cb9b] text-[#54cb9b]' : 'border-transparent text-gray-400 hover:text-gray-600'"
                >
                    1. GENERAL
                </button>
                <button 
                    @click="activeTab = 'logistica'"
                    class="px-4 py-3 text-sm font-bold border-b-2 transition-colors flex items-center gap-2"
                    :class="activeTab === 'logistica' ? 'border-[#54cb9b] text-[#54cb9b]' : 'border-transparent text-gray-400 hover:text-gray-600'"
                    :disabled="isNew"
                >
                    2. LOGÍSTICA
                    <span v-if="isNew" class="text-[10px] bg-gray-100 px-1 rounded text-gray-400">Guardar primero</span>
                </button>
                <button 
                    @click="activeTab = 'agenda'"
                    class="px-4 py-3 text-sm font-bold border-b-2 transition-colors flex items-center gap-2"
                    :class="activeTab === 'agenda' ? 'border-[#54cb9b] text-[#54cb9b]' : 'border-transparent text-gray-400 hover:text-gray-600'"
                    :disabled="isNew"
                >
                    3. AGENDA
                </button>
                
                <div class="w-px h-6 bg-gray-200 mx-2 self-center"></div>

                <button disabled class="px-4 py-3 text-sm font-bold border-b-2 border-transparent text-gray-300 cursor-not-allowed">
                    4. HISTORIAL
                </button>
                <button disabled class="px-4 py-3 text-sm font-bold border-b-2 border-transparent text-gray-300 cursor-not-allowed">
                    5. DOCUMENTOS
                </button>
            </div>

            <!-- CONTENT -->
            <div class="flex-1 overflow-y-auto p-6 bg-slate-50 relative">
                
                <!-- TAB: GENERAL -->
                <div v-show="activeTab === 'general'" class="max-w-7xl mx-auto">
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        
                        <!-- LEFT COLUMN (FORMS) -->
                        <div class="lg:col-span-2 space-y-6">
                            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                                <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 border-b border-gray-100 pb-2">Datos Principales</h3>
                                <div class="grid grid-cols-12 gap-4">
                                    <div class="col-span-12 md:col-span-8">
                                        <label class="block text-xs font-bold text-gray-600 mb-1">Razón Social *</label>
                                        <input v-model="formData.razon_social" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" placeholder="Nombre legal de la empresa" />
                                    </div>
                                    <div class="col-span-12 md:col-span-4">
                                        <label class="block text-xs font-bold text-gray-600 mb-1">CUIT *</label>
                                        <input 
                                            v-model="formData.cuit" 
                                            @input="handleCuitInput"
                                            @blur="handleCuitBlur"
                                            type="text" 
                                            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none font-mono" 
                                            placeholder="Solo números"
                                            maxlength="11"
                                        />
                                    </div>
                                    <div class="col-span-12 md:col-span-6">
                                        <label class="block text-xs font-bold text-gray-600 mb-1">Nombre de Fantasía</label>
                                        <input v-model="formData.nombre_fantasia" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                                    </div>
                                    <div class="col-span-12 md:col-span-6">
                                        <label class="block text-xs font-bold text-gray-600 mb-1">Condición IVA</label>
                                        <select v-model="formData.condicion_iva_id" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none bg-white">
                                            <option :value="null">Seleccionar...</option>
                                            <option v-for="c in condicionesIva" :key="c.id" :value="c.id">{{ c.nombre }}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                                <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 border-b border-gray-100 pb-2">Gestión y Contacto</h3>
                                <div class="grid grid-cols-12 gap-4">
                                    <div class="col-span-12 md:col-span-6">
                                        <SmartSelect 
                                            label="Segmento / Ramo"
                                            v-model="formData.segmento_id"
                                            :options="segmentos"
                                            @create-new="handleCreateSegmento"
                                        />
                                    </div>
                                    <div class="col-span-12 md:col-span-6">
                                        <label class="block text-xs font-bold text-gray-600 mb-1">WhatsApp Empresa</label>
                                        <input 
                                            v-model="formData.whatsapp_empresa" 
                                            @focus="handleWhatsappFocus"
                                            @blur="handleWhatsappBlur"
                                            type="text" 
                                            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" 
                                            placeholder="+54 9 ..." 
                                        />
                                    </div>
                                    <div class="col-span-12">
                                        <label class="block text-xs font-bold text-gray-600 mb-1">Web / Portal de Pagos</label>
                                        <input v-model="formData.web_portal_pagos" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" placeholder="https://..." />
                                    </div>
                                    <div class="col-span-12">
                                        <label class="block text-xs font-bold text-gray-600 mb-1">Datos de Acceso (Usuario/Pass)</label>
                                        <textarea v-model="formData.datos_acceso_pagos" rows="2" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" placeholder="Información interna para cobranzas..."></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- RIGHT COLUMN (DOMICILE DASHBOARD) -->
                        <div class="lg:col-span-1 space-y-6">
                            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 h-full flex flex-col">
                                <div class="flex justify-between items-center mb-4 border-b border-gray-100 pb-2">
                                    <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider">Logística</h3>
                                    <button @click="activeTab = 'logistica'" class="text-xs text-[#54cb9b] font-bold hover:underline">VER DETALLE</button>
                                </div>
                                
                                <div class="space-y-4 flex-1 overflow-y-auto pr-1">
                                    <!-- Fiscal Address Card -->
                                    <div 
                                        class="p-3 rounded border transition-colors cursor-pointer group relative"
                                        :class="domicilioFiscal ? 'bg-blue-50 border-blue-100 hover:border-blue-300' : 'bg-red-50 border-red-100'"
                                        @dblclick="handleEditDomicilio(domicilioFiscal, !domicilioFiscal)"
                                        title="Doble click para editar"
                                    >
                                        <div class="flex justify-between items-start mb-1">
                                            <span class="text-[10px] font-bold uppercase tracking-wider" :class="domicilioFiscal ? 'text-blue-600' : 'text-red-600'">
                                                {{ domicilioFiscal ? 'Domicilio Fiscal' : 'Falta Domicilio Fiscal' }}
                                            </span>
                                            <span v-if="domicilioFiscal" class="text-xs opacity-0 group-hover:opacity-100 transition-opacity text-blue-400">✎</span>
                                        </div>
                                        
                                        <div v-if="domicilioFiscal">
                                            <p class="text-sm font-bold text-gray-800">{{ domicilioFiscal.calle }} {{ domicilioFiscal.numero }}</p>
                                            <p class="text-xs text-gray-600">{{ domicilioFiscal.localidad }}</p>
                                            <p class="text-[10px] text-gray-400 mt-1">{{ provincias.find(p => p.id === domicilioFiscal.provincia_id)?.nombre }}</p>
                                        </div>
                                        <div v-else class="flex flex-col gap-2">
                                            <p class="text-xs text-red-500 font-bold">REQUERIDO</p>
                                            <button 
                                                @click.stop="handleEditDomicilio(null, true)"
                                                class="text-[10px] bg-red-100 text-red-600 px-2 py-1 rounded font-bold hover:bg-red-200 transition-colors text-center"
                                            >
                                                + AGREGAR AHORA
                                            </button>
                                        </div>
                                    </div>

                                    <!-- Delivery Address List -->
                                    <div class="mt-4">
                                        <div class="flex justify-between items-center mb-2">
                                            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider">
                                                Entrega <span class="text-gray-400 font-normal">({{ domiciliosEntrega.length }} sucursales de entrega)</span>
                                            </h4>
                                        </div>

                                        <div class="space-y-2">
                                            <div v-if="domiciliosEntrega.length === 0" class="p-3 bg-gray-50 rounded border border-gray-100 text-center">
                                                <p class="text-xs text-gray-400 italic">No hay sucursales adicionales.</p>
                                                <p v-if="domicilioFiscal?.es_entrega" class="text-[10px] text-green-600 mt-1 font-bold">✓ Se usa el Fiscal para entregas</p>
                                            </div>

                                            <div 
                                                v-for="(dom, index) in domiciliosEntrega.slice(0, 5)" 
                                                :key="dom.id || index"
                                                class="p-2 bg-green-50 rounded border border-green-100 hover:border-green-300 transition-colors cursor-pointer group relative"
                                                @dblclick="handleEditDomicilio(dom)"
                                                title="Doble click para editar"
                                            >
                                                <div class="flex justify-between items-start">
                                                    <div>
                                                        <p class="text-xs font-bold text-gray-800">{{ dom.calle }} {{ dom.numero }}</p>
                                                        <p class="text-[10px] text-gray-600">{{ dom.localidad }}</p>
                                                    </div>
                                                    <span class="text-xs opacity-0 group-hover:opacity-100 transition-opacity text-green-400">✎</span>
                                                </div>
                                                <div class="mt-1 flex gap-1">
                                                    <span v-if="dom.transporte_id" class="text-[9px] bg-white px-1 rounded border border-green-200 text-green-700 truncate max-w-[120px]">
                                                        🚚 {{ transportes.find(t => t.id === dom.transporte_id)?.nombre || 'Transporte' }}
                                                    </span>
                                                </div>
                                            </div>
                                            
                                            <div v-if="domiciliosEntrega.length > 5" class="text-center pt-1">
                                                <span class="text-[10px] text-gray-400 italic">+ {{ domiciliosEntrega.length - 5 }} más... ver en Logística</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- TAB: LOGÍSTICA -->
                <div v-show="activeTab === 'logistica'" class="h-full">
                    <DomicilioGrid 
                        ref="domicileGridRef"
                        :cliente-id="props.clienteId" 
                        @change="handleDomicilioChange"
                    />
                </div>

                <!-- TAB: AGENDA -->
                <div v-show="activeTab === 'agenda'" class="h-full">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
                        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 h-full flex flex-col">
                            <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Contactos</h3>
                            <div class="flex-1 overflow-hidden">
                                <VinculoGrid :cliente-id="props.clienteId" />
                            </div>
                        </div>
                        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                            <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Próximamente</h3>
                            <p class="text-gray-400 text-sm italic">Gestión de eventos y recordatorios en desarrollo.</p>
                        </div>
                    </div>
                </div>

            <div v-if="conflictModal.show" class="absolute inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                <div class="bg-white w-full max-w-md rounded-lg shadow-2xl overflow-hidden animate-scale-in border border-gray-200">
                    <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
                            <span v-if="conflictModal.type === 'INACTIVE'" class="text-red-500">⚠️ Cliente Inactivo</span>
                            <span v-else class="text-orange-500">⚠️ CUIT Existente</span>
                        </h3>
                    </div>
                    <div class="p-6">
                        <p class="text-sm text-gray-600 mb-4">
                            El CUIT <strong>{{ formData.cuit }}</strong> ya está asociado a los siguientes clientes:
                        </p>
                        <ul class="space-y-2 mb-6 max-h-40 overflow-y-auto">
                            <li v-for="c in conflictModal.clients" :key="c.id" class="p-3 bg-gray-50 rounded border border-gray-200 flex justify-between items-center">
                                <div>
                                    <p class="font-bold text-sm text-gray-800">{{ c.razon_social }}</p>
                                    <p class="text-xs text-gray-500" v-if="c.nombre_fantasia">{{ c.nombre_fantasia }}</p>
                                </div>
                                <span class="text-[10px] px-2 py-1 rounded font-bold" :class="c.activo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                                    {{ c.activo ? 'ACTIVO' : 'INACTIVO' }}
                                </span>
                            </li>
                        </ul>
                        
                        <div class="flex flex-col gap-2">
                            <template v-if="conflictModal.type === 'INACTIVE'">
                                <button 
                                    v-for="c in conflictModal.clients"
                                    :key="c.id"
                                    @click="resolveConflict('reactivate', c)"
                                    class="w-full py-2 bg-[#54cb9b] text-white font-bold rounded hover:bg-[#45b085] transition-colors text-sm"
                                >
                                    Reactivar {{ c.razon_social }}
                                </button>
                            </template>
                            <template v-else>
                                <button 
                                    v-for="c in conflictModal.clients"
                                    :key="c.id"
                                    @click="resolveConflict('edit', c)"
                                    class="w-full py-2 bg-blue-500 text-white font-bold rounded hover:bg-blue-600 transition-colors text-sm"
                                >
                                    Editar {{ c.razon_social }}
                                </button>
                                <button 
                                    @click="resolveConflict('create')"
                                    class="w-full py-2 bg-gray-100 text-gray-700 font-bold rounded hover:bg-gray-200 transition-colors text-sm border border-gray-300"
                                >
                                    Crear Cuenta Separada
                                </button>
                            </template>
                            <button 
                                @click="conflictModal.show = false"
                                class="w-full py-2 text-gray-400 font-bold text-xs hover:text-gray-600 mt-2"
                            >
                                Cancelar (Corregir CUIT)
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- STACKED MODALS -->
        <SegmentoForm 
            :show="showSegmentoForm" 
            @close="showSegmentoForm = false" 
            @saved="onSegmentoSaved"
        />

        <TransporteForm 
            :show="showTransporteForm" 
            @close="showTransporteForm = false" 
            @saved="onTransporteSaved"
        />
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
