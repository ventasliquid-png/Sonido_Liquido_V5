// [IDENTIDAD] - frontend\src\views\Facturas\FacturasView.vue
// [S899, Card #212; Carlos 04/11: «Tomy no sabe si ya ingestó, por ejemplo, la 2612… Deberías poner un Menú "Facturas" a la izquierda a nivel Remito o Pedido o Productos,
// para que desde ahí se acceda a ese listado y esos 3 botones»] Qué facturas de ARCA están en V5, cuáles se subieron sin terminar y cuáles faltan.
// Cada número de comprobante sale en UN solo botón. Los huecos se cuentan desde la 2600 (decisión de Carlos). Ver backend/ingesta/facturas_panorama.py.
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans rounded-2xl border-2 border-violet-500/40 p-6" data-test="pantalla-facturas">
    <main class="flex flex-1 flex-col min-w-0 gap-4 overflow-y-auto pr-1">

      <header class="shrink-0 flex flex-wrap gap-4 items-center justify-between border-b border-violet-900/30 pb-4">
        <div>
          <h1 class="font-outfit text-xl font-semibold text-white"><i class="fas fa-file-invoice-dollar mr-2 text-violet-400"></i>Facturas</h1>
          <p class="text-xs text-violet-400/60 font-medium uppercase tracking-wider">Qué facturas de ARCA están en V5, cuáles se subieron sin terminar y cuáles faltan</p>
        </div>
        <div class="flex items-center gap-2">
          <button type="button" @click="cargar" data-test="recargar" class="px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs font-bold">
            <i class="fas fa-rotate mr-1" :class="{ 'fa-spin': cargando }"></i>Actualizar
          </button>
          <button type="button" @click="$router.push({ name: 'IngestaFactura' })" data-test="subir-factura"
            class="px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold">
            <i class="fas fa-file-import mr-1"></i>Subir una factura
          </button>
        </div>
      </header>

      <div v-if="error" class="shrink-0 rounded-lg border border-red-500/40 bg-red-900/20 text-red-200 text-xs p-3" data-test="error">{{ error }}</div>

      <!-- Buscador: un número («2612») o parte del cliente. Si lo que buscás está en otro botón, salta solo. -->
      <div class="shrink-0 flex items-center gap-3">
        <div class="relative flex-1 max-w-md">
          <i class="fas fa-search absolute left-3 top-2.5 text-slate-500 text-xs"></i>
          <input v-model="filtro" type="text" data-test="buscar" placeholder="Buscá un número (ej. 2612) o un cliente"
            class="w-full bg-slate-800/60 border border-slate-600 rounded-lg pl-8 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-400" />
        </div>
        <button v-if="filtro" type="button" @click="filtro = ''" class="text-xs text-slate-400 hover:text-white">Borrar</button>
      </div>

      <!-- Los tres botones -->
      <div class="shrink-0 grid grid-cols-1 sm:grid-cols-3 gap-3" role="tablist">
        <button type="button" role="tab" data-test="boton-cargadas" @click="tab = 'cargadas'"
          class="text-left rounded-xl border-2 p-3 transition-colors"
          :class="tab === 'cargadas' ? 'border-emerald-400 bg-emerald-900/30' : 'border-slate-700 bg-slate-800/40 hover:bg-slate-800'">
          <span class="block text-[10px] uppercase font-bold tracking-wider text-emerald-400">Cargadas</span>
          <span class="block text-2xl font-black text-white" data-test="cuenta-cargadas">{{ cargadasVistas.length }}</span>
          <span class="block text-[11px] text-slate-400">ya están en V5, con su pedido y remito</span>
        </button>
        <button type="button" role="tab" data-test="boton-sin-terminar" @click="tab = 'sin_terminar'"
          class="text-left rounded-xl border-2 p-3 transition-colors"
          :class="tab === 'sin_terminar' ? 'border-amber-400 bg-amber-900/30' : (sinTerminarVistas.length ? 'border-amber-500/50 bg-amber-900/10 hover:bg-amber-900/20' : 'border-slate-700 bg-slate-800/40 hover:bg-slate-800')">
          <span class="block text-[10px] uppercase font-bold tracking-wider text-amber-400">Subidas sin terminar</span>
          <span class="block text-2xl font-black text-white" data-test="cuenta-sin-terminar">{{ sinTerminarVistas.length }}</span>
          <span class="block text-[11px] text-slate-400">se subió el PDF pero la factura no se registró</span>
        </button>
        <button type="button" role="tab" data-test="boton-faltan" @click="tab = 'faltan'"
          class="text-left rounded-xl border-2 p-3 transition-colors"
          :class="tab === 'faltan' ? 'border-red-400 bg-red-900/30' : (faltanVistas.length ? 'border-red-500/50 bg-red-900/10 hover:bg-red-900/20' : 'border-slate-700 bg-slate-800/40 hover:bg-slate-800')">
          <span class="block text-[10px] uppercase font-bold tracking-wider text-red-400">Faltan</span>
          <span class="block text-2xl font-black text-white" data-test="cuenta-faltan">{{ faltanVistas.length }}</span>
          <span class="block text-[11px] text-slate-400">números de ARCA que nunca se subieron</span>
        </button>
      </div>

      <div v-if="cargando && !datos" class="text-center py-10 text-violet-400"><i class="fas fa-spinner fa-spin mr-2"></i>Leyendo las facturas...</div>

      <template v-else-if="datos">
        <!-- CARGADAS -->
        <section v-if="tab === 'cargadas'" data-test="lista-cargadas" class="bg-slate-800/40 border border-slate-700 rounded-xl p-4 text-xs space-y-2 overflow-x-auto">
          <p class="text-slate-400">Facturas registradas en V5, la más nueva arriba. <b class="text-slate-300">Ver PDF</b> abre la factura original que se subió.</p>
          <p v-if="!cargadasVistas.length" class="py-6 text-center text-slate-500" data-test="vacio-cargadas">{{ filtro ? 'Ninguna factura cargada coincide con la búsqueda.' : 'Todavía no hay facturas cargadas desde el corte.' }}</p>
          <table v-else class="w-full">
            <thead>
              <tr class="text-[10px] uppercase text-slate-500 border-b border-slate-700">
                <th class="text-left py-1 pr-2">Comprobante</th>
                <th class="text-left py-1 px-2">Fecha</th>
                <th class="text-left py-1 px-2">Cliente</th>
                <th class="text-right py-1 px-2">Total</th>
                <th class="text-left py-1 px-2">Pedido</th>
                <th class="text-left py-1 px-2">Remito</th>
                <th class="text-right py-1 pl-2">PDF</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="f in cargadasVistas" :key="f.factura_id" class="border-b border-slate-800" data-test="fila-cargada">
                <td class="py-1.5 pr-2 whitespace-nowrap"><span class="text-slate-400">{{ f.tipo_texto }}</span> <span class="font-mono text-white">{{ f.numero_legal }}</span></td>
                <td class="py-1.5 px-2 font-mono whitespace-nowrap">{{ fecha(f.fecha_emision) }}</td>
                <td class="py-1.5 px-2 max-w-[18rem] truncate" :title="f.cliente">{{ f.cliente || '—' }}</td>
                <td class="py-1.5 px-2 text-right font-mono text-emerald-300 whitespace-nowrap">{{ moneda(f.total) }}</td>
                <td class="py-1.5 px-2">
                  <button v-if="f.pedido_id" type="button" @click="$router.push({ name: 'PedidoEditar', params: { id: f.pedido_id } })" class="text-violet-300 hover:text-white underline font-mono">#{{ f.pedido_id }}</button>
                  <span v-else class="text-slate-500">—</span>
                </td>
                <td class="py-1.5 px-2">
                  <template v-if="f.remitos.length">
                    <button v-for="r in f.remitos" :key="r.id" type="button" @click="$router.push({ name: 'RemitoFicha', params: { ref: r.numero_legal || r.id } })"
                      class="mr-2 text-violet-300 hover:text-white underline font-mono">{{ r.numero_legal }}</button>
                  </template>
                  <span v-else class="text-slate-500">—</span>
                </td>
                <td class="py-1.5 pl-2 text-right">
                  <a v-if="f.raw_id" :href="pdfUrl(f.raw_id)" target="_blank" rel="noopener" data-test="pdf-cargada"
                    class="px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-white text-[10px] font-bold uppercase"><i class="fas fa-file-pdf mr-1"></i>Ver PDF</a>
                  <span v-else class="text-slate-600" title="Esta factura se registró sin pasar por la subida de PDF">sin PDF</span>
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- SUBIDAS SIN TERMINAR -->
        <section v-if="tab === 'sin_terminar'" data-test="lista-sin-terminar" class="bg-slate-800/40 border border-amber-500/30 rounded-xl p-4 text-xs space-y-2 overflow-x-auto">
          <p class="text-slate-400">Se subió el PDF pero <b class="text-amber-300">la factura no quedó registrada en V5</b>. Apretá <b class="text-slate-300">Seguir</b> para conciliarla contra su remito. Si el mismo PDF se subió varias veces cuenta una sola vez.</p>
          <p v-if="!sinTerminarVistas.length" class="py-6 text-center text-slate-500" data-test="vacio-sin-terminar">{{ filtro ? 'Ninguna subida sin terminar coincide con la búsqueda.' : 'No hay ninguna factura subida a medias. 👍' }}</p>
          <table v-else class="w-full">
            <thead>
              <tr class="text-[10px] uppercase text-slate-500 border-b border-slate-700">
                <th class="text-left py-1 pr-2">Comprobante</th>
                <th class="text-left py-1 px-2">Cliente (según ARCA)</th>
                <th class="text-right py-1 px-2">Total</th>
                <th class="text-left py-1 px-2">Subida</th>
                <th class="text-left py-1 px-2">Estado</th>
                <th class="text-right py-1 pl-2">Qué hacer</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in sinTerminarVistas" :key="s.raw_id" class="border-b border-slate-800" data-test="fila-sin-terminar">
                <td class="py-1.5 pr-2 whitespace-nowrap"><span class="text-slate-400">{{ s.tipo_texto }}</span> <span class="font-mono text-white">{{ s.numero_legal }}</span></td>
                <td class="py-1.5 px-2 max-w-[18rem] truncate" :title="s.cliente">{{ s.cliente || '—' }}</td>
                <td class="py-1.5 px-2 text-right font-mono text-amber-200 whitespace-nowrap">{{ moneda(s.total) }}</td>
                <td class="py-1.5 px-2 whitespace-nowrap">{{ fechaHora(s.subida) }}
                  <span v-if="s.veces > 1" class="ml-1 px-1.5 py-0.5 rounded-full bg-slate-700 text-slate-300 text-[10px]" :title="'Se subió ' + s.veces + ' veces'">×{{ s.veces }}</span></td>
                <td class="py-1.5 px-2"><span class="px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-200 text-[10px] font-bold" :title="s.warning || ''">{{ s.estado_texto }}</span></td>
                <td class="py-1.5 pl-2 text-right whitespace-nowrap">
                  <button type="button" @click="$router.push({ name: 'ConciliarFactura', params: { rawId: s.raw_id } })" data-test="seguir"
                    class="px-2.5 py-1 rounded bg-amber-500 hover:bg-amber-400 text-slate-900 text-[11px] font-black uppercase mr-1"><i class="fas fa-scale-balanced mr-1"></i>Seguir</button>
                  <a :href="pdfUrl(s.raw_id)" target="_blank" rel="noopener" data-test="pdf-sin-terminar"
                    class="px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-white text-[10px] font-bold uppercase"><i class="fas fa-file-pdf mr-1"></i>Ver PDF</a>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="datos.resumen.repetidas_ignoradas && !filtro" class="text-[10px] text-slate-500" data-test="repetidas-ignoradas">Además hay {{ datos.resumen.repetidas_ignoradas }} subida(s) repetida(s) de facturas que ya están cargadas: no cuentan.</p>
        </section>

        <!-- FALTAN -->
        <section v-if="tab === 'faltan'" data-test="lista-faltan" class="bg-slate-800/40 border border-red-500/30 rounded-xl p-4 text-xs space-y-2 overflow-x-auto">
          <p class="text-slate-400">Números de ARCA que <b class="text-red-300">no están en V5 ni se subieron</b>, aunque hay otros posteriores (la numeración es correlativa, así que el hueco delata la que falta). Si la factura existe, subila; si no se carga a propósito, marcala con su motivo.</p>
          <p v-if="!faltanVistas.length" class="py-6 text-center text-slate-500" data-test="vacio-faltan">{{ filtro ? 'Ningún faltante coincide con la búsqueda.' : 'No falta ningún número. 👍' }}</p>
          <table v-else class="w-full">
            <thead>
              <tr class="text-[10px] uppercase text-slate-500 border-b border-slate-700">
                <th class="text-left py-1 pr-2">Comprobante</th>
                <th class="text-left py-1 px-2">Está entre</th>
                <th class="text-right py-1 pl-2">Qué hacer</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="h in faltanVistas" :key="h.tipo + h.numero_legal">
                <tr class="border-b border-slate-800" data-test="fila-falta">
                  <td class="py-1.5 pr-2 whitespace-nowrap"><span class="text-slate-400">{{ h.tipo_texto }}</span> <span class="font-mono text-white">{{ h.numero_legal }}</span></td>
                  <td class="py-1.5 px-2 text-slate-400">
                    <span v-if="h.anterior">la {{ h.anterior.numero }} ({{ fecha(h.anterior.fecha) }})</span><span v-else>—</span>
                    y
                    <span v-if="h.siguiente">la {{ h.siguiente.numero }} ({{ fecha(h.siguiente.fecha) }})</span><span v-else>—</span>
                  </td>
                  <td class="py-1.5 pl-2 text-right whitespace-nowrap">
                    <button type="button" @click="$router.push({ name: 'IngestaFactura' })"
                      class="px-2.5 py-1 rounded bg-violet-600 hover:bg-violet-500 text-white text-[11px] font-bold mr-1"><i class="fas fa-file-import mr-1"></i>Subirla</button>
                    <button type="button" @click="abrirMarca(h)" data-test="no-se-carga"
                      class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-white text-[11px] font-bold">No se carga</button>
                  </td>
                </tr>
                <tr v-if="marcando && marcando.numero_legal === h.numero_legal && marcando.tipo === h.tipo" class="border-b border-slate-800 bg-slate-900/60">
                  <td colspan="3" class="py-2 px-2">
                    <div class="flex flex-wrap items-center gap-2">
                      <span class="text-slate-300">¿Por qué no se carga la {{ h.numero_legal }}?</span>
                      <input v-model="motivo" type="text" data-test="motivo" placeholder="Ej.: factura de una OC que nunca se completó; la anuló la NC 74"
                        class="flex-1 min-w-[16rem] bg-slate-800 border border-slate-600 rounded px-2 py-1 text-white placeholder-slate-500 focus:outline-none focus:border-violet-400" @keyup.enter="confirmarMarca" />
                      <button type="button" @click="confirmarMarca" :disabled="!motivo.trim() || guardando" data-test="confirmar-marca"
                        class="px-3 py-1 rounded bg-red-600 hover:bg-red-500 disabled:opacity-40 text-white font-bold">Dejar anotado</button>
                      <button type="button" @click="marcando = null" class="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 text-white">Cancelar</button>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>

          <!-- Las que ya se decidió no cargar: no cuentan como hueco -->
          <div v-if="datos.no_se_cargan.length" class="pt-3 mt-2 border-t border-slate-700" data-test="no-se-cargan">
            <h3 class="text-[10px] uppercase font-bold text-slate-500 mb-1">No se cargan a propósito (no cuentan como faltantes)</h3>
            <ul class="space-y-1">
              <li v-for="m in datos.no_se_cargan" :key="m.id" class="flex flex-wrap items-start gap-2">
                <span class="font-mono text-slate-300 whitespace-nowrap">{{ m.tipo_texto }} {{ m.numero_legal }}</span>
                <span class="flex-1 min-w-[12rem] text-slate-400">{{ m.motivo }}<span v-if="m.decidido_por" class="text-slate-600"> — {{ m.decidido_por }}</span></span>
                <button type="button" @click="deshacerMarca(m)" data-test="deshacer-marca" class="text-[10px] text-slate-500 hover:text-white underline">Deshacer</button>
              </li>
            </ul>
          </div>
        </section>

        <p class="shrink-0 text-[10px] text-slate-500 leading-relaxed" data-test="nota-limite">
          Los faltantes se cuentan desde: <span v-for="(c, i) in datos.corte" :key="c.tipo"><b class="text-slate-400">{{ c.tipo_texto }} {{ c.desde_legal }}</b><span v-if="i < datos.corte.length - 1">, </span></span>; lo anterior es histórico y no se muestra.
          V5 no ve ARCA: una factura emitida <i>después</i> de la última que se subió no aparece acá hasta que llegue una posterior.
        </p>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'
import { normalizarBusqueda } from '@/utils/texto'   // [S892] búsqueda sin acentos ni mayúsculas: «pineyro» encuentra «Piñeyro»

const notification = useNotificationStore()
const datos = ref(null)
const cargando = ref(false)
const error = ref('')
const tab = ref('cargadas')
const filtro = ref('')
const marcando = ref(null)    // el faltante al que se le está escribiendo el motivo
const motivo = ref('')
const guardando = ref(false)

const moneda = (v) => (v == null ? '—' : Number(v).toLocaleString('es-AR', { style: 'currency', currency: 'ARS' }))
const fecha = (s) => (s ? `${s.slice(8, 10)}/${s.slice(5, 7)}/${s.slice(0, 4)}` : '—')
// Las horas de la base están en UTC sin marca de zona: se pasan a la hora local del navegador.
const fechaHora = (s) => {
  if (!s) return '—'
  const d = new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(s) ? s : s + 'Z')
  if (isNaN(d.getTime())) return s
  return d.toLocaleString('es-AR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}
const pdfUrl = (rawId) => `/ingesta/raw/${rawId}/pdf`

// Búsqueda: por número (con o sin ceros: «2612», «00002612», «0001-00002612») o por parte del nombre del cliente.
const coincide = (x, q) => {
  const t = normalizarBusqueda(q)
  if (!t) return true
  const digitos = t.replace(/\D/g, '')
  if (digitos && x.numero != null && String(x.numero).includes(digitos.replace(/^0+/, '') || '0')) return true
  if (digitos && x.numero_legal && x.numero_legal.replace(/\D/g, '').includes(digitos)) return true
  return !!(x.cliente && normalizarBusqueda(x.cliente).includes(t))
}
const cargadasVistas = computed(() => (datos.value ? datos.value.cargadas.filter((x) => coincide(x, filtro.value)) : []))
const sinTerminarVistas = computed(() => (datos.value ? datos.value.sin_terminar.filter((x) => coincide(x, filtro.value)) : []))
const faltanVistas = computed(() => (datos.value ? datos.value.faltan.filter((x) => coincide(x, filtro.value)) : []))

// Si lo que se busca no está en el botón abierto pero sí en otro, se pasa a ese.
watch(filtro, (q) => {
  if (!q.trim() || !datos.value) return
  const por = { cargadas: cargadasVistas.value.length, sin_terminar: sinTerminarVistas.value.length, faltan: faltanVistas.value.length }
  if (!por[tab.value]) {
    const otro = ['sin_terminar', 'faltan', 'cargadas'].find((k) => por[k] > 0)
    if (otro) tab.value = otro
  }
})

const cargar = async () => {
  cargando.value = true
  error.value = ''
  try {
    const { data } = await api.get('/ingesta/facturas/panorama')
    datos.value = data
  } catch (e) {
    error.value = 'No se pudo leer el listado de facturas: ' + (e?.response?.data?.detail || e.message || 'error desconocido')
  } finally {
    cargando.value = false
  }
}

const abrirMarca = (h) => { marcando.value = h; motivo.value = '' }
const confirmarMarca = async () => {
  const h = marcando.value
  if (!h || !motivo.value.trim()) return
  guardando.value = true
  try {
    await api.post('/ingesta/facturas/no-se-carga', {
      tipo_comprobante: h.tipo, punto_venta: h.punto_venta, numero_comprobante: h.numero, motivo: motivo.value.trim(),
    })
    notification.add(`La ${h.numero_legal} queda anotada como «no se carga».`, 'success')
    marcando.value = null
    await cargar()
  } catch (e) {
    notification.add(e?.response?.data?.detail || 'No se pudo anotar.', 'error')
  } finally {
    guardando.value = false
  }
}
const deshacerMarca = async (m) => {
  try {
    await api.delete(`/ingesta/facturas/no-se-carga/${m.id}`)
    notification.add(`La ${m.numero_legal} vuelve a contar como faltante si sigue sin estar en V5.`, 'info')
    await cargar()
  } catch (e) {
    notification.add(e?.response?.data?.detail || 'No se pudo deshacer.', 'error')
  }
}

onMounted(cargar)
</script>
