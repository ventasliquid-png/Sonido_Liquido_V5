<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useLogisticaStore } from '../../stores/logistica';
import { useNotificationStore } from '../../stores/notification';
import maestrosService from '../../services/maestros';

const props = defineProps({
    show: Boolean,
    id: {
        type: [String, Number],
        default: null
    }
});

const emit = defineEmits(['close', 'saved']);

const store = useLogisticaStore();
const notificationStore = useNotificationStore();
const isNew = ref(true);
const provincias = ref([]);

// ... (rest of setup)

const handleSaveEmpresa = async () => {
    if (!formData.value.nombre) {
        notificationStore.add('El nombre es obligatorio', 'error');
        return;
    }

    try {
        let savedEmpresa;
        if (isNew.value) {
            savedEmpresa = await store.createEmpresa(formData.value);
            isNew.value = false;
            formData.value = { ...savedEmpresa };
            
            notificationStore.add('Empresa creada exitosamente. Ahora puede agregar nodos/sucursales.', 'success');
            
            // Auto-open node creation for better UX
            setTimeout(() => {
                openNewNodo();
            }, 500);
        } else {
            savedEmpresa = await store.updateEmpresa(formData.value.id, formData.value);
            notificationStore.add('Empresa actualizada exitosamente.', 'success');
        }
        emit('saved', savedEmpresa);
    } catch (error) {
        // Handle 409 Conflict specifically
        if (error.response && error.response.status === 409) {
            notificationStore.add(error.response.data.detail, 'error');
        } else {
            notificationStore.add('Error al guardar empresa: ' + (error.response?.data?.detail || error.message), 'error');
        }
    }
};

// Nodo Logic
const openNewNodo = () => {
    if (isNew.value) {
        notificationStore.add('Primero debe guardar la empresa para agregar nodos.', 'warning');
        return;
    }
    nodoFormData.value = {
        id: null,
        nombre_nodo: '',
        direccion_completa: '',
        provincia_id: '',
        es_punto_despacho: false,
        es_punto_retiro: false,
        horario_operativo: '',
        contacto_operativo: ''
    };
    showNodoForm.value = true;
};

const editNodo = (nodo) => {
    nodoFormData.value = { ...nodo };
    showNodoForm.value = true;
};

const handleSaveNodo = async () => {
    if (!nodoFormData.value.nombre_nodo || !nodoFormData.value.provincia_id) {
        notificationStore.add('Nombre y Provincia son obligatorios', 'error');
        return;
    }

    try {
        const payload = { ...nodoFormData.value, empresa_id: formData.value.id };
        if (nodoFormData.value.id) {
            await store.updateNodo(nodoFormData.value.id, payload);
            notificationStore.add('Nodo actualizado exitosamente.', 'success');
        } else {
            await store.createNodo(payload);
            notificationStore.add('Nodo creado exitosamente.', 'success');
        }
        showNodoForm.value = false;
        await store.fetchNodos(formData.value.id);
        nodosList.value = [...store.nodos];
    } catch (error) {
        notificationStore.add('Error al guardar nodo: ' + error.message, 'error');
    }
};

const getProvinciaName = (id) => {
    const p = provincias.value.find(p => p.id === id);
    return p ? p.nombre : id;
};

const close = () => {
    emit('close');
};

// Keyboard Shortcuts
const handleKeydown = (e) => {
    if (!props.show) return;
    if (e.key === 'Escape') {
        if (showNodoForm.value) {
            showNodoForm.value = false;
        } else {
            close();
        }
    }
    if (e.key === 'F10') {
        e.preventDefault();
        if (showNodoForm.value) {
            handleSaveNodo();
        } else {
            handleSaveEmpresa();
        }
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
    <div v-if="show" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <div class="bg-white w-full max-w-4xl h-[90vh] rounded-lg shadow-2xl flex flex-col overflow-hidden animate-scale-in relative">
            <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                <h2 class="text-lg font-bold text-gray-800">{{ isNew ? 'Nueva Empresa' : 'Editar Empresa' }}</h2>
                <button @click="close" class="text-gray-500 hover:text-gray-700 font-bold">✕</button>
            </div>
            
            <div class="flex-1 overflow-y-auto p-6 bg-slate-50">
                <!-- Datos Generales -->
                <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
                    <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-100 pb-2">Datos Generales</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="md:col-span-2">
                            <label class="block text-xs font-bold text-gray-600 mb-1">Nombre Empresa <span class="text-red-500">*</span></label>
                            <input v-model="formData.nombre" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-600 mb-1">Web Tracking</label>
                            <input v-model="formData.web_tracking" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-600 mb-1">Teléfono Reclamos</label>
                            <input v-model="formData.telefono_reclamos" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                        </div>
                        <div class="flex items-center gap-4 mt-2">
                            <label class="flex items-center gap-2 cursor-pointer">
                                <input v-model="formData.activo" type="checkbox" class="form-checkbox h-4 w-4 text-[#54cb9b] rounded border-gray-300">
                                <span class="text-sm text-gray-700">Activo</span>
                            </label>
                            <label class="flex items-center gap-2 cursor-pointer">
                                <input v-model="formData.requiere_carga_web" type="checkbox" class="form-checkbox h-4 w-4 text-[#54cb9b] rounded border-gray-300">
                                <span class="text-sm text-gray-700">Requiere Carga Web</span>
                            </label>
                        </div>
                    </div>
                    <div class="mt-4 flex justify-end gap-2">
                         <button @click="close" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 text-xs font-bold">CANCELAR (ESC)</button>
                        <button @click="handleSaveEmpresa" class="bg-[#54cb9b] text-white px-4 py-2 rounded font-bold text-xs hover:bg-[#45b085]">
                            {{ isNew ? 'CREAR EMPRESA (F10)' : 'GUARDAR CAMBIOS (F10)' }}
                        </button>
                    </div>
                </div>

                <!-- Nodos / Sucursales -->
                <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 relative">
                    <div v-if="isNew" class="absolute inset-0 bg-white/80 z-10 flex items-center justify-center backdrop-blur-[1px]">
                        <p class="text-gray-500 font-bold text-sm">Guarde la empresa para gestionar sucursales</p>
                    </div>
                    <div class="flex justify-between items-center mb-4 border-b border-gray-100 pb-2">
                        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider">Nodos / Sucursales</h3>
                        <button @click="openNewNodo" class="text-[#54cb9b] text-xs font-bold hover:underline">+ AGREGAR NODO</button>
                    </div>
                    
                    <div v-if="nodosList.length === 0" class="text-center py-4 text-gray-400 text-xs italic">
                        No hay nodos cargados.
                    </div>
                    <div v-else class="space-y-2">
                        <div v-for="nodo in nodosList" :key="nodo.id" class="p-3 border border-gray-200 rounded flex justify-between items-center hover:bg-slate-50">
                            <div>
                                <p class="font-bold text-sm text-gray-800">{{ nodo.nombre_nodo }}</p>
                                <p class="text-xs text-gray-500">{{ nodo.direccion_completa }} - {{ getProvinciaName(nodo.provincia_id) }}</p>
                            </div>
                            <button @click="editNodo(nodo)" class="text-blue-500 text-xs font-bold hover:underline">EDITAR</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- MODAL NODO (Nested) -->
        <div v-if="showNodoForm" class="fixed inset-0 z-[70] flex items-center justify-center bg-black/20 backdrop-blur-sm p-4">
            <div class="bg-white w-full max-w-lg rounded-lg shadow-2xl p-6 animate-scale-in border border-gray-200">
                <h3 class="text-lg font-bold text-gray-800 mb-4">{{ nodoFormData.id ? 'Editar Nodo' : 'Nuevo Nodo' }}</h3>
                
                <div class="space-y-3">
                    <div>
                        <label class="block text-xs font-bold text-gray-600 mb-1">Nombre Nodo <span class="text-red-500">*</span></label>
                        <input v-model="nodoFormData.nombre_nodo" type="text" placeholder="Ej: Depósito Central" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-600 mb-1">Dirección</label>
                        <input v-model="nodoFormData.direccion_completa" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" />
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-600 mb-1">Provincia <span class="text-red-500">*</span></label>
                        <select v-model="nodoFormData.provincia_id" class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none bg-white">
                            <option value="">Seleccionar...</option>
                            <option v-for="prov in provincias" :key="prov.id" :value="prov.id">{{ prov.nombre }}</option>
                        </select>
                    </div>
                    <div class="flex gap-4">
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input v-model="nodoFormData.es_punto_despacho" type="checkbox" class="form-checkbox h-4 w-4 text-[#54cb9b] rounded border-gray-300">
                            <span class="text-xs text-gray-700">Punto Despacho</span>
                        </label>
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input v-model="nodoFormData.es_punto_retiro" type="checkbox" class="form-checkbox h-4 w-4 text-[#54cb9b] rounded border-gray-300">
                            <span class="text-xs text-gray-700">Punto Retiro</span>
                        </label>
                    </div>
                </div>

                <div class="mt-6 flex justify-end gap-2">
                    <button @click="showNodoForm = false" class="px-4 py-2 text-gray-500 font-bold text-xs hover:bg-gray-100 rounded">CANCELAR</button>
                    <button @click="handleSaveNodo" class="bg-[#54cb9b] text-white px-4 py-2 rounded font-bold text-xs hover:bg-[#45b085]">GUARDAR NODO</button>
                </div>
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
