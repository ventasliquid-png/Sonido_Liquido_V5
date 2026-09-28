// [IDENTIDAD] - frontend\src\views\Informes\AbcClientesListado.vue
// [S875] Nivel 2 -- ABC de clientes (ranking por $ neto, entregado y facturado por
// separado). Ver DISENO_MODULO_INFORMES_S875_2026-09-26.md §2.4 y decisión de Carlos
// del 28/09 (las dos medidas, no una sola).
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans rounded-2xl border-2 border-blue-500/60 shadow-[0_0_30px_rgba(59,130,246,0.25)] p-6">
    <main class="flex flex-1 flex-col relative min-w-0">

      <header class="shrink-0 flex flex-wrap gap-4 items-center justify-between border-b border-blue-900/20 pb-4">
        <div>
          <h1 class="font-outfit text-xl font-semibold text-white">Informes · ABC de clientes</h1>
          <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider">Ranking por $ neto — Nivel 2</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <button v-for="f in FORMATOS" :key="f.formato" @click="exportar(f.formato)"
            :disabled="exportando"
            class="px-3 py-1.5 rounded-lg border text-xs font-bold uppercase tracking-wide transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            :class="f.clase">
            <i class="fas" :class="f.icono"></i> {{ f.label }}
          </button>
        </div>
      </header>

      <div class="shrink-0 flex flex-wrap gap-3 items-center py-3 border-b border-blue-900/10 text-[11px] text-blue-400/50">
        <i class="fas fa-circle-info"></i>
        <span>Dos medidas independientes, sin mezclar: <b class="text-blue-300">entregado</b> (lo que efectivamente salió) y <b class="text-blue-300">facturado</b> (solo comprobantes AUTORIZADA_AFIP). Un cliente Rosa factura $0 por diseño — no es un error.</span>
        <button @click="cargar" class="ml-auto h-8 px-3 rounded-lg border border-blue-900/30 text-blue-400 hover:text-blue-200 hover:border-blue-500/50 transition-colors" title="Recargar">
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': loading }"></i>
        </button>
      </div>

      <div class="flex-1 overflow-auto mt-3">
        <table class="w-full text-xs">
          <thead class="sticky top-0 bg-[#0f172a] z-10">
            <tr class="text-[10px] uppercase tracking-widest text-blue-400/50 border-b border-blue-900/20">
              <th class="text-left px-3 py-2 font-bold">#</th>
              <th v-for="col in columnas" :key="col.key" class="text-left px-3 py-2 font-bold">{{ col.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td :colspan="(columnas.length || 7) + 1" class="text-center py-10 text-blue-500">
                <i class="fas fa-spinner fa-spin mr-2"></i> Cargando...
              </td>
            </tr>
            <tr v-else-if="filas.length === 0">
              <td :colspan="(columnas.length || 7) + 1" class="text-center py-10 text-blue-900/40">
                Sin datos
              </td>
            </tr>
            <tr v-for="(fila, i) in filas" :key="i" class="border-b border-blue-900/10 hover:bg-blue-900/10">
              <td class="px-3 py-1.5 font-mono text-blue-400/40">{{ i + 1 }}</td>
              <td v-for="col in columnas" :key="col.key" class="px-3 py-1.5 font-mono text-blue-100/90 whitespace-nowrap">
                <span v-if="col.key === 'clase_entregado' || col.key === 'clase_facturado'"
                  class="px-1.5 py-0.5 rounded text-[10px] font-bold"
                  :class="claseColor(fila[col.key])">
                  {{ fila[col.key] }}
                </span>
                <span v-else-if="col.key === 'neto_entregado' || col.key === 'neto_facturado'">
                  {{ formatoMoneda(fila[col.key]) }}
                </span>
                <span v-else-if="col.key === 'pct_acum_entregado' || col.key === 'pct_acum_facturado'">
                  {{ fila[col.key] }}%
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
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'
import { useInformeExport } from '@/composables/useInformeExport'

const notification = useNotificationStore()

const loading = ref(false)
const filas = ref([])
const columnas = ref([])
const { exportar: exportarArchivo, exportando } = useInformeExport('/informes/abc-clientes/export', 'abc_de_clientes')

const FORMATOS = [
  { formato: 'csv', label: 'CSV', icono: 'fa-file-csv', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-emerald-500/50 hover:text-emerald-300' },
  { formato: 'excel', label: 'Excel', icono: 'fa-file-excel', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-green-500/50 hover:text-green-300' },
  { formato: 'pdf', label: 'PDF', icono: 'fa-file-pdf', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-red-500/50 hover:text-red-300' },
  { formato: 'txt', label: 'TXT', icono: 'fa-file-lines', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-blue-500/50 hover:text-blue-300' },
]

const claseColor = (clase) => ({
  A: 'bg-emerald-500/20 text-emerald-300',
  B: 'bg-amber-500/20 text-amber-300',
  C: 'bg-rose-500/20 text-rose-300',
}[clase] || 'bg-blue-500/20 text-blue-300')

const formatoMoneda = (v) => (v ?? 0).toLocaleString('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 })

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/informes/abc-clientes')
    filas.value = res.data.filas || []
    columnas.value = res.data.columnas || []
  } catch (e) {
    console.error(e)
    notification.add('Error cargando el informe: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    loading.value = false
  }
}

const exportar = (formato) => exportarArchivo(formato, {})

onMounted(cargar)
</script>
