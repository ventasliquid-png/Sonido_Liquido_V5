<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useClientesStore } from '../../stores/clientes';
import DomicilioGrid from './components/DomicilioGrid.vue';
import VinculoGrid from './components/VinculoGrid.vue';

const props = defineProps({
    show: Boolean,
    clienteId: {
        type: String,
        default: null
    }
});

const emit = defineEmits(['close', 'saved']);

const store = useClientesStore();
const activeTab = ref('general');

const formData = ref({
    razon_social: '',
    cuit: '',
    whatsapp_empresa: '',
    web_portal_pagos: '',
    datos_acceso_pagos: '',
    activo: true,
    condicion_iva_id: null, // TODO: Selects de Maestros
    lista_precios_id: null
});

const isNew = computed(() => !props.clienteId);

// Reset or Load Data
watch(() => props.show, async (newVal) => {
    if (newVal) {
        activeTab.value = 'general';
        if (props.clienteId) {
            const cliente = await store.fetchClienteById(props.clienteId);
            if (cliente) {
                formData.value = { ...cliente };
            }
        } else {
            formData.value = {
                razon_social: '',
                cuit: '',
                whatsapp_empresa: '',
                web_portal_pagos: '',
                datos_acceso_pagos: '',
                activo: true,
                condicion_iva_id: null,
                lista_precios_id: null
            };
        }
    }
});

const handleSave = async () => {
    try {
        if (isNew.value) {
            const newCliente = await store.createCliente(formData.value);
            // Si es nuevo, podríamos cerrar o cambiar a modo edición para permitir cargar domicilios.
            // Por UX, mejor cambiar a modo edición (emitimos saved con el ID).
            emit('saved', newCliente.id);
            alert('Cliente creado. Ahora puede cargar domicilios y contactos.');
        } else {
            await store.updateCliente(props.clienteId, formData.value);
            emit('saved', props.clienteId);
            alert('Cliente actualizado.');
        }
    } catch (error) {
        alert('Error al guardar: ' + error);
    }
};

const close = () => {
    emit('close');
};
</script>

<template>
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm">
        <div class="bg-[#1f2937] w-full max-w-4xl h-[90vh] rounded-lg shadow-2xl flex flex-col border border-gray-700">
            <!-- Header -->
            <div class="px-6 py-4 border-b border-gray-700 flex justify-between items-center bg-[#1a1a2e] rounded-t-lg">
                <div>
                    <h2 class="text-xl font-bold text-brand">
                        {{ isNew ? 'Nuevo Cliente' : 'Editar Cliente' }}
                    </h2>
                    <p v-if="!isNew" class="text-sm text-gray-400">{{ formData.razon_social }} ({{ formData.cuit }})</p>
                </div>
                <button @click="close" class="text-gray-400 hover:text-white text-2xl">&times;</button>
            </div>

            <!-- Tabs -->
            <div class="flex border-b border-gray-700 bg-[#1f2937]">
                <button 
                    v-for="tab in ['general', 'logistica', 'agenda', 'historial', 'documentos']" 
                    :key="tab"
                    @click="activeTab = tab"
                    class="px-6 py-3 text-sm font-medium transition-colors border-b-2"
                    :class="activeTab === tab ? 'border-brand text-brand bg-gray-800' : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-800'"
                >
                    {{ tab.charAt(0).toUpperCase() + tab.slice(1) }}
                </button>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto p-6 bg-[#1f2937]">
                
                <!-- Tab: General -->
                <div v-if="activeTab === 'general'" class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-400 mb-1">Razón Social</label>
                            <input v-model="formData.razon_social" type="text" class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-gray-200 focus:border-brand focus:outline-none" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-400 mb-1">CUIT</label>
                            <input v-model="formData.cuit" type="text" class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-gray-200 focus:border-brand focus:outline-none" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-400 mb-1">WhatsApp Empresa</label>
                            <input v-model="formData.whatsapp_empresa" type="text" class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-gray-200 focus:border-brand focus:outline-none" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-400 mb-1">Web Portal Pagos</label>
                            <input v-model="formData.web_portal_pagos" type="text" class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-gray-200 focus:border-brand focus:outline-none" />
                        </div>
                        <div class="md:col-span-2">
                            <label class="block text-sm font-medium text-gray-400 mb-1">Datos Acceso Pagos</label>
                            <textarea v-model="formData.datos_acceso_pagos" rows="3" class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-gray-200 focus:border-brand focus:outline-none"></textarea>
                        </div>
                        <div class="flex items-center">
                            <input v-model="formData.activo" type="checkbox" id="activo" class="mr-2 h-4 w-4 text-brand bg-gray-900 border-gray-700 rounded focus:ring-brand">
                            <label for="activo" class="text-sm font-medium text-gray-400">Cliente Activo</label>
                        </div>
                    </div>
                    
                    <div class="mt-6 flex justify-end">
                        <button @click="handleSave" class="bg-brand hover:bg-green-600 text-white px-6 py-2 rounded font-medium shadow-lg shadow-brand/20 transition-all">
                            {{ isNew ? 'Crear Cliente' : 'Guardar Cambios' }}
                        </button>
                    </div>
                </div>

                <!-- Tab: Logística -->
                <div v-if="activeTab === 'logistica'">
                    <DomicilioGrid :clienteId="clienteId" />
                </div>

                <!-- Tab: Agenda -->
                <div v-if="activeTab === 'agenda'">
                    <VinculoGrid :clienteId="clienteId" />
                </div>

                <!-- Tab: Historial (Stub) -->
                <div v-if="activeTab === 'historial'" class="flex flex-col items-center justify-center h-full text-gray-500">
                    <span class="text-4xl mb-2">🚧</span>
                    <p>Módulo Historial en construcción</p>
                </div>

                <!-- Tab: Documentos (Stub) -->
                <div v-if="activeTab === 'documentos'" class="flex flex-col items-center justify-center h-full text-gray-500">
                    <span class="text-4xl mb-2">📂</span>
                    <p>Gestión Documental próximamente</p>
                </div>

            </div>
        </div>
    </div>
</template>
