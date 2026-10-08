// [IDENTIDAD] - frontend\src\views\Informes\CumplimientoOcListado.vue
// [Card #167, S882] Cumplimiento de OC -- por cada renglón de un pedido con OC: lo pedido, lo entregado (remitos) y lo facturado (neto de NC),
// con lo que falta de cada lado y una situación. Es la rutina para contestar «¿qué pasó con la OC tal?» sin reconstruirlo a mano.
// Las notas de débito no cuentan (ajustan importes, no cantidades). Los pedidos anulados no entran.
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans rounded-2xl border-2 border-blue-500/60 shadow-[0_0_30px_rgba(59,130,246,0.25)] p-6">
    <main class="flex flex-1 flex-col relative min-w-0">

      <header class="shrink-0 flex flex-wrap gap-4 items-center justify-between border-b border-blue-900/20 pb-4">
        <div>
          <h1 class="font-outfit text-xl font-semibold text-white">Informes · Cumplimiento de OC</h1>
          <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider">Pedido, entregado y facturado por renglón — listado exportable</p>
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
        <div>
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">OC</label>
          <input v-model.trim="filtros.oc" type="text" placeholder="Nº de OC" @keyup.enter="cargar"
            class="h-9 w-36 rounded-lg border border-blue-900/30 bg-[#02050f] px-3 text-xs text-blue-100 placeholder-blue-900/50 focus:border-blue-500 focus:outline-none" />
        </div>
        <label class="h-9 flex items-center gap-2 text-xs text-blue-300/80 cursor-pointer select-none" title="Oculta los renglones ya entregados y facturados por completo">
          <input type="checkbox" v-model="filtros.solo_abiertas" class="accent-blue-500" />
          Solo abiertas
        </label>
        <button @click="cargar" class="h-9 px-3 rounded-lg border border-blue-900/30 text-blue-400 hover:text-blue-200 hover:border-blue-500/50 transition-colors" title="Recargar">
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': loading }"></i>
        </button>
        <div class="ml-auto flex flex-wrap items-center gap-2 text-[11px]">
          <span v-for="s in resumen" :key="s.situacion" class="px-2 py-0.5 rounded border font-bold uppercase tracking-wider" :class="claseSituacion(s.situacion)">{{ s.cantidad }} {{ s.situacion }}</span>
          <span class="text-blue-400/40">{{ filas.length }} renglón(es) · {{ cantidadOcs }} OC</span>
        </div>
      </div>

      <div ref="contenedorScroll" class="flex-1 overflow-auto mt-3">
        <table class="w-full text-xs">
          <thead class="sticky top-0 bg-[#0f172a] z-10">
            <tr class="text-[10px] uppercase tracking-widest text-blue-400/50 border-b border-blue-900/20">
              <th v-for="col in columnas" :key="col.key" @click="alternarOrden(col.key)" class="px-3 py-2 font-bold cursor-pointer select-none hover:text-blue-200" :class="esNumerica(col.key) ? 'text-right' : 'text-left'" :title="tituloOrden(col.label)">{{ col.label }}<span class="ml-1 text-blue-300">{{ indicadorOrden(col.key) }}</span></th>
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
                {{ filtros.solo_abiertas ? 'No hay renglones abiertos para estos filtros: todo lo que tiene OC está entregado y facturado' : 'Sin pedidos con OC para estos filtros' }}
              </td>
            </tr>
            <tr v-for="(fila, i) in ordenadas" :key="i" @dblclick="abrirPedido(fila.pedido_id, $event)" class="border-b border-blue-900/10 hover:bg-blue-900/10" :class="claseFilaCircuito(fila.circuito)">
              <td v-for="col in columnas" :key="col.key" class="px-3 py-1.5 font-mono text-blue-100/90 whitespace-nowrap" :class="esNumerica(col.key) ? 'text-right' : ''">
                <span v-if="col.key === 'situacion'" class="inline-block px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider" :class="claseSituacion(fila.situacion)">{{ fila.situacion }}</span>
                <template v-else-if="esNumerica(col.key)">{{ fmt(fila[col.key]) }}</template>
                <CeldaInforme v-else :columna="col.key" :fila="fila" :valor="fila[col.key]" @estado-cambiado="aplicarEstado" />
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
import { useAbrirPedido } from '@/composables/useAbrirPedido'
import { useRefrescoAlGuardarPedido } from '@/composables/useRefrescoAlGuardarPedido'
import { useOrdenColumnas } from '@/composables/useOrdenColumnas'
import { useScrollRecordado } from '@/composables/useScrollRecordado'
import { usePersistirFiltros } from '@/composables/usePersistirFiltros'
import { aplicarEstadoAFilas } from '@/utils/estadosPedido'
import { claseFilaCircuito } from '@/utils/estadosPedido'
import CeldaInforme from '@/components/informes/CeldaInforme.vue'

const notification = useNotificationStore()
// Doble clic en una fila abre el pedido (pestaña nueva); el Estado se cambia desde el informe.
const abrirPedido = useAbrirPedido()
// Al guardar un pedido en otra pestaña, este informe se actualiza solo (sin perder filtros ni scroll).
useRefrescoAlGuardarPedido(() => cargar({ silencioso: true }))
const aplicarEstado = ({ pedidoId, estado }) => aplicarEstadoAFilas(filas.value, pedidoId, estado)
const clientesStore = useClientesStore()
const clientesOrdenados = computed(() =>
  [...clientesStore.clientes].sort((a, b) => (a.razon_social || '').localeCompare(b.razon_social || '', 'es'))
)

const loading = ref(false)
const contenedorScroll = ref(null)
useScrollRecordado('cumplimiento-oc', contenedorScroll, loading)
const filas = ref([])
const { ordenadas, alternarOrden, indicadorOrden, tituloOrden } = useOrdenColumnas(filas, 'cumplimiento-oc')
const columnas = ref([])
const { exportar: exportarArchivo, exportando } = useInformeExport('/informes/cumplimiento-oc/export', 'cumplimiento_de_oc')

// «Solo abiertas» arranca prendido: la rutina es mirar lo que falta; apagarlo muestra también lo ya cerrado.
const filtros = reactive({
  cliente_id: null,
  oc: '',
  solo_abiertas: true,
})
usePersistirFiltros('cumplimiento-oc', filtros)

const FORMATOS = [
  { formato: 'csv', label: 'CSV', icono: 'fa-file-csv', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-emerald-500/50 hover:text-emerald-300' },
  { formato: 'excel', label: 'Excel', icono: 'fa-file-excel', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-green-500/50 hover:text-green-300' },
  { formato: 'pdf', label: 'PDF', icono: 'fa-file-pdf', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-red-500/50 hover:text-red-300' },
  { formato: 'txt', label: 'TXT', icono: 'fa-file-lines', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-blue-500/50 hover:text-blue-300' },
]

const NUMERICAS = new Set(['pedido', 'entregado', 'facturado', 'a_entregar', 'a_facturar'])
const esNumerica = (key) => NUMERICAS.has(key)
const fmt = (n) => (n === null || n === undefined ? '-' : Number(n).toLocaleString('es-AR', { maximumFractionDigits: 2 }))

// Paleta de la situación: lo que está de más es rojo, lo que falta entregar ámbar, lo que falta facturar celeste, lo cerrado verde.
const claseSituacion = (s) => ({
  'SOBRE-FACTURADA': 'bg-red-500/15 border-red-500/40 text-red-300',
  'SOBRE-ENTREGADA': 'bg-red-500/15 border-red-500/40 text-red-300',
  'FALTA ENTREGAR': 'bg-amber-500/15 border-amber-500/40 text-amber-300',
  'FALTA FACTURAR': 'bg-sky-500/15 border-sky-500/40 text-sky-300',
  'CERRADA': 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300',
}[s] || 'bg-white/5 border-white/10 text-white/50')

const ORDEN_SITUACIONES = ['SOBRE-FACTURADA', 'SOBRE-ENTREGADA', 'FALTA ENTREGAR', 'FALTA FACTURAR', 'CERRADA']
const resumen = computed(() => ORDEN_SITUACIONES
  .map((s) => ({ situacion: s, cantidad: filas.value.filter((f) => f.situacion === s).length }))
  .filter((s) => s.cantidad > 0))
const cantidadOcs = computed(() => new Set(filas.value.map((f) => `${f.cliente}|${(f.oc || '').trim().toUpperCase()}`)).size)

const armarParams = () => {
  const params = {}
  if (filtros.cliente_id) params.cliente_id = filtros.cliente_id
  if (filtros.oc) params.oc = filtros.oc
  if (filtros.solo_abiertas) params.solo_abiertas = true
  return params
}

const cargar = async ({ silencioso = false } = {}) => {
  if (!silencioso) loading.value = true
  try {
    const res = await api.get('/informes/cumplimiento-oc', { params: armarParams() })
    filas.value = res.data.filas || []
    columnas.value = res.data.columnas || []
  } catch (e) {
    console.error(e)
    notification.add('Error cargando el informe: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    if (!silencioso) loading.value = false
  }
}

const exportar = (formato) => exportarArchivo(formato, armarParams())

watch(() => [filtros.cliente_id, filtros.solo_abiertas], cargar)

onMounted(() => {
  if (clientesStore.clientes.length === 0) clientesStore.fetchClientes()
  cargar()
})
</script>
