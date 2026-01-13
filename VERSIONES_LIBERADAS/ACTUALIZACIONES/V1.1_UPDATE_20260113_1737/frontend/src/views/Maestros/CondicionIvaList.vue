<template>
    <div :class="['p-6', isStacked ? 'bg-white' : '']">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold text-gray-900">Maestro de Condiciones IVA</h1>
            <div class="flex gap-2">
                <button v-if="isStacked" @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:text-gray-800">
                    Volver
                </button>
                <button @click="openModal()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                    <span class="text-xl">+</span> NUEVA CONDICIÓN
                </button>
            </div>
        </div>

        <!-- Toolbar -->
        <div class="bg-white p-3 shadow-sm rounded-lg mb-4 flex justify-between items-center gap-4 border border-gray-200">
            <span class="text-xs text-gray-400 font-mono pl-2">
                {{ store.condicionesIva.length }} Registros
            </span>
        </div>

        <!-- Table -->
        <div class="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                        <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-if="store.condicionesIva.length === 0">
                        <td colspan="2" class="px-6 py-4 text-center text-gray-500">
                            No se encontraron resultados.
                        </td>
                    </tr>
                    <tr 
                        v-for="condicion in store.condicionesIva" 
                        :key="condicion.id" 
                        class="hover:bg-gray-50 cursor-pointer"
                        @contextmenu.prevent="handleContextMenu($event, condicion)"
                    >
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ condicion.nombre }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button @click="openModal(condicion)" class="text-blue-600 hover:text-blue-900 mr-3">Editar</button>
                            <button @click="handleDelete(condicion)" class="text-red-400 hover:text-red-600" title="Eliminar">
                                🗑️
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Modal -->
        <CondicionIvaForm 
            :show="showModal" 
            :id="editingId" 
            @close="closeModal" 
            @saved="handleSaved"
        />

        <!-- Context Menu -->
        <ContextMenu 
            v-model="contextMenu.show" 
            :x="contextMenu.x" 
            :y="contextMenu.y" 
            :actions="contextMenu.actions"
            @close="contextMenu.show = false"
        />
    </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useMaestrosStore } from '../../stores/maestros';
import CondicionIvaForm from './CondicionIvaForm.vue';
import ContextMenu from '../../components/common/ContextMenu.vue';

const props = defineProps({
    isStacked: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['close']);

const store = useMaestrosStore();
const showModal = ref(false);
const editingId = ref(null);

const contextMenu = reactive({
    show: false,
    x: 0,
    y: 0,
    actions: []
});

onMounted(() => {
    store.fetchCondicionesIva();
});

const openModal = (condicion = null) => {
    editingId.value = condicion ? condicion.id : null;
    showModal.value = true;
};

const closeModal = () => {
    showModal.value = false;
    editingId.value = null;
};

const handleSaved = async () => {
    await store.fetchCondicionesIva();
};

const handleDelete = async (condicion) => {
    if (!confirm(`¿Está seguro de eliminar a ${condicion.nombre}?`)) return;
    try {
        await store.deleteCondicionIva(condicion.id);
    } catch (error) {
        alert('Error al eliminar.');
        console.error(error);
    }
};

const handleContextMenu = (e, condicion) => {
    contextMenu.show = true;
    contextMenu.x = e.clientX;
    contextMenu.y = e.clientY;
    contextMenu.actions = [
        {
            label: 'Editar',
            icon: '✏️',
            handler: () => openModal(condicion)
        },
        {
            label: 'Eliminar',
            icon: '🗑️',
            handler: () => handleDelete(condicion)
        }
    ];
};
</script>
