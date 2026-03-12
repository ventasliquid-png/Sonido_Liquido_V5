<script setup>
import { ref, reactive, watch, onMounted, onUnmounted, computed } from 'vue';
import { useMaestrosStore } from '../../stores/maestros';
import maestrosService from '../../services/maestros';
import ContextMenu from '../../components/common/ContextMenu.vue';

const props = defineProps({
    show: Boolean,
    initialView: {
        type: String,
        default: 'list' // 'list' | 'form'
    }
});

const emit = defineEmits(['close', 'saved']);

const store = useMaestrosStore();
const view = ref('list'); // 'list' | 'form'
const isEditing = ref(false);
const editingId = ref(null);
const searchTerm = ref('');

const form = reactive({
    nombre: ''
});

// Migration / Wizard State
const migrationMode = ref(false);
const migrationData = reactive({ count: 0, examples: [] });
const migrationTargetId = ref('');
const migrationNewName = ref('');
const migrationSourceId = ref(null);
const migrationTitle = ref('');
const migrationMessage = ref('');

const condiciones = computed(() => {
    if (!searchTerm.value) return store.condicionesIva;
    return store.condicionesIva.filter(c => 
        c.nombre.toLowerCase().includes(searchTerm.value.toLowerCase())
    );
});

// Watch show to reset
// Watch show to reset
// Watch show to reset
watch(() => props.show, (newVal) => {
    if (newVal) {
        view.value = props.initialView; // Use prop to set initial view
        store.fetchCondicionesIva();
        if (props.initialView === 'form') {
            switchToNew();
        }
    }
});

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
});



const switchToNew = () => {
    isEditing.value = false;
    editingId.value = null;
    form.nombre = '';
    view.value = 'form';
};

const switchToEdit = (item) => {
    isEditing.value = true;
    editingId.value = item.id;
    form.nombre = item.nombre;
    view.value = 'form';
};

const handleSave = async () => {
    try {
        if (isEditing.value) {
            await store.updateCondicionIva(editingId.value, form);
        } else {
            await store.createCondicionIva(form);
        }
        view.value = 'list';
        emit('saved');
    } catch (error) {
        // Detect Duplicate (Integrity Error or 409)
        if (error.response && (error.response.status === 409 || error.response.status === 500)) {
            // Check if it's a name collision
            const duplicate = store.condicionesIva.find(c => c.nombre.toLowerCase() === form.nombre.toLowerCase());
            if (duplicate && duplicate.id !== editingId.value) {
                // Offer Merge
                if (!confirm(`La condición "${form.nombre}" ya existe. ¿Desea unificar los clientes y eliminar el duplicado actual?`)) return;
                
                // Prepare Merge
                migrationSourceId.value = editingId.value;
                migrationTargetId.value = duplicate.id;
                await confirmMigration(true); // Auto-confirm for simple merge
                return;
            }
        }
        alert('Error al guardar: ' + (error.response?.data?.detail || error.message));
        console.error(error);
    }
};

const handleDelete = async (id) => {
    try {
        // 1. Check Usage
        const usage = await maestrosService.getCondicionIvaUsage(id);
        if (usage.data.count > 0) {
            // Show Migration Wizard
            migrationMode.value = true;
            migrationSourceId.value = id;
            migrationData.count = usage.data.count;
            migrationData.examples = usage.data.examples;
            migrationTargetId.value = ''; // Force user to select
            migrationTitle.value = 'Condición en Uso';
            migrationMessage.value = `Esta condición está asignada a ${usage.data.count} clientes. Debe reasignarlos antes de eliminar.`;
            return;
        }

        // 2. Direct Delete if unused
        if (!confirm('¿Seguro que desea eliminar esta condición?')) return;
        await store.deleteCondicionIva(id);
    } catch (error) {
        console.error(error);
        alert('Error al eliminar: ' + (error.response?.data?.detail || error.message));
    }
};

const confirmMigration = async (skipPrompt = false) => {
    if (!migrationTargetId.value && !migrationNewName.value) return alert('Seleccione un destino o ingrese un nombre para crear uno nuevo.');
    
    if (!skipPrompt && !confirm('¿Confirma la reasignación y eliminación? Esta acción no se puede deshacer.')) return;

    try {
        let finalTargetId = migrationTargetId.value;

        // Create new if specified
        if (migrationNewName.value) {
            const newCond = await store.createCondicionIva({ nombre: migrationNewName.value });
            finalTargetId = newCond.id;
        }

        await maestrosService.replaceCondicionIva(migrationSourceId.value, finalTargetId);
        // Success
        await store.fetchCondicionesIva();
        migrationMode.value = false;
        view.value = 'list';
        emit('saved'); // Refresh parent if needed
    } catch (error) {
         console.error(error);
         alert('Error en la migración: ' + (error.response?.data?.detail || error.message));
    }
};

const cancelMigration = () => {
    migrationMode.value = false;
    migrationSourceId.value = null;
    migrationTargetId.value = '';
    migrationNewName.value = '';
};

const contextMenu = reactive({
    show: false,
    x: 0,
    y: 0,
    actions: []
});

const handleContextMenu = (e, item) => {
    contextMenu.show = true;
    contextMenu.x = e.clientX;
    contextMenu.y = e.clientY;
    contextMenu.actions = [
        {
            label: 'Editar',
            iconClass: 'fas fa-pencil-alt',
            handler: () => switchToEdit(item)
        },
        {
            label: 'Eliminar',
            iconClass: 'fas fa-trash',
            handler: () => handleDelete(item.id)
        }
    ];
};

const close = () => {
    if (view.value === 'form') {
        view.value = 'list';
    } else {
        emit('close');
    }
};

// Keyboard Shortcuts
const handleKeydown = (e) => {
    if (!props.show) return;
    if (e.key === 'Escape') close();
    if (e.key === 'F10' && view.value === 'form') {
        e.preventDefault();
        handleSave();
    }
    if (e.key === 'F4' && view.value === 'list') {
         e.preventDefault();
         switchToNew();
    }
};

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
    <Teleport to="body">
        <div v-if="show" class="fixed inset-0 z-[999999] flex items-center justify-center" style="z-index: 999999 !important;">
            <!-- Backdrop (Clickable) -->
            <div class="absolute inset-0 bg-black/80 backdrop-blur-sm pointer-events-auto" @click="emit('close')"></div>
            
            <!-- Modal Window -->
            <div class="relative pointer-events-auto w-[450px] bg-[#05151f] border-2 border-cyan-500 shadow-2xl rounded-lg flex flex-col max-h-[70vh]">
                
                <!-- HEADER -->
                <div class="flex justify-between items-center p-4 border-b border-cyan-900/30 bg-[#0a253a]/50">
                    <h3 class="text-lg font-bold text-cyan-100">
                        {{ view === 'list' ? 'Administrar Condiciones IVA' : (isEditing ? 'Editar Condición' : 'Nueva Condición') }}
                    </h3>
                    <button @click="emit('close')" class="text-cyan-500 hover:text-cyan-300">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <!-- LIST VIEW -->
                <div v-if="view === 'list'" class="flex-1 flex flex-col overflow-hidden">
                    <div class="p-4 border-b border-cyan-900/30 flex gap-2">
                         <div class="relative flex-1">
                            <i class="fas fa-search absolute left-3 top-2.5 text-cyan-700/50 text-xs"></i>
                            <input 
                                v-model="searchTerm" 
                                class="w-full bg-cyan-900/10 border border-cyan-900/30 rounded pl-8 pr-2 py-1.5 text-sm text-cyan-100 placeholder-cyan-800 transition-colors focus:border-cyan-500/50 outline-none" 
                                placeholder="Buscar..."
                                autofocus
                            />
                        </div>
                        <button @click="switchToNew" class="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-bold transition-colors shadow-lg shadow-cyan-900/20">
                            <i class="fas fa-plus mr-1"></i> NUEVO (F4)
                        </button>
                    </div>
                    
                    <div class="flex-1 overflow-y-auto p-4 space-y-2">
                        <div v-if="condiciones.length === 0" class="text-center text-cyan-900/50 text-sm py-4">
                            No hay condiciones.
                        </div>
                        <div 
                            v-for="item in condiciones" 
                            :key="item.id"
                            class="flex justify-between items-center p-3 bg-cyan-900/20 hover:bg-cyan-900/30 border border-cyan-900/30 rounded-lg group transition-colors cursor-context-menu"
                            @contextmenu.prevent="handleContextMenu($event, item)"
                        >
                            <span class="font-bold text-sm text-cyan-100">{{ item.nombre }}</span>
                            <div class="flex gap-2 opacity-50 group-hover:opacity-100 transition-opacity">
                                <button @click.stop="switchToEdit(item)" class="text-cyan-400 hover:text-cyan-200 p-1" title="Editar">
                                    <i class="fas fa-pencil-alt"></i>
                                </button>
                                <button @click.stop="handleDelete(item.id)" class="text-red-500 hover:text-red-300 p-1" title="Eliminar">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- FORM VIEW -->
                <div v-if="view === 'form'" class="p-6">
                    <form @submit.prevent="handleSave">
                        <div class="mb-6">
                            <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Nombre</label>
                            <input v-model="form.nombre" type="text" required class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors" placeholder="Ej: Responsable Inscripto" />
                        </div>
                        <div class="flex justify-end gap-3">
                            <button type="button" @click="close" class="px-4 py-2 bg-transparent hover:bg-cyan-900/20 text-cyan-500 text-sm font-bold rounded transition-colors border border-transparent hover:border-cyan-900/30">
                                Volver (ESC)
                            </button>
                            <button type="submit" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-sm font-bold shadow-lg shadow-cyan-900/20 transition-colors">
                                Guardar (F10)
                            </button>
                        </div>
                    </form>
                </div>
                
                <!-- MIGRATION WIZARD (Overlay) -->
                <div v-if="migrationMode" class="absolute inset-0 bg-[#05151f] z-50 flex flex-col p-6">
                    <div class="mb-4">
                        <h3 class="text-lg font-bold text-orange-400 mb-2">
                            <i class="fas fa-exclamation-triangle mr-2"></i>{{ migrationTitle }}
                        </h3>
                        <p class="text-cyan-100/90 text-sm mb-4 leading-relaxed">
                            {{ migrationMessage }}
                        </p>
                        
                        <div class="bg-cyan-900/20 p-3 rounded mb-4 border border-cyan-900/30">
                            <h4 class="text-xs font-bold text-cyan-500 uppercase mb-2">Clientes Afectados (Ejemplos)</h4>
                            <ul class="text-sm text-cyan-100 list-disc list-inside">
                                <li v-for="ex in migrationData.examples" :key="ex">{{ ex }}</li>
                                <li v-if="migrationData.count > migrationData.examples.length" class="text-xs text-cyan-500 mt-1 italic">
                                    ...y {{ migrationData.count - migrationData.examples.length }} más.
                                </li>
                            </ul>
                        </div>
                    </div>

                    <div class="flex-1 overflow-y-auto">
                        <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Reasignar a Existente:</label>
                        <select v-model="migrationTargetId" :disabled="!!migrationNewName" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none mb-4 disabled:opacity-50">
                            <option value="" disabled>Seleccione Condición...</option>
                            <option 
                                v-for="c in condiciones.filter(x => x.id !== migrationSourceId)" 
                                :key="c.id" 
                                :value="c.id"
                            >
                                {{ c.nombre }}
                            </option>
                        </select>

                        <div class="flex items-center gap-2 mb-4">
                            <div class="h-px bg-cyan-900/30 flex-1"></div>
                            <span class="text-xs text-cyan-500 font-bold uppercase">O Crear Nueva</span>
                            <div class="h-px bg-cyan-900/30 flex-1"></div>
                        </div>

                        <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Nombre Nueva Condición:</label>
                        <input 
                            v-model="migrationNewName" 
                            type="text" 
                            :disabled="!!migrationTargetId"
                            class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors disabled:opacity-50" 
                            placeholder="Ej: Malo Pagador" 
                        />
                    </div>

                    <div class="flex justify-end gap-3 mt-6">
                        <button @click="cancelMigration" class="px-4 py-2 bg-transparent hover:bg-cyan-900/20 text-cyan-500 text-sm font-bold rounded transition-colors border border-transparent hover:border-cyan-900/30">
                            Cancelar
                        </button>
                        <button @click="confirmMigration(false)" class="px-4 py-2 bg-orange-600 hover:bg-orange-500 text-white rounded text-sm font-bold shadow-lg shadow-orange-900/20 transition-colors">
                            Reasignar y Eliminar
                        </button>
                    </div>
                </div>

            </div>
        </div>
        
        <!-- Context Menu (Nested Teleport to ensure it's on top of everything) -->
        <Teleport to="body">
             <ContextMenu 
                v-if="contextMenu.show" 
                v-model="contextMenu.show" 
                :x="contextMenu.x" 
                :y="contextMenu.y" 
                :actions="contextMenu.actions" 
                @close="contextMenu.show = false"
            />
        </Teleport>
    </Teleport>
</template>

<style scoped>
.animate-scale-in {
    animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}
</style>
