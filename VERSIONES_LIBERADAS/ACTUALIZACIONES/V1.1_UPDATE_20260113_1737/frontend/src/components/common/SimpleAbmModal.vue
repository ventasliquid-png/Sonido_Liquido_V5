<template>
  <div class="fixed inset-0 z-[70] flex items-center justify-center bg-black/60 backdrop-blur-sm" @click.self="$emit('close')">
    <div class="bg-[#0f172a] w-full max-w-md rounded-lg shadow-2xl border border-slate-700 flex flex-col max-h-[80vh]">
      
      <!-- Header -->
      <div class="flex justify-between items-center p-4 border-b border-slate-700 bg-slate-800/50 rounded-t-lg">
        <h3 class="text-slate-100 font-bold text-lg">{{ title }}</h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-white transition-colors">
            <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Add New -->
      <div class="p-4 bg-slate-800/30 border-b border-slate-700 flex gap-2">
        <input 
            v-model="newItemName" 
            @keyup.enter="handleCreate"
            type="text" 
            class="flex-1 bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 outline-none focus:border-emerald-500 transition-colors"
            placeholder="Nuevo ítem..."
        >
        <button 
            @click="handleCreate"
            class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!newItemName.trim()"
        >
            <i class="fas fa-plus"></i>
        </button>
      </div>

      <!-- List -->
      <div class="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
        <div 
            v-for="item in items" 
            :key="item.id"
            class="flex justify-between items-center p-3 rounded hover:bg-slate-800 group transition-colors border border-transparent hover:border-slate-700"
        >
            <span class="text-slate-300 font-medium">{{ item.nombre }}</span>
            <button 
                @click="handleDelete(item)"
                class="text-slate-600 hover:text-rose-500 opacity-0 group-hover:opacity-100 transition-all p-2"
                title="Eliminar"
            >
                <i class="fas fa-trash"></i>
            </button>
        </div>
        
        <div v-if="items.length === 0" class="text-center py-8 text-slate-500 italic text-sm">
            No hay elementos registrados.
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
    title: { type: String, default: 'Administrar' },
    items: { type: Array, default: () => [] }
});

const emit = defineEmits(['close', 'create', 'delete']);

const newItemName = ref('');

const handleCreate = () => {
    if (!newItemName.value.trim()) return;
    emit('create', newItemName.value.trim());
    newItemName.value = '';
};

const handleDelete = (item) => {
    if(confirm(`¿Eliminar "${item.nombre}"?`)) {
        emit('delete', item.id);
    }
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.2); border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(148, 163, 184, 0.4); }
</style>
