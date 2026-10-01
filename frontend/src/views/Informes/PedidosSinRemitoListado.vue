// [IDENTIDAD] - frontend\src\views\Informes\PedidosSinRemitoListado.vue
// [S875, prueba funcional 30/09] Informe F -- pedidos SIN REMITO. Hoja de revisión: en la copia de producción
// 54 de 103 pedidos no tienen ningún remito vigente y no todos son lo mismo. Se separan Blancos y Rosas
// (Carlos: no van en la misma bolsa) y se ordenan para revisar: primero lo incoherente (CUMPLIDO sin ninguna
// salida registrada), después los PENDIENTES, los más viejos primero. Solo lectura: no crea remitos.
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans rounded-2xl border-2 border-blue-500/60 shadow-[0_0_30px_rgba(59,130,246,0.25)] p-6">
    <main class="flex flex-1 flex-col relative min-w-0">

      <header class="shrink-0 flex flex-wrap gap-4 items-center justify-between border-b border-blue-900/20 pb-4">
        <div>
          <h1 class="font-outfit text-xl font-semibold text-white">Informes · Pedidos sin remito</h1>
          <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider">Hoja de revisión — Informe F</p>
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
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Circuito</label>
          <div class="inline-flex rounded-lg border border-blue-900/30 overflow-hidden">
            <button v-for="c in CIRCUITOS" :key="c.valor" @click="filtros.circuito = c.valor"
              class="px-3 py-2 text-xs font-bold transition-colors"
              :class="filtros.circuito === c.valor ? c.activo : 'bg-[#02050f] text-blue-300/60 hover:text-blue-100'">
              {{ c.label }}
            </button>
          </div>
        </div>
        <div>
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Estado</label>
          <select v-model="filtros.estado"
            class="h-9 rounded-lg border border-blue-900/30 bg-[#02050f] px-3 text-xs text-blue-100 focus:border-blue-500 focus:outline-none">
            <option value="todos">Todos</option>
            <option value="CUMPLIDO">Cumplido (sin salida registrada)</option>
            <option value="PENDIENTE">Pendiente</option>
            <option value="ANULADO">Anulado</option>
          </select>
        </div>
        <div class="w-64">
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Cliente</label>
          <BuscadorLista v-model="filtros.cliente_id" :options="opcionesClientes" placeholder="Todos — escribí para buscar" />
        </div>
        <label class="flex items-center gap-2 text-xs text-blue-300/70 cursor-pointer select-none h-9"
          :class="filtros.estado !== 'todos' ? 'opacity-40 pointer-events-none' : ''">
          <input type="checkbox" v-model="filtros.incluir_anulados" class="accent-blue-500" />
          Incluir anulados
        </label>
        <button @click="cargar" class="h-9 px-3 rounded-lg border border-blue-900/30 text-blue-400 hover:text-blue-200 hover:border-blue-500/50 transition-colors" title="Actualizar">
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': loading }"></i>
        </button>
        <div v-if="resumen" class="ml-auto flex flex-wrap gap-2 text-[11px]">
          <span class="px-2 py-1 rounded border border-blue-900/30 text-blue-200">{{ resumen.total }} pedido(s)</span>
          <span class="px-2 py-1 rounded border border-slate-500/30 text-slate-300">{{ resumen.blanco }} Blanco(s)</span>
          <span class="px-2 py-1 rounded border border-pink-500/40 text-pink-300">{{ resumen.rosa }} Rosa(s)</span>
          <span class="px-2 py-1 rounded border border-yellow-500/40 text-yellow-400" title="Figuran cumplidos pero no tienen ninguna salida registrada">{{ resumen.cumplido_sin_salida }} cumplido(s) sin salida</span>
          <span class="px-2 py-1 rounded border border-blue-900/30 text-blue-300/70">{{ resumen.con_factura_candidata }} con factura candidata</span>
        </div>
      </div>

      <div ref="contenedorScroll" class="flex-1 overflow-auto mt-3 space-y-6">
        <div v-if="loading" class="text-center py-10 text-blue-500"><i class="fas fa-spinner fa-spin mr-2"></i> Cargando...</div>
        <div v-else-if="filas.length === 0" class="text-center py-10 text-blue-400/40">Ningún pedido sin remito para estos filtros</div>

        <section v-for="s in secciones" :key="s.circuito" v-show="!loading && s.filas.length">
          <h2 class="flex items-center gap-3 text-sm font-bold text-white mb-1">
            <span class="inline-block px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider" :class="claseCircuito(s.circuito)">{{ s.circuito }}</span>
            {{ s.filas.length }} pedido(s) sin remito
          </h2>
          <p v-if="s.nota" class="text-[11px] text-amber-400/80 mb-2"><i class="fas fa-circle-info mr-1"></i>{{ s.nota }}</p>
          <table class="w-full text-xs">
            <thead class="sticky top-0 bg-[#0f172a] z-10">
              <tr class="text-[10px] uppercase tracking-widest text-blue-400/50 border-b border-blue-900/20">
                <th v-for="col in COLUMNAS_PANTALLA" :key="col.key" @click="alternarOrden(col.key)" class="px-3 py-2 font-bold cursor-pointer select-none hover:text-blue-200" :class="col.align === 'right' ? 'text-right' : 'text-left'" :title="tituloOrden(col.label)">{{ col.label }}<span class="ml-1 text-blue-300">{{ indicadorOrden(col.key) }}</span></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="f in s.filas" :key="f.pedido_id" @dblclick="abrirPedido(f.pedido_id, $event)" class="border-b border-blue-900/10 hover:bg-blue-900/10 align-top"
                :class="claseFilaCircuito(f.circuito)">
                <td class="px-3 py-1.5 font-mono">
                  <EnlacePedido :pedido-id="f.pedido_id" clase="text-blue-300 hover:text-blue-100 underline decoration-dotted" />
                </td>
                <td class="px-3 py-1.5">
                  <EstadoEditable :pedido-id="f.pedido_id" :estado="f.estado_base" :texto="f.estado"
                    @cambiado="(nuevo) => aplicarEstado({ pedidoId: f.pedido_id, estado: nuevo })" />
                </td>
                <td class="px-3 py-1.5">
                  <CircuitoEditable :pedido-id="f.pedido_id" :circuito="f.circuito" />
                </td>
                <td class="px-3 py-1.5 text-blue-100/90">{{ f.cliente ?? '-' }}</td>
                <td class="px-3 py-1.5 font-mono whitespace-nowrap text-blue-100/90">{{ f.fecha_pedido ?? '-' }}</td>
                <td class="px-3 py-1.5 font-mono text-right" :class="f.antiguedad > 60 ? 'text-amber-400 font-bold' : 'text-blue-100/90'">{{ f.antiguedad ?? '-' }}</td>
                <td class="px-3 py-1.5 font-mono text-blue-100/90">{{ f.oc || '-' }}</td>
                <td class="px-3 py-1.5 text-blue-100/80">{{ f.renglones }}</td>
                <td class="px-3 py-1.5 font-mono text-right whitespace-nowrap text-blue-100/90">{{ moneda(f.total) }}</td>
                <td class="px-3 py-1.5 font-mono text-blue-100/70">{{ f.comprobante }}</td>
                <td class="px-3 py-1.5 font-mono text-emerald-300/80">{{ f.factura_candidata || '-' }}</td>
                <td class="px-3 py-1.5 text-blue-200/80">{{ f.observacion }}</td>
              </tr>
            </tbody>
          </table>
        </section>
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
import EstadoEditable from '@/components/informes/EstadoEditable.vue'
import CircuitoEditable from '@/components/informes/CircuitoEditable.vue'
import EnlacePedido from '@/components/informes/EnlacePedido.vue'
import { estadoClase, claseFilaCircuito, claseCircuito } from '@/utils/estadosPedido'
import BuscadorLista from '@/components/informes/BuscadorLista.vue'

const notification = useNotificationStore()
// [S876] Doble clic en una fila abre el pedido (pestaña nueva); el Estado se cambia desde el informe.
const abrirPedido = useAbrirPedido()
// Al guardar un pedido en otra pestaña, este informe se actualiza solo (sin perder filtros ni scroll).
useRefrescoAlGuardarPedido(() => cargar({ silencioso: true }))
const aplicarEstado = ({ pedidoId, estado }) => aplicarEstadoAFilas(filas.value, pedidoId, estado)
const clientesStore = useClientesStore()

const loading = ref(false)
const contenedorScroll = ref(null)
useScrollRecordado('sin-remito', contenedorScroll, loading) // vuelve al mismo lugar de la lista
const filas = ref([])
const { ordenadas, alternarOrden, indicadorOrden, tituloOrden } = useOrdenColumnas(filas, 'sin-remito')
const resumen = ref(null)
const { exportar: exportarArchivo, exportando } = useInformeExport('/informes/pedidos-sin-remito/export', 'pedidos_sin_remito')

const filtros = reactive({ circuito: 'todos', estado: 'todos', cliente_id: null, incluir_anulados: false })
// [S876] Recuerda los filtros y el orden mientras dure la pestaña (al volver de otra pantalla quedan como estaban).
usePersistirFiltros('sin-remito', filtros)

const CIRCUITOS = [
  { valor: 'todos', label: 'Todos', activo: 'bg-blue-600 text-white' },
  { valor: 'blanco', label: 'Blanco', activo: 'bg-slate-500 text-white' },
  { valor: 'rosa', label: 'Rosa', activo: 'bg-pink-600 text-white' },
]
const FORMATOS = [
  { formato: 'csv', label: 'CSV', icono: 'fa-file-csv', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-emerald-500/50 hover:text-emerald-300' },
  { formato: 'excel', label: 'Excel', icono: 'fa-file-excel', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-green-500/50 hover:text-green-300' },
  { formato: 'pdf', label: 'PDF', icono: 'fa-file-pdf', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-red-500/50 hover:text-red-300' },
  { formato: 'txt', label: 'TXT', icono: 'fa-file-lines', clase: 'bg-white/5 border-white/10 text-white/50 hover:border-blue-500/50 hover:text-blue-300' },
]
const COLUMNAS_PANTALLA = [
  { key: 'pedido_id', label: 'Pedido' }, { key: 'estado', label: 'Estado' }, { key: 'circuito', label: 'Circuito' }, { key: 'cliente', label: 'Cliente' },
  { key: 'fecha_pedido', label: 'Fecha' }, { key: 'antiguedad', label: 'Días', align: 'right' }, { key: 'oc', label: 'OC' },
  { key: 'renglones', label: 'Renglones' }, { key: 'total', label: 'Total', align: 'right' },
  { key: 'comprobante', label: 'Comprobante vinculado' }, { key: 'factura_candidata', label: 'Factura de ARCA candidata' },
  { key: 'observacion', label: 'Qué revisar' },
]

// Cada circuito en su propia sección. La nota del Rosa no afirma cuál es su respaldo (remito 0015, ticket
// interno...): eso está en discusión, y el listado muestra solo el hecho.
const secciones = computed(() => [
  { circuito: 'Blanco', filas: ordenadas.value.filter((f) => f.circuito === 'Blanco'), nota: null },
  { circuito: 'Rosa', filas: ordenadas.value.filter((f) => f.circuito === 'Rosa'),
    nota: 'Circuito Rosa: no se factura. Qué documento respalda la salida de estos pedidos (remito 0015, ticket interno) está en definición.' },
])

const opcionesClientes = computed(() =>
  [...clientesStore.clientes]
    .sort((a, b) => (a.razon_social || '').localeCompare(b.razon_social || '', 'es'))
    .map((c) => ({ id: c.id, label: c.razon_social, detalle: [c.codigo_interno ? `#${c.codigo_interno}` : '', c.cuit || ''].filter(Boolean).join(' · ') })))

const moneda = (v) => (v === null || v === undefined ? '-' : Number(v).toLocaleString('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }))

const armarParams = () => {
  const params = {}
  if (filtros.circuito !== 'todos') params.circuito = filtros.circuito
  if (filtros.estado !== 'todos') params.estado = filtros.estado
  if (filtros.cliente_id) params.cliente_id = filtros.cliente_id
  if (filtros.incluir_anulados && filtros.estado === 'todos') params.incluir_anulados = true
  return params
}

const cargar = async ({ silencioso = false } = {}) => {
  if (!silencioso) loading.value = true
  try {
    const res = await api.get('/informes/pedidos-sin-remito', { params: armarParams() })
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
