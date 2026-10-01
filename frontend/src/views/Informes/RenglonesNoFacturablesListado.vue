// [IDENTIDAD] - frontend\src\views\Informes\RenglonesNoFacturablesListado.vue
// [S876] Informe G -- renglones que salieron SIN SER VENTA FIRME (consignación, muestra sin cargo, garantía /
// reemplazo). Es la alerta contra el riesgo "Consignación Eterna" que pidió Nike: mercadería a prueba que sale y
// se olvida sin resolver. Un renglón está abierto mientras conserva su motivo y sigue afuera; se cierra
// facturándolo (botón Facturar en la pantalla de logística del pedido) o devolviéndolo. A los 30 días se marca
// en alerta. Solo lectura.
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans rounded-2xl border-2 border-blue-500/60 shadow-[0_0_30px_rgba(59,130,246,0.25)] p-6">
    <main class="flex flex-1 flex-col relative min-w-0">

      <header class="shrink-0 flex flex-wrap gap-4 items-center justify-between border-b border-blue-900/20 pb-4">
        <div>
          <h1 class="font-outfit text-xl font-semibold text-white">Informes · Renglones sin venta firme</h1>
          <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider">Consignación, muestras y garantías abiertas — Informe G</p>
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

      <div class="shrink-0 flex flex-wrap gap-3 items-end py-3 border-b border-blue-900/10">
        <div>
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Motivo</label>
          <select v-model="filtros.motivo"
            class="h-9 rounded-lg border border-blue-900/30 bg-[#02050f] px-3 text-xs text-blue-100 focus:border-blue-500 focus:outline-none">
            <option value="todos">Todos</option>
            <option v-for="m in MOTIVOS_NO_FACTURABLE" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
        </div>
        <div class="w-64">
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Cliente</label>
          <BuscadorLista v-model="filtros.cliente_id" :options="opcionesClientes" placeholder="Todos — escribí para buscar" />
        </div>
        <label class="flex items-center gap-2 text-xs text-blue-300/70 cursor-pointer select-none h-9">
          <input type="checkbox" v-model="filtros.solo_alerta" class="accent-amber-500" />
          Solo los que están en alerta
        </label>
        <button @click="cargar" class="h-9 px-3 rounded-lg border border-blue-900/30 text-blue-400 hover:text-blue-200 hover:border-blue-500/50 transition-colors" title="Actualizar">
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': loading }"></i>
        </button>
        <div v-if="resumen" class="ml-auto flex flex-wrap gap-2 text-[11px]">
          <span class="px-2 py-1 rounded border border-blue-900/30 text-blue-200">{{ resumen.total }} renglón(es) abierto(s)</span>
          <span class="px-2 py-1 rounded border border-amber-500/40 text-amber-300" title="Llevan 30 días o más sin resolverse">{{ resumen.en_alerta }} en alerta</span>
          <span v-for="m in resumen.por_motivo" :key="m.motivo" class="px-2 py-1 rounded border border-blue-900/30 text-blue-300/70">{{ m.cantidad }} {{ m.motivo.toLowerCase() }}</span>
        </div>
      </div>

      <div ref="contenedorScroll" class="flex-1 overflow-auto mt-3">
        <div v-if="loading" class="text-center py-10 text-blue-500"><i class="fas fa-spinner fa-spin mr-2"></i> Cargando...</div>
        <div v-else-if="filas.length === 0" class="text-center py-10 text-blue-400/40">Ningún renglón abierto para estos filtros</div>
        <table v-else class="w-full text-xs">
          <thead class="sticky top-0 bg-[#0f172a] z-10">
            <tr class="text-[10px] uppercase tracking-widest text-blue-400/50 border-b border-blue-900/20">
              <th v-for="col in COLUMNAS_PANTALLA" :key="col.key" @click="alternarOrden(col.key)" class="px-3 py-2 font-bold cursor-pointer select-none hover:text-blue-200" :class="col.align === 'right' ? 'text-right' : 'text-left'" :title="tituloOrden(col.label)">{{ col.label }}<span class="ml-1 text-blue-300">{{ indicadorOrden(col.key) }}</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in ordenadas" :key="f.remito_item_id" @dblclick="abrirPedido(f.pedido_id, $event)" class="border-b border-blue-900/10 hover:bg-blue-900/10 align-top"
              :class="[claseFilaCircuito(f.circuito), f.en_alerta ? 'bg-amber-900/10' : '']">
              <td class="px-3 py-1.5 font-mono whitespace-nowrap">
                <EnlacePedido :pedido-id="f.pedido_id" clase="text-blue-300 hover:text-blue-100 underline decoration-dotted" />
                <!-- Facturar o devolver el renglón se hace en la logística del pedido. -->
                <EnlacePedido :pedido-id="f.pedido_id" destino="logistica" clase="ml-2 text-amber-300/80 hover:text-amber-200"><i class="fas fa-truck"></i></EnlacePedido>
              </td>
              <td class="px-3 py-1.5 text-blue-100/90">{{ f.cliente ?? '-' }}</td>
              <td class="px-3 py-1.5 text-blue-100/90">{{ f.producto }}</td>
              <td class="px-3 py-1.5 font-mono text-right text-blue-100/90">{{ f.cantidad }}</td>
              <td class="px-3 py-1.5">
                <span class="inline-block px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider" :class="motivoClase(f.motivo_base)">{{ f.motivo }}</span>
              </td>
              <td class="px-3 py-1.5 font-mono text-blue-100/80">{{ f.remito }}</td>
              <td class="px-3 py-1.5 text-blue-100/80">{{ f.entrega }}</td>
              <td class="px-3 py-1.5 font-mono whitespace-nowrap text-blue-100/90">{{ f.desde ?? '-' }}</td>
              <td class="px-3 py-1.5 font-mono text-right" :class="f.en_alerta ? 'text-amber-400 font-bold' : 'text-blue-100/90'">{{ f.antiguedad ?? '-' }}</td>
              <td class="px-3 py-1.5 font-bold text-amber-300">{{ f.alerta }}</td>
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
import { claseFilaCircuito } from '@/utils/estadosPedido'
import { MOTIVOS_NO_FACTURABLE, motivoClase } from '@/utils/remitoEntrega'
import BuscadorLista from '@/components/informes/BuscadorLista.vue'
import EnlacePedido from '@/components/informes/EnlacePedido.vue'

const notification = useNotificationStore()
// [S876] Doble clic en una fila abre el pedido (pestaña nueva).
const abrirPedido = useAbrirPedido()
// Al guardar un pedido en otra pestaña, este informe se actualiza solo (sin perder filtros ni scroll).
useRefrescoAlGuardarPedido(() => cargar({ silencioso: true }))
const clientesStore = useClientesStore()

const loading = ref(false)
const contenedorScroll = ref(null)
useScrollRecordado('no-facturables', contenedorScroll, loading) // vuelve al mismo lugar de la lista
const filas = ref([])
const { ordenadas, alternarOrden, indicadorOrden, tituloOrden } = useOrdenColumnas(filas, 'no-facturables')
const resumen = ref(null)
const { exportar: exportarArchivo, exportando } = useInformeExport('/informes/renglones-no-facturables/export', 'renglones_sin_venta_firme')

const filtros = reactive({ motivo: 'todos', cliente_id: null, solo_alerta: false })
// [S876] Recuerda los filtros y el orden mientras dure la pestaña (al volver de otra pantalla quedan como estaban).
usePersistirFiltros('no-facturables', filtros)

const FORMATOS = [
  { formato: 'csv', label: 'CSV', icono: 'fa-file-csv', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-emerald-500/50 hover:text-emerald-300' },
  { formato: 'excel', label: 'Excel', icono: 'fa-file-excel', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-green-500/50 hover:text-green-300' },
  { formato: 'pdf', label: 'PDF', icono: 'fa-file-pdf', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-red-500/50 hover:text-red-300' },
  { formato: 'txt', label: 'TXT', icono: 'fa-file-lines', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-blue-500/50 hover:text-blue-300' },
]
const COLUMNAS_PANTALLA = [
  { key: 'pedido_id', label: 'Pedido' }, { key: 'cliente', label: 'Cliente' }, { key: 'producto', label: 'Producto' },
  { key: 'cantidad', label: 'Cantidad', align: 'right' }, { key: 'motivo', label: 'Motivo' }, { key: 'remito', label: 'Remito' },
  { key: 'entrega', label: 'Entrega' }, { key: 'desde', label: 'Desde' }, { key: 'antiguedad', label: 'Días', align: 'right' },
  { key: 'alerta', label: 'Alerta' },
]

const opcionesClientes = computed(() =>
  [...clientesStore.clientes]
    .sort((a, b) => (a.razon_social || '').localeCompare(b.razon_social || '', 'es'))
    .map((c) => ({ id: c.id, label: c.razon_social, detalle: [c.codigo_interno ? `#${c.codigo_interno}` : '', c.cuit || ''].filter(Boolean).join(' · ') })))

const armarParams = () => {
  const params = {}
  if (filtros.motivo !== 'todos') params.motivo = filtros.motivo
  if (filtros.cliente_id) params.cliente_id = filtros.cliente_id
  if (filtros.solo_alerta) params.solo_alerta = true
  return params
}

const cargar = async ({ silencioso = false } = {}) => {
  if (!silencioso) loading.value = true
  try {
    const res = await api.get('/informes/renglones-no-facturables', { params: armarParams() })
    filas.value = res.data.filas || []
    resumen.value = res.data.resumen || null
  } catch (e) {
    console.error(e)
    notification.add('Error cargando el informe: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    if (!silencioso) loading.value = false
  }
}

const exportar = (formato) => exportarArchivo(formato, armarParams())

watch(() => JSON.stringify(armarParams()), cargar)

onMounted(() => {
  if (clientesStore.clientes.length === 0) clientesStore.fetchClientes()
  cargar()
})
</script>
