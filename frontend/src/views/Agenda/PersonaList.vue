<template>
    <div :class="['p-6', isStacked ? 'bg-white' : '']">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold text-gray-900">Agenda Global (Personas)</h1>
            <div class="flex gap-2">
                <button v-if="isStacked" @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:text-gray-800">
                    Volver
                </button>
                <button @click="openModal()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                    <span class="text-xl">+</span> NUEVA PERSONA
                </button>
            </div>
        </div>

        <!-- Toolbar -->
        <div class="bg-white p-3 shadow-sm rounded-lg mb-4 flex justify-between items-center gap-4 border border-gray-200">
            <span class="text-xs text-gray-400 font-mono pl-2">
                {{ store.personas.length }} Registros (Mostrando)
            </span>
            <div class="flex bg-gray-100 p-1 rounded-md border border-gray-200">
                <button 
                    @click="filterState = 'all'"
                    class="px-4 py-1.5 text-xs font-bold rounded transition-all"
                    :class="filterState === 'all' ? 'bg-white text-gray-800 shadow-sm ring-1 ring-gray-200' : 'text-gray-500 hover:text-gray-700'"
                >
                    TODOS
                </button>
                <button 
                    @click="filterState = 'active'"
                    class="px-4 py-1.5 text-xs font-bold rounded transition-all"
                    :class="filterState === 'active' ? 'bg-[#54cb9b] text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                >
                    ACTIVOS
                </button>
                <button 
                    @click="filterState = 'inactive'"
                    class="px-4 py-1.5 text-xs font-bold rounded transition-all"
                    :class="filterState === 'inactive' ? 'bg-gray-600 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'"
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
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre Completo</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contacto Personal</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Redes</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Observaciones</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                        <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="persona in store.personas" :key="persona.id" class="hover:bg-gray-50">
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ persona.nombre_completo }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <div>{{ persona.email_personal }}</div>
                            <div class="text-xs">{{ persona.celular_personal }}</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <a v-if="persona.linkedin" :href="persona.linkedin" target="_blank" class="text-blue-600 hover:underline">LinkedIn</a>
                            <span v-else>-</span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ persona.observaciones || '-' }}</td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span :class="[
                                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                                persona.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            ]">
                                {{ persona.activo ? 'Activo' : 'Inactivo' }}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button @click="openModal(persona)" class="text-blue-600 hover:text-blue-900 mr-3">Editar</button>
                            <button @click="handleDelete(persona)" class="text-red-400 hover:text-red-600" title="Dar de Baja">
                                🗑️
                            </button>
                        </td>
                    </tr>
                    <tr v-if="store.personas.length === 0">
                        <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                            No hay personas registradas.
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Modal -->
        <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
            <div class="relative mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">{{ isEditing ? 'Editar Persona' : 'Nueva Persona' }}</h3>
                    <form @submit.prevent="handleSave">
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Nombre Completo</label>
                            <input v-model="form.nombre_completo" type="text" required class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Email Personal</label>
                            <input v-model="form.email_personal" type="email" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Celular Personal</label>
                            <input v-model="form.celular_personal" type="text" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">LinkedIn</label>
                            <input v-model="form.linkedin" type="url" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Observaciones</label>
                            <textarea v-model="form.observaciones" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"></textarea>
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
import { ref, onMounted, reactive, watch } from 'vue';
import { useAgendaStore } from '../../stores/agenda';

const props = defineProps({
    isStacked: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['close', 'select']);

const store = useAgendaStore();
const showModal = ref(false);
const isEditing = ref(false);
const editingId = ref(null);
const filterState = ref('active'); // Server-side filter: 'active', 'inactive', 'all'

const form = reactive({
    nombre_completo: '',
    celular_personal: '',
    email_personal: '',
    linkedin: '',
    observaciones: '',
    activo: true
});

onMounted(() => {
    store.fetchPersonas({ status: filterState.value });
});

watch(filterState, (newVal) => {
    store.fetchPersonas({ status: newVal });
});

const openModal = (persona = null) => {
    if (persona) {
        isEditing.value = true;
        editingId.value = persona.id;
        form.nombre_completo = persona.nombre_completo;
        form.celular_personal = persona.celular_personal;
        form.email_personal = persona.email_personal;
        form.linkedin = persona.linkedin;
        form.observaciones = persona.observaciones;
        form.activo = persona.activo;
    } else {
        isEditing.value = false;
        editingId.value = null;
        form.nombre_completo = '';
        form.celular_personal = '';
        form.email_personal = '';
        form.linkedin = '';
        form.observaciones = '';
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
            await store.updatePersona(editingId.value, form);
        } else {
            await store.createPersona(form);
        }
        closeModal();
    } catch (error) {
        alert('Error al guardar la persona.');
        console.error(error);
    }
};

const handleDelete = async (persona) => {
    if (!confirm(`¿Está seguro de dar de baja a ${persona.nombre_completo}?`)) return;
    try {
        await store.updatePersona(persona.id, { ...persona, activo: false });
        await store.fetchPersonas({ status: filterState.value });
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
