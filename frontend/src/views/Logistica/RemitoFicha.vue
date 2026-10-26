// [IDENTIDAD] - frontend\src\views\Logistica\RemitoFicha.vue
// [S893, Carlos 26/10] La FICHA del remito, el centro del nodo Remitos. Mismo molde que la ficha de Producto y la de Cliente (DEOU, Manual
// operativo cap. 1): una ventana central sobre la lista, con su propia dirección (/remitos/:ref) para que «volver atrás» y ESC cierren la
// ficha y dejen la lista como estaba. Los atajos de teclado (F10, ESC) tienen SIEMPRE su botón visible: las teclas son memoria muscular,
// los botones son lo que le enseña a quien no la tiene que puede accionar. Color naranja: Logística, el movimiento físico (DEOU 1.3).
// Las acciones (anular, fecha, depósito, retiro, sin papel, imprimir) son las del listado: se las pasa por `provide` (remitosAcciones).

<template>
  <div data-ficha="remito" class="fixed inset-0 z-[60] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 md:p-8" @click.self="cerrar">
    <div class="w-full max-w-5xl h-[85vh] flex flex-col rounded-xl bg-[#0f172a] text-gray-100 shadow-2xl overflow-hidden border-2 border-orange-500/40 animate-fade-in-up"
         style="box-shadow: 0 0 30px rgba(249, 115, 22, 0.18)">

      <!-- Cabecera: identidad del remito y acciones principales -->
      <div class="flex items-center justify-between gap-3 border-b border-orange-900/30 bg-black/40 p-3 shrink-0">
        <div class="flex items-center gap-3 min-w-0">
          <div class="h-10 w-10 shrink-0 rounded-xl bg-gradient-to-br from-orange-500/20 to-black flex items-center justify-center text-orange-400 border border-orange-500/20">
            <i class="fas fa-dolly text-lg"></i>
          </div>
          <div class="min-w-0">
            <label class="text-[9px] font-bold text-orange-400/50 uppercase tracking-widest block">Remito</label>
            <div class="font-mono text-lg font-bold text-white truncate" data-campo="numero">{{ f ? (f.remito.numero_legal || 'SIN NÚMERO') : '…' }}</div>
          </div>
          <div class="flex flex-wrap gap-1.5" data-insignias>
            <span v-for="b in insignias" :key="b.k" :data-insignia="b.k" class="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider border" :class="b.c" :title="b.title">{{ b.t }}</span>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <button v-if="f && acc && !anulado && !esCorreccion" @click="acc.imprimirRemito(remitoLista)" data-accion="imprimir"
                  class="px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-orange-600 hover:bg-orange-500 transition-colors">
            <i :class="r.impreso ? 'fas fa-copy' : 'fas fa-print'" class="mr-1"></i>
            {{ r.impreso ? 'Reimprimir' : (conNumero ? 'Imprimir' : 'Imprimir (toma el número)') }}
          </button>
          <button v-if="f && acc && !conNumero && !anulado && !esCorreccion" @click="acc.vistaPrevia(remitoLista)" data-accion="vista-previa"
                  class="px-3 py-1.5 rounded-lg text-xs font-bold text-orange-200 border border-orange-500/30 hover:bg-orange-500/10 transition-colors" title="Vista previa: no gasta el número">
            <i class="fas fa-eye mr-1"></i> Vista previa
          </button>
          <button @click="cerrar" data-accion="cerrar" class="px-3 py-1.5 rounded-lg text-xs text-gray-300 hover:text-white hover:bg-white/10 transition-colors" title="Cerrar (ESC)">
            <i class="fas fa-times mr-1"></i> Cerrar (ESC)
          </button>
        </div>
      </div>

      <!-- Cuerpo -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4">

        <div v-if="cargando && !f" class="text-center text-orange-300/60 py-16"><i class="fas fa-spinner fa-spin mr-2"></i> Cargando el remito…</div>
        <div v-else-if="error" data-ficha-error class="rounded-lg border border-red-500/30 bg-red-900/10 p-4 text-sm text-red-200">
          <p class="font-bold mb-1">No se pudo abrir el remito</p>
          <p>{{ error }}</p>
        </div>

        <template v-else-if="f">
          <!-- Resumen -->
          <section data-seccion="resumen" class="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-3 rounded-lg border border-white/10 bg-black/20 p-3">
            <div class="col-span-2"><label class="etq">Cliente</label>
              <div class="val truncate">{{ f.cliente ? f.cliente.razon_social : '—' }} <span v-if="f.cliente && f.cliente.cuit" class="text-gray-500 font-mono text-xs">{{ f.cliente.cuit }}</span></div></div>
            <div><label class="etq">Pedido</label>
              <div class="val"><a v-if="f.pedido" href="#" @click.prevent="irAlPedido" data-vinculo="pedido" class="text-orange-300 hover:underline">#{{ f.pedido.id }}</a><span v-else>—</span>
                <span v-if="f.pedido" class="text-gray-500 text-xs ml-1">{{ f.pedido.estado }}</span></div></div>
            <div><label class="etq">OC</label><div class="val font-mono" data-campo="oc">{{ r.oc || '—' }}</div></div>
            <div v-if="!esCorreccion"><label class="etq">Emisión</label><div class="val" data-campo="emision">{{ conNumero ? fechaCorta(r.fecha_emision || r.fecha_creacion) : '— (sin número)' }}</div></div>
            <div v-if="!esCorreccion"><label class="etq">Salida</label><div class="val" data-campo="salida">{{ r.fecha_salida ? fechaCorta(r.fecha_salida) : (enDeposito ? 'en depósito' : '—') }}</div></div>
            <div><label class="etq">Armado</label><div class="val">{{ fechaCorta(r.fecha_creacion) }}</div></div>
            <div v-if="!esCorreccion"><label class="etq">Método de entrega</label><div class="val">{{ metodo(r.metodo_entrega) }}</div></div>
            <div v-if="!esCorreccion" class="col-span-2"><label class="etq">Transporte</label>
              <div class="val truncate">{{ f.transporte ? f.transporte.nombre : '—' }}
                <a v-if="f.transporte && f.transporte.web_retiro" :href="urlWeb(f.transporte.web_retiro)" target="_blank" rel="noopener" class="ml-2 text-xs text-orange-300 hover:underline" data-vinculo="web-retiro">Pedir retiro ↗</a></div></div>
            <div v-if="!esCorreccion"><label class="etq">Bultos</label><div class="val">{{ r.bultos ?? '—' }}</div></div>
            <div v-if="!esCorreccion"><label class="etq">Valor declarado</label><div class="val">{{ plata(r.valor_declarado) }}</div></div>
            <div v-if="!esCorreccion" class="col-span-2 md:col-span-3"><label class="etq">Domicilio (el del papel)</label><div class="val truncate" :title="f.domicilio_entrega">{{ f.domicilio_entrega }}</div></div>
            <div v-if="!esCorreccion"><label class="etq">Factura</label>
              <div class="val font-mono text-xs" data-campo="factura">{{ f.factura ? f.factura.numero : '—' }}<span v-if="f.factura && f.factura.cae" class="text-gray-500 block">CAE {{ f.factura.cae }}</span></div></div>
          </section>

          <!-- [S893] Un remito de corrección: no tiene papel ni número; dice qué corrige -->
          <div v-if="esCorreccion" data-banner="correccion" class="rounded-lg border border-amber-500/30 bg-amber-900/10 px-3 py-2 text-sm text-amber-200">
            <i class="fas fa-rotate-left mr-2"></i>Este remito es una <b>corrección</b> de otro: baja lo que quedó de un renglón (no tiene papel ni número).
            <template v-for="it in f.items" :key="'c' + it.id"><template v-if="it.corrige">
              <a href="#" @click.prevent="abrirOtro({ id: it.corrige.remito_id, numero_legal: it.corrige.numero_legal })" data-vinculo="remito-corregido" class="ml-1 font-mono underline">{{ it.corrige.numero_legal || 'ver el remito' }}</a>
              <span class="ml-1 text-amber-300/80">({{ etiquetaCausa(it.causa) }})</span>
            </template></template>
          </div>

          <!-- La tabla del PR, renglón por renglón. Lo que quedó de un renglón se corrige con su causa (el pedido vuelve a deber la diferencia): no es una nota suelta -->
          <section data-seccion="tabla-pr" class="rounded-lg border border-white/10 bg-black/20">
            <div class="px-3 py-2 border-b border-white/10 flex items-center justify-between">
              <h3 class="text-[11px] font-black uppercase tracking-widest text-orange-300">Renglones</h3>
              <span class="text-[10px] text-gray-500">Impreso · salió · llegó · quedó · facturado · acreditado · pendientes</span>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="text-[10px] uppercase tracking-wider text-gray-500 border-b border-white/5">
                    <th class="text-left px-3 py-2">Producto</th>
                    <th class="text-right px-2">Pedido</th><th class="text-right px-2">Impreso</th><th class="text-right px-2">Salió</th><th class="text-right px-2">Llegó</th><th class="text-right px-2">Quedó</th>
                    <th class="text-right px-2">Facturado</th><th class="text-right px-2">Acreditado</th><th class="text-right px-2">Pend. remitir</th><th class="text-right px-3">Pend. facturar</th><th class="px-2"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="it in f.items" :key="it.id" data-renglon class="border-b border-white/5 last:border-0">
                    <td class="px-3 py-2 text-white">{{ it.producto }}<span v-if="it.sku" class="text-gray-500 font-mono text-[10px] ml-2">{{ it.sku }}</span>
                      <span v-if="it.motivo_no_facturable" class="ml-2 text-[10px] text-amber-300/80" :title="'No facturable: ' + it.motivo_no_facturable">{{ it.motivo_no_facturable }}</span>
                      <div v-for="c in it.correcciones" :key="c.item_id" data-correccion class="mt-0.5 text-[10px] text-amber-300/90">
                        <i class="fas fa-rotate-left mr-1"></i>−{{ cant(c.cantidad) }} {{ etiquetaCausa(c.causa) }} <span class="text-gray-500">({{ fechaCorta(c.fecha) }})</span>
                      </div></td>
                    <td class="text-right px-2 font-mono text-gray-400">{{ cant(it.pedido_cantidad) }}</td>
                    <td class="text-right px-2 font-mono">{{ cant(it.impreso) }}</td>
                    <td class="text-right px-2 font-mono font-bold text-white" data-celda="salio">{{ cant(it.salio) }}</td>
                    <td class="text-right px-2 font-mono" data-celda="llego">{{ cant(it.llego) }}</td>
                    <td class="text-right px-2 font-mono" data-celda="quedo"><span :class="it.corregido > 0 ? 'text-amber-300 font-bold' : 'text-gray-400'">{{ it.corrige ? '—' : cant(it.quedo) }}</span></td>
                    <td class="text-right px-2 font-mono" data-celda="facturado"><template v-if="it.facturado !== null">{{ cant(it.facturado) }}</template><span v-else class="no-aplica" title="Sin cantidad facturada registrada: no aplica (renglón fuera de lo fiscal, p. ej. Rosa) o es un dato anterior al registro por renglón">no aplica</span></td>
                    <td class="text-right px-2 font-mono" data-celda="acreditado"><template v-if="it.acreditado !== null">{{ cant(it.acreditado) }}</template><span v-else class="no-aplica" title="Sin facturado registrado, no hay acreditado">no aplica</span></td>
                    <td class="text-right px-2 font-mono" :class="it.pendiente_remitir > 0 ? 'text-orange-300' : 'text-gray-500'">{{ cant(it.pendiente_remitir) }}</td>
                    <td class="text-right px-3 font-mono" data-celda="pend-facturar"><template v-if="it.pendiente_facturar !== null"><span :class="it.pendiente_facturar > 0 ? 'text-orange-300' : 'text-gray-500'">{{ cant(it.pendiente_facturar) }}</span></template><span v-else class="no-aplica">no aplica</span></td>
                    <td class="text-right px-2">
                      <button v-if="puedeCorregir && !it.corrige && it.quedo > 0" @click="abrirCorreccion(null, it.id)" data-accion="corregir-renglon"
                              class="px-2 py-0.5 rounded-md text-[10px] font-bold border border-amber-500/30 text-amber-200 hover:bg-amber-500/10 whitespace-nowrap" title="Corregir lo que quedó de este renglón (el pedido vuelve a deber la diferencia)">Corregir</button>
                    </td>
                  </tr>
                  <tr v-if="!f.items.length"><td colspan="11" class="px-3 py-4 text-center text-gray-500">Sin renglones.</td></tr>
                </tbody>
              </table>
            </div>
          </section>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Historia: las notas -->
            <section data-seccion="historia" class="md:col-span-2 rounded-lg border border-white/10 bg-black/20 flex flex-col">
              <div class="px-3 py-2 border-b border-white/10 flex items-center justify-between">
                <h3 class="text-[11px] font-black uppercase tracking-widest text-orange-300">Historia (notas)</h3>
                <span class="text-[10px] text-gray-500">{{ f.notas.length }} {{ f.notas.length === 1 ? 'nota' : 'notas' }}</span>
              </div>
              <!-- [S893, Carlos 26/10] Lo que pasó con la mercadería MUEVE el renglón del pedido: no es una nota suelta. Cada botón abre la corrección con su causa. -->
              <div v-if="puedeCorregir" class="px-3 py-2 border-b border-white/10 flex flex-wrap items-center gap-2" data-corregir>
                <span class="text-[10px] uppercase tracking-wider text-gray-500">Corregir lo que pasó:</span>
                <button v-for="c in CAUSAS" :key="c.k" @click="abrirCorreccion(c.k)" :data-accion="'corregir-' + c.k.toLowerCase()"
                        class="px-2 py-0.5 rounded-md text-[11px] font-bold border border-amber-500/30 text-amber-200 hover:bg-amber-500/10 transition-colors"
                        :title="c.ayuda">{{ c.t }}</button>
              </div>
              <div class="p-3 border-b border-white/10 space-y-2" data-nueva-nota>
                <div class="flex flex-wrap items-center gap-2">
                  <span class="text-[10px] uppercase tracking-wider text-gray-500">Anotar una novedad (no cambia cantidades):</span>
                  <select v-model="itemNota" class="ml-auto bg-[#0f172a] border border-white/10 rounded-md text-xs text-gray-300 px-2 py-1" data-campo="renglon-nota" title="Sobre qué renglón (opcional)">
                    <option value="">Todo el remito</option>
                    <option v-for="it in f.items" :key="it.id" :value="it.id">{{ it.producto }}</option>
                  </select>
                </div>
                <textarea ref="cajaNota" v-model="textoNota" rows="2" data-campo="texto-nota" placeholder="Una novedad del remito: quién lo recibió, un aviso del transporte…"
                          class="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-white/30 focus:border-orange-500/50 focus:outline-none"></textarea>
                <div class="flex justify-end">
                  <button @click="guardarNota" :disabled="!textoNota.trim() || guardandoNota" data-accion="guardar-nota"
                          class="px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-orange-600 hover:bg-orange-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
                    <i v-if="guardandoNota" class="fas fa-spinner fa-spin mr-1"></i> Guardar nota (F10)
                  </button>
                </div>
              </div>
              <ul class="divide-y divide-white/5 max-h-64 overflow-y-auto">
                <li v-for="n in f.notas" :key="n.id" data-nota class="px-3 py-2 text-sm">
                  <div class="flex items-center gap-2 text-[10px] text-gray-500">
                    <span>{{ fechaHora(n.fecha) }}</span><span v-if="n.autor">· {{ n.autor }}</span>
                    <span v-if="n.remito_item_id" class="text-orange-300/70">· renglón {{ nombreRenglon(n.remito_item_id) }}</span>
                  </div>
                  <p class="whitespace-pre-wrap" :class="n.texto.startsWith('[SISTEMA]') ? 'text-gray-400' : 'text-white'">{{ n.texto }}</p>
                </li>
                <li v-if="!f.notas.length" class="px-3 py-4 text-center text-gray-500 text-sm">Todavía no hay notas.</li>
              </ul>
            </section>

            <!-- Acciones y vínculos -->
            <section data-seccion="acciones" class="rounded-lg border border-white/10 bg-black/20">
              <div class="px-3 py-2 border-b border-white/10"><h3 class="text-[11px] font-black uppercase tracking-widest text-orange-300">Acciones</h3></div>
              <div class="p-3 flex flex-col gap-2">
                <template v-if="acc">
                  <button v-if="esCorreccion && !anulado" @click="acc.abrirAnulacion(remitoLista, 'deshacer-correccion')" data-accion="deshacer-correccion" class="btn-ficha text-amber-300 border-amber-500/30 hover:bg-amber-500/10"><i class="fas fa-rotate-left mr-2"></i>Deshacer la corrección</button>
                  <button v-if="!conNumero && !anulado && !esCorreccion" @click="acc.openEditModal(remitoLista)" data-accion="editar" class="btn-ficha"><i class="fas fa-pen mr-2"></i>Editar el remito</button>
                  <button v-if="!conNumero && !anulado && !esCorreccion" @click="acc.abrirAccionFecha(remitoLista, 'sin-papel')" data-accion="sin-papel" class="btn-ficha"><i class="fas fa-file-circle-xmark mr-2"></i>Salió sin papel</button>
                  <button v-if="conNumero && !anulado" @click="acc.abrirCambioFecha(remitoLista)" data-accion="cambiar-fecha" class="btn-ficha"><i class="fas fa-calendar-day mr-2"></i>Cambiar la fecha</button>
                  <button v-if="conNumero && estado === 'BORRADOR' && !enDeposito" @click="acc.marcarEnDeposito(remitoLista)" data-accion="en-deposito" class="btn-ficha"><i class="fas fa-warehouse mr-2"></i>Queda en depósito</button>
                  <button v-if="enDeposito" @click="acc.abrirAccionFecha(remitoLista, 'retiro')" data-accion="retiro" class="btn-ficha"><i class="fas fa-truck-ramp-box mr-2"></i>Retiró el transporte</button>
                  <button v-if="conNumero && !anulado" @click="acc.abrirAnulacion(remitoLista, 'anular')" data-accion="anular" class="btn-ficha text-red-300 border-red-500/30 hover:bg-red-500/10"><i class="fas fa-ban mr-2"></i>Anular</button>
                  <button v-if="anulado && !esCorreccion" @click="acc.abrirAnulacion(remitoLista, 'deshacer')" data-accion="deshacer-anulacion" class="btn-ficha text-amber-300 border-amber-500/30 hover:bg-amber-500/10"><i class="fas fa-rotate-left mr-2"></i>Deshacer la anulación</button>
                </template>
                <button v-if="f.pedido && conNumero && !anulado && !esCorreccion" @click="irAlPedido('devolucion')" data-accion="registrar-devolucion" class="btn-ficha" title="Abre «Registrar Devolución» en la pantalla de entregas del pedido"><i class="fas fa-rotate-left mr-2"></i>Registrar devolución</button>
                <button v-if="f.pedido" @click="irAlPedido('entregas')" data-accion="entregas-del-pedido" class="btn-ficha"><i class="fas fa-truck-loading mr-2"></i>Entregas y remitos del pedido</button>
                <p v-if="!acc" class="text-xs text-gray-500">Las acciones se habilitan desde el listado de Remitos.</p>
              </div>
              <div v-if="f.otros_remitos_del_pedido.length" class="px-3 pb-3" data-seccion="otros-remitos">
                <label class="etq">Otros remitos del pedido</label>
                <div class="flex flex-wrap gap-1.5 mt-1">
                  <a v-for="o in f.otros_remitos_del_pedido" :key="o.id" href="#" @click.prevent="abrirOtro(o)" data-vinculo="otro-remito"
                     class="px-2 py-0.5 rounded-md text-[11px] font-mono border border-white/10 hover:border-orange-500/40 hover:text-orange-200 transition-colors"
                     :class="o.estado === 'ANULADO' ? 'line-through text-gray-500' : 'text-gray-300'">{{ o.numero_legal || 'sin número' }}</a>
                </div>
              </div>
            </section>
          </div>
        </template>
      </div>
    </div>

    <!-- [S893, Carlos 26/10] Corregir lo que quedó de un renglón: cuánto quedó realmente y por qué. El pedido vuelve a deber la diferencia (y se reabre si estaba cumplido). -->
    <div v-if="correccion.visible" data-modal="correccion" class="fixed inset-0 z-[70] bg-black/70 flex items-center justify-center p-4" @click.self="cerrarCorreccion">
      <div class="w-full max-w-lg rounded-xl bg-[#0b1220] border border-amber-500/40 p-5 shadow-2xl">
        <h3 class="text-white font-bold text-lg mb-1"><i class="fas fa-rotate-left mr-2 text-amber-300"></i>Corregir lo que quedó</h3>
        <p class="text-xs text-amber-200/70 mb-4">Lo impreso y lo que salió quedan como están. El pedido vuelve a deber la diferencia.</p>
        <label class="etq">Renglón</label>
        <select v-model="correccion.itemId" data-campo="correccion-renglon" class="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-white mb-3">
          <option v-for="it in renglonesCorregibles" :key="it.id" :value="it.id">{{ it.producto }} — quedan {{ cant(it.quedo) }}</option>
        </select>
        <label class="etq">¿Qué pasó?</label>
        <div class="flex flex-wrap gap-2 mb-3">
          <label v-for="c in CAUSAS" :key="c.k" class="cursor-pointer">
            <input type="radio" class="sr-only peer" v-model="correccion.causa" :value="c.k" :data-causa="c.k" />
            <span class="px-3 py-1 rounded-md text-xs font-bold border border-white/10 text-gray-300 peer-checked:border-amber-400 peer-checked:text-amber-200 peer-checked:bg-amber-500/10 block" :title="c.ayuda">{{ c.t }}</span>
          </label>
        </div>
        <label class="etq">¿Cuánto quedó realmente?</label>
        <div class="flex items-center gap-3 mb-1">
          <input v-model.number="correccion.real" type="number" min="0" step="any" data-campo="correccion-cantidad" class="w-32 bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-amber-400 focus:outline-none" />
          <span class="text-xs text-gray-400" data-campo="correccion-resumen">{{ resumenCorreccion }}</span>
        </div>
        <label class="etq mt-3">Nota (opcional)</label>
        <textarea v-model="correccion.nota" rows="2" data-campo="correccion-nota" placeholder="Ej.: se mojó en el camión; el chofer avisó a las 18"
                  class="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-white/30 focus:border-amber-400 focus:outline-none"></textarea>
        <p v-if="correccion.error" data-campo="correccion-error" class="mt-2 text-xs text-red-300">{{ correccion.error }}</p>
        <div class="flex justify-end gap-2 mt-4">
          <button @click="cerrarCorreccion" data-accion="cancelar-correccion" class="px-4 py-2 rounded-lg text-sm text-amber-200 hover:text-white">Cancelar (ESC)</button>
          <button @click="guardarCorreccion" :disabled="!correccionValida || correccion.guardando" data-accion="guardar-correccion"
                  class="px-4 py-2 rounded-lg text-sm font-bold text-white bg-amber-600 hover:bg-amber-500 disabled:opacity-40 disabled:cursor-not-allowed">
            <i v-if="correccion.guardando" class="fas fa-spinner fa-spin mr-1"></i> Guardar corrección (F10)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted, inject, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'

const route = useRoute()
const router = useRouter()
const notification = useNotificationStore()
const acc = inject('remitosAcciones', null)   // las acciones del listado (anular, fecha, depósito, retiro, sin papel, imprimir)

// [S893, Carlos 26/10] Lo que pasó con la mercadería: mueve el renglón del pedido (RemitosService.corregir_renglon). La causa queda para Stock.
const CAUSAS = [
  { k: 'NO_SALIO', t: 'No salió todo', ayuda: 'El remito dice más de lo que realmente salió' },
  { k: 'SE_PERDIO', t: 'Se perdió', ayuda: 'Salió y se perdió en el camino' },
  { k: 'SE_RECHAZO', t: 'Se rechazó', ayuda: 'Llegó y el cliente no lo aceptó' },
  { k: 'VOLVIO', t: 'Volvió', ayuda: 'Llegó y después volvió una parte (devolución del cliente)' },
]
const etiquetaCausa = (k) => { const c = CAUSAS.find((x) => x.k === k); return c ? c.t.toLowerCase() : (k || '') }
const correccion = reactive({ visible: false, itemId: null, causa: 'SE_PERDIO', real: null, nota: '', guardando: false, error: '' })
const f = ref(null)
const cargando = ref(true)
const error = ref('')
const textoNota = ref('')
const itemNota = ref('')
const guardandoNota = ref(false)
const cajaNota = ref(null)
let saltearCambio = false

const r = computed(() => (f.value ? f.value.remito : {}))
const conNumero = computed(() => !!(f.value && f.value.remito.numero_legal))
const estado = computed(() => (f.value ? f.value.remito.estado : ''))
const anulado = computed(() => estado.value === 'ANULADO')
const enDeposito = computed(() => !!(f.value && f.value.remito.genoma.logistica === 'EN_DEPOSITO'))
const esCorreccion = computed(() => !!(f.value && f.value.remito.es_correccion))
// Se corrige lo que salió: un remito con número, no anulado y que no es él mismo una corrección
const puedeCorregir = computed(() => !!(f.value && f.value.remito.numero_legal && !anulado.value && !esCorreccion.value))
const renglonesCorregibles = computed(() => (f.value ? f.value.items.filter((it) => !it.corrige && it.quedo > 0) : []))
const renglonElegido = computed(() => renglonesCorregibles.value.find((it) => it.id === correccion.itemId) || null)
const correccionValida = computed(() => {
  const it = renglonElegido.value
  const v = Number(correccion.real)
  return !!(it && correccion.causa && correccion.real !== null && correccion.real !== '' && Number.isFinite(v) && v >= 0 && v < it.quedo - 0.0005)
})
const resumenCorreccion = computed(() => {
  const it = renglonElegido.value
  if (!it) return ''
  const v = Number(correccion.real)
  if (correccion.real === null || correccion.real === '' || !Number.isFinite(v)) return `Hoy quedan ${cant(it.quedo)}.`
  if (v < 0) return 'No puede ser negativo.'
  if (v >= it.quedo - 0.0005) return `Tiene que ser menos que lo que queda hoy (${cant(it.quedo)}).`
  return `Se descuentan ${cant(it.quedo - v)}: el pedido vuelve a deber ${cant(it.quedo - v)}.`
})
// lo que esperan las funciones del listado (anular, fecha, depósito, retiro, imprimir)
const remitoLista = computed(() => (f.value ? {
  id: f.value.remito.id, numero_legal: f.value.remito.numero_legal, estado: f.value.remito.estado, flags_estado: f.value.remito.flags_estado,
  razon_social: f.value.cliente ? f.value.cliente.razon_social : '', pedido_id: f.value.pedido ? f.value.pedido.id : null,
  fecha_emision: f.value.remito.fecha_emision, fecha_salida: f.value.remito.fecha_salida, fecha_creacion: f.value.remito.fecha_creacion,
} : null))

const insignias = computed(() => {
  if (!f.value) return []
  const x = f.value.remito, g = x.genoma, m = g.marcas
  const out = []
  const porEstado = { BORRADOR: 'bg-slate-500/15 text-slate-300 border-slate-500/30', EN_CAMINO: 'bg-sky-500/15 text-sky-300 border-sky-500/30', ENTREGADO: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30', ANULADO: 'bg-red-500/15 text-red-300 border-red-500/30' }
  out.push({ k: 'estado', t: String(x.estado || '').replace('_', ' '), c: porEstado[x.estado] || porEstado.BORRADOR })
  if (x.es_correccion) out.push({ k: 'correccion', t: 'Corrección', c: 'bg-amber-500/15 text-amber-300 border-amber-500/30', title: 'Baja lo que quedó de un renglón de otro remito: no tiene papel ni número' })
  if (g.logistica === 'EN_DEPOSITO') out.push({ k: 'en-deposito', t: 'En depósito', c: 'bg-amber-500/15 text-amber-300 border-amber-500/30', title: 'Esperando que lo retire el transporte' })
  if (x.numero_legal) out.push(x.impreso ? { k: 'impreso', t: 'Impreso', c: 'bg-white/5 text-gray-300 border-white/10' } : { k: 'sin-imprimir', t: 'Sin imprimir', c: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30', title: 'Salió sin papel: tiene número pero no se imprimió' })
  if (x.numero_legal && g.logistica && g.logistica !== 'EN_DEPOSITO' && g.estado === 'EMITIDO')
    out.push(m.includes('SALIDA_CONFIRMADA') ? { k: 'salida-confirmada', t: 'Salida confirmada', c: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30', title: 'Una persona, la guía o la copia firmada confirmó que salió' }
                                             : { k: 'salida-asumida', t: 'Salida asumida', c: 'bg-white/5 text-gray-400 border-white/10', title: 'Se da por salido al emitir; nadie lo confirmó todavía' })
  if (m.includes('CIRCULACION_ROSA')) out.push({ k: 'rosa', t: 'Rosa · no se factura', c: 'bg-pink-500/10 text-pink-300 border-pink-500/30', title: 'Remito de un pedido Rosa: no se factura' })
  if (m.includes('SALIDA_DIFERIDA')) out.push({ k: 'salida-diferida', t: 'Salida diferida', c: 'bg-white/5 text-gray-400 border-white/10', title: 'Salió otro día que el de la emisión' })
  if (m.includes('FUE_ANULADO') && x.estado !== 'ANULADO') out.push({ k: 'fue-anulado', t: 'Anulado alguna vez', c: 'bg-white/5 text-gray-400 border-white/10' })
  if (m.includes('DIFERENCIA_RECEPCION')) out.push({ k: 'diferencia', t: 'Diferencia al recibir', c: 'bg-amber-500/10 text-amber-300 border-amber-500/30' })
  return out
})

const fechaCorta = (s) => (s ? new Date(s).toLocaleDateString('es-AR') : '—')
const fechaHora = (s) => (s ? new Date(s).toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' }) : '—')
const cant = (x) => (x === null || x === undefined ? '—' : Number(x).toLocaleString('es-AR', { maximumFractionDigits: 2 }))
const plata = (x) => (x === null || x === undefined ? '—' : '$ ' + Number(x).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }))
const urlWeb = (u) => (/^https?:\/\//i.test(u) ? u : 'https://' + u)
const METODOS = { MOSTRADOR: 'Retira en planta', FLETE_TERCERO: 'Flete de terceros', TRANSPORTE_PROPIO: 'Transporte propio', MOTO_CADETERIA: 'Moto / cadetería', REMITO_EXTERNO: 'Con remito o etiqueta de un tercero' }
const metodo = (m) => (m ? (METODOS[m] || m) : '—')
const nombreRenglon = (id) => { const it = f.value && f.value.items.find((x) => x.id === id); return it ? it.producto : `#${id}` }

const cargar = async () => {
  cargando.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/remitos/ficha/${encodeURIComponent(route.params.ref)}`)
    f.value = data
    const num = data.remito.numero_legal
    // la dirección legible: con número se ve «/remitos/0015-00003031», no el UUID (solo si el número es el de siempre: 4 + 8 dígitos)
    if (num && /^\d{4}-\d{8}$/.test(num) && route.params.ref !== num) { saltearCambio = true; router.replace({ name: 'RemitoFicha', params: { ref: num } }) }
  } catch (e) {
    f.value = null
    error.value = (e.response && e.response.data && e.response.data.detail) || e.message
  } finally {
    cargando.value = false
  }
}

const cerrar = () => {
  if (window.history.state && window.history.state.back) router.back()
  else router.push({ name: 'RemitoList' })
}
const irAlPedido = (donde) => {
  if (!f.value || !f.value.pedido) return
  if (donde === 'entregas') router.push({ name: 'PedidoLogistica', params: { id: f.value.pedido.id } })
  else if (donde === 'devolucion') router.push({ name: 'PedidoLogistica', params: { id: f.value.pedido.id }, query: { devolucion: 1 } })
  else router.push({ name: 'PedidoEditar', params: { id: f.value.pedido.id } })
}
const abrirOtro = (o) => router.push({ name: 'RemitoFicha', params: { ref: (o.numero_legal && /^\d{4}-\d{8}$/.test(o.numero_legal)) ? o.numero_legal : o.id } })

const abrirCorreccion = (causa = null, itemId = null) => {
  const elegibles = renglonesCorregibles.value
  if (!elegibles.length) return
  const it = elegibles.find((x) => x.id === itemId) || elegibles[0]
  Object.assign(correccion, { visible: true, itemId: it.id, causa: causa || correccion.causa || 'SE_PERDIO', real: null, nota: '', guardando: false, error: '' })
}
const cerrarCorreccion = () => { correccion.visible = false }
const guardarCorreccion = async () => {
  if (!correccionValida.value || correccion.guardando || !f.value) return
  correccion.guardando = true
  correccion.error = ''
  try {
    const { data } = await api.post(`/remitos/${f.value.remito.id}/correccion`, {
      remito_item_id: correccion.itemId, cantidad_real: Number(correccion.real), causa: correccion.causa, nota: (correccion.nota || '').trim() || null })
    correccion.visible = false
    notification.add(`Corrección guardada: el pedido vuelve a deber ${cant(data.diferencia)}${data.pedido_reabierto ? ' y se reabrió (estaba cumplido)' : ''}.`, 'success')
    if (acc && acc.refresh) await acc.refresh()   // el listado se vuelve a leer y la ficha se relee sola (versión)
    else await cargar()
  } catch (e) {
    correccion.error = (e.response && e.response.data && e.response.data.detail) || e.message
  } finally {
    correccion.guardando = false
  }
}
const guardarNota = async () => {
  const texto = textoNota.value.trim()
  if (!texto || !f.value || guardandoNota.value) return
  guardandoNota.value = true
  try {
    await api.post(`/remitos/${f.value.remito.id}/notas`, { texto, remito_item_id: itemNota.value ? Number(itemNota.value) : null })
    textoNota.value = ''
    itemNota.value = ''
    notification.add('Nota guardada.', 'success')
    await cargar()
  } catch (e) {
    notification.add('No se pudo guardar la nota: ' + ((e.response && e.response.data && e.response.data.detail) || e.message), 'error')
  } finally {
    guardandoNota.value = false
  }
}

// ESC y F10 son atajos de un botón que está a la vista (Cerrar, Guardar nota). Con una ventana del listado abierta (anular, fecha…), ESC no cierra la ficha.
const onKey = (e) => {
  if (e.key === 'Escape') {
    if (correccion.visible) { e.preventDefault(); cerrarCorreccion(); return }   // la ventana de arriba primero
    if (acc && acc.hayModalAbierto && acc.hayModalAbierto()) return
    e.preventDefault()
    cerrar()
  } else if (e.key === 'F10') {
    e.preventDefault()
    if (correccion.visible) guardarCorreccion()
    else guardarNota()
  }
}

watch(() => route.params.ref, () => { if (saltearCambio) { saltearCambio = false; return } cargar() })
watch(() => (acc && acc.version ? acc.version.value : 0), () => cargar())   // una acción del listado cambió algo: se vuelve a leer
onMounted(() => { window.addEventListener('keydown', onKey); cargar() })
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<style scoped>
.etq { display: block; font-size: 9px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(255, 255, 255, 0.35); margin-bottom: 2px; }
.val { font-size: 0.875rem; color: #fff; }
.no-aplica { font-size: 10px; color: rgba(255, 255, 255, 0.3); font-family: ui-sans-serif, system-ui, sans-serif; }
.btn-ficha { text-align: left; padding: 0.4rem 0.75rem; border-radius: 0.5rem; font-size: 0.75rem; font-weight: 700; color: #fed7aa; border: 1px solid rgba(249, 115, 22, 0.3); transition: background-color 0.15s; }
.btn-ficha:hover { background-color: rgba(249, 115, 22, 0.1); }
</style>
