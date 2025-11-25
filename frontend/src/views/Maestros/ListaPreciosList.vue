<template>
    <div :class="['p-6', isStacked ? 'bg-white' : '']">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold text-gray-900">Maestro de Listas de Precios</h1>
            <div class="flex gap-2">
                <button v-if="isStacked" @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:text-gray-800">
                    Volver
                </button>
                <button @click="openModal()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                    <span class="text-xl">+</span> NUEVA LISTA
                </button>
            </div>
        </div>

        <!-- Table -->
        <div class="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Coeficiente</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                        <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="lista in store.listasPrecios" :key="lista.id" class="hover:bg-gray-50">
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ lista.nombre }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ lista.coeficiente }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <span :class="[
                                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                                lista.tipo === 'FISCAL' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'
                            ]">
                                {{ lista.tipo }}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span :class="[
                                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                                lista.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            ]">
                                {{ lista.activo ? 'Activo' : 'Inactivo' }}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button @click="openModal(lista)" class="text-blue-600 hover:text-blue-900 mr-3">Editar</button>
                            <button @click="handleDelete(lista)" class="text-red-400 hover:text-red-600" title="Dar de Baja">
                                🗑️
                            </button>
                        </td>
                    </tr>
                    <tr v-if="store.listasPrecios.length === 0">
                        <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                            No hay listas de precios registradas.
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Modal -->
        <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
            <div class="relative mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">{{ isEditing ? 'Editar Lista' : 'Nueva Lista' }}</h3>
                    <form @submit.prevent="handleSave">
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Nombre</label>
                            <input v-model="form.nombre" type="text" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Coeficiente</label>
                            <input v-model="form.coeficiente" type="number" step="0.0001" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                            <p class="text-xs text-gray-500 mt-1">Ej: 0.9000 (10% descuento)</p>
                        </div>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Tipo</label>
                            <select v-model="form.tipo" class="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                                <option value="PRESUPUESTO">PRESUPUESTO</option>
                                <option value="FISCAL">FISCAL</option>
                            </select>
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
import { ref, onMounted, reactive } from 'vue';
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

const form = reactive({
    nombre: '',
    coeficiente: 1.0,
    tipo: 'PRESUPUESTO',
    activo: true
});

onMounted(() => {
    store.fetchListasPrecios();
});

const openModal = (lista = null) => {
    if (lista) {
        isEditing.value = true;
        editingId.value = lista.id;
        form.nombre = lista.nombre;
        form.coeficiente = lista.coeficiente;
        form.tipo = lista.tipo;
        form.activo = lista.activo;
    } else {
        isEditing.value = false;
        editingId.value = null;
        form.nombre = '';
        form.coeficiente = 1.0;
        form.tipo = 'PRESUPUESTO';
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
            await store.updateListaPrecios(editingId.value, form);
        } else {
            await store.createListaPrecios(form);
        }
        closeModal();
    } catch (error) {
        alert('Error al guardar la lista de precios.');
        console.error(error);
    }
};

const handleDelete = async (lista) => {
    if (!confirm(`¿Está seguro de dar de baja a ${lista.nombre}?`)) return;
    try {
        await store.updateListaPrecios(lista.id, { ...lista, activo: false });
        await store.fetchListasPrecios();
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
