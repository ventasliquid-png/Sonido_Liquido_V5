// [IDENTIDAD] - frontend\src\views\Informes\RemitosListado.vue
// [S875] Informe A -- remitos. Misma fuente de datos que EntregasView.vue (GET /remitos/entregas), acá
// en forma de listado -- esa pantalla queda para el drill-down operativo, esta para el reporte que se
// exporta o se manda por fuera del sistema.
// [S875, prueba funcional 30/09] Se elige CÓMO presentarlo (por cliente / por fecha / por número de
// remito), cada remito es una CAJA con sus renglones adentro, y el Estado y el Circuito (Blanco/Rosa)
// del pedido se ven con los mismos colores que en la lista de pedidos.
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans rounded-2xl border-2 border-blue-500/60 shadow-[0_0_30px_rgba(59,130,246,0.25)] p-6">
    <main class="flex flex-1 flex-col relative min-w-0">

      <header class="shrink-0 flex flex-wrap gap-4 items-center justify-between border-b border-blue-900/20 pb-4">
        <div>
          <h1 class="font-outfit text-xl font-semibold text-white">Informes · Remitos por fecha o cliente</h1>
          <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider">Listado exportable — Informe A</p>
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

      <!-- CÓMO PRESENTARLO -->
      <div class="shrink-0 flex flex-wrap items-center gap-3 pt-4">
        <span class="text-[10px] font-bold uppercase text-blue-400/50">Presentar</span>
        <div class="inline-flex rounded-lg border border-blue-900/30 overflow-hidden">
          <!-- [S876] Cada orden lleva su par de flechitas (arriba = ascendente, abajo = descendente), la prendida es la que rige. Un clic en el
               orden ya elegido invierte el sentido; un clic en una flecha lo fija. Reemplaza al botón Ascendente / Descendente. -->
          <button v-for="o in ORDENES" :key="o.valor" @click="clicOrden(o.valor)"
            class="px-3 py-1.5 text-xs font-bold transition-colors inline-flex items-center gap-2"
            :class="filtros.orden === o.valor ? 'bg-blue-600 text-white' : 'bg-[#02050f] text-blue-300/60 hover:text-blue-100'"
            :title="filtros.orden === o.valor ? 'Clic: invertir el sentido (ahora ' + (sentidoEfectivo === 'asc' ? 'ascendente' : 'descendente') + ')' : 'Presentar ' + o.label.toLowerCase()">
            {{ o.label }}
            <span class="inline-flex flex-col leading-none text-[9px]">
              <span @click.stop="fijarOrden(o.valor, 'asc')" :class="claseFlecha(o.valor, 'asc')" class="px-0.5 hover:text-white" title="Ascendente (A→Z, más viejos primero)">▲</span>
              <span @click.stop="fijarOrden(o.valor, 'desc')" :class="claseFlecha(o.valor, 'desc')" class="px-0.5 hover:text-white" title="Descendente (Z→A, más recientes primero)">▼</span>
            </span>
          </button>
        </div>
        <span class="text-[10px] text-blue-400/30">(próximamente: por producto)</span>

        <span class="ml-4 text-[10px] font-bold uppercase text-blue-400/50">Circuito</span>
        <div class="inline-flex rounded-lg border border-blue-900/30 overflow-hidden">
          <button v-for="c in CIRCUITOS" :key="c.valor" @click="filtros.circuito = c.valor"
            class="px-3 py-1.5 text-xs font-bold transition-colors"
            :class="filtros.circuito === c.valor ? c.activo : 'bg-[#02050f] text-blue-300/60 hover:text-blue-100'">
            {{ c.label }}
          </button>
        </div>
      </div>

      <!-- FILTROS -->
      <div class="shrink-0 flex flex-wrap gap-3 items-end py-3 border-b border-blue-900/10">
        <div class="w-64">
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Cliente</label>
          <BuscadorLista v-model="filtros.cliente_id" :options="opcionesClientes" placeholder="Todos — escribí para buscar" />
        </div>
        <div>
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Desde</label>
          <input v-model="filtros.desde" type="date"
            class="h-9 rounded-lg border border-blue-900/30 bg-[#02050f] px-3 text-xs text-blue-100 focus:border-blue-500 focus:outline-none" />
        </div>
        <div>
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Hasta</label>
          <input v-model="filtros.hasta" type="date"
            class="h-9 rounded-lg border border-blue-900/30 bg-[#02050f] px-3 text-xs text-blue-100 focus:border-blue-500 focus:outline-none" />
        </div>
        <div>
          <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">OC</label>
          <input v-model="filtros.oc" type="text" placeholder="Nº de OC" @keyup.enter="cargar"
            class="h-9 w-32 rounded-lg border border-blue-900/30 bg-[#02050f] px-3 text-xs text-blue-100 focus:border-blue-500 focus:outline-none" />
        </div>
        <label class="flex items-center gap-2 text-xs text-blue-300/70 cursor-pointer select-none h-9">
          <input type="checkbox" v-model="filtros.incluir_anulados" class="accent-blue-500" />
          Incluir anulados
        </label>
        <label class="flex items-center gap-2 text-xs text-blue-300/70 cursor-pointer select-none h-9"
          title="Renglones de pedido que todavía no tienen ningún remito (los pendientes están en el Informe B)">
          <input type="checkbox" v-model="filtros.incluir_sin_remito" class="accent-blue-500" />
          Incluir renglones sin remito
        </label>
        <button @click="mostrarRangos = !mostrarRangos"
          class="h-9 px-3 rounded-lg border text-xs font-bold transition-colors"
          :class="hayRangos ? 'border-blue-500/60 text-blue-200 bg-blue-900/20' : 'border-blue-900/30 text-blue-400/70 hover:border-blue-500/50'">
          <i class="fas fa-sliders-h mr-1"></i> Rangos desde/hasta<span v-if="hayRangos"> ●</span>
        </button>
        <button @click="cargar" class="h-9 px-3 rounded-lg border border-blue-900/30 text-blue-400 hover:text-blue-200 hover:border-blue-500/50 transition-colors" title="Actualizar">
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': loading }"></i>
        </button>
        <span class="text-[11px] text-blue-400/40 ml-auto">{{ filas.length }} renglón(es) en {{ grupos.length }} {{ filtros.incluir_sin_remito ? 'grupo(s)' : 'remito(s)' }}</span>
      </div>

      <!-- RANGOS -->
      <div v-if="mostrarRangos" class="shrink-0 flex flex-wrap gap-x-6 gap-y-3 items-end py-3 border-b border-blue-900/10">
        <div class="flex items-end gap-2">
          <div class="w-52">
            <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Clientes desde</label>
            <BuscadorLista v-model="filtros.cliente_desde" :options="opcionesClientesRango" libre placeholder="A… (escribí o elegí)" />
          </div>
          <div class="w-52">
            <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">hasta</label>
            <BuscadorLista v-model="filtros.cliente_hasta" :options="opcionesClientesRango" libre placeholder="…Z (escribí o elegí)" />
          </div>
        </div>
        <div class="flex items-end gap-2">
          <div class="w-56">
            <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">Productos desde (código)</label>
            <BuscadorLista v-model="filtros.producto_desde" :options="opcionesProductosRango" libre placeholder="VS0001… (escribí o elegí)" />
          </div>
          <div class="w-56">
            <label class="block text-[10px] font-bold uppercase text-blue-400/50 mb-1">hasta</label>
            <BuscadorLista v-model="filtros.producto_hasta" :options="opcionesProductosRango" libre placeholder="…VS0050 (escribí o elegí)" />
          </div>
        </div>
        <button v-if="hayRangos" @click="limpiarRangos" class="h-9 px-3 text-xs text-blue-400/70 hover:text-blue-200">
          <i class="fas fa-eraser mr-1"></i> Quitar rangos
        </button>
        <p v-if="rangoInvertido" class="basis-full text-xs text-amber-400">
          <i class="fas fa-triangle-exclamation mr-1"></i>El «desde» es posterior al «hasta»: con ese rango no va a aparecer nada.
        </p>
      </div>

      <!-- LISTADO: una caja por remito -->
      <div ref="contenedorScroll" class="flex-1 overflow-auto mt-3">
        <table class="w-full text-xs">
          <thead class="sticky top-0 bg-[#0f172a] z-10">
            <tr class="text-[10px] uppercase tracking-widest text-blue-400/50 border-b border-blue-900/20">
              <th class="text-left px-3 py-2 font-bold">Producto</th>
              <th class="text-right px-3 py-2 font-bold w-32">Cant. pedida</th>
              <th class="text-right px-3 py-2 font-bold w-32">Cant. remitida</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="3" class="text-center py-10 text-blue-500">
                <i class="fas fa-spinner fa-spin mr-2"></i> Cargando...
              </td>
            </tr>
            <tr v-else-if="filas.length === 0">
              <td colspan="3" class="text-center py-10 text-blue-400/40">Sin resultados para estos filtros</td>
            </tr>
            <template v-for="g in grupos" :key="g.id">
              <tr @dblclick="abrirPedido(g.cab.pedido_id, $event)" class="border-t-2 border-blue-800/50 bg-blue-950/40" :class="[claseFilaCircuito(g.cab.circuito), g.cab.remito_estado === 'ANULADO' ? 'opacity-40' : '']">
                <td colspan="3" class="px-3 py-2">
                  <div class="flex flex-wrap items-center gap-x-4 gap-y-1">
                    <span class="font-mono font-bold text-white text-sm">{{ g.cab.remito_id ? 'Remito ' + g.cab.remito : 'Sin remito' }}</span>
                    <span class="font-mono text-blue-200/80">{{ g.cab.fecha_documento || g.cab.fecha_pedido || '-' }}</span>
                    <span class="font-semibold text-white">{{ g.cab.cliente || '(sin cliente)' }}</span>
                    <span v-if="g.cab.oc" class="text-blue-300/70">OC {{ g.cab.oc }}</span>
                    <span class="text-blue-300/70">Pedido
                      <EnlacePedido v-if="g.cab.pedido_id != null" :pedido-id="g.cab.pedido_id" clase="text-blue-300 hover:text-blue-100 underline decoration-dotted" />
                      <template v-else>-</template>
                    </span>
                    <span v-if="g.cab.factura" class="text-blue-300/70">Factura {{ g.cab.factura }}</span>
                    <span v-if="g.cab.remito_estado" class="text-[10px] uppercase text-blue-300/40">remito {{ g.cab.remito_estado }}</span>
                    <EstadoEditable v-if="g.cab.estado && g.cab.pedido_id != null" :pedido-id="g.cab.pedido_id" :estado="g.cab.estado_base" :texto="g.cab.estado"
                      @cambiado="(nuevo) => aplicarEstado({ pedidoId: g.cab.pedido_id, estado: nuevo })" />
                    <span v-else-if="g.cab.estado" class="inline-block px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider"
                      :class="estadoClase(g.cab.estado_base)">{{ g.cab.estado }}</span>
                    <CircuitoEditable v-if="g.cab.circuito && g.cab.pedido_id != null" :pedido-id="g.cab.pedido_id" :circuito="g.cab.circuito" />
                    <span v-else-if="g.cab.circuito" class="inline-block px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider"
                      :class="claseCircuito(g.cab.circuito)">{{ g.cab.circuito }}</span>
                  </div>
                </td>
              </tr>
              <tr v-for="(f, i) in g.filas" :key="g.id + '-' + i" @dblclick="abrirPedido(f.pedido_id, $event)"
                class="border-b border-blue-900/10 hover:bg-blue-900/10"
                :class="[claseFilaCircuito(f.circuito), f.remito_estado === 'ANULADO' ? 'opacity-40' : '']">
                <td class="pl-8 pr-3 py-1.5 font-mono text-blue-100/90">{{ f.producto ?? '-' }}</td>
                <td class="px-3 py-1.5 font-mono text-right text-blue-100/90">{{ f.cantidad_pedida ?? '-' }}</td>
                <td class="px-3 py-1.5 font-mono text-right font-bold"
                  :class="f.cantidad_remitida < 0 ? 'text-red-400' : 'text-blue-100'">{{ f.cantidad_remitida ?? '-' }}</td>
              </tr>
            </template>
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
import { useProductosStore } from '@/stores/productos'
import { useInformeExport } from '@/composables/useInformeExport'
import { useAbrirPedido } from '@/composables/useAbrirPedido'
import { useRefrescoAlGuardarPedido } from '@/composables/useRefrescoAlGuardarPedido'
import { usePersistirFiltros } from '@/composables/usePersistirFiltros'
import { useScrollRecordado } from '@/composables/useScrollRecordado'
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
const productosStore = useProductosStore()

const loading = ref(false)
const contenedorScroll = ref(null)
useScrollRecordado('remitos', contenedorScroll, loading) // vuelve al mismo lugar de la lista
const filas = ref([])
const mostrarRangos = ref(false)
const { exportar: exportarArchivo, exportando } = useInformeExport('/informes/remitos/export', 'remitos_por_fecha_cliente')

const filtros = reactive({
  orden: 'cliente',
  sentido: null,           // null = el de cada orden (cliente A-Z, fecha recientes primero, remito ascendente)
  circuito: 'todos',
  cliente_id: null,
  desde: '',
  hasta: '',
  oc: '',
  incluir_anulados: false,
  incluir_sin_remito: false,
  cliente_desde: null,
  cliente_hasta: null,
  producto_desde: null,
  producto_hasta: null,
})
// [S876] Recuerda los filtros y el orden mientras dure la pestaña (al volver de otra pantalla quedan como estaban).
usePersistirFiltros('remitos', filtros)

const ORDENES = [
  { valor: 'cliente', label: 'Remito / cliente' },
  { valor: 'fecha', label: 'Remitos por fecha' },
  { valor: 'remito', label: 'Remitos por Nº de remito' },
]
const SENTIDO_POR_DEFECTO = { cliente: 'asc', fecha: 'desc', remito: 'asc' }
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

const sentidoEfectivo = computed(() => filtros.sentido ?? SENTIDO_POR_DEFECTO[filtros.orden])
// Un clic en un orden que no estaba elegido lo elige con su sentido de siempre; en el que ya estaba, invierte el sentido.
const clicOrden = (valor) => {
  if (filtros.orden !== valor) { filtros.orden = valor; filtros.sentido = null }
  else filtros.sentido = sentidoEfectivo.value === 'asc' ? 'desc' : 'asc'
}
// Un clic en una flecha elige ese orden con ese sentido.
const fijarOrden = (valor, sentido) => { filtros.orden = valor; filtros.sentido = sentido }
// La flecha que rige se ve prendida; la otra, apagada (y en un orden no elegido, casi invisibles).
const claseFlecha = (valor, sentido) => {
  if (filtros.orden !== valor) return 'text-blue-300/25'
  return sentidoEfectivo.value === sentido ? 'text-white' : 'text-white/35'
}

const hayRangos = computed(() => !!(filtros.cliente_desde || filtros.cliente_hasta || filtros.producto_desde || filtros.producto_hasta))
const sinAcentos = (s) => String(s ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
// Un "desde" posterior al "hasta" no encuentra nada: se avisa en vez de devolver la lista vacía sin explicación.
const rangoInvertido = computed(() =>
  !!(filtros.cliente_desde && filtros.cliente_hasta && sinAcentos(filtros.cliente_desde) > sinAcentos(filtros.cliente_hasta)) ||
  !!(filtros.producto_desde && filtros.producto_hasta && filtros.producto_desde.toUpperCase() > filtros.producto_hasta.toUpperCase())
)
const limpiarRangos = () => {
  filtros.cliente_desde = filtros.cliente_hasta = filtros.producto_desde = filtros.producto_hasta = null
}

// Clientes ordenados por razón social; se busca por nombre, código interno o CUIT.
const clientesOrdenados = computed(() =>
  [...clientesStore.clientes].sort((a, b) => (a.razon_social || '').localeCompare(b.razon_social || '', 'es'))
)
const detalleCliente = (c) => [c.codigo_interno ? `#${c.codigo_interno}` : '', c.cuit || ''].filter(Boolean).join(' · ')
const opcionesClientes = computed(() =>
  clientesOrdenados.value.map((c) => ({ id: c.id, label: c.razon_social, detalle: detalleCliente(c) })))
// En los rangos el valor que viaja es la razón social (el "hasta" cubre todo lo que empieza así).
const opcionesClientesRango = computed(() =>
  clientesOrdenados.value.map((c) => ({ id: c.razon_social, label: c.razon_social, detalle: detalleCliente(c) })))
// Productos: el rango va por código visual (VS0001…), que es lo que el operador usa para abreviar.
const opcionesProductosRango = computed(() =>
  [...productosStore.productos]
    .filter((p) => p.codigo_visual)
    .sort((a, b) => a.codigo_visual.localeCompare(b.codigo_visual))
    .map((p) => ({ id: p.codigo_visual, label: p.codigo_visual, detalle: p.nombre })))

const armarParams = () => {
  const params = { orden: filtros.orden }
  if (filtros.sentido) params.sentido = filtros.sentido
  if (filtros.circuito !== 'todos') params.circuito = filtros.circuito
  if (filtros.cliente_id) params.cliente_id = filtros.cliente_id
  if (filtros.desde) params.desde = filtros.desde
  if (filtros.hasta) params.hasta = filtros.hasta
  if (filtros.oc) params.oc = filtros.oc
  if (filtros.incluir_anulados) params.incluir_anulados = true
  if (filtros.incluir_sin_remito) params.incluir_sin_remito = true
  for (const k of ['cliente_desde', 'cliente_hasta', 'producto_desde', 'producto_hasta']) {
    if (filtros[k]) params[k] = filtros[k]
  }
  return params
}

// Cada remito es una caja: la cabecera lleva los datos del remito y adentro van sus renglones. El servidor ya
// entrega las filas ordenadas y con los renglones de un remito seguidos; acá solo se cortan donde cambia `grupo`.
const grupos = computed(() => {
  const salida = []
  let actual = null
  for (const fila of filas.value) {
    if (!actual || actual.id !== fila.grupo) {
      actual = { id: fila.grupo, cab: fila, filas: [] }
      salida.push(actual)
    }
    actual.filas.push(fila)
  }
  return salida
})

const cargar = async ({ silencioso = false } = {}) => {
  if (!silencioso) loading.value = true
  try {
    const res = await api.get('/informes/remitos', { params: armarParams() })
    filas.value = res.data.filas || []
  } catch (e) {
    console.error(e)
    notification.add('Error cargando el informe: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    if (!silencioso) loading.value = false
  }
}

const exportar = (formato) => exportarArchivo(formato, armarParams())

// Todo filtro recarga solo, salvo el texto de la OC (Enter o el botón de actualizar).
watch(() => JSON.stringify({ ...armarParams(), oc: '' }), cargar)

onMounted(() => {
  if (clientesStore.clientes.length === 0) clientesStore.fetchClientes()
  if (productosStore.productos.length === 0) productosStore.fetchProductos()
  cargar()
})
</script>
