<template>
  <div class="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md transition-all duration-500 overflow-hidden">
    <!-- Main Modal Container -->
    <div class="relative w-full max-w-4xl bg-[#020617]/90 border border-cyan-500/30 rounded-2xl shadow-[0_0_50px_rgba(6,182,212,0.15)] flex flex-col max-h-[90vh] overflow-hidden transition-all duration-300 transform scale-100 ring-1 ring-white/10">
      
      <!-- Animated Border Effect (Scanner) -->
      <div class="absolute inset-0 pointer-events-none overflow-hidden rounded-2xl">
          <div class="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-20 animate-scan"></div>
      </div>

      <!-- Header -->
      <div class="p-6 border-b border-cyan-500/20 bg-gradient-to-r from-cyan-900/20 to-transparent flex justify-between items-center shrink-0">
        <div class="flex items-center gap-4">
          <div class="h-12 w-12 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)]">
            <i class="fas fa-satellite-dish text-xl animate-pulse"></i>
          </div>
          <div>
            <h2 class="text-xl font-black text-white tracking-widest uppercase italic">Infiltración de Identidad</h2>
            <p class="text-[10px] text-cyan-400 font-bold uppercase tracking-tighter opacity-70">Puente RAR V1 <i class="fas fa-arrow-right mx-1 text-[8px]"></i> Sincronización ARCA A13</p>
          </div>
        </div>
        <button @click="$emit('close')" class="text-cyan-900/50 hover:text-white transition-colors p-2">
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>

      <!-- Body / Comparison Grid -->
      <div class="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-thin scrollbar-thumb-cyan-500/20 scrollbar-track-transparent">
        
        <!-- Comparison Header Labels -->
        <div class="grid grid-cols-2 gap-8 sticky top-0 z-10 bg-[#020617]/90 py-2">
            <div class="text-[10px] font-black uppercase tracking-[0.3em] text-cyan-900/60 pl-2 border-l-2 border-cyan-900/30">Local Core (V5)</div>
            <div class="text-[10px] font-black uppercase tracking-[0.3em] text-yellow-500/60 pl-2 border-l-2 border-yellow-500/30">Fiscal Truth (RAR)</div>
        </div>

        <!-- REASON SOCIAL -->
        <div class="grid grid-cols-2 gap-8 items-center group">
          <div class="p-4 bg-white/5 border border-white/5 rounded-xl transition-all group-hover:bg-white/[0.07]">
             <label class="block text-[9px] font-bold text-cyan-500/50 uppercase mb-1">Razón Social Actual</label>
             <p class="text-white font-medium text-sm">{{ localData.razon_social || '[VACÍO]' }}</p>
          </div>
          <div class="p-4 bg-yellow-500/5 border rounded-xl transition-all" :class="hasDiff('razon_social') ? 'border-yellow-500/30' : 'border-emerald-500/30 bg-emerald-500/5'">
             <label class="block text-[9px] font-bold text-yellow-500/50 uppercase mb-1">Dato Oficial</label>
             <div class="flex justify-between items-center">
                <p class="text-white font-bold text-sm tracking-tight">{{ arcaData.razon_social }}</p>
                <i v-if="!hasDiff('razon_social')" class="fas fa-check-circle text-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.3)]"></i>
                <i v-else class="fas fa-sync text-yellow-500 animate-spin-slow"></i>
             </div>
          </div>
        </div>

        <!-- CONDICION IVA -->
        <div class="grid grid-cols-2 gap-8 items-center group">
          <div class="p-4 bg-white/5 border border-white/5 rounded-xl transition-all group-hover:bg-white/[0.07]">
             <label class="block text-[9px] font-bold text-cyan-500/50 uppercase mb-1">Condición IVA Local</label>
             <p class="text-white/70 font-medium text-xs">{{ getIvaName(localData.condicion_iva_id) }}</p>
          </div>
          <div class="p-4 bg-yellow-500/5 border rounded-xl transition-all" :class="hasDiff('condicion_iva_id') ? 'border-yellow-500/30' : 'border-emerald-500/30 bg-emerald-500/5'">
             <label class="block text-[9px] font-bold text-yellow-500/50 uppercase mb-1">Validación Fiscal</label>
             <div class="flex justify-between items-center">
                <p class="text-white font-bold text-xs uppercase">{{ arcaData.condicion_iva }}</p>
                <i v-if="!hasDiff('condicion_iva_id')" class="fas fa-check-circle text-emerald-400"></i>
                <i v-else class="fas fa-sync text-yellow-500"></i>
             </div>
          </div>
        </div>

        <!-- DOMICILIO -->
        <div class="grid grid-cols-2 gap-8 items-start group">
          <div class="p-4 bg-white/5 border border-white/5 rounded-xl transition-all group-hover:bg-white/[0.07]"
               :class="hasDiff('domicilio') ? 'ring-1 ring-red-500/20' : ''">
             <label class="block text-[9px] font-bold text-cyan-500/50 uppercase mb-1">Domicilio en V5</label>
             <p class="text-white/60 text-xs leading-relaxed" :class="hasDiff('domicilio') ? 'text-red-300' : ''">{{ formatLocalAddress }}</p>
          </div>
          <div class="p-4 bg-yellow-500/5 border rounded-xl transition-all" :class="hasDiff('domicilio') ? 'border-yellow-500/30' : 'border-emerald-500/30 bg-emerald-500/5'">
             <label class="block text-[9px] font-bold text-yellow-500/50 uppercase mb-1">Domicilio Detectado (ARCA)</label>
             <div class="flex flex-col gap-1">
                <p class="text-white font-bold text-xs leading-relaxed uppercase">{{ arcaData.domicilio_fiscal }}</p>
                <div v-if="arcaData.parsed_address" class="mt-2 flex flex-wrap gap-1">
                    <span class="text-[8px] bg-yellow-500/10 text-yellow-200 px-1 rounded uppercase">Localidad: {{ arcaData.parsed_address.localidad }}</span>
                    <span class="text-[8px] bg-yellow-500/10 text-yellow-200 px-1 rounded uppercase">CP: {{ arcaData.parsed_address.cp }}</span>
                </div>
                <p v-if="hasDiff('domicilio')" class="text-[8px] text-yellow-500 font-bold mt-2 animate-pulse">
                    <i class="fas fa-exclamation-triangle mr-1"></i> DISCREPANCIA DETECTADA
                </p>
             </div>
          </div>
        </div>

        <!-- DOCTRINA DE VIRGINIDAD STATUS -->
        <div class="p-4 bg-cyan-400/5 border border-cyan-500/20 rounded-2xl flex items-center justify-between">
            <div class="flex items-center gap-4">
                <div class="p-2 rounded-lg bg-cyan-500/20 text-cyan-400">
                    <i class="fas fa-dna text-xl"></i>
                </div>
                <div>
                    <h4 class="text-xs font-black text-cyan-100 uppercase tracking-widest">Protocolo de Aplicación</h4>
                    <p class="text-[9px] text-cyan-400/60 uppercase font-bold tracking-tighter">
                        Asignación prevista: 
                        <span class="text-white px-1.5 py-0.5 rounded bg-cyan-900/40 ml-1">FLAG {{ projectedFlag }}</span>
                        <span class="ml-2 opacity-50">({{ projectedFlagName }})</span>
                    </p>
                </div>
            </div>
            <div class="text-right">
                <p class="text-[8px] text-cyan-400/40 font-mono italic">"La virginidad de los datos es sagrada"</p>
            </div>
        </div>

      </div>

      <!-- Footer / Actions -->
      <div class="p-8 border-t border-cyan-500/20 bg-black/40 flex justify-end gap-4 shrink-0">
        <button @click="$emit('close')" class="px-6 py-2.5 rounded-lg border border-white/10 text-white/40 hover:text-white hover:bg-white/5 transition-all text-xs font-bold uppercase tracking-widest">
            Abortar
        </button>
        <button @click="confirmInfiltration" class="px-8 py-3 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-300 hover:to-yellow-400 text-black font-black text-xs uppercase tracking-[0.2em] rounded-lg shadow-[0_0_25px_rgba(250,204,21,0.5)] transition-all transform active:scale-95 group overflow-hidden relative border border-yellow-200/50">
            <div class="absolute inset-0 bg-white/30 -translate-x-full group-hover:translate-x-full transition-transform duration-700 skew-x-12"></div>
            <i class="fas fa-bolt mr-2 text-yellow-900"></i>
            Infiltrar Datos (Audit/Flag 15)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  localData: { type: Object, required: true },
  arcaData: { type: Object, required: true },
  condicionesIva: { type: Array, required: true },
  isNew: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'confirm'])

// Logica de Inconsistencia para Visualización
const hasDiff = (field) => {
    if (field === 'razon_social') {
        const local = (props.localData.razon_social || '').trim().toUpperCase()
        const arca = (props.arcaData.razon_social || '').trim().toUpperCase()
        return local !== arca && local !== ''
    }
    if (field === 'condicion_iva_id') {
        const arcaName = props.arcaData.condicion_iva.toUpperCase()
        const currentIvaName = getIvaName(props.localData.condicion_iva_id).toUpperCase()
        return arcaName !== currentIvaName && currentIvaName !== 'SELECCIONAR...'
    }
    if (field === 'domicilio') {
        const local = formatLocalAddress.value.toUpperCase().replace(/\s+/g, ' ').trim()
        const arca = (props.arcaData.domicilio_fiscal || '').toUpperCase().replace(/\s+/g, ' ').trim()
        return local !== arca && arca !== ''
    }
    return false
}

const getIvaName = (id) => {
    const target = props.condicionesIva.find(c => c.id === id)
    return target ? target.nombre : 'Seleccionar...'
}

const formatLocalAddress = computed(() => {
    const d = props.localData.fiscalAddress || {}
    if (!d.calle) {
        // [V14] Try to find fiscal address in domicilios if not passed explicitly as fiscalAddress
        const fiscal = props.localData.domicilios?.find(dom => dom.es_fiscal && dom.activo !== false)
        if (fiscal) return `${fiscal.calle} ${fiscal.numero || ''}, ${fiscal.localidad || ''}`.trim()
        return '[SIN DOMICILIO FISCAL]'
    }
    return `${d.calle} ${d.numero || ''}, ${d.localidad || ''}`.trim()
})

const currentFlag = computed(() => props.localData.flags_estado || 9)

const projectedFlag = computed(() => {
    // [V14 GENOMA]
    let flag = currentFlag.value
    
    // 1. Siempre activamos GOLD_ARCA (+4) si estamos en este overlay
    flag |= 4
    
    // 2. Escudo de Virginidad: Si era 9 (Amarillo), le sumamos virginidad (+2)
    // Pero si ya es un registro con movimientos (Bit 1 es 0), no lo re-virginalizamos.
    if (props.isNew) {
        flag |= 2 // Todo cliente nuevo nace Virgen
    } else {
        // Si no es nuevo, preservamos el estado del Bit 1 actual.
        // Si ya era 15 (tenía Bit 1), seguirá siendo 15.
        // Si era 13 (no tenía Bit 1), seguirá sin tenerlo.
    }
    
    // 3. Estructura V14 (+8) - Aseguramos que se mantenga/agregue
    flag |= 8
    
    // 4. Existencia (+1)
    flag |= 1

    return flag
})

const projectedFlagName = computed(() => {
    const flag = projectedFlag.value
    if (flag === 15) return "Blanco: Virgen Gold"
    if (flag === 13) return "Blanco: Activo Gold"
    if (flag === 47) return "Azul: Multicliente Gold"
    return `Gold (Flag ${flag})`
})

const confirmInfiltration = () => {
    emit('confirm', {
        flag: projectedFlag.value,
        data: props.arcaData
    })
}
</script>

<style scoped>
@keyframes scan {
    0% { top: 0% }
    100% { top: 100% }
}
.animate-scan {
    animation: scan 4s linear infinite;
}
.animate-spin-slow {
    animation: spin 3s linear infinite;
}
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
</style>
