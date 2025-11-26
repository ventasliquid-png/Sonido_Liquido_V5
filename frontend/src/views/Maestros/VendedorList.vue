<template>
    <div :class="['p-6', isStacked ? 'bg-white' : '']">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold text-gray-900">Maestro de Vendedores</h1>
            <div class="flex gap-2">
                <button v-if="isStacked" @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:text-gray-800">
                    Volver
                </button>
                <button @click="openModal()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                    <span class="text-xl">+</span> NUEVO VENDEDOR
                </button>
            </div>
        </div>

        <!-- Toolbar -->
        <div class="bg-white p-3 shadow-sm rounded-lg mb-4 flex justify-between items-center gap-4 border border-gray-200">
            <span class="text-xs text-gray-400 font-mono pl-2">
                {{ filteredVendedores.length }} Registros
            </span>
            <div class="flex bg-gray-100 p-1 rounded-md border border-gray-200">
                <button 
                    @click="filterState = 'todos'"
                    class="px-4 py-1.5 text-xs font-bold rounded transition-all"
                    :class="filterState === 'todos' ? 'bg-white text-gray-800 shadow-sm ring-1 ring-gray-200' : 'text-gray-500 hover:text-gray-700'"
                >
                    TODOS
                </button>
                <button 
                    @click="filterState = 'activos'"
                    class="px-4 py-1.5 text-xs font-bold rounded transition-all"
                    :class="filterState === 'activos' ? 'bg-[#54cb9b] text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                >
                    ACTIVOS
                </button>
                <button 
                    @click="filterState = 'inactivos'"
                    class="px-4 py-1.5 text-xs font-bold rounded transition-all"
                    :class="filterState === 'inactivos' ? 'bg-gray-600 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                >
                    INACTIVOS
                </button>
            </div>
        </div>

        <!-- Table -->
        <div class="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contacto</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Comisión</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Datos Pago</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                        <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-if="filteredVendedores.length === 0">
                        <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                            No se encontraron resultados.
                        </td>
                    </tr>
                    <tr v-for="vendedor in filteredVendedores" :key="vendedor.id" class="hover:bg-gray-50">
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ vendedor.nombre }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <div>{{ vendedor.email }}</div>
                            <div class="text-xs">{{ vendedor.telefono }}</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ vendedor.comision_porcentaje }}%</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ vendedor.cbu_alias || '-' }}</td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span :class="[
                                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                                vendedor.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            ]">
                                {{ vendedor.activo ? 'Activo' : 'Inactivo' }}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button @click="openModal(vendedor)" class="text-blue-600 hover:text-blue-900 mr-3">Editar</button>
                            <button @click="handleDelete(vendedor)" class="text-red-400 hover:text-red-600" title="Dar de Baja">
                                🗑️
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Modal -->
        <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
            <div class="relative mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">{{ isEditing ? 'Editar Vendedor' : 'Nuevo Vendedor' }}</h3>
                    <form @submit.prevent="handleSave">
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Nombre</label>
                            <input v-model="form.nombre" type="text" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Email</label>
                            <input v-model="form.email" type="email" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Teléfono</label>
                            <input v-model="form.telefono" type="text" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Comisión (%)</label>
                            <input v-model="form.comision_porcentaje" type="number" step="0.01" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Alias CBU</label>
                            <input v-model="form.cbu_alias" type="text" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div class="mb-4 flex items-center">
                            <input v-model="form.activo" type="checkbox" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                            <label class="ml-2 block text-gray-900 text-sm">Activo</label>
                        </div>
                        <div class="flex justify-end gap-2 mt-4">
                            <button type="button" @click="closeModal" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">Cancelar</button>
                            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Guardar</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue';
import { useMaestrosStore } from '../../stores/maestros';

const props = defineProps({
    isStacked: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['close', 'select']);

const store = useMaestrosStore();
const showModal = ref(false);
const isEditing = ref(false);
const editingId = ref(null);
const filterState = ref('todos');

const form = reactive({
    nombre: '',
    email: '',
    telefono: '',
    comision_porcentaje: 0,
    cbu_alias: '',
    activo: true
});

onMounted(() => {
    store.fetchVendedores('all');
});

const filteredVendedores = computed(() => {
    if (filterState.value === 'todos') return store.vendedores;
    if (filterState.value === 'activos') return store.vendedores.filter(v => v.activo);
    if (filterState.value === 'inactivos') return store.vendedores.filter(v => !v.activo);
    return store.vendedores;
});

const openModal = (vendedor = null) => {
    if (vendedor) {
        isEditing.value = true;
        editingId.value = vendedor.id;
        form.nombre = vendedor.nombre;
        form.email = vendedor.email;
        form.telefono = vendedor.telefono;
        form.comision_porcentaje = vendedor.comision_porcentaje;
        form.cbu_alias = vendedor.cbu_alias;
        form.activo = vendedor.activo;
    } else {
        isEditing.value = false;
        editingId.value = null;
        form.nombre = '';
        form.email = '';
        form.telefono = '';
        form.comision_porcentaje = 0;
        form.cbu_alias = '';
        form.activo = true;
    }
    showModal.value = true;
};

const closeModal = () => {
    showModal.value = false;
};

const handleSave = async () => {
    try {
        if (isEditing.value) {
            await store.updateVendedor(editingId.value, form);
        } else {
            await store.createVendedor(form);
        }
        closeModal();
    } catch (error) {
        alert('Error al guardar el vendedor.');
        console.error(error);
    }
};

const handleDelete = async (vendedor) => {
    if (!confirm(`¿Está seguro de dar de baja a ${vendedor.nombre}?`)) return;
    try {
        await store.updateVendedor(vendedor.id, { ...vendedor, activo: false });
        await store.fetchVendedores('all');
    } catch (error) {
        alert('Error al dar de baja.');
        console.error(error);
    }
};

// Keyboard Shortcuts
import { useKeyboardShortcuts } from '../../composables/useKeyboardShortcuts';

useKeyboardShortcuts({
    'F10': () => {
        if (showModal.value) {
            handleSave();
        }
    }
});
</script>
