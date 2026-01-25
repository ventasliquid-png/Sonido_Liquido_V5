<template>
  <div
    class="ficha-card group relative flex flex-col rounded-xl border border-white/10 bg-white/10 p-4 transition-all duration-300 hover:border-cyan-400/50 hover:bg-white/20 hover:shadow-lg hover:shadow-cyan-500/20 cursor-pointer"
    :class="[
        { 'ring-2 ring-cyan-400 bg-white/20': selected },
        { 'border-red-500 ring-4 ring-red-500': debugClick }, 
        isExpanded ? 'absolute top-0 left-0 w-full z-50 scale-110 bg-[#0f344e] shadow-2xl shadow-black/50 h-auto min-h-[160px] pb-12' : 'overflow-hidden h-[140px]'
    ]"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    @dblclick="handleDblClick"
  >
    <!-- Header Row: Avatar + Status Stack -->
    <div class="mb-4 flex gap-3 items-start">
        <!-- Avatar -->
        <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-gray-800 text-2xl text-gray-400 group-hover:text-cyan-400 transition-colors shrink-0">
          <slot name="icon">
            <i class="fas fa-cube"></i>
          </slot>
        </div>

        <!-- Status Stack (Semáforo) -->
        <div class="flex flex-col gap-1 pt-1">
            <!-- Fiscal (Purple) -->
            <div class="flex items-center gap-1.5 opacity-80" title="Condición Fiscal Verificada">
                <div class="h-2 w-2 rounded-full bg-purple-500 shadow-[0_0_5px] shadow-purple-500/50"></div>
                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider leading-none">Fiscal</span>
            </div>

            <!-- Entrega (Orange) - Logistics Alert -->
            <div v-if="hasLogisticsAlert" class="flex items-center gap-1.5" title="Requiere Entrega (Logística)">
                <div class="h-2 w-2 rounded-full bg-orange-500 shadow-[0_0_8px] shadow-orange-500"></div>
                <span class="text-[10px] font-bold text-orange-200 uppercase tracking-wider leading-none">Envíos</span>
            </div>

            <!-- Transporte (Yellow) -->
            <div v-if="hasTransport" class="flex items-center gap-1.5" title="Transporte Asignado">
                <div class="h-2 w-2 rounded-full bg-yellow-400 shadow-[0_0_5px] shadow-yellow-400/50"></div>
                <span class="text-[10px] font-bold text-yellow-200 uppercase tracking-wider leading-none">Transp.</span>
            </div>
        </div>
    </div>

    <!-- Content -->
    <div class="flex flex-col">
      <h3 class="font-outfit text-lg font-semibold text-gray-100 group-hover:text-white" :class="{ 'truncate': !isExpanded, 'whitespace-normal': isExpanded }">{{ title }}</h3>
      <p class="text-sm text-gray-500 font-mono" :class="{ 'truncate': !isExpanded }">{{ subtitle }}</p>
      
      <!-- Extra content shown only when expanded -->
      <div v-if="isExpanded" class="mt-3 pt-3 border-t border-white/10 text-xs text-white/60 animate-fade-in space-y-1">
          <div v-if="extraData.segmento" class="text-cyan-400 font-bold uppercase text-[10px]">{{ extraData.segmento }}</div>
          
          <div v-if="extraData.domicilio" class="flex items-start gap-2">
            <i class="fas fa-map-marker-alt mt-0.5 text-white/30"></i>
            <span class="leading-tight">{{ formatAddress(extraData.domicilio) }}</span>
          </div>

          <div v-if="extraData.contacto" class="flex items-center gap-2">
            <i class="fas fa-user-circle text-white/30"></i>
            <span>{{ extraData.contacto }}</span>
          </div>
          
          <div v-if="!extraData.domicilio && !extraData.contacto" class="italic opacity-50">Click para ver detalle</div>
      </div>
    </div>

    <!-- Hover Actions (Optional) -->
    <!-- Actions Slot -->
    <div class="absolute bottom-2 right-2 z-20">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  hasLogisticsAlert: {
    type: Boolean,
    default: false
  },
  hasTransport: {
    type: Boolean,
    default: false
  },
  extraData: {
    type: Object,
    default: () => ({})
  },
  selected: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'dblclick'])

const isExpanded = ref(false)
let hoverTimeout = null

const handleMouseEnter = () => {
  hoverTimeout = setTimeout(() => {
    isExpanded.value = true
    // emit('select') // Removed to prevent accidental selection triggers on hover
  }, 1000)
}

const handleMouseLeave = () => {
  if (hoverTimeout) clearTimeout(hoverTimeout)
  isExpanded.value = false
}

const debugClick = ref(false)
const handleDblClick = (e) => {
    debugClick.value = true
    emit('dblclick', e)
    setTimeout(() => debugClick.value = false, 500)
}

const formatAddress = (address) => {
    if (!address) return ''
    return address.replace(/\|/g, ', ')
}
</script>

<style scoped>
.ficha-card {
  backdrop-filter: blur(10px);
}
</style>
