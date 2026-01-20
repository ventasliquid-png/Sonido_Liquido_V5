<template>
    <div :class="['p-6', 'bg-[#0a0a0a] min-h-screen text-white']">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
            <div class="flex items-center gap-3">
                 <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-green-500/20 to-black flex items-center justify-center text-green-500 border border-green-500/20 shadow-lg shadow-green-900/20">
                    <i class="fas fa-dollar-sign text-lg"></i>
                 </div>
                 <div>
                    <h1 class="font-outfit text-2xl font-bold text-white tracking-tight leading-none">Listas de Precios</h1>
                    <span class="text-xs text-green-400/50 font-mono">Configuración de Coeficientes</span>
                 </div>
            </div>

            <div class="flex gap-2">
                <button v-if="isStacked" @click="$emit('close')" class="px-4 py-2 text-white/50 hover:text-white transition-colors">
                    <i class="fas fa-arrow-left mr-2"></i>Volver
                </button>
                <button @click="openModal()" class="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 text-white font-bold py-2 px-6 rounded-xl shadow-lg shadow-green-900/40 transition-all active:scale-95 flex items-center gap-2">
                    <i class="fas fa-plus"></i> NUEVA LISTA
                </button>
            </div>
        </div>

        <!-- Toolbar -->
        <div class="bg-white/5 p-1 rounded-xl mb-6 flex justify-between items-center gap-4 border border-white/5">
            <span class="text-xs text-emerald-400/50 font-mono font-bold pl-4 uppercase tracking-widest">
                {{ filteredListas.length }} Registros
            </span>
            <div class="flex bg-black/40 p-1 rounded-lg border border-white/5">
                <button 
                    @click="filterState = 'todos'"
                    class="px-4 py-1.5 text-[10px] font-bold rounded-md transition-all uppercase tracking-wider"
                    :class="filterState === 'todos' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'text-gray-500 hover:text-gray-300'"
                >
                    TODOS
                </button>
                <button 
                    @click="filterState = 'activos'"
                    class="px-4 py-1.5 text-[10px] font-bold rounded-md transition-all uppercase tracking-wider"
                    :class="filterState === 'activos' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-gray-500 hover:text-gray-300'"
                >
                    ACTIVOS
                </button>
                <button 
                    @click="filterState = 'inactivos'"
                    class="px-4 py-1.5 text-[10px] font-bold rounded-md transition-all uppercase tracking-wider"
                    :class="filterState === 'inactivos' ? 'bg-red-500/10 text-red-500 border border-red-500/20' : 'text-gray-500 hover:text-gray-300'"
                >
                    INACTIVOS
                </button>
            </div>
        </div>

        <!-- Table -->
        <div class="bg-black/20 rounded-xl overflow-hidden border border-white/5 backdrop-blur-sm">
            <table class="min-w-full divide-y divide-white/5">
                <thead class="bg-white/5">
                    <tr>
                        <th class="px-6 py-4 text-left text-[10px] font-bold text-white/30 uppercase tracking-widest">Nombre</th>
                        <th class="px-6 py-4 text-left text-[10px] font-bold text-white/30 uppercase tracking-widest">Coeficiente</th>
                        <th class="px-6 py-4 text-left text-[10px] font-bold text-white/30 uppercase tracking-widest">Tipo</th>
                        <th class="px-6 py-4 text-left text-[10px] font-bold text-white/30 uppercase tracking-widest">Estado</th>
                        <th class="px-6 py-4 text-right text-[10px] font-bold text-white/30 uppercase tracking-widest">Acciones</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-white/5">
                    <tr v-if="filteredListas.length === 0">
                        <td colspan="5" class="px-6 py-12 text-center text-white/20 italic">
                            No se encontraron resultados.
                        </td>
                    </tr>
                    <tr v-for="lista in filteredListas" :key="lista.id" class="hover:bg-white/5 transition-colors group">
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-white group-hover:text-green-400 transition-colors">{{ lista.nombre }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-emerald-400">{{ lista.coeficiente }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                            <span :class="[
                                'px-2 py-0.5 inline-flex text-[10px] font-bold uppercase rounded border',
                                lista.tipo === 'FISCAL' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                            ]">
                                {{ lista.tipo }}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span :class="[
                                'px-2 py-0.5 inline-flex text-[10px] font-bold uppercase rounded border',
                                lista.activo ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-500 border-red-500/20'
                            ]">
                                {{ lista.activo ? 'Activo' : 'Inactivo' }}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button @click="openModal(lista)" class="text-white/20 hover:text-green-400 mr-3 transition-colors"><i class="fas fa-pencil-alt"></i></button>
                            <button @click="handleDelete(lista)" class="text-white/20 hover:text-red-500 transition-colors" title="Dar de Baja">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Modal -->
        <div v-if="showModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
            <div class="relative mx-auto border border-rose-500/30 w-full max-w-md shadow-2xl rounded-2xl bg-[#1a050b] overflow-hidden">
                 <!-- Modal Header -->
                 <div class="bg-rose-950/30 p-4 border-b border-rose-500/20 flex justify-between items-center">
                     <h3 class="text-lg font-outfit font-bold text-white">{{ isEditing ? 'Editar Lista' : 'Nueva Lista' }}</h3>
                     <button @click="closeModal" class="text-white/50 hover:text-white"><i class="fas fa-times"></i></button>
                 </div>
                 
                <div class="p-6">
                    <form @submit.prevent="handleSave" class="space-y-4">
                        <div class="space-y-1">
                            <label class="block text-rose-200/50 text-[10px] font-bold uppercase tracking-widest">Nombre</label>
                            <input v-model="form.nombre" type="text" required class="bg-black/40 border border-white/10 rounded-lg w-full py-3 px-3 text-white focus:border-rose-500/50 focus:outline-none transition-colors">
                        </div>
                        <div class="space-y-1">
                            <label class="block text-rose-200/50 text-[10px] font-bold uppercase tracking-widest">Coeficiente</label>
                            <input v-model="form.coeficiente" type="number" step="0.0001" required class="bg-black/40 border border-white/10 rounded-lg w-full py-3 px-3 text-white font-mono focus:border-rose-500/50 focus:outline-none transition-colors">
                            <p class="text-[10px] text-white/30 italic">Ej: 0.9000 (10% descuento)</p>
                        </div>
                        <div class="space-y-1">
                            <label class="block text-rose-200/50 text-[10px] font-bold uppercase tracking-widest">Tipo</label>
                            <select v-model="form.tipo" class="bg-black/40 border border-white/10 rounded-lg w-full py-3 px-3 text-white focus:border-rose-500/50 focus:outline-none transition-colors">
                                <option value="PRESUPUESTO">PRESUPUESTO</option>
                                <option value="FISCAL">FISCAL</option>
                            </select>
                        </div>
                        <div class="flex items-center p-3 bg-white/5 rounded-lg border border-white/5">
                            <input v-model="form.activo" type="checkbox" class="h-4 w-4 bg-black/50 border-rose-500/30 text-rose-600 focus:ring-rose-500 rounded cursor-pointer">
                            <label class="ml-2 block text-white/70 text-sm font-bold">Lista Activa</label>
                        </div>
                        
                        <div class="flex justify-end gap-3 mt-6 pt-4 border-t border-white/5">
                            <button type="button" @click="closeModal" class="px-4 py-2 text-white/50 hover:text-white font-bold text-xs uppercase tracking-wider">Cancelar</button>
                            <button type="submit" class="bg-rose-600 hover:bg-rose-500 text-white font-bold py-2 px-6 rounded-lg shadow-lg shadow-rose-900/40 transition-all">Guardar</button>
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
    coeficiente: 1.0,
    tipo: 'PRESUPUESTO',
    activo: true
});

onMounted(() => {
    store.fetchListasPrecios('all');
});

const filteredListas = computed(() => {
    if (filterState.value === 'todos') return store.listasPrecios;
    if (filterState.value === 'activos') return store.listasPrecios.filter(l => l.activo);
    if (filterState.value === 'inactivos') return store.listasPrecios.filter(l => !l.activo);
    return store.listasPrecios;
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
        await store.fetchListasPrecios('all');
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
