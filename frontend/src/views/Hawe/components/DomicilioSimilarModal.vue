// [IDENTIDAD] - frontend\src\views\Hawe\components\DomicilioSimilarModal.vue
// [S883, Card #158 / paso 1 de "un domicilio, muchos clientes"] Antes de crear un domicilio, el sistema busca si ya existe uno igual o parecido
// (aunque esté escrito distinto: «Justo, JB Av 687» = «Avenida Juan B Justo N°687») y SIEMPRE le pregunta a una persona: usar el que ya existe o crear uno nuevo.
// Nunca une solo. Mismo estilo que CuitConflictModal.
// ------------------------------------------

<template>
  <div class="fixed inset-0 z-[120] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md overflow-hidden" @keydown.esc="$emit('cancelar')" tabindex="-1" ref="raiz">
    <div class="relative w-full max-w-2xl bg-[#020617]/95 border border-cyan-500/30 rounded-2xl shadow-[0_0_50px_rgba(6,182,212,0.15)] flex flex-col max-h-[90vh] overflow-hidden">

      <div class="p-5 border-b border-cyan-500/20 bg-gradient-to-r from-cyan-900/20 to-transparent flex justify-between items-center shrink-0">
        <div class="flex items-center gap-4">
          <div class="h-11 w-11 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <i class="fas fa-location-dot text-lg"></i>
          </div>
          <div>
            <h2 class="text-lg font-black text-white tracking-widest uppercase">¿Ya existe este domicilio?</h2>
            <p class="text-[11px] text-cyan-300/70 font-bold">Estás cargando: <span class="text-white">{{ direccion }}</span></p>
          </div>
        </div>
        <button @click="$emit('cancelar')" class="text-white/40 hover:text-white transition-colors p-2" title="Cancelar (Esc)"><i class="fas fa-times text-lg"></i></button>
      </div>

      <div class="flex-1 overflow-y-auto p-5 space-y-3">
        <p class="text-xs text-white/60 leading-relaxed">
          Encontré {{ candidatos.length === 1 ? 'un domicilio' : candidatos.length + ' domicilios' }} que {{ candidatos.length === 1 ? 'parece ser el mismo lugar' : 'parecen ser el mismo lugar' }}.
          Compartir un domicilio evita tenerlo repetido: queda <strong>una sola dirección</strong> y cada cliente que la usa la referencia. Vos decidís.
        </p>

        <div v-for="c in candidatos" :key="c.id" class="rounded-xl border p-4 flex flex-col gap-2"
             :class="c.nivel === 'IGUAL' ? 'border-emerald-500/40 bg-emerald-500/[0.04]' : 'border-amber-500/40 bg-amber-500/[0.04]'">
          <div class="flex items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-bold text-white truncate">{{ c.calle }} {{ c.numero }} <span class="text-white/40 font-normal">· {{ c.localidad || '—' }}</span></p>
              <p class="text-[10px] text-white/40">{{ (c.razones || []).join(' · ') }}</p>
            </div>
            <span class="shrink-0 text-[9px] font-black uppercase px-2 py-0.5 rounded-full border"
                  :class="c.nivel === 'IGUAL' ? 'text-emerald-300 border-emerald-500/50 bg-emerald-500/10' : 'text-amber-300 border-amber-500/50 bg-amber-500/10'">
              {{ c.nivel === 'IGUAL' ? 'Mismo lugar' : 'Parecida: mirala' }}
            </span>
          </div>

          <p class="text-[11px] text-white/60">
            <i class="fas fa-users mr-1 text-white/30"></i>
            <template v-if="c.usado_por && c.usado_por.length">Usada por: <strong class="text-white/80">{{ c.usado_por.map(u => u.razon_social).join(', ') }}</strong></template>
            <template v-else>No la usa ningún cliente (quedó suelta).</template>
            <span v-if="c.es_fiscal" class="ml-2 text-fuchsia-300/80">· fiscal</span>
            <span v-if="c.es_entrega" class="ml-2 text-emerald-300/80">· entrega</span>
          </p>

          <p v-if="!c.compatible" class="text-[11px] text-amber-300/90 leading-snug"><i class="fas fa-triangle-exclamation mr-1"></i>No se puede usar con el rol que estás cargando: {{ c.motivo_incompatible }}.</p>

          <div class="flex justify-end">
            <button v-if="c.ya_es_de_este_cliente" @click="$emit('usar', c)"
                    class="px-4 py-1.5 rounded-lg bg-cyan-700 hover:bg-cyan-600 text-white text-[11px] font-bold uppercase tracking-wide">
              Ya la tiene este cliente: no crear otra
            </button>
            <button v-else :disabled="!c.compatible" @click="$emit('usar', c)"
                    class="px-4 py-1.5 rounded-lg text-white text-[11px] font-bold uppercase tracking-wide"
                    :class="c.compatible ? 'bg-emerald-700 hover:bg-emerald-600' : 'bg-white/10 text-white/30 cursor-not-allowed'">
              Usar esta
            </button>
          </div>
        </div>
      </div>

      <div class="p-4 border-t border-white/10 flex justify-between items-center shrink-0 bg-black/30">
        <button @click="$emit('cancelar')" class="text-[11px] font-bold uppercase text-white/50 hover:text-white">Cancelar</button>
        <button @click="$emit('crear')" class="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-[11px] font-bold uppercase tracking-wide">
          Es otra: crear un domicilio nuevo
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

defineProps({
  candidatos: { type: Array, required: true },
  direccion: { type: String, default: '' },
})
defineEmits(['usar', 'crear', 'cancelar'])

const raiz = ref(null)
onMounted(() => nextTick(() => raiz.value?.focus()))
</script>
