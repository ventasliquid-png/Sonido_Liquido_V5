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

// ... (rest of setup)

const handleCuitBlur = async () => {
    if (formData.value.cuit) {
        let clean = formData.value.cuit.replace(/\D/g, '');
        if (clean.length > 11) clean = clean.slice(0, 11);
        formData.value.cuit = clean;
        
        if (clean.length > 0) {
            if (!isValidCuit(clean)) {
                notificationStore.add('El CUIT ingresado no es válido. Verifique los dígitos.', 'error');
                return;
            }

            // Smart CUIT Check
            try {
                const response = await clientesService.checkCuit(clean);
                const { status, existing_clients } = response.data;

                if (status === 'NEW') return;

                // Filter out current client if editing
                const otherClients = existing_clients.filter(c => c.id !== props.clienteId);
                
                if (otherClients.length === 0) return; // Only self found

                conflictModal.value = {
                    show: true,
                    type: status, // INACTIVE or EXISTS
                    clients: otherClients
                };

            } catch (error) {
                console.error("Error checking CUIT:", error);
            }
        }
    }
};

// ...

// Reset or Load Data
watch(() => props.show, async (newVal) => {
    if (newVal) {
        activeTab.value = 'general';
        await fetchMaestros(); // Ensure maestros are loaded
        
        if (props.clienteId) {
            loading.value = true;
            const cliente = await store.fetchClienteById(props.clienteId);
            if (cliente) {
                formData.value = { ...cliente };
                if (pendingReactivation.value) {
                    formData.value.activo = true;
                    pendingReactivation.value = false;
                    notificationStore.add(`El cliente "${cliente.razon_social}" ha sido marcado para REACTIVACIÓN. Verifique los datos y presione GUARDAR (F10) para confirmar.`, 'info', 5000);
                }
            }
            loading.value = false;
        } else {
            // ... (reset form)
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
                requiere_auditoria: false
            };
        }
    }
});

watch(() => props.clienteId, async (newId) => {
    if (props.show && newId) {
        loading.value = true;
        const cliente = await store.fetchClienteById(newId);
        if (cliente) {
            formData.value = { ...cliente };
            if (pendingReactivation.value) {
                formData.value.activo = true;
                pendingReactivation.value = false;
                notificationStore.add(`El cliente "${cliente.razon_social}" ha sido marcado para REACTIVACIÓN. Verifique los datos y presione GUARDAR (F10) para confirmar.`, 'info', 5000);
            }
        }
        loading.value = false;
    }
});

const handleSave = async (force = false) => {
    // Pre-save validation
    let cleanCuit = formData.value.cuit.replace(/\D/g, '');
    if (cleanCuit.length > 11) cleanCuit = cleanCuit.slice(0, 11);
    
    if (!isValidCuit(cleanCuit)) {
        notificationStore.add('No se puede guardar: El CUIT es inválido.', 'error');
        return;
    }

    // ... (Smart CUIT Check logic remains same)
    if (!force && !props.clienteId) {
        try {
            const response = await clientesService.checkCuit(cleanCuit);
            const { status, existing_clients } = response.data;

            if (status !== 'NEW') {
                // Filter out current client if editing (redundant check for new, but safe)
                const otherClients = existing_clients.filter(c => c.id !== props.clienteId);
                
                if (otherClients.length > 0) {
                    conflictModal.value = {
                        show: true,
                        type: status, // INACTIVE or EXISTS
                        clients: otherClients
                    };
                    return; // Stop save to show modal
                }
            }
        } catch (error) {
            console.error("Error checking CUIT:", error);
        }
    }
    
    // Prepare Payload (Sanitization)
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
        transporte_id: formData.value.transporte_id,
    };

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
            if (error.response.data.detail) {
                if (typeof error.response.data.detail === 'string') {
                    msg += ' ' + error.response.data.detail;
                } else if (Array.isArray(error.response.data.detail)) {
                    msg += '\n' + error.response.data.detail.map(e => `- ${e.loc.join('.')}: ${e.msg}`).join('\n');
                } else {
                    msg += ' ' + JSON.stringify(error.response.data.detail);
                }
            }
        } else if (error.message) {
            msg += ' ' + error.message;
        }
        notificationStore.add(msg, 'error');
    }
};

const handleDelete = async () => {
    // Baja Lógica
    if (!confirm('¿Está seguro de dar de BAJA a este cliente? Esta acción es lógica y no borrará historial.')) return;
    try {
        await store.deleteCliente(props.clienteId);
        emit('saved', props.clienteId); // Refresh list
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
            notificationStore.add('⛔ NO SE PUEDE ELIMINAR: El cliente tiene historial (ventas, movimientos, etc).\n\nDebe usar la BAJA LÓGICA (Botón "BAJA").', 'error', 5000);
        } else {
            notificationStore.add('Error al eliminar cliente: ' + (error.response?.data?.detail || error.message), 'error');
        }
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

const handleCreateSegmento = () => {
    showSegmentoForm.value = true;
};

const handleCreateTransporte = () => {
    showTransporteForm.value = true;
};

const onSegmentoSaved = async (newSegmento) => {
    // Refresh list and select new item
    const res = await maestrosService.getSegmentos();
    segmentos.value = res.data;
    formData.value.segmento_id = newSegmento.id;
    showSegmentoForm.value = false;
};

const onTransporteSaved = async (newTransporte) => {
    // Refresh list and select new item
    const res = await maestrosService.getTransportes();
    transportes.value = res.data;
    formData.value.transporte_id = newTransporte.id;
    // Note: TransporteForm might stay open if user wants to add nodes, 
    // but here we might want to close it or let the user close it.
    // The TransporteForm emits 'saved' on create/update.
    // If we want to auto-select, we do it here.
    // If the form stays open, that's fine, but usually F4 flow implies "create and return".
    // Let's assume the user closes it manually or we close it.
    // In my TransporteForm implementation, I emit 'close' after save if it's an update, but not if new.
    // Wait, I changed it to emit 'close' always? No, I left a comment.
    // Let's force close here if we want "Quick Add" behavior.
    showTransporteForm.value = false; 
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
                <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/50 z-10">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#54cb9b]"></div>
                </div>

                <!-- TAB: GENERAL -->
                <div v-if="activeTab === 'general'" class="max-w-4xl mx-auto">
                    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
                        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-100 pb-2">Datos de Identificación</h3>
                        <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
                            <div class="md:col-span-8">
                                <label class="block text-xs font-bold text-gray-600 mb-1">Razón Social <span class="text-red-500">*</span></label>
                                <input v-model="formData.razon_social" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                            </div>
                            <div class="md:col-span-4">
                                <label class="block text-xs font-bold text-gray-600 mb-1">CUIT <span class="text-red-500">*</span></label>
                                <input 
                                    v-model="formData.cuit" 
                                    @input="handleCuitInput"
                                    @blur="handleCuitBlur"
                                    type="text" 
                                    placeholder="Sin guiones"
                                    class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none font-mono" 
                                />
                            </div>
                            <div class="md:col-span-6">
                                <label class="block text-xs font-bold text-gray-600 mb-1">Nombre Fantasía</label>
                                <input v-model="formData.nombre_fantasia" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                            </div>
                            <div class="md:col-span-6">
                                <label class="block text-xs font-bold text-gray-600 mb-1">Condición IVA</label>
                                <select v-model="formData.condicion_iva_id" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none bg-white">
                                    <option :value="null">Seleccionar...</option>
                                    <option v-for="cond in condicionesIva" :key="cond.id" :value="cond.id">
                                        {{ cond.nombre }}
                                    </option>
                                </select>
                            </div>
                            <div class="md:col-span-6">
                                <SmartSelect 
                                    label="Segmento"
                                    v-model="formData.segmento_id"
                                    :options="segmentos"
                                    @create-new="handleCreateSegmento"
                                />
                            </div>
                            <div class="md:col-span-6">
                                <SmartSelect 
                                    label="Transporte"
                                    v-model="formData.transporte_id"
                                    :options="transportes"
                                    @create-new="handleCreateTransporte"
                                />
                            </div>
                        </div>
                    </div>

                    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-100 pb-2">Gestión y Contacto</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-xs font-bold text-gray-600 mb-1">WhatsApp Empresa</label>
                                <input v-model="formData.whatsapp_empresa" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-600 mb-1">Web / Portal Pagos</label>
                                <input v-model="formData.web_portal_pagos" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                            </div>
                            <div class="md:col-span-2">
                                <label class="block text-xs font-bold text-gray-600 mb-1">Datos de Acceso (Interno)</label>
                                <textarea v-model="formData.datos_acceso_pagos" rows="2" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none font-mono text-xs"></textarea>
                            </div>
                            <div class="flex items-center mt-2">
                                <label class="flex items-center gap-2 cursor-pointer">
                                    <input v-model="formData.activo" type="checkbox" class="form-checkbox h-4 w-4 text-[#54cb9b] rounded border-gray-300 focus:ring-[#54cb9b]">
                                    <span class="text-sm font-bold text-gray-700">Cliente Activo</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- TAB: LOGÍSTICA -->
                <div v-if="activeTab === 'logistica'" class="h-full">
                    <DomicilioGrid :clienteId="clienteId" />
                </div>

                <!-- TAB: AGENDA -->
                <div v-if="activeTab === 'agenda'" class="h-full">
                    <VinculoGrid :clienteId="clienteId" />
                </div>

            </div>

            <!-- CONFLICT MODAL OVERLAY -->
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
