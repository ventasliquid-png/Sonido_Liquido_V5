<template>
    <div :class="['p-6', 'bg-[#0a0a0a] min-h-screen text-white']">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
            <div class="flex items-center gap-3">
                 <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-black flex items-center justify-center text-indigo-500 border border-indigo-500/20 shadow-lg shadow-indigo-900/20">
                    <i class="fas fa-user-tie text-lg"></i>
                 </div>
                 <div>
                    <h1 class="font-outfit text-2xl font-bold text-white tracking-tight leading-none">Gestión de Vendedores</h1>
                    <span class="text-xs text-indigo-400/50 font-mono">Maestro de Fuerza de Ventas</span>
                 </div>
            </div>

            <div class="flex gap-2">
                <button v-if="isStacked" @click="$emit('close')" class="px-4 py-2 text-white/50 hover:text-white transition-colors">
                    <i class="fas fa-arrow-left mr-2"></i>Volver
                </button>
                <button @click="openModal()" class="bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-bold py-2 px-6 rounded-xl shadow-lg shadow-indigo-900/40 transition-all active:scale-95 flex items-center gap-2">
                    <i class="fas fa-plus"></i> NUEVO VENDEDOR
                </button>
            </div>
        </div>

        <!-- Toolbar -->
        <div class="bg-white/5 p-1 rounded-xl mb-6 flex justify-between items-center gap-4 border border-white/5">
            <span class="text-xs text-indigo-400/50 font-mono font-bold pl-4 uppercase tracking-widest">
                {{ filteredVendedores.length }} Registros
            </span>
            <div class="flex bg-black/40 p-1 rounded-lg border border-white/5">
                <button 
                    @click="filterState = 'todos'"
                    class="px-4 py-1.5 text-[10px] font-bold rounded-md transition-all uppercase tracking-wider"
                    :class="filterState === 'todos' ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30' : 'text-gray-500 hover:text-gray-300'"
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
                        <th class="px-6 py-4 text-left text-[10px] font-bold text-white/30 uppercase tracking-widest">Contacto</th>
                        <th class="px-6 py-4 text-left text-[10px] font-bold text-white/30 uppercase tracking-widest">Comisión</th>
                        <th class="px-6 py-4 text-left text-[10px] font-bold text-white/30 uppercase tracking-widest">Datos Pago</th>
                        <th class="px-6 py-4 text-left text-[10px] font-bold text-white/30 uppercase tracking-widest">Estado</th>
                        <th class="px-6 py-4 text-right text-[10px] font-bold text-white/30 uppercase tracking-widest">Acciones</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-white/5">
                    <tr v-if="filteredVendedores.length === 0">
                        <td colspan="6" class="px-6 py-12 text-center text-white/20 italic">
                            No se encontraron resultados.
                        </td>
                    </tr>
                    <tr v-for="vendedor in filteredVendedores" :key="vendedor.id" class="hover:bg-white/5 transition-colors group">
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-white group-hover:text-indigo-400 transition-colors">{{ vendedor.nombre }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                            <div>{{ vendedor.email }}</div>
                            <div class="text-[10px] opacity-70">{{ vendedor.telefono }}</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-emerald-400">{{ vendedor.comision_porcentaje }}%</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{{ vendedor.cbu_alias || '-' }}</td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span :class="[
                                'px-2 py-0.5 inline-flex text-[10px] font-bold uppercase rounded border',
                                vendedor.activo ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-500 border-red-500/20'
                            ]">
                                {{ vendedor.activo ? 'Activo' : 'Inactivo' }}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button @click="openModal(vendedor)" class="text-white/20 hover:text-indigo-400 mr-3 transition-colors"><i class="fas fa-pencil-alt"></i></button>
                            <button @click="handleDelete(vendedor)" class="text-white/20 hover:text-red-500 transition-colors" title="Dar de Baja">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Modal -->
        <div v-if="showModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
            <div class="relative mx-auto border border-indigo-500/30 w-full max-w-md shadow-2xl rounded-2xl bg-[#1a050b] overflow-hidden">
                 <!-- Modal Header -->
                 <div class="bg-indigo-950/30 p-4 border-b border-indigo-500/20 flex justify-between items-center">
                     <h3 class="text-lg font-outfit font-bold text-white">{{ isEditing ? 'Editar Vendedor' : 'Nuevo Vendedor' }}</h3>
                     <button @click="closeModal" class="text-white/50 hover:text-white"><i class="fas fa-times"></i></button>
                 </div>
                 
                <div class="p-6">
                    <form @submit.prevent="handleSave" class="space-y-4">
                        <div class="space-y-1">
                            <label class="block text-indigo-200/50 text-[10px] font-bold uppercase tracking-widest">Nombre</label>
                            <input v-model="form.nombre" type="text" required class="bg-black/40 border border-white/10 rounded-lg w-full py-3 px-3 text-white focus:border-indigo-500/50 focus:outline-none transition-colors">
                        </div>
                        <div class="space-y-1">
                            <label class="block text-indigo-200/50 text-[10px] font-bold uppercase tracking-widest">Email</label>
                            <input v-model="form.email" type="email" class="bg-black/40 border border-white/10 rounded-lg w-full py-3 px-3 text-white focus:border-indigo-500/50 focus:outline-none transition-colors">
                        </div>
                         <div class="space-y-1">
                            <label class="block text-indigo-200/50 text-[10px] font-bold uppercase tracking-widest">Teléfono</label>
                            <input v-model="form.telefono" type="text" class="bg-black/40 border border-white/10 rounded-lg w-full py-3 px-3 text-white focus:border-indigo-500/50 focus:outline-none transition-colors">
                        </div>
                        <div class="space-y-1">
                            <label class="block text-indigo-200/50 text-[10px] font-bold uppercase tracking-widest">Comisión (%)</label>
                            <input v-model="form.comision_porcentaje" type="number" step="0.01" class="bg-black/40 border border-white/10 rounded-lg w-full py-3 px-3 text-white font-mono focus:border-indigo-500/50 focus:outline-none transition-colors">
                        </div>
                         <div class="space-y-1">
                            <label class="block text-indigo-200/50 text-[10px] font-bold uppercase tracking-widest">Alias CBU</label>
                            <input v-model="form.cbu_alias" type="text" class="bg-black/40 border border-white/10 rounded-lg w-full py-3 px-3 text-white focus:border-indigo-500/50 focus:outline-none transition-colors">
                        </div>
                        
                        <div class="flex items-center p-3 bg-white/5 rounded-lg border border-white/5">
                            <input v-model="form.activo" type="checkbox" class="h-4 w-4 bg-black/50 border-indigo-500/30 text-indigo-600 focus:ring-indigo-500 rounded cursor-pointer">
                            <label class="ml-2 block text-white/70 text-sm font-bold">Vendedor Activo</label>
                        </div>
                        
                        <div class="flex justify-end gap-3 mt-6 pt-4 border-t border-white/5">
                            <button type="button" @click="closeModal" class="px-4 py-2 text-white/50 hover:text-white font-bold text-xs uppercase tracking-wider">Cancelar</button>
                            <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-6 rounded-lg shadow-lg shadow-indigo-900/40 transition-all">Guardar</button>
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
