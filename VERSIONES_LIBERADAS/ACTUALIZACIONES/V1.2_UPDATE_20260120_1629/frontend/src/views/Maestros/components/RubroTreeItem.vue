<template>
  <div class="pl-4">
    <div 
      class="flex items-center gap-2 py-1 px-2 rounded cursor-pointer hover:bg-white/5 group transition-colors"
      :class="{ 'bg-rose-500/20 text-rose-300': isSelected }"
      @click="$emit('select', rubro)"
    >
      <!-- Toggle Icon -->
      <button 
        v-if="hasChildren"
        @click.stop="isOpen = !isOpen"
        class="w-4 h-4 flex items-center justify-center text-gray-500 hover:text-white transition-colors"
      >
        <i :class="['fa-solid', isOpen ? 'fa-chevron-down' : 'fa-chevron-right', 'text-xs']"></i>
      </button>
      <div v-else class="w-4"></div>

      <!-- Icono Carpeta -->
      <i :class="['fa-solid', isOpen ? 'fa-folder-open' : 'fa-folder', 'text-amber-500/80 text-sm']"></i>

      <!-- Nombre -->
      <span class="text-sm truncate select-none flex-1">{{ rubro.nombre }}</span>
      
      <!-- Código Badge -->
      <span class="text-[10px] font-mono bg-gray-800 text-gray-400 px-1.5 rounded border border-gray-700">
        {{ rubro.codigo }}
      </span>

      <!-- Estado -->
      <div v-if="!rubro.activo" class="w-2 h-2 rounded-full bg-red-500/50" title="Inactivo"></div>
    </div>

    <!-- Recursive Children -->
    <div v-if="isOpen && hasChildren" class="border-l border-gray-800 ml-2">
      <RubroTreeItem 
        v-for="child in rubro.hijos" 
        :key="child.id" 
        :rubro="child"
        :selected-id="selectedId"
        @select="$emit('select', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

defineOptions({
  name: 'RubroTreeItem'
});

const props = defineProps({
  rubro: {
    type: Object,
    required: true
  },
  selectedId: {
    type: [Number, null],
    default: null
  }
});

defineEmits(['select']);

const isOpen = ref(true);

const hasChildren = computed(() => props.rubro.hijos && props.rubro.hijos.length > 0);
const isSelected = computed(() => props.selectedId === props.rubro.id);
</script>
