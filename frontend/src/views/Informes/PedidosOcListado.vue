// [IDENTIDAD] - frontend\src\views\Informes\PedidosOcListado.vue
// [S875] Informe C -- pedidos con OC (Pedido.oc IS NOT NULL).
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans rounded-2xl border-2 border-blue-500/60 shadow-[0_0_30px_rgba(59,130,246,0.25)] p-6">
    <main class="flex flex-1 flex-col relative min-w-0">

      <header class="shrink-0 flex flex-wrap gap-4 items-center justify-between border-b border-blue-900/20 pb-4">
        <div>
          <h1 class="font-outfit text-xl font-semibold text-white">Informes · Pedidos con OC</h1>
          <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider">Listado exportable — Informe C</p>
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

      <div class="shrink-0 flex flex-wrap gap-3 items-end py-4 border-b border-blue-900/10">
        <div>
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Cliente</label>
          <select v-model="filtros.cliente_id"
            class="h-9 w-56 rounded-lg border border-blue-900/30 bg-[#02050f] px-3 text-xs text-blue-100 focus:border-blue-500 focus:outline-none">
            <option :value="null">Todos</option>
            <option v-for="c in clientesOrdenados" :key="c.id" :value="c.id">{{ c.razon_social }}</option>
          </select>
        </div>
        <button @click="cargar" class="h-9 px-3 rounded-lg border border-blue-900/30 text-blue-400 hover:text-blue-200 hover:border-blue-500/50 transition-colors" title="Recargar">
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': loading }"></i>
        </button>
        <span class="text-[11px] text-blue-400/40 ml-auto">{{ filas.length }} pedido(s)</span>
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
              <td :colspan="columnas.length" class="text-center py-10 text-blue-500">
                <i class="fas fa-spinner fa-spin mr-2"></i> Cargando...
              </td>
            </tr>
            <tr v-else-if="filas.length === 0">
              <td :colspan="columnas.length" class="text-center py-10 text-blue-900/40">
                Sin pedidos con OC para estos filtros
              </td>
            </tr>
            <tr v-for="(fila, i) in filas" :key="i" class="border-b border-blue-900/10 hover:bg-blue-900/10" :class="claseFilaCircuito(fila.circuito)">
              <td v-for="col in columnas" :key="col.key" class="px-3 py-1.5 font-mono text-blue-100/90 whitespace-nowrap">
                <CeldaInforme :columna="col.key" :fila="fila" :valor="fila[col.key]" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'
import { useClientesStore } from '@/stores/clientes'
import { useInformeExport } from '@/composables/useInformeExport'
import { claseFilaCircuito } from '@/utils/estadosPedido'
import CeldaInforme from '@/components/informes/CeldaInforme.vue'

const notification = useNotificationStore()
const clientesStore = useClientesStore()
const clientesOrdenados = computed(() =>
  [...clientesStore.clientes].sort((a, b) => (a.razon_social || '').localeCompare(b.razon_social || '', 'es'))
)

const loading = ref(false)
const filas = ref([])
const columnas = ref([])
const { exportar: exportarArchivo, exportando } = useInformeExport('/informes/pedidos-oc/export', 'pedidos_con_oc')

const filtros = reactive({
  cliente_id: null,
})

const FORMATOS = [
  { formato: 'csv', label: 'CSV', icono: 'fa-file-csv', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-emerald-500/50 hover:text-emerald-300' },
  { formato: 'excel', label: 'Excel', icono: 'fa-file-excel', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-green-500/50 hover:text-green-300' },
  { formato: 'pdf', label: 'PDF', icono: 'fa-file-pdf', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-red-500/50 hover:text-red-300' },
  { formato: 'txt', label: 'TXT', icono: 'fa-file-lines', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-blue-500/50 hover:text-blue-300' },
]

const armarParams = () => {
  const params = {}
  if (filtros.cliente_id) params.cliente_id = filtros.cliente_id
  return params
}

const cargar = async () => {
  loading.value = true
  try {
    const res = await api.get('/informes/pedidos-oc', { params: armarParams() })
    filas.value = res.data.filas || []
    columnas.value = res.data.columnas || []
  } catch (e) {
    console.error(e)
    notification.add('Error cargando el informe: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    loading.value = false
  }
}

const exportar = (formato) => exportarArchivo(formato, armarParams())

watch(() => filtros.cliente_id, cargar)

onMounted(() => {
  if (clientesStore.clientes.length === 0) clientesStore.fetchClientes()
  cargar()
})
</script>
