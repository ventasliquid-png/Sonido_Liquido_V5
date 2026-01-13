<template>
  <div class="absolute inset-0 z-40 bg-[#1a050b] text-gray-200 flex flex-col font-sans">
    <!-- Header -->
    <header class="h-16 flex items-center justify-between px-8 border-b border-rose-900/30 bg-[#2e0a13] shrink-0">
      <div class="flex items-center gap-4">
        <div class="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center text-red-500 text-xl border border-red-500/30">
            <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <div>
            <h2 class="text-lg font-bold text-white tracking-wide">Asistente de Migración</h2>
            <p class="text-xs text-rose-400">Eliminando rubro: <span class="text-white font-mono bg-rose-900/50 px-1 rounded">{{ sourceRubro?.nombre }}</span></p>
        </div>
      </div>
      <div>
        <button @click="$emit('cancel')" class="px-4 py-2 text-sm font-medium text-gray-400 hover:text-white transition-colors">
            Cancelar Operación
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex overflow-hidden">
        <!-- Left: Items to Migrate (Subrubros) -->
        <div class="flex-1 flex flex-col border-r border-rose-900/30">
            <div class="p-4 border-b border-rose-900/20 bg-[#2e0a13]/30 flex justify-between items-center">
                <h3 class="font-bold text-rose-200 uppercase text-xs tracking-wider">
                    Sub-rubros Huérfanos ({{ orphans.length }})
                </h3>
                <div class="flex gap-2">
                    <button 
                        v-if="selectedOrphans.length > 0"
                        @click="assignToOrphanRubro"
                        class="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-xs font-bold rounded flex items-center gap-2"
                        title="Enviar a Rubro 'Huérfanos' (Failsafe)"
                    >
                        <i class="fa-solid fa-box-archive"></i>
                        A Huérfanos
                    </button>
                    <button 
                         v-if="selectedOrphans.length > 0 && targetRubro"
                         @click="assignToTarget"
                         class="px-3 py-1 bg-green-600 hover:bg-green-500 text-white text-xs font-bold rounded shadow-lg shadow-green-900/20 flex items-center gap-2"
                    >
                        <i class="fa-solid fa-check"></i>
                        Mover a "{{ targetRubro.nombre }}"
                    </button>
                </div>
            </div>

            <div class="flex-1 p-4 overflow-y-auto custom-scrollbar bg-black/20">
                <div v-if="orphans.length === 0" class="h-full flex flex-col items-center justify-center text-green-500/50">
                    <i class="fa-solid fa-check-circle text-4xl mb-4"></i>
                    <p class="text-sm font-medium">Bandeja limpia</p>
                </div>
                <div v-else class="space-y-2">
                    <div 
                        v-for="orphan in orphans" 
                        :key="orphan.id"
                        @click="toggleSelection(orphan.id)"
                        class="flex items-center gap-4 p-3 rounded border border-rose-900/10 bg-[#2e0a13]/40 hover:bg-[#2e0a13]/80 cursor-pointer transition-all group"
                        :class="{'ring-1 ring-rose-500 bg-rose-900/20': selectedOrphans.includes(orphan.id)}"
                    >
                        <div class="relative flex items-center">
                            <input type="checkbox" :checked="selectedOrphans.includes(orphan.id)" class="w-4 h-4 rounded border-rose-700 text-rose-600 bg-black/50 pointer-events-none">
                        </div>
                        <div class="w-8 h-8 rounded bg-rose-900/30 flex items-center justify-center text-rose-400 font-bold text-xs ring-1 ring-white/5">
                            {{ orphan.children_count || 0 }}
                        </div>
                        <div>
                            <h4 class="text-sm font-bold text-rose-100">{{ orphan.nombre }}</h4>
                            <span class="text-xs font-mono text-rose-500">{{ orphan.codigo }}</span>
                        </div>
                        <div class="ml-auto opacity-0 group-hover:opacity-100 transition-opacity">
                             <span class="text-[10px] text-gray-500 uppercase font-bold mr-2">Click para seleccionar</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="p-4 bg-[#2e0a13]/50 border-t border-rose-900/20 text-xs text-rose-200/50 flex justify-between">
                <span>{{ selectedOrphans.length }} seleccionados</span>
                <span>Seleccione ítems y un destino para reasignar</span>
            </div>
        </div>

        <!-- Right: Target Selector -->
        <div class="w-96 flex flex-col bg-[#150305]">
            <div class="p-4 border-b border-rose-900/20 bg-[#2e0a13]/30">
                <h3 class="font-bold text-rose-200 uppercase text-xs tracking-wider mb-2">Destino de Migración</h3>
                <input 
                    v-model="searchTarget"
                    type="text" 
                    placeholder="Buscar rubro activo..." 
                    class="w-full bg-black/30 border border-rose-900/30 rounded px-3 py-1.5 text-sm text-white focus:border-rose-500 focus:outline-none placeholder-rose-900/50"
                >
            </div>

            <div class="flex-1 overflow-y-auto custom-scrollbar p-2">
                 <!-- Option: New Rubro -->
                 <button 
                    @click="$emit('create-new')"
                    class="w-full flex items-center gap-3 p-3 mb-2 rounded border border-dashed border-rose-500/30 text-rose-400 hover:bg-rose-500/10 transition-colors text-left"
                 >
                    <div class="w-8 h-8 rounded-full bg-rose-500/20 flex items-center justify-center">
                        <i class="fa-solid fa-plus"></i>
                    </div>
                    <div>
                        <span class="text-sm font-bold block">Crear Nuevo Rubro</span>
                        <span class="text-xs opacity-70">Como destino de los ítems</span>
                    </div>
                 </button>

                 <!-- List -->
                 <div class="space-y-1">
                    <button 
                        v-for="rubro in filteredTargets" 
                        :key="rubro.id"
                        @click="targetRubro = rubro"
                        @dblclick="selectAndAssign(rubro)"
                        class="w-full flex items-center gap-3 p-2 rounded border text-left transition-all"
                        :class="[
                            targetRubro?.id === rubro.id 
                                ? 'bg-rose-600 border-rose-500 text-white shadow-lg' 
                                : 'bg-transparent border-transparent hover:bg-white/5 text-gray-400'
                        ]"
                    >
                        <div class="w-2 h-2 rounded-full" :class="rubro.activo ? 'bg-green-500' : 'bg-red-500'"></div>
                        <div class="flex-1 min-w-0">
                            <span class="block text-sm font-medium truncate" :class="{'text-white': targetRubro?.id === rubro.id, 'text-gray-300': rubro.activo, 'text-red-400/70': !rubro.activo}">
                                {{ rubro.nombre }}
                            </span>
                            <span class="block text-[10px] font-mono opacity-50">{{ rubro.codigo }}</span>
                        </div>
                        <i v-if="targetRubro?.id === rubro.id" class="fa-solid fa-check text-white"></i>
                    </button>
                 </div>
            </div>
            
            <!-- Footer Action -->
            <div class="p-4 border-t border-rose-900/20 bg-[#0a0204]">
                <button 
                    @click="finishMigration"
                    :disabled="orphans.length > 0"
                    class="w-full py-3 rounded font-bold text-sm transition-all shadow-lg flex items-center justify-center gap-2"
                    :class="orphans.length === 0 ? 'bg-red-600 hover:bg-red-500 text-white' : 'bg-gray-800 text-gray-500 cursor-not-allowed'"
                >
                    <i class="fa-solid fa-trash-can"></i>
                    Confirmar Eliminación
                </button>
                <p v-if="orphans.length > 0" class="text-center text-[10px] text-rose-500 mt-2">
                    Debe reasignar todos los sub-rubros antes de eliminar.
                </p>
            </div>
        </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useKeyboardShortcuts } from '../../../composables/useKeyboardShortcuts.js';

const props = defineProps({
  sourceRubro: Object,
  orphans: {
    type: Array, // items to migrate
    default: () => []
  },
  allRubros: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['cancel', 'create-new', 'assign', 'finish']);

const searchTarget = ref('');
const targetRubro = ref(null);
const selectedOrphans = ref([]);

// Filter targets (exclude self and nulls)
const filteredTargets = computed(() => {
    const query = searchTarget.value.toLowerCase();
    return props.allRubros.filter(r => 
        r.id !== props.sourceRubro.id && // Not self
        !r.padre_id && // Only roots (Rubros) can be parents of Subrubros (simplification for now, or allow n-level?)
                       // If hierarchy is strictly 2-level (Rubro->Subrubro), then target must be a Rubro (Top Level).
                       // We check !padre_id to properly list only potential parents.
        (r.nombre.toLowerCase().includes(query) || r.codigo.toLowerCase().includes(query))
    );
});

const toggleSelection = (id) => {
    if (selectedOrphans.value.includes(id)) {
        selectedOrphans.value = selectedOrphans.value.filter(x => x !== id);
    } else {
        selectedOrphans.value.push(id);
    }
};

const selectAndAssign = (rubro) => {
    targetRubro.value = rubro;
    assignToTarget();
};

const assignToTarget = () => {
    if (!targetRubro.value || selectedOrphans.value.length === 0) return;
    
    emit('assign', {
        ids: [...selectedOrphans.value],
        targetId: targetRubro.value.id
    });
    
    selectedOrphans.value = [];
};

const assignToOrphanRubro = () => {
    // We need to find the orphan rubro component ID or special flag
    // For now we emit with a special flag
    emit('assign', {
        ids: [...selectedOrphans.value],
        targetId: 'ORPHAN_FAILSAFE'
    });
    selectedOrphans.value = [];
};

const finishMigration = () => {
    if (props.orphans.length === 0) {
        emit('finish');
    }
};

// Select all helper?

useKeyboardShortcuts({
    'F4': () => emit('create-new'),
    'F10': () => assignToTarget()
});
</script>

<style scoped>
/* Custom Scrollbar for dark theme */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(244, 63, 94, 0.3);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(244, 63, 94, 0.5);
}
</style>
