// [IDENTIDAD] - frontend\src\views\Pedidos\ConciliarFacturaView.vue
// [Etapa 7b] Conciliar una factura de ARCA contra el/los PR que ya existen. Camino nuevo; la
// ingesta vieja (crea pedido/remito/espejo) sigue viva al lado hasta que esta funcione en la
// operación real. Ver PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md §9 y DISENO_CIRCUITO_PR_S869.md §5-§7.
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans rounded-2xl border-2 border-emerald-500/40 p-6">
    <main class="flex flex-1 flex-col min-w-0 gap-4 overflow-y-auto pr-1">

      <header class="shrink-0 flex flex-wrap gap-4 items-center justify-between border-b border-emerald-900/30 pb-4">
        <div>
          <h1 class="font-outfit text-xl font-semibold text-white"><i class="fas fa-scale-balanced mr-2 text-emerald-400"></i>Conciliar factura contra PR</h1>
          <p class="text-xs text-emerald-400/50 font-medium uppercase tracking-wider">La factura cierra un PR que ya existe — no crea pedido ni remito</p>
        </div>
        <button @click="$router.push({ name: 'IngestaFactura' })" class="text-xs text-slate-400 hover:text-white">
          <i class="fas fa-arrow-left mr-1"></i> Volver a Ingesta
        </button>
      </header>

      <div v-if="loading" class="text-center py-10 text-emerald-400"><i class="fas fa-spinner fa-spin mr-2"></i>Leyendo la factura...</div>

      <template v-else-if="cand">
        <!-- FACTURA (lo que manda ARCA) -->
        <section class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-xs">
          <div><span class="block text-[10px] uppercase text-slate-500 font-bold">Comprobante</span>
            <span class="font-mono text-white text-sm">{{ cand.factura.tipo_comprobante || '¿?' }} {{ cand.factura.numero }}</span></div>
          <div><span class="block text-[10px] uppercase text-slate-500 font-bold">Emitida</span>
            <span class="font-mono text-white">{{ cand.factura.fecha_emision || '—' }}</span></div>
          <div><span class="block text-[10px] uppercase text-slate-500 font-bold">CUIT comprador</span>
            <span class="font-mono text-white">{{ cand.factura.cuit || '—' }}</span></div>
          <div><span class="block text-[10px] uppercase text-slate-500 font-bold">Total</span>
            <span class="font-mono text-emerald-300 text-sm">{{ moneda(cand.factura.total_final) }}</span></div>
          <div class="col-span-2 md:col-span-4 text-[10px] text-slate-500">
            Razón social según ARCA: <span class="text-slate-400">{{ cand.factura.razon_social_arca || '—' }}</span>
            (solo referencia: se concilia por CUIT, nunca por razón social) · CAE {{ cand.factura.cae || '—' }}
          </div>
        </section>

        <ul v-if="bloqueosVisibles.length" class="space-y-1">
          <li v-for="(b, i) in bloqueosVisibles" :key="'b' + i" class="text-xs bg-red-900/30 border border-red-600/40 text-red-300 rounded-lg px-3 py-2">
            <i class="fas fa-ban mr-1"></i>{{ b }}
          </li>
        </ul>
        <ul v-if="cand.avisos.length" class="space-y-1">
          <li v-for="(a, i) in cand.avisos" :key="'a' + i" class="text-xs bg-amber-900/20 border border-amber-600/30 text-amber-300 rounded-lg px-3 py-2">
            <i class="fas fa-circle-exclamation mr-1"></i>{{ a }}
          </li>
        </ul>

        <!-- PR CANDIDATOS -->
        <section v-if="cand.prs.length" class="space-y-2">
          <h2 class="text-sm font-bold text-white">1 · Elegí contra qué PR cierra esta factura</h2>
          <label v-for="p in cand.prs" :key="p.remito_id"
            class="flex gap-3 items-start bg-slate-800/40 border rounded-xl p-3 cursor-pointer transition-colors"
            :class="seleccion.has(p.remito_id) ? 'border-emerald-500/60' : 'border-slate-700 hover:border-slate-500'">
            <input type="checkbox" class="mt-1 accent-emerald-500" :checked="seleccion.has(p.remito_id)" @change="togglePr(p.remito_id)" />
            <div class="flex-1 min-w-0 text-xs">
              <div class="flex flex-wrap gap-3 text-white">
                <span class="font-mono font-bold">{{ p.numero_legal || 'PR sin numerar' }}</span>
                <span class="text-slate-400">Pedido #{{ p.pedido_id }}</span>
                <span v-if="p.pedido_oc" class="text-slate-400">OC {{ p.pedido_oc }}</span>
                <span class="text-slate-500">{{ p.estado }}</span>
                <span class="text-slate-500">{{ (p.fecha_creacion || '').slice(0, 10) }}</span>
              </div>
              <div class="mt-1 text-slate-400">
                <span v-for="r in p.renglones" :key="r.remito_item_id" class="inline-block mr-3">
                  {{ r.producto }} <b class="text-slate-200">{{ r.pendiente_facturar }}</b>
                </span>
              </div>
            </div>
          </label>
          <button @click="evaluar(null)" :disabled="!seleccion.size || evaluando"
            class="px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-xs font-bold uppercase tracking-wide">
            <i class="fas" :class="evaluando ? 'fa-spinner fa-spin' : 'fa-magnifying-glass'"></i> Comparar
          </button>
        </section>

        <!-- EMPAREJAMIENTO + DIFERENCIAS -->
        <section v-if="ev" class="space-y-3">
          <h2 class="text-sm font-bold text-white">2 · Renglón por renglón</h2>
          <table class="w-full text-xs">
            <thead>
              <tr class="text-[10px] uppercase text-slate-500 border-b border-slate-700">
                <th class="text-left py-1 pr-2">Factura (ARCA)</th>
                <th class="text-right py-1 px-2">Cant.</th>
                <th class="text-right py-1 px-2">Precio</th>
                <th class="text-left py-1 pl-2">Renglón del PR</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(it, i) in ev.factura.items" :key="i" class="border-b border-slate-800">
                <td class="py-1.5 pr-2 text-slate-200">{{ it.descripcion }}</td>
                <td class="py-1.5 px-2 text-right font-mono">{{ it.cantidad }}</td>
                <td class="py-1.5 px-2 text-right font-mono">{{ moneda(it.precio_unitario) }}</td>
                <td class="py-1.5 pl-2">
                  <div class="flex items-center gap-2">
                    <select :value="parDe(i) ?? ''" @change="cambiarPar(i, $event.target.value)"
                      class="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs text-white w-full max-w-xs">
                      <option value="">— sin par (no está en el PR) —</option>
                      <option v-for="r in ev.renglones_pr" :key="r.remito_item_id" :value="r.remito_item_id">
                        {{ r.producto }} · pendiente {{ r.pendiente_facturar }}
                      </option>
                    </select>
                    <span v-if="comoDe(i)" class="text-[9px] uppercase px-1.5 py-0.5 rounded bg-slate-700 text-slate-300">{{ comoDe(i) }}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <ul class="space-y-1">
            <li v-for="(d, i) in ev.diferencias" :key="'d' + i" class="text-xs rounded-lg px-3 py-2 border flex gap-2" :class="claseEstilo(d.clase)">
              <span class="font-bold shrink-0 w-16">{{ etiqueta(d.clase) }}</span>
              <span>{{ d.detalle }}</span>
            </li>
          </ul>
          <p v-if="hayClaseB" class="text-[11px] text-amber-400/80">
            Las diferencias clase B no frenan: la factura se registra igual, queda una nota [SISTEMA] en el PR y el desfase
            se ve en la resta (facturado ≠ remitido) hasta que llegue la nota de crédito o débito.
          </p>

          <button @click="confirmar" :disabled="!!ev.bloqueos.length || confirmando"
            class="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm font-bold">
            <i class="fas" :class="confirmando ? 'fa-spinner fa-spin' : 'fa-check'"></i> Confirmar conciliación
          </button>
        </section>

        <!-- RESULTADO -->
        <section v-if="resultado" class="bg-emerald-900/20 border border-emerald-500/40 rounded-xl p-4 text-sm text-emerald-200">
          <i class="fas fa-circle-check mr-2 text-emerald-400"></i>
          Registrada {{ resultado.tipo_comprobante }} {{ resultado.numero }} y vinculada a {{ resultado.remito_ids.length }} PR.
        </section>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'

const route = useRoute()
const notification = useNotificationStore()
const rawId = route.params.rawId

const loading = ref(true)
const cand = ref(null)
const seleccion = ref(new Set())
const ev = ref(null)
const emparejamiento = ref(null)
const evaluando = ref(false)
const confirmando = ref(false)
const resultado = ref(null)

const bloqueosVisibles = computed(() => (ev.value ? ev.value.bloqueos : cand.value?.bloqueos) || [])
const hayClaseB = computed(() => ev.value?.diferencias.some(d => d.clase === 'B'))

const moneda = (v) => (v == null ? '—' : Number(v).toLocaleString('es-AR', { style: 'currency', currency: 'ARS' }))
const ESTILOS = {
  A: 'bg-sky-900/20 border-sky-600/30 text-sky-200',
  B: 'bg-amber-900/25 border-amber-500/40 text-amber-200',
  C: 'bg-red-900/30 border-red-600/40 text-red-200',
  PARCIAL: 'bg-slate-800/60 border-slate-600/40 text-slate-300',
  AVISO: 'bg-amber-900/10 border-amber-700/30 text-amber-300/80',
}
const ETIQUETAS = { A: 'Clase A', B: 'Clase B', C: 'Clase C', PARCIAL: 'Parcial', AVISO: 'Aviso' }
const claseEstilo = (c) => ESTILOS[c] || ESTILOS.AVISO
const etiqueta = (c) => ETIQUETAS[c] || c

const parDe = (i) => emparejamiento.value?.find(e => e.item_pdf === i)?.remito_item_id ?? null
const comoDe = (i) => emparejamiento.value?.find(e => e.item_pdf === i)?.como ?? null

const error = (e, pref) => notification.add(pref + ': ' + (e.response?.data?.detail || e.message), 'error')

const cargar = async () => {
  loading.value = true
  try {
    cand.value = (await api.get(`/ingesta/raw/${rawId}/conciliacion/candidatos`)).data
  } catch (e) {
    error(e, 'No se pudo leer la factura')
  } finally {
    loading.value = false
  }
}

const togglePr = (id) => {
  if (seleccion.value.has(id)) seleccion.value.delete(id)
  else seleccion.value.add(id)
  ev.value = null
  emparejamiento.value = null
}

const evaluar = async (emp) => {
  evaluando.value = true
  try {
    const body = { remito_ids: [...seleccion.value] }
    if (emp) body.emparejamiento = emp
    ev.value = (await api.post(`/ingesta/raw/${rawId}/conciliacion/evaluar`, body)).data
    emparejamiento.value = ev.value.emparejamiento
  } catch (e) {
    error(e, 'No se pudo comparar')
  } finally {
    evaluando.value = false
  }
}

const cambiarPar = (i, valor) => {
  const nuevo = emparejamiento.value.map(e =>
    e.item_pdf === i ? { item_pdf: i, remito_item_id: valor === '' ? null : Number(valor), como: 'operador' } : e)
  evaluar(nuevo.map(({ item_pdf, remito_item_id }) => ({ item_pdf, remito_item_id })))
}

const confirmar = async () => {
  confirmando.value = true
  try {
    const body = {
      remito_ids: [...seleccion.value],
      emparejamiento: emparejamiento.value.map(({ item_pdf, remito_item_id }) => ({ item_pdf, remito_item_id })),
    }
    resultado.value = (await api.post(`/ingesta/raw/${rawId}/conciliacion/confirmar`, body)).data
    notification.add(`Factura ${resultado.value.numero} conciliada`, 'success')
    ev.value = null
    await cargar()
  } catch (e) {
    error(e, 'No se pudo conciliar')
  } finally {
    confirmando.value = false
  }
}

onMounted(cargar)
</script>
