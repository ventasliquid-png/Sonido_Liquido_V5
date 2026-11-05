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
          <h1 class="font-outfit text-xl font-semibold text-white"><i class="fas fa-scale-balanced mr-2 text-emerald-400"></i>{{ esAjuste ? 'Conciliar nota de crédito / débito' : 'Conciliar factura contra PR' }}</h1>
          <p class="text-xs text-emerald-400/50 font-medium uppercase tracking-wider">{{ esAjuste ? 'La nota ajusta una o varias facturas ya registradas — no cierra ningún PR' : 'La factura cierra un PR que ya existe — no crea pedido ni remito' }}</p>
        </div>
        <!-- [S899, Carlos 04/11: «que todo se maneje desde una misma pantalla»] si se llegó desde «Facturas», se vuelve a Facturas -->
        <button @click="$router.push({ name: vieneDeFacturas ? 'FacturasPanel' : 'IngestaFactura' })" class="text-xs text-slate-400 hover:text-white" data-test="volver">
          <i class="fas fa-arrow-left mr-1"></i> {{ vieneDeFacturas ? 'Volver a Facturas' : 'Volver a Ingesta' }}
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

        <!-- [S899, Carlos 04/11: «no tenemos un sistema que nos muestre las facturas ingeridas; debemos abrir el PDF en otra pestaña e ir conciliando contra el pedido»]
             La factura a la vista: sus renglones (lo que lee el sistema del PDF de ARCA) y el PDF original en la misma pantalla, para compararla contra el pedido de cada alternativa sin cambiar de pestaña. -->
        <section v-if="!resultado && !esAjuste && (cand.factura.items || []).length" class="bg-slate-800/40 border border-slate-700 rounded-xl p-4 text-xs space-y-2" data-test="renglones-factura">
          <div class="flex items-center justify-between gap-3">
            <h2 class="text-sm font-bold text-white">Renglones de la factura (ARCA)</h2>
            <button type="button" @click="pdfAbierto = !pdfAbierto" data-test="ver-pdf"
              class="px-3 py-1 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-[11px] font-bold uppercase tracking-wide">
              <i class="fas fa-file-pdf mr-1"></i>{{ pdfAbierto ? 'Ocultar PDF' : 'Ver PDF' }}
            </button>
          </div>
          <table class="w-full">
            <thead>
              <tr class="text-[10px] uppercase text-slate-500 border-b border-slate-700">
                <th class="text-left py-1 pr-2">Descripción</th>
                <th class="text-right py-1 px-2">Cant.</th>
                <th class="text-right py-1 px-2">Precio unit.</th>
                <th class="text-right py-1 pl-2">Subtotal neto</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(it, i) in cand.factura.items" :key="'fi' + i" class="border-b border-slate-800">
                <td class="py-1.5 pr-2 text-slate-200">{{ it.descripcion }}<span v-if="it.bonificacion" class="ml-2 text-amber-400">(bonif. {{ it.bonificacion }} %)</span></td>
                <td class="py-1.5 px-2 text-right font-mono">{{ it.cantidad }}</td>
                <td class="py-1.5 px-2 text-right font-mono">{{ moneda(it.precio_unitario) }}</td>
                <td class="py-1.5 pl-2 text-right font-mono">{{ moneda(it.subtotal) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="pdfAbierto" class="space-y-1" data-test="visor-pdf">
            <iframe :src="pdfSrc" class="w-full h-[70vh] rounded-lg border border-slate-700 bg-white" title="PDF de la factura"></iframe>
            <a :href="pdfSrc" target="_blank" rel="noopener" class="text-[10px] text-cyan-400 hover:text-cyan-300 underline">abrir el PDF en otra pestaña</a>
          </div>
        </section>

        <!-- [S898, Carlos 03/11] Ya conciliada, queda solo el cartel verde: el bloqueo (FACTURA_DUPLICADA) y el aviso (SIN_PR_PENDIENTE) los genera la propia factura recién registrada al releer los candidatos -->
        <ul v-if="!resultado && bloqueosVisibles.length" class="space-y-1">
          <li v-for="(b, i) in bloqueosVisibles" :key="'b' + i" class="text-xs bg-red-900/30 border border-red-600/40 text-red-300 rounded-lg px-3 py-2">
            <i class="fas fa-ban mr-1"></i>{{ b }}
          </li>
        </ul>
        <ul v-if="!resultado && cand.avisos.length" class="space-y-1">
          <li v-for="(a, i) in cand.avisos" :key="'a' + i" class="text-xs bg-amber-900/20 border border-amber-600/30 text-amber-300 rounded-lg px-3 py-2">
            <i class="fas fa-circle-exclamation mr-1"></i>{{ a }}
          </li>
        </ul>

        <!-- [Etapa 7d] NC / ND: se eligen FACTURAS (no PR) y se empareja renglón por renglón (solo NC) -->
        <template v-if="esAjuste && !resultado">
          <section class="space-y-2">
            <h2 class="text-sm font-bold text-white">
              1 · {{ esNC ? 'Elegí qué factura(s) acredita esta nota' : 'Elegí qué factura ajusta esta nota (o dejala suelta)' }}
            </h2>
            <div v-if="cand.clientes.length > 1 && !ajSel.size" class="text-xs">
              <span class="block text-[10px] uppercase text-slate-500 font-bold mb-1">Varios clientes comparten este CUIT — ¿a cuál se atribuye?</span>
              <select v-model="ajCliente" @change="ajEv = null" class="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-white">
                <option :value="null">— elegir —</option>
                <option v-for="c in cand.clientes" :key="c.id" :value="c.id">{{ c.razon_social }}</option>
              </select>
            </div>
            <label v-for="f in cand.facturas" :key="f.factura_id"
              class="flex gap-3 items-start bg-slate-800/40 border rounded-xl p-3 cursor-pointer transition-colors"
              :class="ajSel.has(f.factura_id) ? 'border-emerald-500/60' : 'border-slate-700 hover:border-slate-500'">
              <input type="checkbox" class="mt-1 accent-emerald-500" :checked="ajSel.has(f.factura_id)" @change="toggleFactura(f.factura_id)" />
              <div class="flex-1 min-w-0 text-xs">
                <div class="flex flex-wrap gap-3 text-white">
                  <span class="font-mono font-bold">{{ f.tipo_comprobante }} {{ f.numero || 'sin número' }}</span>
                  <span class="text-slate-400">{{ f.fecha_emision || '—' }}</span>
                  <span class="text-emerald-300 font-mono">{{ moneda(f.total) }}</span>
                </div>
                <div class="mt-1 text-slate-400">
                  <span v-for="r in f.renglones" :key="r.factura_item_id" class="inline-block mr-3">
                    {{ r.descripcion }} <b class="text-slate-200">{{ r.cantidad }}</b>
                    <span v-if="r.disponible != null && r.disponible < r.cantidad" class="text-amber-400"> (quedan {{ r.disponible }})</span>
                  </span>
                </div>
              </div>
            </label>
            <p v-if="!cand.facturas.length" class="text-xs text-slate-500">El cliente no tiene facturas con CAE registradas en el sistema.</p>
            <button @click="evaluarAjuste(null)" :disabled="(esNC && !ajSel.size) || ajEvaluando || !!cand.bloqueos.length"
              class="px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-xs font-bold uppercase tracking-wide">
              <i class="fas" :class="ajEvaluando ? 'fa-spinner fa-spin' : 'fa-magnifying-glass'"></i> Comparar
            </button>
          </section>

          <section v-if="ajEv" class="space-y-3">
            <h2 class="text-sm font-bold text-white">2 · {{ esNC ? 'Renglón por renglón' : 'Renglones de la nota de débito' }}</h2>
            <table class="w-full text-xs">
              <thead>
                <tr class="text-[10px] uppercase text-slate-500 border-b border-slate-700">
                  <th class="text-left py-1 pr-2">Nota (ARCA)</th>
                  <th class="text-right py-1 px-2">Cant.</th>
                  <th class="text-right py-1 px-2">Precio</th>
                  <th v-if="esNC" class="text-left py-1 pl-2">Renglón de la factura que acredita</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(it, i) in ajEv.factura.items" :key="i" class="border-b border-slate-800">
                  <td class="py-1.5 pr-2 text-slate-200">{{ it.descripcion }}</td>
                  <td class="py-1.5 px-2 text-right font-mono">{{ it.cantidad }}</td>
                  <td class="py-1.5 px-2 text-right font-mono">{{ moneda(it.precio_unitario) }}</td>
                  <td v-if="esNC" class="py-1.5 pl-2">
                    <div class="flex items-center gap-2">
                      <select :value="ajParDe(i) ?? ''" @change="cambiarParAjuste(i, $event.target.value)"
                        class="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs text-white w-full max-w-sm">
                        <option value="">— sin par (concepto de solo monto) —</option>
                        <option v-for="r in renglonesElegibles" :key="r.factura_item_id" :value="r.factura_item_id">
                          {{ r.factura_numero }} · {{ r.descripcion }} · {{ r.cantidad }}{{ r.disponible != null ? ' (quedan ' + r.disponible + ')' : '' }}
                        </option>
                      </select>
                      <span v-if="ajComoDe(i)" class="text-[9px] uppercase px-1.5 py-0.5 rounded bg-slate-700 text-slate-300">{{ ajComoDe(i) }}</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>

            <ul class="space-y-1">
              <li v-for="(d, i) in ajEv.diferencias" :key="'ad' + i" class="text-xs rounded-lg px-3 py-2 border flex gap-2" :class="claseEstilo(d.clase)">
                <span class="font-bold shrink-0 w-16">{{ etiqueta(d.clase) }}</span>
                <span>{{ d.detalle }}</span>
              </li>
            </ul>
            <ul v-if="ajEv.avisos.length" class="space-y-1">
              <li v-for="(a, i) in ajEv.avisos" :key="'aa' + i" class="text-xs bg-amber-900/20 border border-amber-600/30 text-amber-300 rounded-lg px-3 py-2">
                <i class="fas fa-circle-exclamation mr-1"></i>{{ a }}
              </li>
            </ul>
            <p v-if="ajHayClaseB" class="text-[11px] text-amber-400/80">
              Las diferencias clase B no frenan: la nota se registra igual y queda una nota [SISTEMA] en el PR del renglón acreditado de más.
            </p>

            <button @click="confirmarAjuste" :disabled="!!ajEv.bloqueos.length || ajConfirmando"
              class="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm font-bold">
              <i class="fas" :class="ajConfirmando ? 'fa-spinner fa-spin' : 'fa-check'"></i> Confirmar {{ esNC ? 'nota de crédito' : 'nota de débito' }}
            </button>
          </section>
        </template>

        <!-- PR CANDIDATOS -->
        <section v-if="!esAjuste && cand.prs.length" class="space-y-2">
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
                <!-- [S898, Carlos 03/11] total del pedido para el control rápido contra el total de la factura; si es el mismo importe, lo marca -->
                <span v-if="p.pedido_total != null" class="text-slate-300" data-total-pedido>
                  Total del pedido <b class="text-white font-mono">{{ moneda(p.pedido_total) }}</b>
                  <span v-if="mismoImporte(p.pedido_total, cand.factura.total_final)" class="ml-1 text-emerald-400"><i class="fas fa-equals"></i> igual a la factura</span>
                </span>
              </div>
              <div class="mt-1 text-slate-400">
                <span v-for="r in p.renglones" :key="r.remito_item_id" class="inline-block mr-3">
                  {{ r.producto }} <b class="text-slate-200">{{ r.pendiente_facturar }}</b>
                  <span v-if="r.precio_pedido != null" class="text-slate-500"> a {{ moneda(r.precio_pedido) }}</span>
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
        <section v-if="!esAjuste && ev" class="space-y-3">
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
            <template v-if="diferenciasPrecioEv.length">Las diferencias de precio con el pedido piden tu confirmación al registrar. </template>
            Las demás diferencias clase B no frenan: la factura se registra igual, queda una nota [SISTEMA] en el PR y el desfase
            se ve en la resta (facturado ≠ remitido) hasta que llegue la nota de crédito o débito.
          </p>

          <button @click="confirmar()" :disabled="!!ev.bloqueos.length || confirmando"
            class="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm font-bold">
            <i class="fas" :class="confirmando ? 'fa-spinner fa-spin' : 'fa-check'"></i> Confirmar conciliación
          </button>
        </section>

        <!-- RESULTADO -->
        <section v-if="resultado" class="bg-emerald-900/20 border border-emerald-500/40 rounded-xl p-4 text-sm text-emerald-200">
          <i class="fas fa-circle-check mr-2 text-emerald-400"></i>
          <template v-if="resultado.facturas_ajustadas">
            Registrada {{ resultado.tipo_comprobante }} {{ resultado.numero }}
            <span v-if="resultado.facturas_ajustadas.length">y vinculada a {{ resultado.facturas_ajustadas.length }} factura(s).</span>
            <span v-else>sin factura asociada (suelta).</span>
          </template>
          <template v-else>
            Registrada {{ resultado.tipo_comprobante }} {{ resultado.numero }} y vinculada a {{ resultado.remito_ids.length }} PR.
            <span v-if="resultado.pedido_id"> Pedido retroactivo #{{ resultado.pedido_id }} (contra natura).</span>
          </template>
          <!-- [S900, Card #214; Carlos 05/11: «¿Pasamos a Cumplido?» y «fecha rto = fecha FAC, que el operador la cambie»] Dos propuestas al conciliar: nada es automático.
               (1) un remito más de un día POSTERIOR a la factura (cargado después) se ofrece fechar como la factura; (2) un pedido que quedó completo (remitido y facturado) se ofrece pasar a Cumplido. -->
          <div v-if="remitosAFechar.length || pedidosACumplir.length || hechos.length" class="mt-4 space-y-3 border-t border-emerald-500/30 pt-3 text-xs" data-test="proximos-pasos">
            <h3 class="text-[10px] uppercase font-bold tracking-wider text-emerald-300/80">Para dejarlo prolijo</h3>
            <p v-for="(h, i) in hechos" :key="'h' + i" class="text-emerald-300" data-test="hecho">✔ {{ h }}</p>
            <div v-for="r in remitosAFechar" :key="'f' + r.remito_id" class="rounded-lg border border-amber-500/40 bg-amber-900/20 p-3 space-y-2 text-amber-100" data-test="cartel-fecha">
              <p>El remito <b>{{ r.numero_legal }}</b> es del <b>{{ fechaCorta(r.fecha) }}</b> y la factura es del <b>{{ fechaCorta(proximos.factura.fecha) }}</b> ({{ r.dias_despues_de_la_factura }} días antes). ¿Fechamos el remito como la factura?</p>
              <div class="flex flex-wrap items-center gap-2">
                <button type="button" :disabled="procesando" data-test="fechar-como-factura"
                  @click="fecharRemito(r, proximos.factura.fecha, 'Igualada a la fecha de la factura ' + proximos.factura.numero + ' al conciliar')"
                  class="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-900 font-black">Sí, poner {{ fechaCorta(proximos.factura.fecha) }}</button>
                <span class="text-amber-200/70">o</span>
                <input type="date" v-model="otraFecha[r.remito_id]" :max="hoyIso" data-test="otra-fecha" class="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-white" />
                <button type="button" :disabled="procesando || !otraFecha[r.remito_id]" data-test="poner-otra-fecha"
                  @click="fecharRemito(r, otraFecha[r.remito_id], 'Fecha ajustada al conciliar la factura ' + proximos.factura.numero)"
                  class="px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-bold disabled:opacity-40">Poner esta fecha</button>
                <button type="button" data-test="dejar-fecha" @click="descartar('r' + r.remito_id)"
                  class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300">Dejar {{ fechaCorta(r.fecha) }}</button>
              </div>
            </div>
            <div v-for="p in pedidosACumplir" :key="'c' + p.pedido_id" class="rounded-lg border border-emerald-500/40 bg-emerald-900/20 p-3 space-y-2 text-emerald-100" data-test="cartel-cumplido">
              <p>Pedido <b>#{{ p.pedido_id }}</b>: {{ p.remitida }} de {{ p.pedida }} remitidos y facturados ({{ p.remitos.join(', ') }}). ¿Pasarlo a Cumplido?</p>
              <p v-if="p.salida_asumida" class="text-amber-300" data-test="salida-asumida">La salida de su remito está <b>asumida</b>, no confirmada: pasalo a Cumplido solo si ya salió.</p>
              <div class="flex flex-wrap items-center gap-2">
                <button type="button" :disabled="procesando" data-test="pasar-a-cumplido" @click="pasarACumplido(p)"
                  :class="p.salida_asumida ? 'bg-slate-700 hover:bg-slate-600 text-white font-bold' : 'bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-black'"
                  class="px-3 py-1.5 rounded-lg disabled:opacity-50">Sí, pasar a Cumplido</button>
                <button type="button" data-test="ahora-no" @click="descartar('p' + p.pedido_id)"
                  :class="p.salida_asumida ? 'bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-black' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'"
                  class="px-3 py-1.5 rounded-lg">Ahora no</button>
              </div>
            </div>
          </div>
          <!-- [S899] desde «Facturas»: volver, o seguir con la próxima subida sin terminar (la más baja primero) -->
          <div v-if="vieneDeFacturas" class="mt-3 flex flex-wrap items-center gap-2" data-test="despues-de-conciliar">
            <button type="button" data-test="volver-a-facturas" @click="$router.push({ name: 'FacturasPanel' })"
              class="px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs font-bold"><i class="fas fa-list-check mr-1"></i>Volver a Facturas</button>
            <button v-if="siguiente" type="button" data-test="seguir-con-la-siguiente"
              @click="$router.push({ name: 'ConciliarFactura', params: { rawId: siguiente.raw_id }, query: { volver: 'facturas' } })"
              class="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-900 text-xs font-black"><i class="fas fa-forward mr-1"></i>Seguir con la siguiente: {{ siguiente.tipo_texto }} {{ siguiente.numero_legal }}
              <span class="font-normal">({{ pendientesRestantes }} pendiente{{ pendientesRestantes === 1 ? '' : 's' }})</span></button>
            <span v-else-if="siguienteListo" class="text-xs text-emerald-300/80">No queda ninguna subida sin terminar. 👍</span>
          </div>
        </section>

        <!-- [Etapa 7c] CONTRA NATURA: factura emitida en ARCA sin PR previo -->
        <section v-if="!resultado && !esAjuste" class="border-t border-slate-700/60 pt-4 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 class="text-sm font-bold text-white"><i class="fas fa-triangle-exclamation mr-1 text-orange-400"></i>¿La factura no tiene PR? Contra natura</h2>
              <p class="text-[11px] text-slate-500">Se emitió en ARCA sin pasar por el circuito. Si el cliente y la mercadería existen, se reconstruyen pedido y PR desde el PDF, marcados. Si no, corresponde nota de crédito por el total.</p>
            </div>
            <button @click="evaluarCN()" :disabled="cnCargando"
              class="px-3 py-1.5 rounded-lg border border-orange-500/40 text-orange-300 hover:bg-orange-900/20 text-xs font-bold uppercase tracking-wide">
              <i class="fas" :class="cnCargando ? 'fa-spinner fa-spin' : 'fa-magnifying-glass'"></i> Evaluar contra natura
            </button>
          </div>

          <template v-if="cn">
            <div class="text-xs rounded-lg px-3 py-2 border font-bold"
              :class="cn.veredicto === 'RETROACTIVO' ? 'bg-emerald-900/20 border-emerald-600/40 text-emerald-300' : 'bg-red-900/30 border-red-600/40 text-red-300'">
              {{ cn.veredicto === 'RETROACTIVO' ? 'Se puede reconstruir retroactivo' : 'Desmadre: nota de crédito por el total y rehacer el circuito' }}
              <ul v-if="cn.motivos_desmadre.length" class="font-normal mt-1 list-disc list-inside">
                <li v-for="(m, i) in cn.motivos_desmadre" :key="'m' + i">{{ m }}</li>
              </ul>
            </div>
            <ul class="space-y-1">
              <li v-for="(b, i) in cn.bloqueos" :key="'cb' + i" class="text-xs bg-red-900/30 border border-red-600/40 text-red-300 rounded-lg px-3 py-2"><i class="fas fa-ban mr-1"></i>{{ b }}</li>
              <li v-for="(a, i) in cn.avisos" :key="'ca' + i" class="text-xs bg-amber-900/20 border border-amber-600/30 text-amber-300 rounded-lg px-3 py-2"><i class="fas fa-circle-exclamation mr-1"></i>{{ a }}</li>
            </ul>

            <div v-if="cn.clientes.length" class="grid md:grid-cols-3 gap-3 text-xs">
              <label class="block"><span class="block text-[10px] uppercase text-slate-500 font-bold mb-1">Cliente</span>
                <select v-model="cnSel.cliente_id" @change="evaluarCN()" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-white">
                  <option v-for="c in cn.clientes" :key="c.id" :value="c.id">{{ c.razon_social }}</option>
                </select></label>
              <label class="block"><span class="block text-[10px] uppercase text-slate-500 font-bold mb-1">Sede de entrega</span>
                <select v-model="cnSel.domicilio_entrega_id" @change="evaluarCN()" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-white">
                  <option v-for="d in cn.domicilios" :key="d.id" :value="d.id">{{ d.texto }}</option>
                </select></label>
              <label class="block"><span class="block text-[10px] uppercase text-slate-500 font-bold mb-1">Transporte</span>
                <select v-model="cnSel.transporte_id" @change="evaluarCN()" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-white">
                  <option :value="null">— elegir —</option>
                  <option v-for="t in cn.transportes" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                </select></label>
            </div>

            <table v-if="cn.renglones.length" class="w-full text-xs">
              <thead><tr class="text-[10px] uppercase text-slate-500 border-b border-slate-700">
                <th class="text-left py-1 pr-2">Factura (ARCA)</th><th class="text-right py-1 px-2">Cant.</th>
                <th class="text-right py-1 px-2">Precio</th><th class="text-left py-1 pl-2">Producto del catálogo</th></tr></thead>
              <tbody>
                <tr v-for="r in cn.renglones" :key="r.item_pdf" class="border-b border-slate-800">
                  <td class="py-1.5 pr-2 text-slate-200">{{ r.descripcion }}</td>
                  <td class="py-1.5 px-2 text-right font-mono">{{ r.cantidad }}</td>
                  <td class="py-1.5 px-2 text-right font-mono">{{ moneda(r.precio_unitario) }}</td>
                  <td class="py-1.5 pl-2"><div class="flex items-center gap-2">
                    <select :value="r.producto_id ?? ''" @change="cambiarProducto(r.item_pdf, $event.target.value)"
                      class="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs text-white w-full max-w-xs">
                      <option value="">— no está en el catálogo —</option>
                      <option v-for="p in cn.catalogo" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                    </select>
                    <span v-if="r.como" class="text-[9px] uppercase px-1.5 py-0.5 rounded bg-slate-700 text-slate-300">{{ r.como }}</span>
                  </div></td>
                </tr>
              </tbody>
            </table>

            <div class="flex gap-2">
              <button v-if="cn.veredicto === 'RETROACTIVO'" @click="confirmarCN" :disabled="!!cn.bloqueos.length || cnCargando"
                class="px-4 py-2 rounded-lg bg-orange-600 hover:bg-orange-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-xs font-bold">
                <i class="fas fa-rotate-left mr-1"></i> Reconstruir pedido y PR, y registrar la factura
              </button>
              <button v-else @click="marcarDesmadre" :disabled="cnCargando || cnMarcado"
                class="px-4 py-2 rounded-lg bg-red-800 hover:bg-red-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-xs font-bold">
                <i class="fas fa-flag mr-1"></i> {{ cnMarcado ? 'Marcada: falta NC por el total' : 'Marcar como desmadre (falta NC)' }}
              </button>
            </div>
          </template>
        </section>
      </template>
    </main>

    <!-- [S894, Card #144] El precio de la factura no coincide con el del pedido: el operador confirma a conciencia (motivo opcional) -->
    <ConfirmarDiferenciasPrecio
      v-if="diferenciasPrecio"
      :diferencias="diferenciasPrecio.diferencias"
      :mensaje="diferenciasPrecio.mensaje"
      :enviando="confirmando"
      @confirmar="(motivo) => { diferenciasPrecio = null; confirmar({ motivo }) }"
      @cancelar="diferenciasPrecio = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'
import ConfirmarDiferenciasPrecio from './components/ConfirmarDiferenciasPrecio.vue'   // [S894, Card #144]
import { usePedidoEstado } from '@/composables/usePedidoEstado'   // [S900, Card #214] el cambio de estado de siempre, con sus guardas

const route = useRoute()
const notification = useNotificationStore()
const rawId = route.params.rawId
// [S899] el PDF original de la factura (se guarda en la ingesta; GET /ingesta/raw/{id}/pdf) se ve en la misma pantalla
const pdfAbierto = ref(false)
const pdfSrc = `/ingesta/raw/${rawId}/pdf`

// [S899, Carlos 04/11] se llega desde la pantalla «Facturas» con ?volver=facturas: al terminar se vuelve ahí y se ofrece la próxima subida sin terminar
const vieneDeFacturas = route.query.volver === 'facturas'
const siguiente = ref(null)
const pendientesRestantes = ref(0)
const siguienteListo = ref(false)

const loading = ref(true)
const cand = ref(null)
const seleccion = ref(new Set())
const ev = ref(null)
const emparejamiento = ref(null)
const evaluando = ref(false)
const confirmando = ref(false)
const resultado = ref(null)

// [Etapa 7d] modo AJUSTE: el PDF es una nota de crédito o débito (el servidor lo dice en `candidatos`)
const esAjuste = computed(() => cand.value?.modo === 'AJUSTE')
const esNC = computed(() => cand.value?.factura?.clase_comprobante === 'NOTA_CREDITO')
const ajSel = ref(new Set())
const ajCliente = ref(null)
const ajEv = ref(null)
const ajEmp = ref(null)
const ajEvaluando = ref(false)
const ajConfirmando = ref(false)
const ajHayClaseB = computed(() => ajEv.value?.diferencias.some(d => d.clase === 'B'))
const renglonesElegibles = computed(() =>
  (cand.value?.facturas || []).filter(f => ajSel.value.has(f.factura_id))
    .flatMap(f => f.renglones.map(r => ({ ...r, factura_numero: f.numero || f.tipo_comprobante }))))

const bloqueosVisibles = computed(() =>
  (esAjuste.value ? (ajEv.value ? ajEv.value.bloqueos : cand.value?.bloqueos) : (ev.value ? ev.value.bloqueos : cand.value?.bloqueos)) || [])
const hayClaseB = computed(() => ev.value?.diferencias.some(d => d.clase === 'B'))
// [S894, Card #144] diferencias de precio con el pedido (precio efectivo de los dos lados): piden la confirmación del operador
const diferenciasPrecioEv = computed(() => (ev.value?.diferencias || []).filter(d => d.tipo === 'PRECIO').map(d => d.precio))
const diferenciasPrecio = ref(null)

const moneda = (v) => (v == null ? '—' : Number(v).toLocaleString('es-AR', { style: 'currency', currency: 'ARS' }))
// [S898] mismo importe a los centavos (el total del pedido y el de la factura vienen con redondeos distintos)
const mismoImporte = (a, b) => a != null && b != null && Math.abs(Number(a) - Number(b)) < 0.005
const ESTILOS = {
  INFO: 'bg-slate-800/60 border-slate-600/40 text-slate-300',
  A: 'bg-sky-900/20 border-sky-600/30 text-sky-200',
  B: 'bg-amber-900/25 border-amber-500/40 text-amber-200',
  C: 'bg-red-900/30 border-red-600/40 text-red-200',
  PARCIAL: 'bg-slate-800/60 border-slate-600/40 text-slate-300',
  AVISO: 'bg-amber-900/10 border-amber-700/30 text-amber-300/80',
}
const ETIQUETAS = { A: 'Clase A', B: 'Clase B', C: 'Clase C', PARCIAL: 'Parcial', AVISO: 'Aviso', INFO: 'Info' }
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

// confirmacionPrecios: { motivo } cuando el operador ya confirmó las diferencias de precio [S894, Card #144]
const confirmar = async (confirmacionPrecios = null) => {
  // solo cuenta la confirmación del modal ({ motivo }): un evento de clic pasado por error no confirma nada
  if (!(confirmacionPrecios && typeof confirmacionPrecios === 'object' && 'motivo' in confirmacionPrecios)) confirmacionPrecios = null
  if (diferenciasPrecioEv.value.length && !confirmacionPrecios) {
    diferenciasPrecio.value = {
      mensaje: 'Revisalo y confirmá para registrar la factura así; el pedido no se cambia.',
      diferencias: diferenciasPrecioEv.value,
    }
    return
  }
  confirmando.value = true
  try {
    const body = {
      remito_ids: [...seleccion.value],
      emparejamiento: emparejamiento.value.map(({ item_pdf, remito_item_id }) => ({ item_pdf, remito_item_id })),
      ...(confirmacionPrecios ? { confirmar_diferencias_precio: true, motivo_diferencias_precio: confirmacionPrecios.motivo || null } : {}),
    }
    resultado.value = (await api.post(`/ingesta/raw/${rawId}/conciliacion/confirmar`, body)).data
    notification.add(`Factura ${resultado.value.numero} conciliada`, 'success')
    ev.value = null
    await cargar()
  } catch (e) {
    if (e.response?.status === 409 && e.response.data?.detail?.codigo === 'DIFERENCIA_DE_PRECIO') {
      diferenciasPrecio.value = e.response.data.detail
      return
    }
    error(e, 'No se pudo conciliar')
  } finally {
    confirmando.value = false
  }
}

// [Etapa 7d] NC / ND
const ajParDe = (i) => ajEmp.value?.find(e => e.item_pdf === i)?.factura_item_id ?? null
const ajComoDe = (i) => ajEmp.value?.find(e => e.item_pdf === i)?.como ?? null

const toggleFactura = (id) => {
  if (ajSel.value.has(id)) ajSel.value.delete(id)
  else ajSel.value.add(id)
  ajEv.value = null
  ajEmp.value = null
}

const evaluarAjuste = async (emp) => {
  ajEvaluando.value = true
  try {
    const body = { factura_ids: [...ajSel.value] }
    if (emp) body.emparejamiento = emp
    if (ajCliente.value) body.cliente_id = ajCliente.value
    ajEv.value = (await api.post(`/ingesta/raw/${rawId}/ajuste/evaluar`, body)).data
    ajEmp.value = ajEv.value.emparejamiento
  } catch (e) {
    error(e, 'No se pudo comparar')
  } finally {
    ajEvaluando.value = false
  }
}

const cambiarParAjuste = (i, valor) => {
  const nuevo = ajEmp.value.map(e =>
    e.item_pdf === i ? { item_pdf: i, factura_item_id: valor === '' ? null : Number(valor), como: 'operador' } : e)
  evaluarAjuste(nuevo.map(({ item_pdf, factura_item_id }) => ({ item_pdf, factura_item_id })))
}

const confirmarAjuste = async () => {
  ajConfirmando.value = true
  try {
    const body = {
      factura_ids: [...ajSel.value],
      emparejamiento: ajEmp.value.map(({ item_pdf, factura_item_id }) => ({ item_pdf, factura_item_id })),
    }
    if (ajCliente.value) body.cliente_id = ajCliente.value
    resultado.value = (await api.post(`/ingesta/raw/${rawId}/ajuste/confirmar`, body)).data
    notification.add(`${resultado.value.tipo_comprobante} ${resultado.value.numero} conciliada`, 'success')
    ajEv.value = null
    await cargar()
  } catch (e) {
    error(e, 'No se pudo conciliar la nota')
  } finally {
    ajConfirmando.value = false
  }
}

// [Etapa 7c] Contra natura
const cn = ref(null)
const cnCargando = ref(false)
const cnMarcado = ref(false)
const cnSel = ref({ cliente_id: null, domicilio_entrega_id: null, transporte_id: null, productos: null })

const cnBody = () => {
  const b = {}
  for (const k of ['cliente_id', 'domicilio_entrega_id', 'transporte_id', 'productos']) {
    if (cnSel.value[k] != null) b[k] = cnSel.value[k]
  }
  return b
}

const evaluarCN = async () => {
  cnCargando.value = true
  try {
    cn.value = (await api.post(`/ingesta/raw/${rawId}/contra-natura/evaluar`, cnBody())).data
    // Lo que el servidor resolvió (sugerencias incluidas) pasa a ser la selección vigente.
    cnSel.value.cliente_id = cn.value.cliente_id
    cnSel.value.domicilio_entrega_id = cn.value.domicilio_entrega_id
    cnSel.value.transporte_id = cn.value.transporte_id
    cnSel.value.productos = cn.value.renglones.map(r => ({ item_pdf: r.item_pdf, producto_id: r.producto_id }))
  } catch (e) {
    error(e, 'No se pudo evaluar')
  } finally {
    cnCargando.value = false
  }
}

const cambiarProducto = (i, valor) => {
  cnSel.value.productos = cnSel.value.productos.map(p =>
    p.item_pdf === i ? { item_pdf: i, producto_id: valor === '' ? null : Number(valor) } : p)
  evaluarCN()
}

const confirmarCN = async () => {
  if (!confirm('Se va a crear un pedido y un PR retroactivos desde esta factura, marcados como contra natura. ¿Seguir?')) return
  cnCargando.value = true
  try {
    resultado.value = (await api.post(`/ingesta/raw/${rawId}/contra-natura/confirmar`, cnBody())).data
    notification.add(`Factura ${resultado.value.numero} registrada contra natura (pedido #${resultado.value.pedido_id})`, 'success')
    cn.value = null
    await cargar()
  } catch (e) {
    error(e, 'No se pudo registrar')
  } finally {
    cnCargando.value = false
  }
}

const marcarDesmadre = async () => {
  cnCargando.value = true
  try {
    await api.post(`/ingesta/raw/${rawId}/contra-natura/marcar-desmadre`, cnBody())
    cnMarcado.value = true
    notification.add('Factura marcada: pendiente nota de crédito por el total', 'success')
  } catch (e) {
    error(e, 'No se pudo marcar')
  } finally {
    cnCargando.value = false
  }
}

onMounted(cargar)

// [S900, Card #214] Propuestas al conciliar (solo lectura en el servidor: GET /ingesta/facturas/{id}/proximos-pasos). Nada se cambia sin que el operador conteste.
const { cambiarEstado } = usePedidoEstado()
const proximos = ref(null)
const descartados = ref(new Set())
const hechos = ref([])
const otraFecha = ref({})
const procesando = ref(false)
const hoyIso = new Date().toLocaleDateString('en-CA')   // AAAA-MM-DD, hora local
const fechaCorta = (s) => (s ? `${s.slice(8, 10)}/${s.slice(5, 7)}/${s.slice(0, 4)}` : '—')
const remitosAFechar = computed(() => (proximos.value?.remitos_a_fechar || []).filter(r => !descartados.value.has('r' + r.remito_id)))
const pedidosACumplir = computed(() => (proximos.value?.pedidos_a_cumplir || []).filter(p => !descartados.value.has('p' + p.pedido_id)))
const descartar = (clave) => { descartados.value = new Set([...descartados.value, clave]) }
const cargarProximosPasos = async (facturaId) => {
  try {
    proximos.value = (await api.get(`/ingesta/facturas/${facturaId}/proximos-pasos`)).data
  } catch (e) {
    proximos.value = null   // sin las propuestas el cartel verde queda como siempre
  }
}
watch(resultado, (r) => { if (r && !r.facturas_ajustadas && r.factura_id) cargarProximosPasos(r.factura_id) })
const fecharRemito = async (r, fecha, motivo) => {
  procesando.value = true
  try {
    await api.patch(`/remitos/${r.remito_id}/fecha`, { fecha, motivo })
    hechos.value.push(`Remito ${r.numero_legal} fechado ${fechaCorta(fecha)}.`)
    notification.add(`Remito ${r.numero_legal} fechado ${fechaCorta(fecha)}`, 'success')
    await cargarProximosPasos(proximos.value.factura.factura_id)
  } catch (e) {
    notification.add('No se pudo cambiar la fecha: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    procesando.value = false
  }
}
const pasarACumplido = async (p) => {
  procesando.value = true
  try {
    if (await cambiarEstado(p.pedido_id, 'CUMPLIDO')) {
      hechos.value.push(`Pedido #${p.pedido_id} pasado a Cumplido.`)
      await cargarProximosPasos(proximos.value.factura.factura_id)
    }
  } finally {
    procesando.value = false
  }
}

// [S899] con la factura ya registrada, se busca la próxima subida sin terminar (por número, la más baja primero); si falla, solo queda «Volver a Facturas»
watch(resultado, async (r) => {
  if (!r || !vieneDeFacturas) return
  try {
    const { data } = await api.get('/ingesta/facturas/panorama')
    const otras = (data.sin_terminar || []).filter(s => s.raw_id !== rawId && s.numero != null)
      .sort((a, b) => a.numero - b.numero)
    siguiente.value = otras[0] || null
    pendientesRestantes.value = otras.length
  } catch (e) {
    siguiente.value = null
  } finally {
    siguienteListo.value = true
  }
})
</script>
