<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans hud-border-amber">
    
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative min-w-0 z-10">
      
      <!-- Top Bar -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-rose-900/20 bg-black/20 px-6 backdrop-blur-sm shrink-0">
        <!-- Title -->
        <div class="flex items-center gap-3">
            <h1 class="font-outfit text-xl font-semibold text-rose-100">
                Explorador de Rubros
            </h1>
            <span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-bold uppercase tracking-wider border border-rose-500/30">
                Flat View
            </span>
        </div>

        <!-- Search & Tools -->
        <div class="flex items-center gap-4">
          <div class="relative">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-rose-400/50"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar rubro..."
              class="h-9 w-64 rounded-full border border-rose-900/30 bg-[#0a0204] pl-10 pr-4 text-sm text-rose-100 placeholder-rose-900/50 focus:border-rose-500 focus:outline-none focus:ring-1 focus:ring-rose-500"
            />
          </div>
          
          <div class="h-6 w-px bg-rose-900/20"></div>

          <!-- Status Filter -->
          <div class="flex bg-rose-900/10 rounded-lg p-1 border border-rose-900/20">
            <button 
                @click="filterStatus = 'all'"
                class="px-3 py-1 text-xs font-medium rounded-md transition-all"
                :class="filterStatus === 'all' ? 'bg-rose-600 text-white shadow-sm' : 'text-rose-100/50 hover:text-rose-100'"
            >
                Todos
            </button>
            <button 
                @click="filterStatus = 'active'"
                class="px-3 py-1 text-xs font-medium rounded-md transition-all"
                :class="filterStatus === 'active' ? 'bg-green-600 text-white shadow-sm' : 'text-rose-100/50 hover:text-rose-100'"
            >
                Activos
            </button>
            <button 
                @click="filterStatus = 'inactive'"
                class="px-3 py-1 text-xs font-medium rounded-md transition-all"
                :class="filterStatus === 'inactive' ? 'bg-red-600 text-white shadow-sm' : 'text-rose-100/50 hover:text-rose-100'"
            >
                Inactivos
            </button>
          </div>

          <div class="h-6 w-px bg-rose-900/20"></div>

          <!-- Sort Menu -->
          <div class="relative">
            <button 
                @click="showSortMenu = !showSortMenu" 
                class="flex items-center gap-2 rounded-lg border border-rose-900/20 bg-rose-900/10 px-3 py-1.5 text-xs font-medium text-rose-200 hover:bg-rose-900/20 transition-colors" 
                title="Ordenar"
            >
                <i class="fas fa-sort-amount-down"></i>
                <span v-if="sortBy === 'alpha_asc'">A-Z</span>
                <span v-else-if="sortBy === 'alpha_desc'">Z-A</span>
                <span v-else-if="sortBy === 'id_desc'">Recientes</span>
                <span v-else>ordenar</span>
            </button>
            
            <!-- Dropdown -->
            <div v-if="showSortMenu" class="absolute right-0 mt-2 w-48 bg-[#2e0a13] border border-rose-500/30 rounded-lg shadow-xl z-50 overflow-hidden">
                <div class="fixed inset-0 z-40" @click="showSortMenu = false"></div>
                <div class="relative z-50 py-1">
                    <button @click="sortBy = 'alpha_asc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-rose-100 hover:bg-rose-500/10" :class="{ 'text-rose-400 font-bold': sortBy === 'alpha_asc' }">A-Z Alfabético</button>
                    <button @click="sortBy = 'alpha_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-rose-100 hover:bg-rose-500/10" :class="{ 'text-rose-400 font-bold': sortBy === 'alpha_desc' }">Z-A Alfabético</button>
                    <button @click="sortBy = 'id_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-rose-100 hover:bg-rose-500/10" :class="{ 'text-rose-400 font-bold': sortBy === 'id_desc' }">Más Recientes</button>
                </div>
            </div>
          </div>

          <div class="h-6 w-px bg-rose-900/20"></div>

          <!-- View Toggle -->
          <div class="flex bg-rose-900/10 rounded-lg p-1 border border-rose-900/20">
            <button 
                @click="viewMode = 'grid'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'grid' ? 'bg-rose-500/20 text-rose-400' : 'text-rose-900/50 hover:text-rose-200'"
                title="Vista Cuadrícula"
            >
                <i class="fas fa-border-all"></i>
            </button>
            <button 
                @click="viewMode = 'list'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'list' ? 'bg-rose-500/20 text-rose-400' : 'text-rose-900/50 hover:text-rose-200'"
                title="Vista Lista"
            >
                <i class="fas fa-list"></i>
            </button>
          </div>

          <div class="h-6 w-px bg-rose-900/20"></div>

          <button 
            @click="openNewInspector"
            class="ml-2 flex items-center gap-2 rounded-lg bg-orange-600 px-4 py-1.5 text-sm font-bold text-white shadow-lg shadow-orange-500/20 transition-all hover:bg-orange-500 hover:shadow-orange-500/40"
          >
            <i class="fas fa-plus"></i>
            <span class="hidden sm:inline">Nuevo Rubro</span>
          </button>

        </div>
      </header>

      <!-- Content Area -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-rose-900/20 scrollbar-thumb-rose-900/50">
         <div v-if="loading" class="flex justify-center py-8">
            <i class="fa-solid fa-circle-notch fa-spin text-rose-500 text-4xl"></i>
         </div>
         
         <div v-else-if="filteredRubros.length === 0" class="flex flex-col items-center justify-center h-64 text-rose-900/50">
             <i class="fas fa-search text-4xl mb-4 opacity-50"></i>
             <p>No se encontraron rubros.</p>
         </div>

         <div v-else>
             <!-- Grid View -->
             <div v-if="viewMode === 'grid'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
                 <div 
                     v-for="rubro in filteredRubros"
                     :key="rubro.id"
                     class="relative w-full min-h-[140px]"
                 >
                    <FichaCard
                        class="w-full cursor-pointer"
                        :title="rubro.nombre"
                        :subtitle="`${rubro.codigo}`"
                        :status="rubro.activo ? 'active' : 'inactive'"
                        :selected="selectedRubro?.id === rubro.id"
                        @click="openEditInspector(rubro)"
                    >
                        <template #icon>
                            <i class="fas fa-tag"></i>
                        </template>
                        <template #actions>
                            <button 
                                @click.stop="toggleRubroStatus(rubro)"
                                v-if="rubro.activo"
                                class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 mr-2 bg-green-500/50"
                                title="Desactivar"
                            >
                                <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm translate-x-3.5" />
                            </button>
                             <button 
                                @click.stop="toggleRubroStatus(rubro)"
                                v-else
                                class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 mr-2 bg-red-500/50"
                                title="Activar"
                            >
                                <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm translate-x-1" />
                            </button>

                            <button 
                                @click.stop="initiateDelete(rubro)"
                                class="text-rose-900/50 hover:text-red-500 transition-colors"
                                title="Eliminar Rubro"
                            >
                                <i class="fas fa-trash"></i>
                            </button>
                        </template>
                    </FichaCard>
                 </div>
             </div>

             <!-- List View -->
             <div v-else class="space-y-1">
                 <div 
                     v-for="rubro in filteredRubros"
                     :key="rubro.id"
                     @click="openEditInspector(rubro)"
                     class="flex items-center justify-between p-2 rounded border transition-all cursor-pointer group"
                     :class="selectedRubro?.id === rubro.id ? 'bg-rose-900/30 border-rose-500' : 'bg-transparent border-rose-900/10 hover:bg-rose-900/10'"
                 >
                     <div class="flex items-center gap-3">
                         <div class="w-2 h-2 rounded-full" :class="rubro.activo ? 'bg-green-500' : 'bg-red-500'"></div>
                         <span class="font-bold text-sm" :class="selectedRubro?.id === rubro.id ? 'text-white' : 'text-rose-100'">
                             {{ rubro.nombre }}
                         </span>
                         <span class="font-mono text-xs text-rose-500">{{ rubro.codigo }}</span>
                     </div>
                     
                    <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                            @click.stop="toggleRubroStatus(rubro)"
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0"
                            :class="rubro.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                            title="Click para cambiar estado"
                        >
                            <span 
                                class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                :class="rubro.activo ? 'translate-x-3.5' : 'translate-x-1'"
                            />
                        </button>
                        <button @click.stop="initiateDelete(rubro)" class="w-6 h-6 rounded bg-rose-500/10 hover:bg-red-600 hover:text-white text-red-400 flex items-center justify-center">
                            <i class="fas fa-trash text-xs"></i>
                        </button>
                     </div>
                 </div>
             </div>
         </div>
      </div>
    </main>

    <!-- INSPECTOR -->
    <aside class="w-96 border-l border-rose-900/20 bg-[#1e293b] flex flex-col shrink-0 custom-scrollbar overflow-hidden shadow-2xl relative z-30">
        
        <div v-if="!inspectorTarget && !isCreating" class="h-full flex flex-col items-center justify-center text-rose-900/20 p-8 text-center select-none">
            <i class="fas fa-pencil text-6xl mb-4"></i>
            <h3 class="text-xl font-bold uppercase tracking-widest mb-2 text-rose-900/40">Inspector</h3>
            <p class="text-sm">Seleccione un rubro para ver sus detalles</p>
        </div>

        <div v-else class="flex flex-col h-full">
            <!-- Inspector Header -->
            <div class="h-16 flex items-center justify-between px-6 border-b border-rose-900/20 bg-[#2e0a13]/30 shrink-0">
                <h3 class="text-sm font-bold uppercase tracking-wider text-rose-400">
                    {{ isCreating ? 'Nuevo' : 'Editar' }} Rubro
                </h3>
                <button @click="closeInspector" class="text-gray-500 hover:text-white transition-colors">
                    <i class="fa-solid fa-times"></i>
                </button>
            </div>

            <div class="flex-1 p-6 space-y-6 overflow-y-auto">
                 <!-- Icon -->
                 <div class="flex justify-center mb-4">
                    <div class="w-16 h-16 rounded-full bg-rose-900/10 flex items-center justify-center text-2xl text-rose-500 border border-rose-500/20">
                        <i class="fas fa-tag"></i>
                    </div>
                 </div>

                 <!-- Form -->
                 <div class="space-y-4">
                     <div>
                        <label class="block text-xs font-bold text-gray-500 mb-1 uppercase">Código</label>
                        <input v-model="form.codigo" type="text" maxlength="8" class="w-full bg-black/30 border border-rose-900/30 rounded p-2 text-white font-mono uppercase focus:border-rose-500 outline-none">
                     </div>
                     
                     <div>
                        <label class="block text-xs font-bold text-gray-500 mb-1 uppercase">Nombre</label>
                        <input v-model="form.nombre" type="text" class="w-full bg-black/30 border border-rose-900/30 rounded p-2 text-white focus:border-rose-500 outline-none">
                     </div>

                     <!-- Margen Default (V6) -->
                     <div class="p-3 bg-rose-500/5 rounded border border-rose-500/20">
                        <label class="block text-[0.6rem] font-bold text-rose-400 mb-1 uppercase tracking-widest">Margen Propuesto (%)</label>
                        <div class="flex items-center gap-3">
                            <input 
                                v-model.number="form.margen_default" 
                                type="number" 
                                step="0.5"
                                class="w-24 bg-black/40 border border-rose-900/30 rounded p-2 text-white font-mono focus:border-rose-500 outline-none text-right"
                            >
                            <span class="text-[0.65rem] text-rose-400/50 italic">Este margen se aplicará a todos los productos de este rubro que no tengan una Cm artesanal definida.</span>
                        </div>
                     </div>

                      <!-- Activo Toggle -->
                     <div class="flex items-center gap-3 pt-2">
                         <button 
                            @click="form.activo = !form.activo"
                            class="w-10 h-5 rounded-full relative transition-colors"
                            :class="form.activo ? 'bg-green-600' : 'bg-gray-700'"
                         >
                            <div class="absolute top-1 left-1 bg-white w-3 h-3 rounded-full transition-transform" :class="{'translate-x-5': form.activo}"></div>
                         </button>
                         <span class="text-sm text-gray-400">{{ form.activo ? 'Activo' : 'Inactivo' }}</span>
                     </div>
                 </div>
            </div>

            <!-- Footer Actions -->
            <div class="p-6 border-t border-rose-900/20 bg-[#2e0a13]/20 shrink-0">
                <button 
                    @click="saveInspector"
                    :disabled="saving"
                    class="w-full py-3 rounded bg-rose-600 font-bold text-sm text-white shadow-lg shadow-rose-600/20 hover:bg-rose-500 transition-all flex items-center justify-center gap-2"
                >
                    <i v-if="saving" class="fas fa-circle-notch fa-spin"></i>
                    <span v-else>Guardar Cambios (F10)</span>
                </button>
                <div v-if="!isCreating" class="mt-3 text-center">
                    <button @click="initiateDelete(inspectorTarget)" class="text-xs text-red-400 hover:text-red-300 underline">
                        Eliminar Registro
                    </button>
                </div>
            </div>
        </div>
    </aside>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import FichaCard from '../../components/hawe/FichaCard.vue';
import { useProductosStore } from '../../stores/productos.js';
import { useNotificationStore } from '../../stores/notification.js';

const productosStore = useProductosStore();
const notificationStore = useNotificationStore();

// State
const loading = ref(productosStore.rubros.length === 0);
const saving = ref(false);
const searchQuery = ref('');
const filterStatus = ref('all');
const viewMode = ref('grid');
const sortBy = ref('alpha_asc');
const showSortMenu = ref(false);

// Inspector State
const inspectorTarget = ref(null);
const isCreating = ref(false);
const form = ref({
    id: null,
    codigo: '',
    nombre: '',
    padre_id: null, // Always null in flat model
    activo: true,
    margen_default: 0
});

const selectedRubro = computed(() => inspectorTarget.value);

const filteredRubros = computed(() => {
    let result = [...productosStore.rubros]; // Use Store State
    
    // Filter Query
    if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase();
        result = result.filter(r => 
            r.nombre.toLowerCase().includes(q) || 
            r.codigo.toLowerCase().includes(q)
        );
    }

    if (filterStatus.value === 'active') result = result.filter(r => r.activo);
    if (filterStatus.value === 'inactive') result = result.filter(r => !r.activo);
    
    return result.sort((a,b) => {
        switch (sortBy.value) {
            case 'alpha_asc': return a.nombre.localeCompare(b.nombre);
            case 'alpha_desc': return b.nombre.localeCompare(a.nombre);
            case 'id_desc': return b.id - a.id;
            case 'id_asc': return a.id - b.id;
            default: return 0;
        }
    });
});

const fetchRubros = async () => {
    // Only show spinner if we have no data
    if (productosStore.rubros.length === 0) {
        loading.value = true;
    }
    try {
        await productosStore.fetchRubros();
    } finally {
        loading.value = false;
    }
};

const openNewInspector = () => {
    isCreating.value = true;
    inspectorTarget.value = {}; 
    form.value = { codigo: '', nombre: '', padre_id: null, activo: true, margen_default: 0 };
};

const openEditInspector = (rubro) => {
    isCreating.value = false;
    inspectorTarget.value = rubro;
    form.value = { ...rubro };
};

const closeInspector = () => {
    inspectorTarget.value = null;
    isCreating.value = false;
};

const saveInspector = async () => {
    if (!form.value.codigo || !form.value.nombre) {
        notificationStore.add('Datos incompletos', 'warning');
        return;
    }
    
    saving.value = true;
    try {
        const payload = { ...form.value };
        
        if (form.value.id) {
            await productosStore.updateRubro(form.value.id, payload);
        } else {
            await productosStore.createRubro(payload);
        }
        closeInspector();
    } catch (e) {
        // Error already handled in store
    } finally {
        saving.value = false;
    }
};

const toggleRubroStatus = async (rubro) => {
    try {
        // We reuse updateRubro
        await productosStore.updateRubro(rubro.id, { ...rubro, activo: !rubro.activo });
        // Store updates the list automatically
        if (inspectorTarget.value?.id === rubro.id) {
            form.value.activo = !rubro.activo; // Toggle local form state if open
        }
    } catch (e) {
        // Handled in store
    }
};

const initiateDelete = async (rubro) => {
    if (confirm(`¿Eliminar definitivamente el rubro "${rubro.nombre}"?`)) {
        try {
            await productosStore.deleteRubro(rubro.id);
            if (inspectorTarget.value?.id === rubro.id) closeInspector();
        } catch (e) {
             // Handled in store
        }
    }
};

const handleKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault();
        if (inspectorTarget.value || isCreating.value) saveInspector();
    }
    if (e.key === 'Escape') {
        if (inspectorTarget.value) closeInspector();
    }
};

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
    fetchRubros();
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});

</script>
