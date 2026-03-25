<template>
  <div class="space-y-4">
    <!-- OmniSearch Input -->
    <div class="flex items-center gap-2">
      <div class="relative group flex-1">
        <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-white/20 text-xs"></i>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Buscar por calle o alias..." 
          class="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-cyan-500/50 transition-all placeholder-white/10"
        />
      </div>
      
      <!-- ADD NEW ADDRESS BUTTON (Prominent) -->
      <button 
        @click="$emit('add')" 
        class="h-9 px-4 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white transition-all flex items-center gap-2 shadow-lg shadow-cyan-900/40 group active:scale-95"
        title="Agregar Nueva Dirección de Entrega"
      >
        <i class="fas fa-plus text-xs group-hover:rotate-90 transition-transform duration-300"></i>
        <span class="text-[10px] font-black uppercase tracking-widest">Sede</span>
      </button>

      <!-- Toggle Ver Inactivos -->
      <button 
        @click="showInactive = !showInactive"
        class="h-9 px-3 rounded-xl border transition-all flex items-center gap-2 shrink-0 group"
        :class="showInactive ? 'bg-amber-500/20 border-amber-500/50 text-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.2)]' : 'bg-white/5 border-white/10 text-white/30 hover:bg-white/10 hover:text-white/50'"
        title="Ver direcciones dadas de baja"
      >
        <i class="fas" :class="showInactive ? 'fa-eye' : 'fa-eye-slash'"></i>
        <span class="text-[10px] font-bold uppercase tracking-tight hidden sm:inline">Inactivos</span>
      </button>
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

        <div class="flex items-center gap-2 mt-1 px-2 py-1 rounded border w-fit group/tag">
          <div class="flex items-center gap-1.5 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
            <i class="fas fa-dolly text-emerald-400 text-[10px]"></i>
            <span class="text-[10px] font-bold text-emerald-300 uppercase">
              {{ getTransportName(primaryDelivery.transporte_id) }}
            </span>
          </div>

          <!-- Mirror Indicator (Bit 21) -->
          <div 
            v-if="isMirrored(primaryDelivery)"
            class="flex items-center gap-1 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/20 animate-pulse"
            title="Sincronía Espejo Activa (Ley de Paridad)"
          >
            <i class="fas fa-link text-cyan-400 text-[10px]"></i>
            <span class="text-[9px] font-bold text-cyan-300 uppercase tracking-tighter">ESPEJO</span>
          </div>
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
                <!-- Mirror Badge for Secondary -->
                <div v-if="isMirrored(dom)" class="mt-1 flex items-center gap-1 text-[8px] text-cyan-400/60 font-bold uppercase tracking-widest">
                   <i class="fas fa-link text-[7px]"></i>
                   ESPEJO FISCAL
                </div>
              </div>
            </div>
            
            <div class="flex items-center gap-1">
              <!-- Equalize to Fiscal (Mirror Start) -->
              <button 
                v-if="!dom.es_fiscal && !isMirrored(dom) && dom.activo !== false"
                @click.stop="syncFiscal(dom)"
                class="text-white/10 hover:text-cyan-400 transition-colors p-1"
                title="Sincronizar con Fiscal (Mirror ON)"
              >
                <i class="fas fa-sync-alt text-[10px]"></i>
              </button>

              <!-- Restore Button (Only for inactive) -->
              <button 
                v-if="dom.activo === false"
                @click.stop="restore(dom)"
                class="text-amber-500/50 hover:text-amber-400 transition-colors p-1"
                title="Reactivar Domicilio"
              >
                <i class="fas fa-rotate-left text-[10px]"></i>
              </button>

              <!-- Promotion Button -->
              <button 
                v-if="!dom.es_fiscal && dom.activo !== false"
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
                v-if="!dom.es_fiscal && dom.activo !== false"
                @click.stop="$emit('delete', dom)"
                class="text-white/5 hover:text-red-500 transition-colors p-1"
                title="Dar de Baja"
              >
                <i class="fas fa-trash-alt text-[9px]"></i>
              </button>

              <div v-else-if="dom.es_fiscal" class="ml-2 text-purple-500/50 p-1" title="Domicilio Fiscal (No Promovible / No Eliminable)">
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
    
    <!-- EMPTY STATE FOR SECONDARY (Call to Action) -->
    <div v-else class="pt-4 mt-2 border-t border-white/5">
        <button 
          @click="$emit('add')"
          class="w-full py-4 border-2 border-dashed border-cyan-500/20 rounded-xl text-cyan-500/40 hover:text-cyan-400 hover:border-cyan-500/50 hover:bg-cyan-500/5 transition-all flex flex-col items-center justify-center gap-2 group"
        >
            <div class="h-10 w-10 rounded-full border border-dashed border-cyan-500/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                <i class="fas fa-plus text-lg"></i>
            </div>
            <span class="text-[10px] font-black uppercase tracking-widest">Agregar otra sede de entrega</span>
        </button>
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

const emit = defineEmits(['update:domicilios', 'edit', 'delete', 'restore', 'add', 'sync-fiscal'])

const searchQuery = ref('')
const showInactive = ref(false)
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
    // If not showing inactive, filter them out
    if (!showInactive.value && d.activo === false) return false
    
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
      return { ...d, es_predeterminado: true, es_entrega: true, activo: true }
    } else {
      return { ...d, es_predeterminado: false }
    }
  })
  
  emit('update:domicilios', newDomicilios)
}

const restore = (dom) => {
  emit('restore', dom)
}

const isMirrored = (dom) => {
    // Bit 21 Logic: (flags & 2097152) 
    // We assume the backend delivers flags and we check if Bit 21 is ON
    return !!(dom.flags & 2097152) || dom.is_mirror // Fallback to property if mapped
}

const syncFiscal = (dom) => {
    if (confirm("¿Sincronizar esta dirección con el domicilio fiscal? Se activará el Mirror dinámico.")) {
        // Emit event to parent to perform backend sync
        emit('sync-fiscal', dom)
    }
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
