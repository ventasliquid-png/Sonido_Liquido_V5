// [IDENTIDAD] - frontend\src\views\Informes\BuscarNotasListado.vue
// [S875] Informe E -- buscar en notas (Pedido.nota + RemitoNota.texto), con cruce por
// cliente y sin distinguir acentos. Ver DISENO_MODULO_INFORMES_S875_2026-09-26.md §2.3.E.
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans rounded-2xl border-2 border-blue-500/60 shadow-[0_0_30px_rgba(59,130,246,0.25)] p-6">
    <main class="flex flex-1 flex-col relative min-w-0">

      <header class="shrink-0 flex flex-wrap gap-4 items-center justify-between border-b border-blue-900/20 pb-4">
        <div>
          <h1 class="font-outfit text-xl font-semibold text-white">Informes · Buscar en notas</h1>
          <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider">Listado exportable — Informe E</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <button v-for="f in FORMATOS" :key="f.formato" @click="exportar(f.formato)"
            :disabled="exportando || !q.trim()"
            class="px-3 py-1.5 rounded-lg border text-xs font-bold uppercase tracking-wide transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            :class="f.clase">
            <i class="fas" :class="f.icono"></i> {{ f.label }}
          </button>
        </div>
      </header>

      <div class="shrink-0 flex flex-wrap gap-3 items-end py-4 border-b border-blue-900/10">
        <div class="flex-1 min-w-[240px]">
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Buscar</label>
          <input v-model="q" @keyup.enter="buscar"
            type="text" placeholder="Un número de remito, una palabra, un cliente..."
            class="h-9 w-full rounded-lg border border-blue-900/30 bg-[#02050f] px-3 text-xs text-blue-100 focus:border-blue-500 focus:outline-none" />
        </div>
        <label class="flex items-center gap-1.5 text-[11px] px-2 py-1.5 rounded-lg border cursor-pointer select-none transition-colors border-blue-900/20 text-blue-400/60 hover:border-blue-700/40">
          <input type="checkbox" class="accent-sky-500" v-model="excluirSistema" @change="buscar" />
          Excluir notas de sistema
        </label>
        <button @click="buscar" :disabled="!q.trim()"
          class="h-9 px-4 rounded-lg border border-sky-500/40 bg-sky-900/20 text-sky-300 text-xs font-bold uppercase tracking-wide hover:bg-sky-900/40 transition-colors disabled:opacity-40 disabled:cursor-not-allowed">
          <i class="fas fa-search mr-1"></i> Buscar
        </button>
        <span class="text-[11px] text-blue-400/40 ml-auto">{{ buscado ? `${filas.length} resultado(s)` : '' }}</span>
      </div>

      <div class="flex-1 overflow-auto mt-3">
        <table class="w-full text-xs">
          <thead class="sticky top-0 bg-[#0f172a] z-10">
            <tr class="text-[10px] uppercase tracking-widest text-blue-400/50 border-b border-blue-900/20">
              <th v-for="col in columnas" :key="col.key" class="text-left px-3 py-2 font-bold">{{ col.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td :colspan="columnas.length || 7" class="text-center py-10 text-blue-500">
                <i class="fas fa-spinner fa-spin mr-2"></i> Buscando...
              </td>
            </tr>
            <tr v-else-if="!buscado">
              <td :colspan="columnas.length || 7" class="text-center py-10 text-blue-900/40">
                Escribí un término y presioná Buscar
              </td>
            </tr>
            <tr v-else-if="filas.length === 0">
              <td :colspan="columnas.length || 7" class="text-center py-10 text-blue-900/40">
                Sin resultados para "{{ ultimaBusqueda }}"
              </td>
            </tr>
            <tr v-for="(fila, i) in filas" :key="i" class="border-b border-blue-900/10 hover:bg-blue-900/10 align-top">
              <td v-for="col in columnas" :key="col.key" class="px-3 py-1.5 whitespace-pre-wrap"
                :class="col.key === 'fragmento' ? 'text-blue-100/80 font-mono' : 'font-mono text-blue-100/90 whitespace-nowrap'">
                <span v-if="col.key === 'origen'"
                  class="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase"
                  :class="fila[col.key] === 'Remito' ? 'bg-sky-500/20 text-sky-300' : 'bg-blue-500/20 text-blue-300'">
                  {{ fila[col.key] }}
                </span>
                <template v-else>{{ fila[col.key] ?? '-' }}</template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'
import { useInformeExport } from '@/composables/useInformeExport'

const notification = useNotificationStore()

const q = ref('')
const excluirSistema = ref(false)
const loading = ref(false)
const buscado = ref(false)
const ultimaBusqueda = ref('')
const filas = ref([])
const columnas = ref([])
const { exportar: exportarArchivo, exportando } = useInformeExport('/informes/buscar-notas/export', 'buscar_en_notas')

const FORMATOS = [
  { formato: 'csv', label: 'CSV', icono: 'fa-file-csv', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-emerald-500/50 hover:text-emerald-300' },
  { formato: 'excel', label: 'Excel', icono: 'fa-file-excel', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-green-500/50 hover:text-green-300' },
  { formato: 'pdf', label: 'PDF', icono: 'fa-file-pdf', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-red-500/50 hover:text-red-300' },
  { formato: 'txt', label: 'TXT', icono: 'fa-file-lines', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-blue-500/50 hover:text-blue-300' },
]

const armarParams = () => ({ q: q.value.trim(), excluir_sistema: excluirSistema.value })

const buscar = async () => {
  if (!q.value.trim()) return
  loading.value = true
  try {
    const res = await api.get('/informes/buscar-notas', { params: armarParams() })
    filas.value = res.data.filas || []
    columnas.value = res.data.columnas || []
    ultimaBusqueda.value = q.value.trim()
    buscado.value = true
  } catch (e) {
    console.error(e)
    notification.add('Error buscando en notas: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    loading.value = false
  }
}

const exportar = (formato) => exportarArchivo(formato, armarParams())
</script>
