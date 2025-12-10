<template>
  <div
    class="producto-card group relative flex flex-col rounded-xl border border-white/10 bg-white/5 p-4 transition-all duration-300 hover:border-rose-500/50 hover:bg-white/10 hover:shadow-lg hover:shadow-rose-500/20 cursor-pointer"
    :class="[
        { 'ring-2 ring-rose-500 bg-white/10': selected },
        isExpanded ? 'absolute top-0 left-0 w-full z-50 scale-110 bg-[#3f0e1a] shadow-2xl shadow-black/50 h-auto min-h-[180px]' : 'overflow-hidden h-[160px]',
        { 'opacity-60': !producto.activo }
    ]"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- Status Action Slot (Top Right) -->
    <div class="absolute right-3 top-3 z-30 transform scale-90">
      <slot name="status-action"></slot>
    </div>

    <!-- Kit Indicator -->
    <div v-if="producto.es_kit" class="absolute right-8 top-2 text-xs text-yellow-400 font-bold tracking-wider" title="Es Kit">
        <i class="fas fa-box-open"></i> KIT
    </div>

    <!-- Icon / Thumbnail -->
    <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-black/30 text-2xl text-rose-400/50 group-hover:text-rose-400 transition-colors shrink-0">
      <i class="fas fa-box"></i>
    </div>

    <!-- Content -->
    <div class="flex flex-col">
      <!-- Visual Code Badge -->
      <div v-if="producto.codigo_visual" class="mb-1">
          <span class="inline-block px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
              {{ producto.codigo_visual }}
          </span>
      </div>

      <h3 class="font-outfit text-lg font-semibold text-gray-100 group-hover:text-white leading-tight" :class="{ 'truncate': !isExpanded, 'whitespace-normal': isExpanded }">
          {{ producto.nombre }}
      </h3>
      
      <div class="flex items-center gap-2 mt-1">
          <p class="text-xs text-gray-500 font-mono">SKU: {{ producto.sku }}</p>
          <span v-if="producto.rubro" class="text-xs text-gray-600">• {{ producto.rubro.nombre }}</span>
      </div>
      
      <!-- Extra content shown only when expanded -->
      <div v-if="isExpanded" class="mt-3 pt-3 border-t border-white/10 text-xs text-white/60 animate-fade-in">
          <div class="flex justify-between items-center">
              <span>{{ producto.unidad_medida }}</span>
              <span class="text-rose-400">Click para editar</span>
          </div>
      </div>
    </div>
    <!-- Actions Slot -->

  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  producto: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select'])

const isExpanded = ref(false)
let hoverTimeout = null

const handleMouseEnter = () => {
  hoverTimeout = setTimeout(() => {
    isExpanded.value = true
    // emit('select')
  }, 800) // Slightly faster than clients
}

const handleMouseLeave = () => {
  if (hoverTimeout) clearTimeout(hoverTimeout)
  isExpanded.value = false
}
</script>

<style scoped>
.producto-card {
  backdrop-filter: blur(10px);
}
</style>
