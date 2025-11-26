<script setup>
import { ref, onMounted, computed } from 'vue';
import { useLogisticaStore } from '../../stores/logistica';
import TransporteForm from './TransporteForm.vue';

const store = useLogisticaStore();
const showModal = ref(false);
const editingId = ref(null);
const filterState = ref('todos'); // 'todos', 'activos', 'inactivos'

onMounted(async () => {
    await store.fetchEmpresas('all'); // Fetch ALL for client-side filtering
});

const filteredEmpresas = computed(() => {
    if (filterState.value === 'todos') return store.empresas;
    if (filterState.value === 'activos') return store.empresas.filter(e => e.activo);
    if (filterState.value === 'inactivos') return store.empresas.filter(e => !e.activo);
    return store.empresas;
});

const openNew = () => {
    editingId.value = null;
    showModal.value = true;
};

const openEdit = async (empresa) => {
    editingId.value = empresa.id;
    showModal.value = true;
};

const closeModal = () => {
    showModal.value = false;
    editingId.value = null;
};

const handleSaved = async () => {
    await store.fetchEmpresas('all');
};

const handleDeleteEmpresa = async (empresa) => {
    if (!confirm(`¿Está seguro de dar de baja a ${empresa.nombre}?`)) return;

    try {
        await store.updateEmpresa(empresa.id, { ...empresa, activo: false });
        alert('Empresa dada de baja.');
        await store.fetchEmpresas('all');
    } catch (error) {
        alert('Error al dar de baja: ' + error.message);
    }
};
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

        <!-- TOOLBAR -->
        <div class="bg-white px-6 py-3 shadow-sm z-10 flex justify-between items-center gap-4 border-b border-gray-200">
            <span class="text-xs text-gray-400 font-mono pl-2">
                {{ filteredEmpresas.length }} Registros
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
                        <tr v-if="filteredEmpresas.length === 0">
                            <td colspan="5" class="px-6 py-10 text-center text-sm text-gray-500 italic">
                                No se encontraron resultados.
                            </td>
                        </tr>
                        <tr v-for="empresa in filteredEmpresas" :key="empresa.id" class="hover:bg-slate-50">
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
        <TransporteForm 
            :show="showModal" 
            :id="editingId" 
            @close="closeModal" 
            @saved="handleSaved"
        />
    </div>
</template>

<style scoped>
/* Styles handled by Tailwind */
</style>
