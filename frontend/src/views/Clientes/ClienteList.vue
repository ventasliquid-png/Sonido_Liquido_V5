<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useClientesStore } from '../../stores/clientes';
import clientesService from '../../services/clientes';
import ClienteForm from './ClienteForm.vue';

const store = useClientesStore();

const searchQuery = ref('');
const filterState = ref('todos'); // 'todos', 'activos', 'inactivos'
const showModal = ref(false);
const selectedClienteId = ref(null);
const recentClientes = ref([]);

const filteredClientes = computed(() => {
    return store.clientes.filter(c => {
        const matchesSearch = c.razon_social.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                              c.cuit.includes(searchQuery.value);
        
        let matchesFilter = true;
        if (filterState.value === 'activos') matchesFilter = c.activo;
        if (filterState.value === 'inactivos') matchesFilter = !c.activo;
        
        return matchesSearch && matchesFilter;
    });
});

const fetchTopClients = async () => {
    try {
        const response = await clientesService.getTopClients();
        recentClientes.value = response.data.map(c => ({
            ...c,
            // Map backend data to UI format
            sub: c.nombre_fantasia || c.cuit,
            saldo: c.saldo_actual || 0,
            estado: c.activo ? 'ACT' : 'INA',
            color: (c.saldo_actual || 0) < 0 ? 'border-l-red-500' : 'border-l-green-500',
            badge: c.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }));
    } catch (error) {
        console.error("Error fetching top clients:", error);
    }
};

const openNew = () => {
    selectedClienteId.value = null;
    showModal.value = true;
};

const openEdit = (id) => {
    selectedClienteId.value = id;
    showModal.value = true;
    // Track interaction in background
    clientesService.incrementUsage(id).catch(err => console.error("Error tracking usage:", err));
};

const handleModalClose = () => {
    showModal.value = false;
    selectedClienteId.value = null;
    fetchTopClients(); // Refresh top clients on close
};

const handleSaved = (id) => {
    if (!selectedClienteId.value) {
        selectedClienteId.value = id;
    }
    fetchTopClients(); // Refresh top clients on save
};

// Keyboard Shortcuts
const handleKeydown = (e) => {
    if (e.key === 'F4') {
        e.preventDefault();
        openNew();
    }
};

onMounted(() => {
    store.fetchClientes();
    fetchTopClients();
    window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
    <div class="h-full flex flex-col bg-slate-100 text-gray-900 font-sans">
        <!-- 1. MASTER HEADER (Green Bar) -->
        <div class="bg-[#54cb9b] text-white px-6 py-2 flex justify-between items-center shadow-sm z-20">
            <div>
                <h1 class="text-lg font-bold uppercase tracking-wide">Maestro de Clientes</h1>
                <p class="text-xs text-white/80 font-medium">Sonido Líquido V5</p>
            </div>
            <div class="flex items-center gap-3 text-xs font-mono bg-white/10 px-3 py-1 rounded">
                <span class="opacity-80">Admin</span>
                <span class="w-px h-3 bg-white/30"></span>
                <span class="opacity-80">v5.2.1</span>
            </div>
        </div>

        <!-- 2. ACTION TOOLBAR (White Bar) -->
        <div class="bg-white px-6 py-4 shadow-sm z-10 flex flex-col md:flex-row justify-between items-center gap-4 border-b border-gray-200">
            <!-- Search -->
            <div class="relative w-full md:w-1/2 lg:w-1/3">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                    </svg>
                </div>
                <input 
                    v-model="searchQuery"
                    type="text" 
                    class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] sm:text-sm transition-all" 
                    placeholder="Buscar por Razón Social, CUIT o Fantasía... (Escribe para filtrar)" 
                />
            </div>

            <!-- Filters & Actions -->
            <div class="flex items-center gap-4 w-full md:w-auto">
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

                <button 
                    @click="openNew"
                    class="w-full md:w-auto px-4 py-2 bg-[#54cb9b] text-white text-sm font-bold rounded hover:bg-[#45b085] transition-colors shadow-sm flex items-center justify-center gap-2"
                >
                    <span class="bg-white/20 px-1.5 py-0.5 rounded text-[10px]">F4</span> Nuevo Cliente
                </button>
            </div>
        </div>

        <!-- 3. SPEED DIAL (Quick Access) -->
        <div class="px-6 py-4 overflow-x-auto">
            <div class="flex justify-between items-center mb-2">
                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider">Recientes / Frecuentes</h3>
                <button class="text-xs text-[#54cb9b] hover:underline">Gestionar Accesos Rápidos</button>
            </div>
            <div v-if="recentClientes.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div 
                    v-for="cliente in recentClientes" 
                    :key="cliente.id"
                    @click="openEdit(cliente.id)"
                    class="bg-white p-3 rounded border-l-4 shadow-sm hover:shadow-md transition-all cursor-pointer flex justify-between items-start group"
                    :class="cliente.color"
                >
                    <div>
                        <h4 class="text-sm font-bold text-gray-800 group-hover:text-[#54cb9b] transition-colors truncate max-w-[150px]">{{ cliente.razon_social }}</h4>
                        <p class="text-[10px] text-gray-500 truncate max-w-[150px]">{{ cliente.sub }}</p>
                        <p class="text-[10px] text-gray-400 mt-1">Saldo:</p>
                    </div>
                    <div class="flex flex-col items-end gap-1">
                        <span class="text-[10px] font-bold px-1.5 py-0.5 rounded" :class="cliente.badge">{{ cliente.estado }}</span>
                        <span class="text-sm font-bold text-gray-700" :class="{'text-red-500': cliente.saldo < 0}">$ {{ cliente.saldo.toLocaleString('es-AR', { minimumFractionDigits: 2 }) }}</span>
                    </div>
                </div>
            </div>
            <div v-else class="text-center py-4 text-gray-400 text-xs italic">
                No hay clientes recientes. Interactúa con el padrón para verlos aquí.
            </div>
        </div>

        <!-- 4. MAIN DATA GRID (Padrón General) -->
        <div class="flex-1 px-6 pb-6 overflow-hidden flex flex-col">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col h-full">
                <!-- Grid Header -->
                <div class="bg-[#54cb9b] px-4 py-2 flex justify-between items-center">
                    <h3 class="text-white font-bold text-lg uppercase tracking-wide">Padrón General</h3>
                    <span class="bg-white/20 text-white text-xs px-2 py-1 rounded font-mono">{{ filteredClientes.length }} Registros</span>
                </div>

                <!-- Table Container -->
                <div class="flex-1 overflow-auto">
                    <div class="min-w-full inline-block align-middle">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50 sticky top-0 z-10">
                                <tr>
                                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">ID</th>
                                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Razón Social / Nombre</th>
                                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Fantasía</th>
                                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">CUIT</th>
                                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Localidad</th>
                                    <th scope="col" class="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Saldo</th>
                                    <th scope="col" class="px-6 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">Est.</th>
                                    <th scope="col" class="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                                <tr v-if="filteredClientes.length === 0">
                                    <td colspan="8" class="px-6 py-10 text-center text-sm text-gray-500 italic">
                                        No se encontraron resultados.
                                    </td>
                                </tr>
                                <tr 
                                    v-for="cliente in filteredClientes" 
                                    :key="cliente.id"
                                    class="hover:bg-slate-50 transition-colors cursor-pointer group"
                                    @dblclick="openEdit(cliente.id)"
                                >
                                    <td class="px-6 py-3 whitespace-nowrap text-xs text-gray-400 font-mono">
                                        {{ cliente.codigo_interno || '----' }}
                                    </td>
                                    <td class="px-6 py-3 whitespace-nowrap">
                                        <div class="flex items-center gap-2">
                                            <div class="text-sm font-medium text-gray-900 group-hover:text-[#54cb9b]">{{ cliente.razon_social }}</div>
                                            <span v-if="cliente.requiere_auditoria" class="text-[10px] bg-orange-100 text-orange-700 px-1.5 py-0.5 rounded font-bold border border-orange-200" title="Requiere Auditoría (CUIT Duplicado)">
                                                👁️ REVISAR
                                            </span>
                                        </div>
                                    </td>
                                    <td class="px-6 py-3 whitespace-nowrap text-xs text-gray-500">
                                        {{ cliente.nombre_fantasia || '-' }}
                                    </td>
                                    <td class="px-6 py-3 whitespace-nowrap text-xs text-gray-500 font-mono">
                                        {{ cliente.cuit }}
                                    </td>
                                    <td class="px-6 py-3 whitespace-nowrap text-xs text-gray-500">
                                        -
                                    </td>
                                    <td class="px-6 py-3 whitespace-nowrap text-xs text-gray-900 font-bold text-right">
                                        $ {{ (cliente.saldo_actual || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 }) }}
                                    </td>
                                    <td class="px-6 py-3 whitespace-nowrap text-center">
                                        <span 
                                            class="inline-block w-2 h-2 rounded-full"
                                            :class="cliente.activo ? 'bg-green-500' : 'bg-red-500'"
                                        ></span>
                                    </td>
                                    <td class="px-6 py-3 whitespace-nowrap text-right text-sm font-medium">
                                        <button @click.stop="openEdit(cliente.id)" class="text-gray-400 hover:text-[#54cb9b]">
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                                                <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                                            </svg>
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal -->
        <ClienteForm 
            :show="showModal" 
            :clienteId="selectedClienteId" 
            @close="handleModalClose"
            @saved="handleSaved"
            @edit-existing="openEdit"
        />
    </div>
</template>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
