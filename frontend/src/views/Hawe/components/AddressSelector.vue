<template>
  <div class="space-y-4">
    <!-- OmniSearch Input -->
    <div class="relative group">
      <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-white/20 text-xs"></i>
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Buscar por calle o alias..." 
        class="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-cyan-500/50 transition-all placeholder-white/10"
      />
    </div>

    <!-- PRIMARY DELIVERY CARD (Drop Zone) -->
    <div 
      class="bg-emerald-900/10 border rounded-2xl p-4 relative group transition-all overflow-hidden"
      :class="[
        primaryDelivery ? 'border-emerald-500/30' : 'border-dashed border-white/10',
        isDraggingOver ? 'bg-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.4)] scale-[1.02]' : ''
      ]"
      @dragover.prevent="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDropPrimary"
      @click="$emit('edit', primaryDelivery)"
    >
      <div v-if="primaryDelivery" class="flex flex-col h-full justify-between gap-4">
        <!-- Header -->
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
            <i class="fas fa-truck-fast text-emerald-400 text-lg"></i>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="text-xs font-bold text-white uppercase tracking-widest">Entrega Principal</h3>
            <span class="text-[10px] text-emerald-400/60 font-mono truncate block">
              {{ primaryDelivery.alias || 'Sede Central' }}
            </span>
          </div>
        </div>

        <!-- Details -->
        <div class="flex items-start gap-2">
          <i class="fas fa-map-pin text-emerald-500 mt-0.5 text-[10px]"></i>
          <div class="min-w-0">
            <p class="text-sm font-bold text-white leading-tight truncate">
              {{ primaryDelivery.calle_entrega || primaryDelivery.calle }} {{ primaryDelivery.numero_entrega || primaryDelivery.numero }}
            </p>
            <p class="text-[10px] text-white/50 truncate">
              {{ primaryDelivery.localidad_entrega || primaryDelivery.localidad }} • {{ primaryDelivery.cp_entrega || primaryDelivery.cp }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2 mt-1 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20 w-fit">
          <i class="fas fa-dolly text-emerald-400 text-[10px]"></i>
          <span class="text-[10px] font-bold text-emerald-300 uppercase">
            {{ getTransportName(primaryDelivery.transporte_id) }}
          </span>
        </div>
      </div>
      <div v-else class="text-center py-8 text-white/20 italic text-xs">
        <i class="fas fa-shipping-fast mb-2 text-xl block opacity-30"></i>
        No hay una sucursal de entrega principal asignada.<br>
        Arrastre una sucursal aquí para promoverla.
      </div>
    </div>

    <!-- SECONDARY DELIVERY LIST -->
    <div v-if="secondaryDeliveries.length > 0" class="border-t border-white/5 pt-2">
      <h4 class="text-[9px] font-bold text-white/30 uppercase tracking-widest mb-2 flex items-center justify-between px-1">
        <span>Otras Direcciones ({{ filteredSecondary.length }})</span>
        <button 
          @click="$emit('add')" 
          class="text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/20"
        >
          <i class="fas fa-plus text-[8px]"></i>
          <span class="text-[8px]">Nuevo</span>
        </button>
      </h4>
      
      <div class="space-y-1.5 max-h-[200px] overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 pr-1">
        <TransitionGroup name="list">
          <div 
            v-for="dom in filteredSecondary" 
            :key="dom.id || dom.local_id"
            draggable="true"
            @dragstart="onDragStart($event, dom)"
            class="flex items-center justify-between p-2 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 hover:border-white/10 cursor-move group transition-all"
            :class="{ 'opacity-50': isDragging && draggedDom?.id === dom.id }"
          >
            <div class="flex items-center gap-3 min-w-0 flex-1">
              <div class="h-8 w-8 rounded bg-white/5 flex items-center justify-center text-white/30 group-hover:text-emerald-400 transition-colors font-bold text-[10px] shrink-0 border border-white/5">
                {{ (dom.alias || dom.calle || 'SU').substring(0,2).toUpperCase() }}
              </div>
              <div class="min-w-0">
                <p class="text-[10px] font-bold text-white/70 group-hover:text-white truncate">
                  {{ dom.calle_entrega || dom.calle || 'Sin Calle' }} {{ dom.numero_entrega || dom.numero }}
                </p>
                <p class="text-[9px] text-white/30 truncate">
                  {{ dom.alias ? dom.alias + ' • ' : '' }}{{ dom.localidad_entrega || dom.localidad || 'Sin Localidad' }}
                </p>
              </div>
            </div>
            
            <div class="flex items-center gap-1">
              <!-- Promotion Button -->
              <button 
                v-if="!dom.es_fiscal"
                @click.stop="promote(dom)"
                class="text-white/10 hover:text-amber-400 transition-colors p-1"
                title="Promover a Principal"
              >
                <i class="fas fa-star text-[10px]"></i>
              </button>
              
              <!-- Edit Button -->
              <button 
                @click.stop="$emit('edit', dom)"
                class="text-white/10 hover:text-cyan-400 transition-colors p-1"
                title="Editar Domicilio"
              >
                <i class="fas fa-pencil-alt text-[10px]"></i>
              </button>

              <!-- Delete Button -->
              <button 
                v-if="!dom.es_fiscal"
                @click.stop="$emit('delete', dom)"
                class="text-white/5 hover:text-red-500 transition-colors p-1"
                title="Dar de Baja"
              >
                <i class="fas fa-trash-alt text-[9px]"></i>
              </button>

              <div v-else class="ml-2 text-purple-500/50 p-1" title="Domicilio Fiscal (No Promovible / No Eliminable)">
                  <i class="fas fa-file-invoice text-[10px]"></i>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </div>
    
    <div v-else-if="searchQuery" class="text-center py-4 text-white/20 italic text-[10px]">
        No se encontraron domicilios que coincidan con "{{ searchQuery }}"
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  domicilios: {
    type: Array,
    required: true
  },
  transportes: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:domicilios', 'edit', 'delete', 'add'])

const searchQuery = ref('')
const isDraggingOver = ref(false)
const isDragging = ref(false)
const draggedDom = ref(null)

const primaryDelivery = computed(() => {
  if (!props.domicilios) return null;
  return props.domicilios.find(d => !d.es_fiscal && d.es_predeterminado && d.activo !== false)
    || props.domicilios.find(d => !d.es_fiscal && d.es_entrega && d.activo !== false)
    || props.domicilios.find(d => d.es_fiscal && d.es_entrega && d.activo !== false)
    || props.domicilios.find(d => d.es_fiscal && d.activo !== false)
    || props.domicilios.find(d => d.activo !== false)
    || props.domicilios[0];
})

const secondaryDeliveries = computed(() => {
  const primary = primaryDelivery.value
  if (!props.domicilios) return []
  
  return props.domicilios.filter(d => {
    if (d.activo === false) return false
    // If it's the current primary card, filter it out
    const isPrimary = primary && (d.id ? String(d.id) === String(primary.id) : d.local_id === primary.local_id)
    return !isPrimary
  })
})

const filteredSecondary = computed(() => {
  if (!searchQuery.value) return secondaryDeliveries.value
  const query = searchQuery.value.toLowerCase()
  return secondaryDeliveries.value.filter(d => 
    (d.calle || '').toLowerCase().includes(query) || 
    (d.alias || '').toLowerCase().includes(query) ||
    (d.localidad || '').toLowerCase().includes(query)
  )
})

const getTransportName = (id) => {
  if (!id) return 'Retira Cliente'
  const t = props.transportes.find(tr => tr.id === id)
  return t ? t.nombre : 'Transporte no asignado'
}

// Drag & Drop Handlers
const onDragStart = (e, dom) => {
  if (dom.es_fiscal) {
      e.preventDefault()
      return
  }
  isDragging.value = true
  draggedDom.value = dom
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', dom.id || dom.local_id)
}

const onDragOver = (e) => {
  e.preventDefault()
  e.dataTransfer.dropEffect = 'move'
  isDraggingOver.value = true
}

const onDragLeave = () => {
  isDraggingOver.value = false
}

const onDropPrimary = (e) => {
  isDraggingOver.value = false
  isDragging.value = false
  
  if (!draggedDom.value) return
  
  // Fiscal Lock
  if (draggedDom.value.es_fiscal) return

  promote(draggedDom.value)
  draggedDom.value = null
}

const promote = (dom) => {
  const newDomicilios = props.domicilios.map(d => {
    // Clear es_predeterminado for others
    const isTarget = d.id ? d.id === dom.id : d.local_id === dom.local_id
    if (isTarget) {
      return { ...d, es_predeterminado: true, es_entrega: true }
    } else {
      return { ...d, es_predeterminado: false }
    }
  })
  
  emit('update:domicilios', newDomicilios)
}
</script>

<style scoped>
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(10px);
}

.list-leave-active {
  position: absolute;
}
</style>
