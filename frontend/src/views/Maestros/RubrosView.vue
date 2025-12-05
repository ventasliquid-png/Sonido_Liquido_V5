<template>
  <div class="flex h-full w-full bg-[#1a050b] text-gray-200 overflow-hidden font-sans">
    
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative">
      <!-- Top Bar -->
      <!-- Top Bar -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-rose-900/20 bg-[#2e0a13]/50 px-6 backdrop-blur-sm">
        <!-- Title -->
        <h1 class="font-outfit text-xl font-semibold text-rose-100">
            Explorador de Rubros
        </h1>

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
                <span v-else>Ordenar</span>
            </button>
            
            <!-- Dropdown -->
            <div v-if="showSortMenu" class="absolute right-0 mt-2 w-56 bg-[#0a253a] border border-white/10 rounded-lg shadow-xl z-50 overflow-hidden">
                <div class="fixed inset-0 z-40" @click="showSortMenu = false"></div>
                <div class="relative z-50 py-1">
                    <button class="block w-full text-left px-4 py-2 text-sm text-white/50 hover:bg-white/5 cursor-not-allowed">Más Usados (Popularidad)</button>
                    <div class="h-px bg-white/10 my-1"></div>
                    <button @click="sortBy = 'alpha_asc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_asc' }">A-Z Alfabético</button>
                    <button @click="sortBy = 'alpha_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'alpha_desc' }">Z-A Alfabético</button>
                    <div class="h-px bg-white/10 my-1"></div>
                    <button @click="sortBy = 'oldest'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'oldest' }">Más Antiguos</button>
                    <button @click="sortBy = 'newest'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10" :class="{ 'text-cyan-400 font-bold': sortBy === 'newest' }">Más Recientes</button>
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

          <button 
            @click="createNewRoot"
            class="ml-2 flex items-center gap-2 rounded-lg bg-orange-600 px-4 py-1.5 text-sm font-bold text-white shadow-lg shadow-orange-500/20 transition-all hover:bg-orange-500 hover:shadow-orange-500/40"
          >
            <i class="fas fa-plus"></i>
            <span class="hidden sm:inline">Nuevo</span>
          </button>

        </div>
      </header>

      <!-- Content List -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-rose-900/20 scrollbar-thumb-rose-900/50">
        <div v-if="loading" class="flex justify-center py-8">
          <i class="fa-solid fa-circle-notch fa-spin text-rose-500"></i>
        </div>
        
        <div v-else-if="filteredRubros.length === 0" class="text-center py-8 text-rose-900/50 text-sm">
          No se encontraron rubros.
        </div>

        <div v-else>
            <!-- Grid View -->
            <div v-if="viewMode === 'grid'" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
              <div 
                v-for="rubro in filteredRubros"
                :key="rubro.id"
                class="relative w-full min-h-[140px]"
              >
                <FichaCard
                    class="w-full"
                    :title="rubro.nombre"
                    :subtitle="rubro.codigo"
                    :status="rubro.activo ? 'active' : 'inactive'"
                    :selected="selectedRubro?.id === rubro.id"
                    @click="selectRubro(rubro)"
                    @select="selectRubro(rubro)"
                >
                    <template #icon>
                        <i class="fas fa-layer-group"></i>
                    </template>
                    <template #actions>
                         <button 
                            @click.stop="toggleRubroStatus(rubro)"
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 ml-2"
                            :class="rubro.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                            title="Click para cambiar estado"
                        >
                            <span 
                                class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                :class="rubro.activo ? 'translate-x-3.5' : 'translate-x-1'"
                            />
                        </button>
                    </template>
                </FichaCard>
              </div>
            </div>

            <!-- List View -->
            <div v-else class="flex flex-col gap-2">
                <!-- Header Row -->
                <div class="flex items-center justify-between px-4 py-2 text-xs font-bold text-rose-900/50 uppercase tracking-wider">
                    <div class="flex-1">Nombre</div>
                    <div class="w-24 text-center">Código</div>
                    <div class="w-24 text-center">Estado</div>
                    <div class="w-10"></div>
                </div>

                <!-- Items -->
                <div 
                    v-for="rubro in filteredRubros" 
                    :key="rubro.id"
                    @click="selectRubro(rubro)"
                    class="group flex items-center justify-between p-3 rounded-lg border border-rose-900/10 bg-rose-900/5 hover:bg-rose-900/10 cursor-pointer transition-colors"
                    :class="{ 'ring-1 ring-rose-500 bg-rose-900/20': selectedRubro?.id === rubro.id }"
                >
                    <div class="flex items-center gap-4 flex-1 min-w-0">
                        <div class="h-8 w-8 rounded bg-gradient-to-br from-rose-600 to-pink-700 flex items-center justify-center text-white shrink-0 text-xs shadow-lg shadow-rose-900/50">
                            <i class="fas fa-layer-group"></i>
                        </div>
                        <div class="min-w-0 flex-1">
                            <h3 class="font-bold text-rose-100 truncate flex items-center gap-2">
                                {{ rubro.nombre }}
                                <span v-if="rubro.hijos && rubro.hijos.length > 0" class="text-[10px] bg-rose-500/10 px-1.5 py-0.5 rounded text-rose-300">
                                    {{ rubro.hijos.length }} sub
                                </span>
                            </h3>
                        </div>
                    </div>
                    
                    <div class="w-24 text-center font-mono text-sm text-rose-400 font-bold">
                        {{ rubro.codigo }}
                    </div>

                    <div class="w-24 flex justify-center">
                         <div class="flex items-center gap-2 bg-black/20 px-2 py-1 rounded-full border border-rose-900/10">
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
                            <span class="text-[10px] uppercase font-bold text-white/50 hidden sm:inline">{{ rubro.activo ? 'Activo' : 'Inactivo' }}</span>
                        </div>
                    </div>

                    <div class="w-10 flex justify-end">
                        <button class="text-rose-900/30 hover:text-rose-200 opacity-0 group-hover:opacity-100 transition-opacity">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </main>

    <!-- Right: Inspector (Form) -->
    <aside 
      class="w-96 flex flex-col border-l border-rose-900/20 bg-[#0f0306]/95 backdrop-blur-xl z-20 shadow-2xl transition-all"
    >
      <!-- Inspector Header -->
      <div class="h-16 flex items-center justify-between px-6 border-b border-rose-900/20 bg-[#2e0a13]/30 shrink-0">
        <h3 class="text-sm font-bold uppercase tracking-wider text-rose-400">
          {{ isCreating ? 'Nuevo Rubro' : (selectedRubro ? 'Propiedades' : 'Inspector') }}
        </h3>
        <button v-if="selectedRubro || isCreating" @click="cancelEdit" class="text-gray-500 hover:text-white transition-colors">
          <i class="fa-solid fa-times"></i>
        </button>
      </div>

      <!-- Inspector Body (Form) -->
      <div v-if="selectedRubro || isCreating" class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
        
        <!-- Icon / Preview -->
        <div class="flex justify-center mb-4">
           <div class="w-20 h-20 rounded-full bg-rose-900/20 flex items-center justify-center text-3xl text-rose-500 border border-rose-500/30 shadow-[0_0_15px_rgba(244,63,94,0.2)]">
             <i class="fa-solid fa-layer-group"></i>
           </div>
        </div>

        <!-- Padre Info -->
        <div v-if="form.padre_id" class="bg-rose-900/10 border border-rose-900/20 rounded px-4 py-3 flex items-center gap-3">
          <i class="fa-solid fa-level-up-alt text-rose-500/50 text-xl"></i>
          <div>
            <span class="text-[10px] text-rose-400/70 uppercase tracking-wider font-bold block">Rubro Padre</span>
            <div class="text-rose-200 text-sm font-medium">{{ getRubroName(form.padre_id) }}</div>
          </div>
        </div>

        <!-- Title Display (Read-onlyish feel until edited) -->
        <div class="text-center mb-6" v-if="!isCreating">
            <h2 class="text-xl font-bold text-white">{{ form.nombre }}</h2>
            <p class="font-mono text-rose-400">{{ form.codigo }}</p>
        </div>

        <!-- Form Fields -->
        <div class="space-y-4">
          <!-- Código -->
          <div>
            <label class="block text-xs font-bold text-gray-500 mb-1 uppercase">Código <span class="text-rose-500">*</span></label>
            <input 
              v-model="form.codigo"
              @input="form.codigo = $event.target.value.toUpperCase()"
              type="text" 
              class="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500 transition-colors font-mono tracking-wider"
              placeholder="Ej: BEB"
              maxlength="3"
            >
            <p class="text-[10px] text-gray-600 mt-1 text-right">{{ form.codigo.length }}/3</p>
          </div>

          <!-- Nombre -->
          <div>
            <label class="block text-xs font-bold text-gray-500 mb-1 uppercase">Nombre <span class="text-rose-500">*</span></label>
            <input 
              v-model="form.nombre"
              type="text" 
              class="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500 transition-colors"
              placeholder="Ej: Bebidas sin Alcohol"
            >
          </div>

          <!-- Activo -->
          <div class="pt-2">
            <label class="flex items-center gap-3 cursor-pointer group p-3 rounded border border-white/10 hover:bg-white/5 transition-colors">
              <div class="relative">
                <input type="checkbox" v-model="form.activo" class="sr-only peer">
                <div class="w-10 h-5 bg-gray-800 rounded-full peer-checked:bg-rose-600 transition-colors"></div>
                <div class="absolute left-1 top-1 w-3 h-3 bg-white rounded-full peer-checked:translate-x-5 transition-transform"></div>
              </div>
              <span class="text-sm font-medium text-gray-400 group-hover:text-gray-300 transition-colors">Rubro Activo</span>
            </label>
          </div>
        </div>

        <!-- Sub-rubros List (If editing) -->
        <div v-if="!isCreating && selectedRubro?.hijos?.length > 0" class="pt-4 border-t border-white/10">
            <h4 class="text-xs font-bold text-gray-500 uppercase mb-3">Sub-rubros</h4>
            <div class="space-y-2">
                <div v-for="hijo in selectedRubro.hijos" :key="hijo.id" class="flex items-center justify-between p-2 bg-white/5 rounded border border-white/5">
                    <span class="text-sm text-white">{{ hijo.nombre }}</span>
                    <span class="text-xs font-mono text-rose-400">{{ hijo.codigo }}</span>
                </div>
            </div>
        </div>

        <!-- Actions (Add Child / Delete) -->
        <div v-if="!isCreating" class="pt-6 border-t border-white/10 space-y-3">
           <button 
            @click="createNewChild"
            class="w-full py-2 border border-dashed border-rose-500/30 rounded text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition-colors text-xs font-bold uppercase flex items-center justify-center gap-2"
          >
            <i class="fa-solid fa-level-down-alt"></i>
            Agregar Sub-rubro
          </button>
          
          <button 
            @click="confirmDelete"
            class="w-full py-2 border border-transparent rounded text-red-500/50 hover:text-red-400 hover:bg-red-900/10 transition-colors text-xs font-bold uppercase flex items-center justify-center gap-2"
          >
            <i class="fa-solid fa-trash"></i>
            Eliminar Rubro
          </button>
        </div>

      </div>

      <!-- Empty State -->
      <div v-else class="flex flex-1 flex-col items-center justify-center p-8 text-center text-rose-900/40">
        <i class="fas fa-mouse-pointer mb-4 text-3xl"></i>
        <p class="text-sm font-medium">Selecciona un elemento para ver sus propiedades</p>
      </div>

      <!-- Inspector Footer -->
      <div v-if="selectedRubro || isCreating" class="p-6 border-t border-white/10 bg-black/20">
        <button 
          @click="saveRubro"
          :disabled="saving"
          class="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white text-sm font-bold rounded shadow-lg shadow-rose-900/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transform active:scale-95"
        >
          <i v-if="saving" class="fa-solid fa-circle-notch fa-spin"></i>
          {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
        </button>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import FichaCard from '../../components/hawe/FichaCard.vue';
import rubrosApi from '../../services/rubrosApi.js';
import { useNotificationStore } from '../../stores/notification.js';

const rubros = ref([]);
const loading = ref(true);
const saving = ref(false);
const selectedRubro = ref(null);
const isCreating = ref(false);

const form = ref({
  id: null,
  codigo: '',
  nombre: '',
  padre_id: null,
  activo: true
});

const searchQuery = ref('');
const viewMode = ref('grid');
const sortBy = ref('alpha_asc');
const showSortMenu = ref(false);
const filterStatus = ref('all');

// Helper para aplanar el árbol y buscar nombres
const flatRubros = computed(() => {
  const flatten = (list) => {
    let result = [];
    list.forEach(r => {
      result.push(r);
      if (r.hijos) result = result.concat(flatten(r.hijos));
    });
    return result;
  };
  return flatten(rubros.value);
});

const filteredRubros = computed(() => {
    let result = flatRubros.value;
    
    // Filter by Status
    if (filterStatus.value === 'active') {
        result = result.filter(r => r.activo);
    } else if (filterStatus.value === 'inactive') {
        result = result.filter(r => !r.activo);
    }

    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(r => 
            r.nombre.toLowerCase().includes(query) || 
            r.codigo.toLowerCase().includes(query)
        );
    }

    return result.sort((a, b) => {
        if (sortBy.value === 'alpha_asc') {
            return a.nombre.localeCompare(b.nombre);
        } else if (sortBy.value === 'alpha_desc') {
            return b.nombre.localeCompare(a.nombre);
        } else if (sortBy.value === 'newest') {
            return b.id - a.id;
        } else if (sortBy.value === 'oldest') {
            return a.id - b.id;
        }
        return 0;
    });
});

const getRubroName = (id) => {
  const r = flatRubros.value.find(x => x.id === id);
  return r ? r.nombre : 'Desconocido';
};

const fetchRubros = async () => {
  loading.value = true;
  try {
    const { data } = await rubrosApi.getAll();
    rubros.value = data;
  } catch (error) {
    console.error('Error cargando rubros:', error);
    useNotificationStore().add('Error al cargar rubros', 'error');
  } finally {
    loading.value = false;
  }
};

const selectRubro = (rubro) => {
  if (isCreating.value) {
    if (!confirm('Hay cambios sin guardar. ¿Descartar?')) return;
  }
  isCreating.value = false;
  selectedRubro.value = rubro;
  form.value = { ...rubro }; // Copia simple
};

const toggleRubroStatus = async (rubro) => {
    // If turning OFF (Active -> Inactive), ask for confirmation
    if (rubro.activo) {
        if (!confirm(`¿Está seguro que quiere dar de baja el rubro "${rubro.nombre}"?`)) {
            return;
        }
    }

    try {
        const newStatus = !rubro.activo;
        // Optimistic update
        rubro.activo = newStatus;
        
        await rubrosApi.update(rubro.id, { ...rubro, activo: newStatus });
        useNotificationStore().add(`Rubro ${newStatus ? 'activado' : 'desactivado'}`, 'success');
        
        // If currently selected, update form
        if (selectedRubro.value?.id === rubro.id) {
            form.value.activo = newStatus;
        }
    } catch (error) {
        // Revert on error
        rubro.activo = !rubro.activo;
        useNotificationStore().add('Error al cambiar estado', 'error');
    }
};

const createNewRoot = () => {
  selectedRubro.value = null; // Deselect to show "New Root" context if needed, or just open inspector
  isCreating.value = true;
  form.value = {
    id: null,
    codigo: '',
    nombre: '',
    padre_id: null,
    activo: true
  };
};

const createNewChild = () => {
  if (!selectedRubro.value) return;
  const parent = selectedRubro.value;
  isCreating.value = true;
  // Keep parent selected in tree? Or deselect? 
  // Let's keep it selected visually in tree, but form is for new child.
  form.value = {
    id: null,
    codigo: '',
    nombre: '',
    padre_id: parent.id,
    activo: true
  };
};

const cancelEdit = () => {
  isCreating.value = false;
  selectedRubro.value = null;
  form.value = { id: null, codigo: '', nombre: '', padre_id: null, activo: true };
};

const saveRubro = async () => {
  if (!form.value.codigo || !form.value.nombre) {
    useNotificationStore().add('Código y Nombre son obligatorios', 'warning');
    return;
  }

  saving.value = true;
  try {
    if (form.value.id) {
      await rubrosApi.update(form.value.id, form.value);
      useNotificationStore().add('Rubro actualizado correctamente', 'success');
    } else {
      await rubrosApi.create(form.value);
      useNotificationStore().add('Rubro creado correctamente', 'success');
    }
    await fetchRubros();
    
    // After save, select the saved item? Or close?
    // Let's close inspector for now or select the new item if possible.
    // For simplicity, close inspector.
    cancelEdit(); 
  } catch (error) {
    console.error('Error guardando rubro:', error);
    useNotificationStore().add(error.response?.data?.detail || 'Error al guardar', 'error');
  } finally {
    saving.value = false;
  }
};

const confirmDelete = async () => {
  if (!selectedRubro.value) return;
  if (!confirm(`¿Estás seguro de eliminar el rubro "${selectedRubro.value.nombre}"?`)) return;

  try {
    await rubrosApi.delete(selectedRubro.value.id);
    useNotificationStore().add('Rubro eliminado correctamente', 'success');
    await fetchRubros();
    cancelEdit();
  } catch (error) {
    console.error('Error eliminando rubro:', error);
    useNotificationStore().add(error.response?.data?.detail || 'Error al eliminar', 'error');
  }
};

onMounted(() => {
  fetchRubros();
});
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #4c1d29;
  border-radius: 2px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #fb7185;
}
</style>
