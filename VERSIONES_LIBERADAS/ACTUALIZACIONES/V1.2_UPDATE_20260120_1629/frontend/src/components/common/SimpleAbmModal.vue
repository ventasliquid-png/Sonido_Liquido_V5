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
            :disabled="isLoading"
            class="flex-1 bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 outline-none focus:border-emerald-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            placeholder="Nuevo ítem..."
        >
        <button 
            @click="handleCreate"
            class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed min-w-[50px] flex justify-center items-center"
            :disabled="!newItemName.trim() || isLoading"
        >
            <i v-if="isLoading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-plus"></i>
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
    items: { type: Array, default: () => [] },
    isLoading: { type: Boolean, default: false }
});

const emit = defineEmits(['close', 'create', 'delete']);

const newItemName = ref('');

const handleCreate = () => {
    if (!newItemName.value.trim() || props.isLoading) return;
    emit('create', newItemName.value.trim());
    // Note: Do not clear strictly here if we want to preserve input on error?
    // But per user request we want to clear or close. 
    // We will clear it in the parent or if successful the modal closes.
    // For now keep it as is, but maybe wait? 
    // actually, let's keep clearing it only if we assume success, 
    // but better to let the parent handle the flow or just clear it. 
    // If the parent closes the modal, it doesn't matter.
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
