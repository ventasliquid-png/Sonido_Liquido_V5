<template>
  <div class="h-full bg-[#0a151b] text-white flex flex-col font-outfit">
    <!-- Header -->
    <div class="px-8 py-6 border-b border-white/10 shrink-0">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="h-10 w-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20">
            <i class="fas fa-bug text-lg"></i>
          </div>
          <div>
            <h1 class="text-2xl font-bold tracking-tight">Bug Tracker V1</h1>
            <p class="text-xs text-white/50 uppercase tracking-widest mt-1">Control de Calidad del Sistema</p>
          </div>
        </div>
        <button 
          @click="showNewModal = true"
          class="px-4 py-2 bg-indigo-500 hover:bg-indigo-400 text-white rounded-lg text-sm font-semibold transition-colors flex items-center gap-2 shadow-lg shadow-indigo-500/20">
          <i class="fas fa-plus"></i> Reportar Bug
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-auto p-8">
      <div v-if="loading" class="text-center py-12 text-white/50">
        <i class="fas fa-circle-notch fa-spin text-2xl mb-4"></i>
        <p>Cargando registros...</p>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
        
        <!-- Pendientes -->
        <div class="space-y-4">
          <h2 class="text-lg font-semibold flex items-center gap-2 text-red-400">
            <i class="fas fa-exclamation-circle"></i> Pendientes ({{ pendingBugs.length }})
          </h2>
          <div v-if="pendingBugs.length === 0" class="p-6 rounded-xl border border-dashed border-white/10 text-center text-white/40">
            No hay bugs pendientes. ¡El sistema está sano!
          </div>
          <div v-for="bug in pendingBugs" :key="bug.id" 
               class="bg-[#121f26] border border-red-500/20 rounded-xl p-5 hover:border-red-500/40 transition-colors relative group">
            <div class="flex justify-between items-start mb-2">
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-white/5 text-white/60">
                  {{ bug.entorno }}
                </span>
                <span v-if="bug.nro_sesion" class="text-xs font-mono text-indigo-400">#{{ bug.nro_sesion }}</span>
              </div>
              <span class="text-[10px] text-white/40">{{ formatDate(bug.fecha_ocurrencia) }}</span>
            </div>
            <h3 class="font-medium text-red-100 mb-1">{{ bug.descripcion }}</h3>
            <p v-if="bug.detalle" class="text-xs text-white/50 bg-black/20 p-2 rounded mb-4 font-mono">{{ bug.detalle }}</p>
            
            <div class="mt-4 flex justify-end">
              <button @click="resolveBug(bug)" :disabled="resolvingId === bug.id"
                      class="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-lg text-xs font-semibold transition-colors border border-emerald-500/20 flex items-center gap-2">
                <i v-if="resolvingId === bug.id" class="fas fa-circle-notch fa-spin"></i>
                <i v-else class="fas fa-check"></i> Marcar Resuelto
              </button>
            </div>
          </div>
        </div>

        <!-- Resueltos -->
        <div class="space-y-4">
          <h2 class="text-lg font-semibold flex items-center gap-2 text-emerald-400">
            <i class="fas fa-check-circle"></i> Resueltos ({{ resolvedBugs.length }})
          </h2>
          <div v-if="resolvedBugs.length === 0" class="p-6 rounded-xl border border-dashed border-white/10 text-center text-white/40">
            Aún no se han resuelto bugs.
          </div>
          <div v-for="bug in resolvedBugs" :key="bug.id" 
               class="bg-[#121f26] border border-white/5 rounded-xl p-5 opacity-75">
            <div class="flex justify-between items-start mb-2">
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-white/5 text-white/60">
                  {{ bug.entorno }}
                </span>
                <span v-if="bug.nro_sesion" class="text-xs font-mono text-indigo-400">#{{ bug.nro_sesion }}</span>
              </div>
            </div>
            <h3 class="font-medium text-emerald-100/70 mb-1 line-through">{{ bug.descripcion }}</h3>
            <div class="flex items-center gap-2 text-[10px] text-emerald-500/50 mt-3">
              <i class="fas fa-check"></i> Resuelto el {{ formatDate(bug.fecha_resolucion) }}
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'

const bugs = ref([])
const loading = ref(true)
const resolvingId = ref(null)
const showNewModal = ref(false) // Pendiente de implementar modal

const pendingBugs = computed(() => bugs.value.filter(b => !b.resuelto))
const resolvedBugs = computed(() => bugs.value.filter(b => b.resuelto))

const fetchBugs = async () => {
  loading.value = true
  try {
    const res = await api.get('/sistema/bugs')
    bugs.value = res.data
  } catch (error) {
    console.error("Error cargando bugs:", error)
  } finally {
    loading.value = false
  }
}

const resolveBug = async (bug) => {
  resolvingId.value = bug.id
  try {
    await api.put(`/sistema/bugs/${bug.id}/resolve`)
    await fetchBugs()
  } catch (error) {
    console.error("Error resolviendo bug:", error)
  } finally {
    resolvingId.value = null
  }
}

const formatDate = (ds) => {
  if (!ds) return ''
  return new Date(ds).toLocaleString('es-AR', {
    day: '2-digit', month: '2-digit', year: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(() => {
  fetchBugs()
})
</script>
