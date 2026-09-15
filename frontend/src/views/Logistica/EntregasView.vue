// [IDENTIDAD] - frontend\src\views\Logistica\EntregasView.vue
// Reporte de Entregas — Zona Verde, solo lectura. Consume GET /remitos/entregas.
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans tokyo-bg neon-blue rounded-2xl border-2 border-blue-500 shadow-[0_0_30px_rgba(59,130,246,0.4)] p-6">
    <main class="flex flex-1 flex-col relative min-w-0">

      <!-- Top Bar -->
      <header class="relative z-20 flex flex-wrap gap-4 items-center justify-between border-b border-blue-900/20 bg-black/20 px-6 py-4 backdrop-blur-sm shrink-0">
        <div>
          <h1 class="font-outfit text-xl font-semibold text-white">Reporte de Entregas</h1>
          <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider">Qué remito cubrió cada renglón de pedido</p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <div class="relative">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-blue-500/50 text-xs"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar cliente, OC o producto..."
              class="h-9 w-64 rounded-full border border-blue-900/30 bg-[#02050f] pl-9 pr-4 text-sm text-blue-100 placeholder-blue-900/50 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <input v-model="filtros.desde" type="date" title="Desde"
            class="h-9 rounded-lg border border-blue-900/30 bg-[#02050f] px-3 text-xs text-blue-100 focus:border-blue-500 focus:outline-none" />
          <input v-model="filtros.hasta" type="date" title="Hasta"
            class="h-9 rounded-lg border border-blue-900/30 bg-[#02050f] px-3 text-xs text-blue-100 focus:border-blue-500 focus:outline-none" />

          <label class="flex items-center gap-2 text-xs text-blue-300/70 cursor-pointer select-none">
            <input type="checkbox" v-model="filtros.incluir_anulados" class="accent-blue-500" />
            Incluir anulados
          </label>

          <button @click="cargar" class="p-2 text-blue-500 hover:text-blue-300 transition-colors" title="Recargar">
            <i class="fas fa-sync-alt" :class="{ 'animate-spin': loading }"></i>
          </button>
        </div>
      </header>

      <!-- Anomaly Banner -->
      <div v-if="anomalias.length" class="shrink-0 px-6 pt-4">
        <div class="rounded-xl border border-amber-500/30 bg-amber-500/5 p-3">
          <button @click="showAnomalias = !showAnomalias" class="w-full flex items-center justify-between text-amber-400 text-xs font-bold uppercase tracking-widest">
            <span><i class="fas fa-triangle-exclamation mr-2"></i>{{ anomalias.length }} anomalía(s) detectada(s)</span>
            <i class="fas fa-chevron-down transition-transform" :class="{ 'rotate-180': showAnomalias }"></i>
          </button>
          <div v-show="showAnomalias" class="mt-3 space-y-1 max-h-40 overflow-y-auto">
            <div v-for="(a, i) in anomalias" :key="i" class="text-[11px] text-amber-200/80 font-mono flex gap-2">
              <span class="font-bold text-amber-400 shrink-0">{{ a.tipo }}</span>
              <span class="truncate">{{ describirAnomalia(a) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tree -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-blue-900/10 scrollbar-thumb-blue-900/30 space-y-3">

        <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-blue-500">
          <i class="fas fa-spinner fa-spin text-4xl mb-4"></i>
          <p>Cargando entregas...</p>
        </div>

        <div v-else-if="clientesTree.length === 0" class="flex flex-col items-center justify-center py-20 text-blue-900/40">
          <i class="fas fa-truck-loading text-4xl mb-4"></i>
          <p>No hay datos para estos filtros</p>
        </div>

        <div v-for="cliente in clientesTree" :key="cliente.cliente_id || cliente.cliente"
          class="rounded-xl border border-blue-900/20 bg-[#070d24] overflow-hidden">

          <!-- Cliente header -->
          <button @click="toggleCliente(cliente.key)" class="w-full flex items-center justify-between px-4 py-3 hover:bg-blue-900/10 transition-colors">
            <div class="flex items-center gap-3 min-w-0">
              <i class="fas fa-chevron-right text-xs text-blue-500 transition-transform" :class="{ 'rotate-90': expandedClientes.has(cliente.key) }"></i>
              <span class="font-bold text-blue-50 text-sm truncate">{{ cliente.cliente }}</span>
              <span class="text-[10px] text-blue-400/40 font-mono">{{ cliente.ocs.length }} OC · {{ cliente.totalPedidos }} pedido(s)</span>
            </div>
            <div class="flex items-center gap-4 text-[11px] font-mono shrink-0">
              <span class="text-blue-200/60">Pend: <b class="text-amber-400">{{ fmt(cliente.totalPendiente) }}</b></span>
            </div>
          </button>

          <div v-show="expandedClientes.has(cliente.key)" class="border-t border-blue-900/10 divide-y divide-blue-900/10">
            <div v-for="oc in cliente.ocs" :key="oc.key" class="px-4 py-2">
              <div class="flex items-center gap-2 text-[11px] uppercase tracking-wider text-blue-400/70 font-bold py-1">
                <i class="fas fa-file-contract text-blue-500/50"></i>
                OC: {{ oc.oc }}
                <span v-if="ocConAnomalia(oc.oc)" class="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 text-[9px] normal-case tracking-normal font-bold">
                  <i class="fas fa-triangle-exclamation"></i> OC repetida en otro pedido
                </span>
              </div>

              <div class="grid grid-cols-12 gap-2 px-3 pt-1 pb-1 ml-4 text-[9px] font-bold uppercase tracking-widest text-blue-400/40">
                <div class="col-span-5">Producto</div>
                <div class="col-span-2 text-right">Pedido</div>
                <div class="col-span-2 text-right">Entregado</div>
                <div class="col-span-2 text-right">Pendiente</div>
                <div class="col-span-1"></div>
              </div>

              <div v-for="pedido in oc.pedidos" :key="pedido.pedido_id" class="ml-4 mb-2 rounded-lg bg-black/20 border border-blue-900/10">
                <div class="flex items-center justify-between px-3 py-2 text-xs">
                  <span class="text-blue-100 font-semibold">Pedido #{{ pedido.pedido_id }}</span>
                  <span class="text-blue-400/40 font-mono">{{ formatDate(pedido.fecha_pedido) }}</span>
                </div>

                <div class="divide-y divide-blue-900/10">
                  <div v-for="prod in pedido.productos" :key="prod.pedido_item_id">
                    <div class="grid grid-cols-12 items-center gap-2 px-3 py-2 text-xs cursor-pointer hover:bg-blue-900/10"
                         @click="toggleProducto(prod.pedido_item_id)">
                      <div class="col-span-5 flex items-center gap-2 min-w-0">
                        <i class="fas fa-chevron-right text-[9px] text-blue-500/50 transition-transform shrink-0"
                           :class="{ 'rotate-90': expandedProductos.has(prod.pedido_item_id) }"></i>
                        <span class="truncate text-blue-50">{{ prod.producto }}</span>
                        <span v-if="prod.sobreEntrega" class="px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 text-[9px] font-bold shrink-0">SOBRE-ENTREGA</span>
                      </div>
                      <div class="col-span-2 text-right font-mono text-blue-200/70">{{ fmt(prod.cantidad_pedida) }}</div>
                      <div class="col-span-2 text-right font-mono" :class="prod.sobreEntrega ? 'text-red-400 font-bold' : 'text-emerald-400'">{{ fmt(prod.entregado) }}</div>
                      <div class="col-span-2 text-right font-mono" :class="prod.pendiente > 0 ? 'text-amber-400 font-bold' : 'text-blue-900/40'">{{ fmt(prod.pendiente) }}</div>
                      <div class="col-span-1 text-right text-blue-900/40">
                        <i class="fas fa-truck text-[9px]" v-if="prod.remitos.length"></i>
                      </div>
                    </div>

                    <div v-show="expandedProductos.has(prod.pedido_item_id)" class="bg-black/30 px-3 py-2">
                      <div v-if="prod.remitos.length === 0" class="text-[10px] text-blue-900/50 italic pl-5">Sin entregas todavía</div>
                      <div v-for="(r, i) in prod.remitos" :key="i" class="flex items-center gap-3 pl-5 py-1 text-[11px] font-mono">
                        <i class="fas fa-truck text-blue-500/40 text-[9px]"></i>
                        <span class="text-blue-300 w-40 truncate">{{ r.remito || 'BORRADOR' }}</span>
                        <span class="text-blue-900/50 w-24">{{ formatDate(r.fecha_documento) }}</span>
                        <span class="text-emerald-400 w-16 text-right">{{ fmt(r.cantidad) }}</span>
                        <span class="text-blue-200/40 truncate">{{ r.factura || 'sin factura' }}</span>
                        <span v-if="r.remito_estado === 'ANULADO'" class="px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 text-[9px] font-bold">ANULADO</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'

const notification = useNotificationStore()

const loading = ref(false)
const filas = ref([])
const anomalias = ref([])
const searchQuery = ref('')
const showAnomalias = ref(false)
const expandedClientes = ref(new Set())
const expandedProductos = ref(new Set())

const filtros = reactive({
  desde: '',
  hasta: '',
  incluir_anulados: false,
})

const cargar = async () => {
  loading.value = true
  try {
    const params = {}
    if (filtros.desde) params.desde = filtros.desde
    if (filtros.hasta) params.hasta = filtros.hasta
    if (filtros.incluir_anulados) params.incluir_anulados = true

    const res = await api.get('/remitos/entregas', { params })
    filas.value = res.data.filas || []
    anomalias.value = res.data.anomalias || []
  } catch (e) {
    console.error(e)
    notification.add('Error cargando el reporte de entregas: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    loading.value = false
  }
}

watch(() => [filtros.desde, filtros.hasta, filtros.incluir_anulados], cargar)

const sobreEntregaPedidoItems = computed(() => {
  const set = new Set()
  for (const a of anomalias.value) {
    if (a.tipo === 'SOBRE_ENTREGA') set.add(a.pedido_item_id)
  }
  return set
})

const ocsRepetidas = computed(() => {
  const set = new Set()
  for (const a of anomalias.value) {
    if (a.tipo === 'OC_EN_VARIOS_PEDIDOS') set.add(a.oc)
  }
  return set
})

const ocConAnomalia = (oc) => ocsRepetidas.value.has((oc || '').trim().toUpperCase())

const filasFiltradas = computed(() => {
  if (!searchQuery.value) return filas.value
  const q = searchQuery.value.toLowerCase()
  return filas.value.filter(f =>
    (f.cliente || '').toLowerCase().includes(q) ||
    (f.oc || '').toLowerCase().includes(q) ||
    (f.producto || '').toLowerCase().includes(q)
  )
})

const clientesTree = computed(() => {
  const clientesMap = new Map()

  for (const f of filasFiltradas.value) {
    const cKey = f.cliente_id || `sin-cliente-${f.cliente || 'x'}`
    if (!clientesMap.has(cKey)) {
      clientesMap.set(cKey, { key: cKey, cliente_id: f.cliente_id, cliente: f.cliente || 'Sin cliente', ocsMap: new Map() })
    }
    const cNode = clientesMap.get(cKey)

    const ocKey = (f.oc || '').trim().toUpperCase() || '(SIN OC)'
    if (!cNode.ocsMap.has(ocKey)) {
      cNode.ocsMap.set(ocKey, { key: ocKey, oc: f.oc || '(sin OC)', pedidosMap: new Map() })
    }
    const ocNode = cNode.ocsMap.get(ocKey)

    if (!ocNode.pedidosMap.has(f.pedido_id)) {
      ocNode.pedidosMap.set(f.pedido_id, { pedido_id: f.pedido_id, fecha_pedido: f.fecha_pedido, productosMap: new Map() })
    }
    const pNode = ocNode.pedidosMap.get(f.pedido_id)

    if (!pNode.productosMap.has(f.pedido_item_id)) {
      pNode.productosMap.set(f.pedido_item_id, {
        pedido_item_id: f.pedido_item_id,
        producto: f.producto,
        cantidad_pedida: f.cantidad_pedida,
        remitos: [],
      })
    }
    const prodNode = pNode.productosMap.get(f.pedido_item_id)
    if (f.remito) {
      prodNode.remitos.push({
        remito: f.remito,
        fecha_documento: f.fecha_documento,
        cantidad: f.cantidad_remitida,
        factura: f.factura,
        remito_estado: f.remito_estado,
      })
    }
  }

  const clientes = []
  for (const cNode of clientesMap.values()) {
    let totalPendiente = 0
    let totalPedidos = 0
    const ocs = []
    for (const ocNode of cNode.ocsMap.values()) {
      const pedidos = []
      for (const pNode of ocNode.pedidosMap.values()) {
        totalPedidos++
        const productos = []
        for (const prod of pNode.productosMap.values()) {
          const entregado = prod.remitos.reduce((s, r) => s + (r.cantidad || 0), 0)
          const pendiente = Math.max(prod.cantidad_pedida - entregado, 0)
          totalPendiente += pendiente
          productos.push({
            ...prod,
            entregado,
            pendiente,
            sobreEntrega: sobreEntregaPedidoItems.value.has(prod.pedido_item_id),
          })
        }
        pedidos.push({ ...pNode, productos })
      }
      ocs.push({ ...ocNode, pedidos })
    }
    clientes.push({ ...cNode, ocs, totalPendiente, totalPedidos })
  }

  clientes.sort((a, b) => a.cliente.localeCompare(b.cliente, 'es'))
  return clientes
})

const toggleCliente = (key) => {
  if (expandedClientes.value.has(key)) expandedClientes.value.delete(key)
  else expandedClientes.value.add(key)
}

const toggleProducto = (id) => {
  if (expandedProductos.value.has(id)) expandedProductos.value.delete(id)
  else expandedProductos.value.add(id)
}

const fmt = (n) => {
  if (n === null || n === undefined) return '-'
  return Number(n).toLocaleString('es-AR', { maximumFractionDigits: 2 })
}

const formatDate = (dateString) => {
  // [FIX] new Date('2026-09-15') sin hora se interpreta como UTC y en AR (UTC-3)
  // muestra el día anterior. Parseamos a mano en vez de dejarlo en manos de Date().
  if (!dateString) return '-'
  const [y, m, d] = dateString.split('T')[0].split('-')
  if (!y || !m || !d) return '-'
  return `${d}/${m}/${y.slice(2)}`
}

const describirAnomalia = (a) => {
  switch (a.tipo) {
    case 'REMITO_SIN_RENGLONES': return `Remito ${a.remito || a.remito_id} no tiene ítems cargados`
    case 'REMITO_SIN_PEDIDO': return `Remito ${a.remito || a.remito_id} apunta a un pedido inexistente (#${a.pedido_id})`
    case 'NUMERO_LEGAL_DUPLICADO': return `Número ${a.numero_legal} repetido en ${a.remito_ids.length} remitos`
    case 'SOBRE_ENTREGA': return `Pedido #${a.pedido_id}: ${a.detalle}`
    case 'OC_EN_VARIOS_PEDIDOS': return `OC ${a.oc} aparece en los pedidos ${a.pedido_ids.join(', ')}`
    default: return JSON.stringify(a)
  }
}

onMounted(cargar)
</script>

<style scoped>
.tokyo-bg {
    background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.05), transparent),
                radial-gradient(circle at bottom left, rgba(37, 99, 235, 0.05), transparent);
}
.neon-blue {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.1), inset 0 0 20px rgba(59, 130, 246, 0.05);
}
</style>
