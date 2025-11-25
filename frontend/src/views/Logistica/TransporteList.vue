<script setup>
import { ref, onMounted, computed } from 'vue';
import { useLogisticaStore } from '../../stores/logistica';
import maestrosService from '../../services/maestros';

const store = useLogisticaStore();
const showModal = ref(false);
const isNew = ref(true);
const provincias = ref([]);

const formData = ref({
    id: null,
    nombre: '',
    web_tracking: '',
    telefono_reclamos: '',
    requiere_carga_web: false,
    formato_etiqueta: 'PROPIA',
    activo: true
});

const nodosList = ref([]);
const showNodoForm = ref(false);
const nodoFormData = ref({
    id: null,
    nombre_nodo: '',
    direccion_completa: '',
    provincia_id: '',
    es_punto_despacho: false,
    es_punto_retiro: false,
    horario_operativo: '',
    contacto_operativo: ''
});

onMounted(async () => {
    await store.fetchEmpresas();
    const provResponse = await maestrosService.getProvincias();
    provincias.value = provResponse.data;
});

const openNew = () => {
    isNew.value = true;
    formData.value = {
        id: null,
        nombre: '',
        web_tracking: '',
        telefono_reclamos: '',
        requiere_carga_web: false,
        formato_etiqueta: 'PROPIA',
        activo: true
    };
    nodosList.value = [];
    showModal.value = true;
};

const openEdit = async (empresa) => {
    isNew.value = false;
    formData.value = { ...empresa };
    await store.fetchNodos(empresa.id);
    nodosList.value = [...store.nodos];
    showModal.value = true;
};

const handleSaveEmpresa = async () => {
    if (!formData.value.nombre) {
        alert('El nombre es obligatorio');
        return;
    }

    try {
        let savedEmpresa;
        if (isNew.value) {
            savedEmpresa = await store.createEmpresa(formData.value);
            isNew.value = false;
            formData.value = { ...savedEmpresa };
            alert('Empresa creada. Ahora puede agregar nodos.');
        } else {
            savedEmpresa = await store.updateEmpresa(formData.value.id, formData.value);
            alert('Empresa actualizada.');
        }
        showModal.value = false;
        // Refresh list
        await store.fetchEmpresas();
    } catch (error) {
        alert('Error al guardar empresa: ' + error.message);
    }
};

const handleDeleteEmpresa = async (empresa) => {
    if (!confirm(`¿Está seguro de dar de baja a ${empresa.nombre}?`)) return;

    try {
        await store.updateEmpresa(empresa.id, { ...empresa, activo: false });
        alert('Empresa dada de baja.');
        await store.fetchEmpresas();
    } catch (error) {
        alert('Error al dar de baja: ' + error.message);
    }
};

// Nodo Logic
const openNewNodo = () => {
    if (isNew.value) {
        alert('Primero debe guardar la empresa para agregar nodos.');
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
        alert('Nombre y Provincia son obligatorios');
        return;
    }

    try {
        const payload = { ...nodoFormData.value, empresa_id: formData.value.id };
        if (nodoFormData.value.id) {
            await store.updateNodo(nodoFormData.value.id, payload);
        } else {
            await store.createNodo(payload);
        }
        showNodoForm.value = false;
        await store.fetchNodos(formData.value.id);
        nodosList.value = [...store.nodos];
    } catch (error) {
        alert('Error al guardar nodo: ' + error.message);
    }
};

const getProvinciaName = (id) => {
    const p = provincias.value.find(p => p.id === id);
    return p ? p.nombre : id;
};

// Keyboard Shortcuts
import { useKeyboardShortcuts } from '../../composables/useKeyboardShortcuts';

useKeyboardShortcuts({
    'F10': () => {
        if (showModal.value) {
            handleSaveEmpresa();
        } else if (showNodoForm.value) {
            handleSaveNodo();
        }
    }
});

</script>

<template>
    <div class="h-full flex flex-col bg-slate-100 text-gray-900 font-sans">
        <!-- HEADER -->
        <div class="bg-[#54cb9b] text-white px-6 py-2 flex justify-between items-center shadow-sm z-20">
            <div>
                <h1 class="text-lg font-bold uppercase tracking-wide">Maestro de Transportes</h1>
                <p class="text-xs text-white/80 font-medium">Logística y Distribución</p>
            </div>
            <button @click="openNew" class="bg-white text-[#54cb9b] px-4 py-1 rounded font-bold text-xs shadow-sm hover:bg-gray-50 transition-colors">
                + NUEVO TRANSPORTE
            </button>
        </div>

        <!-- LIST -->
        <div class="flex-1 p-6 overflow-auto">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Nombre</th>
                            <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Web Tracking</th>
                            <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Teléfono</th>
                            <th class="px-6 py-3 text-center text-xs font-bold text-gray-500 uppercase">Estado</th>
                            <th class="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase">Acciones</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        <tr v-for="empresa in store.empresas" :key="empresa.id" class="hover:bg-slate-50">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ empresa.nombre }}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-blue-600 hover:underline">
                                <a v-if="empresa.web_tracking" :href="empresa.web_tracking" target="_blank">{{ empresa.web_tracking }}</a>
                                <span v-else class="text-gray-400">-</span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ empresa.telefono_reclamos || '-' }}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-center">
                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="empresa.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                                    {{ empresa.activo ? 'Activo' : 'Inactivo' }}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <button @click="openEdit(empresa)" class="text-[#54cb9b] hover:text-[#45b085] font-bold mr-3">EDITAR</button>
                                <button @click="handleDeleteEmpresa(empresa)" class="text-red-400 hover:text-red-600" title="Dar de Baja">
                                    <span class="text-lg">🗑️</span>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- MODAL EMPRESA -->
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div class="bg-white w-full max-w-4xl h-[90vh] rounded-lg shadow-2xl flex flex-col overflow-hidden animate-scale-in">
                <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                    <h2 class="text-lg font-bold text-gray-800">{{ isNew ? 'Nueva Empresa' : 'Editar Empresa' }}</h2>
                    <button @click="showModal = false" class="text-gray-500 hover:text-gray-700 font-bold">✕</button>
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
                        <div class="mt-4 flex justify-end">
                            <button @click="handleSaveEmpresa" class="bg-[#54cb9b] text-white px-4 py-2 rounded font-bold text-xs hover:bg-[#45b085]">
                                {{ isNew ? 'CREAR EMPRESA' : 'GUARDAR CAMBIOS' }}
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
        </div>

        <!-- MODAL NODO (Nested) -->
        <div v-if="showNodoForm" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/20 backdrop-blur-sm p-4">
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
