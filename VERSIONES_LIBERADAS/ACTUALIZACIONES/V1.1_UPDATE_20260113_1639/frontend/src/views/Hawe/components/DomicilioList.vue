<template>
    <div class="p-6 h-full flex flex-col bg-[#0a1f2e]">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6 shrink-0">
            <h1 class="text-2xl font-bold text-white font-outfit">Administrar Domicilios</h1>
            <div class="flex gap-2">
                <button @click="$emit('close')" class="px-4 py-2 text-white/50 hover:text-white transition-colors">
                    Volver
                </button>
                <button @click="$emit('create')" class="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-bold shadow-lg shadow-cyan-900/20 transition-all">
                    <i class="fa-solid fa-plus"></i> NUEVO DOMICILIO
                </button>
            </div>
        </div>

        <!-- Toolbar -->
        <div class="bg-white/5 p-3 rounded-lg mb-4 flex justify-between items-center gap-4 border border-white/10 shrink-0">
            <div class="flex items-center gap-4 flex-1">
                <div class="relative flex-1 max-w-md">
                    <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-white/30"></i>
                    <input 
                        v-model="searchQuery" 
                        type="text" 
                        placeholder="Buscar por calle, localidad..." 
                        class="w-full bg-black/20 border border-white/10 rounded-lg pl-10 pr-4 py-1.5 text-sm text-white focus:outline-none focus:border-cyan-400 transition-colors"
                    />
                </div>
                <span class="text-xs text-white/40 font-mono">
                    {{ filteredDomicilios.length }} Registros
                </span>
            </div>
            <div class="flex bg-black/20 p-1 rounded-md border border-white/10">
                <button 
                    @click="filterState = 'todos'"
                    class="px-4 py-1.5 text-xs font-bold rounded transition-all"
                    :class="filterState === 'todos' ? 'bg-white/10 text-white shadow-sm' : 'text-white/50 hover:text-white'"
                >
                    TODOS
                </button>
                <button 
                    @click="filterState = 'activos'"
                    class="px-4 py-1.5 text-xs font-bold rounded transition-all"
                    :class="filterState === 'activos' ? 'bg-green-500/20 text-green-400 shadow-sm border border-green-500/30' : 'text-white/50 hover:text-white'"
                >
                    ACTIVOS
                </button>
                <button 
                    @click="filterState = 'inactivos'"
                    class="px-4 py-1.5 text-xs font-bold rounded transition-all"
                    :class="filterState === 'inactivos' ? 'bg-red-500/20 text-red-400 shadow-sm border border-red-500/30' : 'text-white/50 hover:text-white'"
                >
                    INACTIVOS
                </button>
            </div>
        </div>

        <!-- Table -->
        <div class="bg-white/5 rounded-lg border border-white/10 flex-1 overflow-hidden flex flex-col">
            <div class="overflow-y-auto flex-1 scrollbar-thin scrollbar-thumb-white/10">
                <table class="min-w-full divide-y divide-white/10">
                    <thead class="bg-black/20 sticky top-0 z-10 backdrop-blur-sm">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-bold text-white/50 uppercase tracking-wider">Calle y Número</th>
                            <th class="px-6 py-3 text-left text-xs font-bold text-white/50 uppercase tracking-wider">Localidad</th>
                            <th class="px-6 py-3 text-left text-xs font-bold text-white/50 uppercase tracking-wider">Tipo</th>
                            <th class="px-6 py-3 text-left text-xs font-bold text-white/50 uppercase tracking-wider">Entrega</th>
                            <th class="px-6 py-3 text-left text-xs font-bold text-white/50 uppercase tracking-wider">Estado</th>
                            <th class="px-6 py-3 text-right text-xs font-bold text-white/50 uppercase tracking-wider">Acciones</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-white/5">
                        <tr v-if="filteredDomicilios.length === 0">
                            <td colspan="5" class="px-6 py-8 text-center text-white/30">
                                <i class="fa-solid fa-magnifying-glass mb-2 text-2xl opacity-50 block"></i>
                                No se encontraron resultados.
                            </td>
                        </tr>
                        <tr 
                            v-for="dom in filteredDomicilios" 
                            :key="dom.id" 
                            class="hover:bg-white/5 cursor-pointer transition-colors group"
                            :class="{ 'opacity-50 grayscale': !dom.activo }"
                            @click="$emit('edit', dom)"
                        >
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-white">
                                {{ dom.calle }} {{ dom.numero }}
                                <span v-if="dom.piso || dom.depto" class="text-white/50 font-normal ml-1">
                                    ({{ dom.piso }} {{ dom.depto }})
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-white/70">{{ dom.localidad }}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span v-if="dom.es_fiscal" class="px-2 py-0.5 inline-flex text-[10px] leading-5 font-bold rounded-full border bg-purple-500/10 text-purple-400 border-purple-500/20">
                                    FISCAL
                                </span>
                                <span v-else class="px-2 py-0.5 inline-flex text-[10px] leading-5 font-bold rounded-full border bg-gray-700/50 text-gray-400 border-gray-600">
                                    SUCURSAL
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-white/70">
                                <div v-if="dom.metodo_entrega" class="flex items-center gap-2" :title="dom.metodo_entrega">
                                    <i v-if="dom.metodo_entrega === 'RETIRO_LOCAL'" class="fa-solid fa-store text-cyan-400"></i>
                                    <i v-else-if="dom.metodo_entrega === 'TRANSPORTE'" class="fa-solid fa-truck text-amber-400"></i>
                                    <i v-else-if="dom.metodo_entrega === 'FLETE_MOTO'" class="fa-solid fa-motorcycle text-blue-400"></i>
                                    <i v-else-if="dom.metodo_entrega === 'PLATAFORMA'" class="fa-solid fa-laptop text-purple-400"></i>
                                    <span class="text-xs font-medium">{{ dom.metodo_entrega.replace('_', ' ') }}</span>
                                </div>
                                <span v-else class="text-white/20 text-xs">-</span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span :class="[
                                    'px-2 py-0.5 inline-flex text-[10px] leading-5 font-bold rounded-full border',
                                    dom.activo ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'
                                ]">
                                    {{ dom.activo ? 'ACTIVO' : 'INACTIVO' }}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <button @click.stop="$emit('edit', dom)" class="text-cyan-400 hover:text-cyan-300 mr-4 transition-colors text-lg" title="Editar">
                                    <i class="fa-solid fa-pencil w-4 h-4"></i>
                                </button>
                                <button v-if="!dom.es_fiscal && dom.activo" @click.stop="$emit('delete', dom)" class="text-red-400 hover:text-red-300 transition-colors text-lg" title="Dar de Baja">
                                    <i class="fa-solid fa-trash w-4 h-4"></i>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
    domicilios: {
        type: Array,
        default: () => []
    }
});

const emit = defineEmits(['close', 'create', 'edit', 'delete']);

const searchQuery = ref('');
const filterState = ref('todos');

const normalizeText = (text) => {
    return text ? text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase() : ''
}

const filteredDomicilios = computed(() => {
    let result = props.domicilios;

    // Filter by State
    if (filterState.value === 'activos') result = result.filter(d => d.activo);
    if (filterState.value === 'inactivos') result = result.filter(d => !d.activo);

    if (searchQuery.value) {
        const query = normalizeText(searchQuery.value);
        result = result.filter(d => 
            normalizeText(d.calle).includes(query) || 
            normalizeText(d.localidad).includes(query)
        );
    }

    // Sort: Fiscal first, then by Alias/Calle
    result.sort((a, b) => {
        if (a.es_fiscal && !b.es_fiscal) return -1;
        if (!a.es_fiscal && b.es_fiscal) return 1;
        return (a.alias || a.calle || '').localeCompare(b.alias || b.calle || '');
    });

    return result;
});
</script>
