// [IDENTIDAD] - frontend\src\views\Hawe\components\CuitConflictModal.vue
// Versión: V5.10 GOLD | Genoma Bit 5 (MULTI_CUIT) — Modal de 3 vías (dictamen Nike S845)
// ------------------------------------------

<template>
  <div class="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md transition-all duration-500 overflow-hidden">
    <!-- Main Modal Container -->
    <div class="relative w-full max-w-3xl bg-[#020617]/90 border border-cyan-500/30 rounded-2xl shadow-[0_0_50px_rgba(6,182,212,0.15)] flex flex-col max-h-[90vh] overflow-hidden transition-all duration-300 transform scale-100 ring-1 ring-white/10">

      <!-- Animated Border Effect (Scanner) -->
      <div class="absolute inset-0 pointer-events-none overflow-hidden rounded-2xl">
          <div class="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-20 animate-scan"></div>
      </div>

      <!-- Header -->
      <div class="p-6 border-b border-cyan-500/20 bg-gradient-to-r from-cyan-900/20 to-transparent flex justify-between items-center shrink-0">
        <div class="flex items-center gap-4">
          <div class="h-12 w-12 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)]">
            <i class="fas fa-clone text-xl"></i>
          </div>
          <div>
            <h2 class="text-xl font-black text-white tracking-widest uppercase italic">Posible Duplicado — CUIT Compartido</h2>
            <p class="text-[10px] text-cyan-400 font-bold uppercase tracking-tighter opacity-70">CUIT {{ cuit }} <i class="fas fa-arrow-right mx-1 text-[8px]"></i> Caso Nestlé / UBA (Unidades de Negocio)</p>
          </div>
        </div>
        <button @click="$emit('cancel')" class="text-cyan-900/50 hover:text-white transition-colors p-2">
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>

      <!-- Body / Comparison Grid -->
      <div class="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-thin scrollbar-thumb-cyan-500/20 scrollbar-track-transparent">

        <div class="p-4 bg-yellow-500/5 border border-yellow-500/20 rounded-xl">
            <p class="text-xs text-yellow-200/80 leading-relaxed">
                <i class="fas fa-exclamation-triangle mr-2 text-yellow-400"></i>
                Matching difuso detectó una similitud alta con {{ existingClients.length }} entidad{{ existingClients.length !== 1 ? 'es' : '' }} que ya usan este CUIT. Elegí una acción: si es el <strong>mismo registro</strong> (error de tipeo, doble carga), descartá y usá el existente. Si es una <strong>unidad de negocio distinta</strong> que legítimamente comparte el CUIT (Sucursal, Facultad, etc.), vinculala o confirmá la creación.
            </p>
        </div>

        <!-- Comparison Header Labels -->
        <div class="grid grid-cols-2 gap-8 sticky top-0 z-10 bg-[#020617]/90 py-2">
            <div class="text-[10px] font-black uppercase tracking-[0.3em] text-cyan-900/60 pl-2 border-l-2 border-cyan-900/30">Existente en V5</div>
            <div class="text-[10px] font-black uppercase tracking-[0.3em] text-emerald-500/60 pl-2 border-l-2 border-emerald-500/30">Estás por Crear</div>
        </div>

        <div v-for="c in existingClients" :key="c.id"
             class="rounded-xl border transition-all"
             :class="c.id === bestMatch?.id ? 'border-cyan-500/40 bg-cyan-500/[0.03]' : 'border-transparent'">

          <div class="flex items-center justify-between px-2 pt-2" v-if="c.similarity_nombre != null || c.similarity_domicilio != null">
            <div class="flex gap-2">
              <span class="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full border"
                    :class="scoreClass(c.similarity_nombre)">
                Nombre: {{ formatScore(c.similarity_nombre) }}
              </span>
              <span class="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full border"
                    :class="scoreClass(c.similarity_domicilio)">
                Domicilio Entrega: {{ formatScore(c.similarity_domicilio) }}
              </span>
            </div>
            <button v-if="c.id === bestMatch?.id" @click="$emit('use-existing', c.id)"
                    class="text-[9px] font-bold uppercase text-cyan-400 hover:text-cyan-200 transition-colors">
              <i class="fas fa-arrow-up-right-from-square mr-1"></i> Usar este
            </button>
          </div>

          <div class="grid grid-cols-2 gap-8 items-start group p-2">
            <div class="p-4 bg-white/5 border border-white/5 rounded-xl transition-all group-hover:bg-white/[0.07]">
               <label class="block text-[9px] font-bold text-cyan-500/50 uppercase mb-1">Razón Social</label>
               <p class="text-white font-medium text-sm mb-3">{{ c.razon_social }}</p>
               <label class="block text-[9px] font-bold text-cyan-500/50 uppercase mb-1">Domicilio de Entrega</label>
               <p class="text-white/60 text-xs">{{ c.domicilio_entrega || 'Sin Domicilio' }}</p>
            </div>
            <div class="p-4 bg-emerald-500/5 border border-emerald-500/20 rounded-xl">
               <label class="block text-[9px] font-bold text-emerald-500/50 uppercase mb-1">Razón Social</label>
               <p class="text-white font-bold text-sm mb-3">{{ newData.razon_social || '[VACÍO]' }}</p>
               <label class="block text-[9px] font-bold text-emerald-500/50 uppercase mb-1">Domicilio de Entrega</label>
               <p class="text-white/60 text-xs">{{ newData.domicilio_entrega || 'Sin Domicilio' }}</p>
            </div>
          </div>
        </div>

      </div>

      <!-- Footer / Actions (3 vías) -->
      <div class="p-8 border-t border-cyan-500/20 bg-black/40 flex flex-wrap justify-end gap-3 shrink-0">
        <button @click="$emit('use-existing', bestMatch?.id)" :disabled="!bestMatch"
                class="px-5 py-2.5 rounded-lg border border-red-500/30 text-red-300 hover:text-white hover:bg-red-500/10 transition-all text-xs font-bold uppercase tracking-widest disabled:opacity-30 disabled:cursor-not-allowed">
            <i class="fas fa-arrow-up-right-from-square mr-2"></i> Descartar y Usar el Existente
        </button>
        <button @click="$emit('link-related')" class="px-5 py-2.5 rounded-lg border border-white/10 text-white/60 hover:text-white hover:bg-white/5 transition-all text-xs font-bold uppercase tracking-widest">
            <i class="fas fa-link mr-2"></i> Vincular como Relacionado
        </button>
        <button @click="$emit('confirm-distinct')" class="px-8 py-3 bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-400 hover:to-cyan-500 text-black font-black text-xs uppercase tracking-[0.2em] rounded-lg shadow-[0_0_25px_rgba(6,182,212,0.5)] transition-all transform active:scale-95 group overflow-hidden relative border border-cyan-200/50">
            <div class="absolute inset-0 bg-white/30 -translate-x-full group-hover:translate-x-full transition-transform duration-700 skew-x-12"></div>
            <i class="fas fa-building mr-2"></i>
            Confirmar Distinto y Crear
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  cuit: { type: String, required: true },
  newData: { type: Object, required: true }, // { razon_social, domicilio_entrega }
  existingClients: { type: Array, required: true } // ClienteSummary[] con similarity_nombre/similarity_domicilio
})

defineEmits(['cancel', 'use-existing', 'link-related', 'confirm-distinct'])

// El candidato más probable de ser "el mismo registro" — mayor similitud combinada
const bestMatch = computed(() => {
  if (!props.existingClients.length) return null
  return [...props.existingClients].sort((a, b) => {
    const scoreA = ((a.similarity_nombre || 0) + (a.similarity_domicilio || 0)) / 2
    const scoreB = ((b.similarity_nombre || 0) + (b.similarity_domicilio || 0)) / 2
    return scoreB - scoreA
  })[0]
})

const formatScore = (s) => s == null ? 'N/D' : `${Math.round(s * 100)}%`

const scoreClass = (s) => {
  if (s == null) return 'border-white/10 text-white/30'
  if (s >= 0.85) return 'border-red-500/40 text-red-300'
  if (s >= 0.6) return 'border-yellow-500/40 text-yellow-300'
  return 'border-emerald-500/40 text-emerald-300'
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
</style>
