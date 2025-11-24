<script setup>
import { ref, computed, onMounted } from 'vue';
import { useClientesStore } from '../../stores/clientes';
import ClienteForm from './ClienteForm.vue';

const store = useClientesStore();

const searchQuery = ref('');
const filterActivo = ref(true);
const showModal = ref(false);
const selectedClienteId = ref(null);

onMounted(() => {
    store.fetchClientes();
});

const filteredClientes = computed(() => {
    return store.clientes.filter(c => {
        const matchesSearch = c.razon_social.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                              c.cuit.includes(searchQuery.value);
        const matchesActive = filterActivo.value ? c.activo : true; // Si filtro activo es true, solo muestra activos? O muestra todos?
        // Requerimiento: "Filtros (Activo/Inactivo)".
        // Asumiremos un toggle: Mostrar solo activos vs Mostrar todos.
        // O mejor, un select.
        // Vamos a hacer que el toggle sea "Solo Activos".
        if (filterActivo.value && !c.activo) return false;
        
        return matchesSearch;
    });
});

const openNew = () => {
    selectedClienteId.value = null;
    showModal.value = true;
};

const openEdit = (id) => {
    selectedClienteId.value = id;
    showModal.value = true;
};

const handleModalClose = () => {
    showModal.value = false;
    selectedClienteId.value = null;
};

const handleSaved = (id) => {
    // Si se creó uno nuevo, podríamos recargar la lista o actualizar el ID seleccionado.
    // store.fetchClientes() ya se llama en create/update del store? No, el store actualiza su estado local.
    // Pero si queremos refrescar todo:
    // store.fetchClientes();
    // Si estamos editando, mantenemos el modal abierto o cerramos?
    // "Al hacer click en 'Nuevo' o 'Editar', no navega a otra URL; abre el MODAL DE EDICIÓN."
    // Asumimos que al guardar se puede seguir editando.
    if (!selectedClienteId.value) {
        selectedClienteId.value = id; // Switch to edit mode
    }
    // No cerramos el modal automáticamente para permitir cargar detalles.
};
</script>

<template>
    <div class="h-full flex flex-col bg-slate-50 text-gray-900">
        <!-- Header -->
        <div class="p-6 border-b border-gray-200 flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
                <h1 class="text-2xl font-bold text-brand">Maestro de Clientes</h1>
                <p class="text-sm text-gray-500">Gestión centralizada de cuentas</p>
            </div>
            <div class="flex gap-4 w-full md:w-auto">
                <input 
                    v-model="searchQuery" 
                    type="text" 
                    placeholder="Buscar por Razón Social o CUIT..." 
                    class="bg-white border border-gray-300 rounded px-4 py-2 w-full md:w-64 focus:border-brand focus:outline-none text-gray-900"
                />
                <label class="flex items-center gap-2 cursor-pointer select-none">
                    <input type="checkbox" v-model="filterActivo" class="form-checkbox h-5 w-5 text-brand rounded bg-white border-gray-300">
                    <span class="text-sm text-gray-600">Solo Activos</span>
                </label>
                <button 
                    @click="openNew"
                    class="bg-brand hover:bg-green-600 text-white px-4 py-2 rounded font-medium shadow-lg shadow-brand/20 transition-all whitespace-nowrap"
                >
                    + Nuevo Cliente
                </button>
            </div>
        </div>

        <!-- Grid -->
        <div class="flex-1 overflow-auto p-6">
            <div v-if="store.loading && store.clientes.length === 0" class="text-center py-10 text-gray-500">
                Cargando clientes...
            </div>
            
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                <div 
                    v-for="cliente in filteredClientes" 
                    :key="cliente.id"
                    @click="openEdit(cliente.id)"
                    class="bg-white border border-gray-200 rounded-lg p-5 hover:border-brand/50 hover:shadow-lg hover:shadow-brand/5 transition-all cursor-pointer group relative overflow-hidden"
                >
                    <div class="absolute top-0 left-0 w-1 h-full" :class="cliente.activo ? 'bg-brand' : 'bg-gray-600'"></div>
                    
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="font-bold text-lg text-gray-900 group-hover:text-brand truncate pr-2">{{ cliente.razon_social }}</h3>
                        <span class="text-xs font-mono bg-gray-100 px-2 py-1 rounded text-gray-500">{{ cliente.codigo_interno || 'N/A' }}</span>
                    </div>
                    
                    <div class="text-sm text-gray-600 space-y-1">
                        <p>CUIT: {{ cliente.cuit }}</p>
                        <p v-if="cliente.whatsapp_empresa" class="flex items-center gap-1">
                            <span class="text-green-500">📱</span> {{ cliente.whatsapp_empresa }}
                        </p>
                        <p v-else class="text-gray-600 italic">Sin contacto</p>
                    </div>

                    <div class="mt-4 pt-3 border-t border-gray-200 flex justify-between items-center text-xs text-gray-500">
                        <span>Saldo: ${{ cliente.saldo_actual || '0.00' }}</span>
                        <span v-if="!cliente.activo" class="text-red-400 font-medium">INACTIVO</span>
                    </div>
                </div>
            </div>

            <div v-if="!store.loading && filteredClientes.length === 0" class="text-center py-10 text-gray-500">
                No se encontraron clientes.
            </div>
        </div>

        <!-- Modal -->
        <ClienteForm 
            :show="showModal" 
            :clienteId="selectedClienteId" 
            @close="handleModalClose"
            @saved="handleSaved"
        />
    </div>
</template>
