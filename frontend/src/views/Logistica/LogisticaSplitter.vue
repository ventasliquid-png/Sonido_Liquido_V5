// [IDENTIDAD] - frontend\src\views\Logistica\LogisticaSplitter.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

<template>
  <div class="min-h-screen bg-slate-900 text-white p-6 font-sans">
    <!-- HEADER -->
    <header class="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
      <div>
        <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          <i class="fas fa-boxes-stacked mr-2"></i> Logística Táctica
        </h1>
        <p v-if="localPedido" class="text-slate-400 mt-1">
          Distribución para Pedido #{{ localPedido.id }} - {{ localPedido.cliente?.razon_social }}
        </p>
      </div>
      <div class="flex gap-4">
        <button @click="$router.back()" class="px-4 py-2 hover:bg-slate-800 rounded text-slate-400 transition">
          <i class="fas fa-arrow-left"></i> Volver al Pedido
        </button>
        <div v-if="loading" class="animate-spin h-6 w-6 border-2 border-blue-500 rounded-full border-t-transparent"></div>
      </div>
    </header>

    <!-- ERROR -->
    <div v-if="error" class="bg-red-500/10 border-l-4 border-red-500 p-4 mb-6 text-red-400">
      <p class="font-bold">Error Operativo</p>
      <p>{{ error }}</p>
    </div>
    
    <!-- [GATEKEEPER] SECURITY BANNER -->
    <div v-if="localPedido && !localPedido.liberado_despacho" class="bg-amber-500/10 border-l-4 border-amber-500 p-4 mb-6 text-amber-500 flex justify-between items-center">
      <div>
          <p class="font-bold uppercase tracking-wider text-xs"><i class="fas fa-lock"></i> Bloqueo Financiero Activo</p>
          <p class="text-sm">Este pedido no tiene la marca "Aprobado para Despacho". Los remitos nacerán bloqueados por defecto.</p>
      </div>
      <!-- [S876, P16] La compuerta estaba en el modelo pero nadie la accionaba: este botón la acciona y deja quién y cuándo en la nota del pedido. -->
      <button @click="liberarDespacho" :disabled="liberando" data-accion="liberar-despacho" class="text-xs bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 px-3 py-1.5 rounded border border-amber-500/30 uppercase font-bold transition disabled:opacity-50">
          <i class="fas fa-unlock"></i> {{ liberando ? 'Liberando…' : 'Liberar despacho' }}
      </button>
    </div>
    <div v-else-if="localPedido" class="mb-6 text-emerald-400 text-xs uppercase tracking-wider font-bold" data-estado="despacho-liberado">
      <i class="fas fa-unlock"></i> Despacho liberado
    </div>

    <!-- [S887] Si el pedido ya está remitido completo, se dice acá (en vez de dejar el botón «Imprimir remito» apagado sin explicación): los remitos están abajo, para reimprimirlos -->
    <div v-if="localPedido && itemsPendientes.length === 0 && remitos.some(r => r.estado !== 'ANULADO')" data-estado-remito="completo"
         class="mb-6 bg-emerald-500/10 border-l-4 border-emerald-500 p-4 text-emerald-300">
      <p class="font-bold uppercase tracking-wider text-xs"><i class="fas fa-check-circle"></i> Este pedido ya está remitido completo</p>
      <p class="text-sm">Los remitos están a la derecha: desde ahí se reimprimen (mismo número, no se crea otro).</p>
    </div>

    <div class="grid grid-cols-12 gap-8" v-if="localPedido">
      
      <!-- LEFT PANEL: POOL DE PENDIENTES -->
      <div class="col-span-4 bg-slate-800/50 rounded-xl p-4 border border-slate-700 flex flex-col h-[calc(100vh-200px)]">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold text-amber-400">
            <i class="fas fa-cubes"></i> Pool de Pendientes
          </h2>
          <span class="text-xs bg-amber-500/20 text-amber-300 px-2 py-1 rounded-full">
            {{ itemsPendientes.length }} Ítems
          </span>
        </div>

        <div class="flex-1 overflow-y-auto space-y-3 pr-2">
          <div v-for="item in itemsPendientes" :key="item.id" 
             draggable="true"
             @dragstart="onDragStart($event, item)"
             class="bg-slate-800 p-3 rounded-lg border border-slate-600 hover:border-amber-500/50 cursor-grab active:cursor-grabbing transition group select-none">
            
            <div class="flex justify-between items-start">
              <div>
                <p class="font-bold text-white">{{ item.producto?.nombre }}</p>
                <p class="text-xs text-slate-400">SKU: {{ item.producto?.sku }}</p>
              </div>
              <div class="text-right">
                <p class="text-amber-400 font-bold text-lg">{{ item.cantidad_pendiente }}</p>
                <p class="text-[10px] text-slate-500 uppercase">Pendiente</p>
              </div>
            </div>

            <!-- Progres Bar -->
            <div class="mt-2 h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
               <div class="h-full bg-amber-500 transition-all duration-500" 
                    :style="{ width: (item.cantidad_remitida / item.cantidad_original * 100) + '%' }"></div>
            </div>
            <div class="flex justify-between text-[10px] text-slate-500 mt-1">
               <span>Total: {{ item.cantidad_original }}</span>
               <span>En Viaje: {{ item.cantidad_remitida }}</span>
            </div>
          </div>

          <div v-if="itemsPendientes.length === 0" class="text-center py-10 text-slate-500 bg-slate-800/30 rounded-lg border-2 border-dashed border-slate-700">
             <i class="fas fa-check-circle text-4xl mb-2 text-green-500/50"></i>
             <p>Todo Asignado</p>
          </div>
        </div>
      </div>

      <!-- RIGHT PANEL: REMITOS ACTIVOS (CANVAS) -->
      <div class="col-span-8 space-y-6 overflow-y-auto h-[calc(100vh-200px)] pr-2">
        
        <!-- ACTION BAR -->
        <div class="flex justify-between items-end">
           <h2 class="text-xl font-semibold text-blue-400">Viajes Activos (Remitos)</h2>
           <!-- [S893, Carlos 26/10] El Remito Manual se retiró: un remito nuevo se arma SIEMPRE desde el pedido, con «Imprimir remito». -->
           <div class="flex gap-2">
              <!-- [Etapa 4, PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md §6] Pantalla de armado
                   (D3, primera pantalla): elige renglones del pedido por pedido_item_id, nunca
                   texto libre. -->
              <button @click="openArmarModal" :disabled="itemsPendientes.length === 0" :title="itemsPendientes.length === 0 ? 'No queda nada por remitar: el pedido ya está remitido completo' : 'Imprimir el remito de lo que queda por remitar'"
                class="bg-amber-600 hover:bg-amber-500 disabled:bg-slate-700 disabled:cursor-not-allowed disabled:text-slate-500 text-white px-4 py-2 rounded-lg shadow-lg hover:shadow-amber-500/20 transition flex items-center gap-2">
                <i class="fas fa-print"></i> Imprimir remito
              </button>
              <!-- [S893, Carlos 26/10] La devolución se fundió con la corrección «Volvió» de la ficha del remito: se elige de QUÉ remito volvió (y qué renglón) y se corrige ahí, con su causa.
                   Debajo sigue siendo lo de la Etapa 6 (un renglón de cantidad negativa, el pedido vuelve a deber), pero atado al remito de origen. -->
              <button @click="abrirDevolucion" :disabled="remitosParaDevolver.length === 0" data-accion="registrar-devolucion"
                :title="remitosParaDevolver.length === 0 ? 'No hay ningún remito con número y mercadería entregada' : 'Registrar lo que volvió: se elige de qué remito'"
                class="bg-rose-700 hover:bg-rose-600 disabled:bg-slate-700 disabled:cursor-not-allowed disabled:text-slate-500 text-white px-4 py-2 rounded-lg shadow-lg hover:shadow-rose-500/20 transition flex items-center gap-2">
                <i class="fas fa-rotate-left"></i> Registrar Devolución
              </button>
           </div>
        </div>

        <!-- REMITOS LIST -->
        <div v-if="remitos.length === 0" class="text-center py-20 bg-slate-800/50 rounded-xl border border-dashed border-slate-700">
           <p class="text-slate-500">No hay remitos creados para este pedido.</p>
           <p class="text-sm text-slate-600">Con «Imprimir remito» se arma el primero para comenzar la distribución.</p>
        </div>

        <div v-for="remito in remitos" :key="remito.id" 
             @dragover.prevent @drop="onDrop($event, remito)"
             :class="{'opacity-75 grayscale': remito.estado === 'EN_CAMINO'}"
             class="bg-slate-800 rounded-xl border border-slate-700 p-4 transition-all duration-300 hover:shadow-xl hover:border-slate-600">
          
          <!-- HEADER REMITO -->
          <div class="flex justify-between items-start mb-4 pb-4 border-b border-slate-700/50">
             <div class="flex items-center gap-4">
                <div class="bg-blue-500/10 p-3 rounded-lg text-blue-400">
                   <i class="fas fa-truck text-xl"></i>
                </div>
                <div>
                   <h3 class="font-bold text-lg text-white">
                      Remito #{{ remito.numero_legal || 'BORRADOR' }}
                      <!-- [S876] Estos dos avisos son de un remito todavía BORRADOR: uno de mostrador nace ENTREGADO. -->
                      <span v-if="remito.estado === 'BORRADOR' && !remito.aprobado_para_despacho" class="ml-2 text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded border border-red-500/30">
                         <i class="fas fa-lock"></i> Bloqueado
                      </span>
                      <span v-else-if="remito.estado === 'BORRADOR' && !remito.numero_legal" class="ml-2 text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded border border-amber-500/30">
                         <i class="fas fa-file-pdf"></i> Sin numerar — generá el PDF Legal antes de despachar
                      </span>
                   </h3>
                   <div class="flex gap-4 text-sm text-slate-400 mt-1">
                      <p><i class="fas fa-map-marker-alt"></i> {{ remitoDireccionLabel(remito) }}</p>
                      <p><i class="fas fa-building"></i> {{ remitoTransporteLabel(remito) }}
                         <!-- [S890] después de imprimir, el enlace para pedir el retiro al transporte -->
                         <a v-if="webRetiroDe(remito.transporte_id)" :href="urlWeb(webRetiroDe(remito.transporte_id))" target="_blank" rel="noopener" data-enlace="web-retiro-remito"
                            class="ml-2 text-[11px] text-amber-400 hover:text-amber-300 underline">Pedir retiro <i class="fas fa-arrow-up-right-from-square text-[9px]"></i></a></p>
                      <!-- [S876] Cómo salió ESTA entrega (congelado al armar). Vacío en remitos anteriores. -->
                      <p v-if="remito.metodo_entrega" class="text-[10px] font-bold uppercase self-center bg-slate-700/60 text-slate-300 px-2 py-0.5 rounded border border-slate-600"
                         :title="metodoLabel(remito.metodo_entrega)">
                         {{ metodoCorto(remito.metodo_entrega) }}
                      </p>
                   </div>
                </div>
             </div>

             <div class="text-right">
                <div class="inline-flex items-center gap-2 mb-2">
                   <span :class="getStatusClass(remito.estado)" class="px-3 py-1 rounded-full text-xs font-bold border">
                      {{ remito.estado }}
                   </span>
                </div>
                <div class="flex flex-col items-end gap-1">
                    <div v-if="remito.estado === 'BORRADOR' && remito.aprobado_para_despacho && remito.numero_legal">
                       <button @click="tryDespachar(remito)" class="text-xs bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded transition w-full">
                          <i class="fas fa-paper-plane mr-1"></i> Despachar
                       </button>
                    </div>
                    <!-- PDF LEGAL BUTTON (una corrección no tiene papel ni número) -->
                    <button v-if="!esCorreccion(remito)" @click="downloadLegalPDF(remito)" class="text-xs bg-slate-600 hover:bg-slate-500 text-white px-3 py-1 rounded transition w-full mt-1 border border-slate-500">
                        <i class="fas fa-file-pdf mr-1"></i> {{ impresoRemito(remito) ? 'Reimprimir' : 'Imprimir PDF' }}
                    </button>
                    <!-- [S891] Vista previa: solo sin número; no gasta el número ni queda guardada -->
                    <button v-if="!remito.numero_legal && remito.estado !== 'ANULADO' && !esCorreccion(remito)" @click="vistaPreviaRemito(remito)" data-accion="vista-previa"
                            class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded transition w-full border border-slate-600">
                        <i class="fas fa-eye mr-1"></i> Vista previa
                    </button>
                    <!-- [S893, Carlos 26/10] «Ver el remito»: el documento verdadero en pantalla, sin imprimir (reemplaza al dibujo HTML, que no seguía las reglas del papel) -->
                    <button v-if="remito.numero_legal && !esCorreccion(remito)" @click="verRemito(remito)" data-accion="ver-remito" class="text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-1 rounded transition w-full">
                        <i class="fas fa-eye mr-1"></i> Ver el remito
                    </button>
                </div>
             </div>
          </div>

          <!-- ITEMS REMITO -->
          <div class="bg-slate-900/50 rounded-lg p-3 min-h-[80px] border border-slate-700/50 mb-2">
             <p v-if="remito.items.length === 0" class="text-center text-slate-600 text-sm py-4 italic">
                Arrastre ítems aquí para asignarlos a este viaje
             </p>
             <div v-else class="space-y-2">
                <div v-for="rItem in remito.items" :key="rItem.id" class="flex justify-between items-center text-sm bg-slate-800 p-2 rounded border border-slate-700">
                   <span class="text-slate-300 flex items-center gap-2 flex-wrap">
                      <span v-if="rItem.cantidad < 0" class="text-[9px] font-bold uppercase bg-rose-500/20 text-rose-300 px-1.5 py-0.5 rounded">
                         <i class="fas fa-rotate-left"></i> Devolución
                      </span>
                      <!-- [S876] Salió sin ser venta firme: no entra a facturación hasta resolverlo (Facturar) o devolverlo. -->
                      <span v-if="rItem.motivo_no_facturable" :class="motivoClase(rItem.motivo_no_facturable)"
                            class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded border"
                            title="Salió sin ser venta firme. Se resuelve facturándolo (botón Facturar) o con una devolución.">
                         {{ motivoLabel(rItem.motivo_no_facturable) }}
                      </span>
                      {{ getProductName(rItem.pedido_item_id) }}
                   </span>
                   <span class="flex items-center gap-3">
                      <button v-if="rItem.motivo_no_facturable && remito.estado !== 'ANULADO'" @click="resolverFacturar(rItem)"
                              class="text-[10px] font-bold uppercase bg-emerald-600/80 hover:bg-emerald-500 text-white px-2 py-1 rounded transition"
                              title="Lo vendido pasa a facturable: sigue el camino normal de facturación">
                         <i class="fas fa-file-invoice-dollar mr-1"></i> Facturar
                      </button>
                      <span class="font-mono font-bold" :class="rItem.cantidad < 0 ? 'text-rose-400' : 'text-blue-300'">
                         {{ rItem.cantidad }} un.
                      </span>
                   </span>
                </div>
             </div>
          </div>
        </div>

      </div>
    </div>

    <!-- MODAL ADD ITEM -->
    <div v-if="showAddItemModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
       <div class="bg-slate-800 p-6 rounded-2xl w-full max-w-sm shadow-2xl border border-slate-700">
          <h3 class="text-lg font-bold text-white mb-4">Asignar Cantidad</h3>
          <p class="text-sm text-slate-400 mb-2">Producto: <span class="text-white">{{ dragItem?.producto?.nombre }}</span></p>
          <p class="text-sm text-slate-400 mb-4">Pendiente: {{ dragItem?.cantidad_pendiente }}</p>
          
          <input type="number" v-model.number="addItemAmount" :max="dragItem?.cantidad_pendiente" min="0.1" 
                 class="w-full bg-slate-900 border border-slate-700 rounded p-3 text-2xl text-center text-white font-mono focus:border-blue-500 outline-none">
          
          <div class="flex justify-end gap-3 mt-6">
             <button @click="cancelDrop" class="text-slate-400 hover:text-white px-4 py-2">Cancelar</button>
             <button @click="confirmDrop" class="bg-amber-600 hover:bg-amber-500 text-white px-6 py-2 rounded-lg font-bold">
                Asignar
             </button>
          </div>
       </div>
    </div>

    <!-- MODAL ARMAR PR [Etapa 4] -->
    <div v-if="showArmarModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
       <div class="bg-slate-800 p-6 rounded-2xl w-full max-w-2xl shadow-2xl border border-slate-700">
          <h3 class="text-lg font-bold text-white mb-1"><i class="fas fa-print mr-2 text-amber-400"></i>Imprimir remito</h3>
          <p class="text-xs text-slate-400 mb-4">
             <strong class="text-slate-200">Esto voy a imprimir: el pedido completo.</strong> Si no cambiás nada, el remito es una copia del pedido.
             Podés modificarlo: destildá un renglón o bajá la cantidad, y lo que no entre queda pendiente para otro remito.
             Al imprimir se le asigna el próximo número 0015.
          </p>

          <!-- [S876] Cómo sale ESTA entrega. Se congela al armar el remito. -->
          <div class="mb-4 p-3 rounded-lg border border-slate-700 bg-slate-900/40 space-y-2">
             <label class="block text-[10px] font-bold uppercase tracking-widest text-slate-400">Cómo sale la entrega</label>
             <select v-model="armarMetodo" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white focus:border-amber-500 outline-none">
                <option value="" disabled>Elegí cómo sale...</option>
                <option v-for="m in METODOS_ENTREGA" :key="m.value" :value="m.value">{{ m.label }}</option>
             </select>
             <p v-if="armarMetodo === 'MOSTRADOR'" class="text-xs text-slate-400">
                <i class="fas fa-store mr-1"></i> Retiro en planta: sin traslado ni transporte. El domicilio queda en la oficina (Roseti 1482).
             </p>
             <template v-else-if="armarMetodo">
                <div v-if="armarMetodo === 'FLETE_TERCERO'">
                   <!-- [S890, Carlos 21/10] El título del recuadro es el enlace a la web del transporte para PEDIR EL RETIRO (si está cargada en el padrón),
                        con un botón para copiarla. «Nuevo transporte» abre el padrón en otra pestaña y ↻ recarga la lista. -->
                   <div class="flex items-center justify-between mb-1 gap-2">
                      <a v-if="transporteElegido?.web_retiro" :href="urlWeb(transporteElegido.web_retiro)" target="_blank" rel="noopener" data-enlace="web-retiro"
                         class="text-[11px] font-bold text-amber-400 hover:text-amber-300 underline truncate" :title="transporteElegido.web_retiro">
                         Pedir retiro en {{ transporteElegido.nombre }} <i class="fas fa-arrow-up-right-from-square text-[9px]"></i></a>
                      <label v-else class="block text-[10px] uppercase text-slate-500">Transporte</label>
                      <span class="flex items-center gap-2 shrink-0 text-[10px]">
                         <button v-if="transporteElegido?.web_retiro" type="button" @click="copiarWebRetiro" data-accion="copiar-web-retiro"
                                 class="text-slate-400 hover:text-white" title="Copiar la dirección de la web de retiro"><i class="fas fa-copy"></i> {{ webCopiada ? 'Copiada' : 'Copiar' }}</button>
                         <button type="button" @click="abrirPadronTransportes" data-accion="nuevo-transporte" class="text-slate-400 hover:text-white"
                                 title="Abre el padrón de transportes en otra pestaña; después tocá ↻ para que aparezca acá"><i class="fas fa-plus"></i> Nuevo transporte</button>
                         <button type="button" @click="logisticaStore.fetchEmpresas()" data-accion="recargar-transportes" class="text-slate-400 hover:text-white" title="Recargar la lista de transportes"><i class="fas fa-rotate-right"></i></button>
                      </span>
                   </div>
                   <select v-model="armarTransporteId" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white focus:border-amber-500 outline-none">
                      <option value="" disabled>Elegí el transporte...</option>
                      <option v-for="emp in logisticaStore.empresas" :key="emp.id" :value="emp.id">{{ emp.nombre }}</option>
                   </select>
                   <p v-if="transporteElegido && !transporteElegido.web_retiro" class="text-[11px] text-slate-500 mt-1">Sin web para pedir el retiro: se carga en el padrón de transportes.</p>
                </div>
                <div v-if="clientDomicilios.length > 0">
                   <label class="block text-[10px] uppercase text-slate-500 mb-1">
                      {{ armarMetodo === 'FLETE_TERCERO' ? 'Domicilio de entrega (o depósito del transportista)' : 'Domicilio de entrega' }}
                   </label>
                   <select v-model="armarDomicilioId" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white focus:border-amber-500 outline-none">
                      <option value="">El del pedido</option>
                      <option v-for="d in clientDomicilios" :key="d.id" :value="d.id">{{ getAddressLabel(d.id) }}</option>
                   </select>
                </div>
             </template>
          </div>

          <div class="max-h-72 overflow-y-auto space-y-2 pr-1">
             <div v-for="sel in armarSeleccion" :key="sel.pedido_item_id"
                  class="flex items-center gap-3 bg-slate-900/50 border border-slate-700 rounded-lg p-3"
                  :class="{'opacity-50': !sel.marcado}">
                <input type="checkbox" v-model="sel.marcado" class="w-4 h-4 accent-amber-500">
                <div class="flex-1 min-w-0">
                   <p class="text-sm text-white truncate">{{ sel.producto_nombre }}</p>
                   <p class="text-[10px] text-slate-500 uppercase">Pendiente: {{ sel.cantidad_pendiente }}</p>
                </div>
                <!-- [S876] Por qué sale sin ser venta firme (por renglón: un mismo envío puede llevar renglones de
                     venta firme y uno en consignación). Vacío = se factura normal. -->
                <select v-model="sel.motivo" :disabled="!sel.marcado"
                        title="Si este renglón sale sin ser venta firme, elegí por qué"
                        class="w-40 bg-slate-900 border border-slate-700 rounded p-2 text-xs text-white focus:border-amber-500 outline-none disabled:opacity-40">
                   <option value="">Venta firme</option>
                   <option v-for="mo in MOTIVOS_NO_FACTURABLE" :key="mo.value" :value="mo.value">{{ mo.label }}</option>
                </select>
                <input type="number" v-model.number="sel.cantidad" :max="sel.cantidad_pendiente" min="0.01"
                       :disabled="!sel.marcado"
                       class="w-24 bg-slate-900 border border-slate-700 rounded p-2 text-right text-white font-mono focus:border-amber-500 outline-none disabled:opacity-40">
             </div>
             <div v-if="armarSeleccion.length === 0" class="text-center py-6 text-slate-500 text-sm">
                No hay renglones pendientes en este pedido.
             </div>
          </div>

          <div class="flex justify-end gap-3 mt-6">
             <p v-if="!armarMetodo" class="mr-auto self-center text-xs text-amber-400"><i class="fas fa-arrow-up mr-1"></i> Elegí cómo sale la entrega para poder imprimir</p>
             <button @click="cancelArmar" class="text-slate-400 hover:text-white px-4 py-2">Cancelar</button>
             <button @click="confirmArmar(false)" :disabled="!armarSeleccion.some(s => s.marcado) || !armarMetodo"
                     title="Deja el remito armado, sin imprimir ni numerarlo todavía"
                     class="text-slate-300 hover:text-white border border-slate-600 hover:border-slate-400 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2 rounded-lg text-sm">
                Solo armar
             </button>
             <button @click="confirmArmar(true)" :disabled="!armarSeleccion.some(s => s.marcado) || !armarMetodo"
                     class="bg-amber-600 hover:bg-amber-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-bold">
                <i class="fas fa-print mr-1"></i> Imprimir remito
             </button>
          </div>
       </div>
    </div>

    <!-- [S890, Carlos 21/10] Al terminar el remito aparecen el valor declarado y los bultos (no son casilleros del formulario).
         Se pueden ignorar: «Cancelar» sigue igual, con 1 bulto y el valor en blanco. -->
    <div v-if="datosTransporte.visible" data-modal="datos-transporte" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-[60]">
       <div class="bg-slate-800 p-6 rounded-2xl w-full max-w-sm shadow-2xl border border-amber-700/50">
          <h3 class="text-lg font-bold text-white mb-1"><i class="fas fa-boxes-stacked mr-2 text-amber-400"></i>Para el transporte</h3>
          <p class="text-xs text-slate-400 mb-4">Van impresos en el remito. «Cancelar» sigue con 1 bulto y el valor sugerido.</p>
          <label class="block text-[10px] uppercase text-slate-500 mb-1">Valor declarado</label>
          <input v-model="datosTransporte.valor" data-campo="valor-declarado" inputmode="decimal" placeholder="Ej: 2.980.000"
                 class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white font-mono mb-1 focus:border-amber-500 outline-none" />
          <p class="text-[11px] text-slate-500 mb-3">Sugerido: el neto de lo que sale, sin impuestos. Se puede cambiar.</p>
          <label class="block text-[10px] uppercase text-slate-500 mb-1">Bultos</label>
          <input type="number" min="1" step="1" v-model.number="datosTransporte.bultos" data-campo="bultos"
                 class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white font-mono mb-5 focus:border-amber-500 outline-none" />
          <div class="flex justify-end gap-3">
             <button @click="omitirDatosTransporte" data-accion="omitir-datos" title="Sigue con 1 bulto y el valor sugerido"
                     class="text-slate-400 hover:text-white px-4 py-2">Cancelar</button>
             <button @click="aceptarDatosTransporte" data-accion="aceptar-datos"
                     class="bg-amber-600 hover:bg-amber-500 text-white px-6 py-2 rounded-lg font-bold">Aceptar</button>
          </div>
       </div>
    </div>

    <!-- [S893] ¿DE QUÉ REMITO VOLVIÓ? -> la ficha de ese remito con la corrección «Volvió» abierta -->
    <div v-if="showElegirRemito" data-modal="elegir-remito-devolucion" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50" @click.self="showElegirRemito = false">
       <div class="bg-slate-800 p-6 rounded-2xl w-full max-w-lg shadow-2xl border border-rose-900/50">
          <h3 class="text-lg font-bold text-white mb-1"><i class="fas fa-rotate-left mr-2 text-rose-400"></i>¿De qué remito volvió?</h3>
          <p class="text-xs text-slate-400 mb-4">La devolución se registra sobre el renglón del remito del que salió la mercadería. Se abre ese remito con la corrección «Volvió».</p>
          <ul class="max-h-72 overflow-y-auto divide-y divide-slate-700 rounded-lg border border-slate-700">
             <li v-for="r in remitosParaDevolver" :key="r.id" class="flex items-center gap-3 px-3 py-2 hover:bg-slate-700/40">
                <span class="font-mono text-sm font-bold text-rose-300 shrink-0">{{ r.numero_legal }}</span>
                <span class="text-xs text-slate-400 truncate flex-1">{{ resumenRemito(r) }}</span>
                <button @click="irADevolver(r)" data-accion="devolver-de-este-remito" class="px-3 py-1 rounded-md text-xs font-bold text-white bg-rose-700 hover:bg-rose-600 whitespace-nowrap">Elegir</button>
             </li>
          </ul>
          <div class="flex justify-end mt-4"><button @click="showElegirRemito = false" class="text-slate-400 hover:text-white px-4 py-2">Cancelar (ESC)</button></div>
       </div>
    </div>


  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useRemitosStore } from '@/stores/remitos';
import { useLogisticaStore } from '@/stores/logistica';
import { usePedidosStore } from '@/stores/pedidos'; // Assuming this exists to fetch full pedido details
// If not, we might need to fetch manually. Assuming it exists.
import api from '@/services/api';
import {
    METODOS_ENTREGA, MOTIVOS_NO_FACTURABLE, ETIQUETA_OFICINA,
    metodoCorto, metodoLabel, motivoLabel, motivoClase,
} from '@/utils/remitoEntrega';

const route = useRoute();
const router = useRouter(); // [S890] para abrir el padrón de transportes en otra pestaña
const remitosStore = useRemitosStore();
const logisticaStore = useLogisticaStore();
// const pedidosStore = usePedidosStore(); // Let's try to just fetch manually or use store if robust

const localPedido = ref(null);
const loading = ref(true);
const error = ref(null);
const clientDomicilios = ref([]);

// Modals
const showAddItemModal = ref(false);
const showArmarModal = ref(false); // [Etapa 4]
const armarSeleccion = ref([]); // [Etapa 4]
// [S876] Cómo sale la entrega: método (lista cerrada), transporte (solo FLETE_TERCERO) y domicilio.
const armarMetodo = ref('');
const armarTransporteId = ref('');
const armarDomicilioId = ref('');
const showElegirRemito = ref(false); // [S893] ¿de qué remito volvió?

// Drag & Drop
const dragItem = ref(null);
const targetRemito = ref(null);
const addItemAmount = ref(0);

// --- Computed ---
const itemsPendientes = computed(() => remitosStore.itemsPendientes);
const remitos = computed(() => remitosStore.remitos);
// [Etapa 6] Pool de una devolución: renglones con algo entregado (neto), a diferencia de
// itemsPendientes (renglones con saldo a favor del cliente) -- un renglón CUMPLIDO no tiene
// pendiente pero sí puede tener devolución.
const itemsConEntrega = computed(() =>
  (localPedido.value?.items || []).filter(i => (i.cantidad_entregada || 0) > 0)
);

// --- Methods ---

onMounted(async () => {
    const id = route.params.id;
    if (!id) {
        error.value = "ID de Pedido no especificado";
        return;
    }
    
    await loadData(id);
    // [S887] «Hacer remito» en la ficha del pedido llega con ?armar=1: el cuadro «Imprimir remito» sale abierto (si hay algo pendiente de remitar)
    if (route.query.armar && itemsPendientes.value.length > 0) openArmarModal();
});

async function loadData(id) {
    loading.value = true;
    try {
        // 1. Load Pedido Full
        const resPedido = await api.get(`/pedidos/${id}`);
        localPedido.value = resPedido.data;
        remitosStore.currentPedido = resPedido.data;

        // 2. Load Remitos
        await remitosStore.fetchRemitos(id);
        
        // 3. Load Logistica Data
        await logisticaStore.fetchEmpresas();
        await logisticaStore.fetchAllNodos(); 
        
        // 4. Client Domicilios
        // [S868] GET /pedidos/{id} devuelve el cliente anidado, no cliente_id: con el campo viejo
        // esto nunca entraba y la pantalla mostraba "Dirección Desconocida".
        if (idCliente.value) {
             const resClient = await api.get(`/clientes/${idCliente.value}`);
             clientDomicilios.value = resClient.data.domicilios || [];
        }

    } catch (e) {
        error.value = e.message;
    } finally {
        loading.value = false;
    }
}

// Helpers
const getAddressLabel = (id) => {
   // [S868] El domicilio viene con calle/numero/localidad (o resumen), no con "direccion":
   // con el campo viejo la pantalla mostraba "undefined (Localidad)".
   const dom = clientDomicilios.value.find(d => d.id === id);
   if (!dom) return 'Dirección Desconocida';
   const calle = dom.resumen || [dom.calle, dom.numero].filter(Boolean).join(' ') || 'Sin calle';
   return dom.localidad ? `${calle} (${dom.localidad})` : calle;
};

const getTransportLabel = (id) => {
   const opt = logisticaStore.transportOptions.find(t => t.id === id);
   // If not found (maybe raw ID?), try to find name manually or shorten UUID
   return opt ? opt.nombre : 'Transporte...';
};

const getProductName = (pedidoItemId) => {
   const item = localPedido.value?.items.find(i => i.id === pedidoItemId);
   return item?.producto?.nombre || 'Producto Desconocido';
};

// [S868] El pedido trae el cliente anidado; algunas respuestas viejas traían cliente_id suelto.
const idCliente = computed(() => localPedido.value?.cliente?.id || localPedido.value?.cliente_id || null);

const getStatusClass = (status) => {
   switch(status) {
      case 'BORRADOR': return 'bg-slate-700 text-slate-300 border-slate-600';
      case 'EN_CAMINO': return 'bg-blue-900/50 text-blue-300 border-blue-500/50';
      case 'ENTREGADO': return 'bg-green-900/50 text-green-300 border-green-500/50';
      default: return 'bg-slate-800 text-slate-400';
   }
};

// [S876, P16] Liberar el despacho del pedido (compuerta financiera). El servidor aprueba también los PR en borrador ya armados
// y deja la constancia (usuario y hora) en la nota del pedido; acá se vuelve a cargar todo para que los avisos de bloqueo se apaguen.
const liberando = ref(false);
const liberarDespacho = async () => {
    if (!localPedido.value || liberando.value) return;
    const bloqueados = (remitosStore.remitos || []).filter(r => r.estado === 'BORRADOR' && !r.aprobado_para_despacho).length;
    const extra = bloqueados === 1 ? '\n\nEl remito en borrador ya armado de este pedido también queda aprobado.'
        : bloqueados > 1 ? `\n\nLos ${bloqueados} remitos en borrador ya armados de este pedido también quedan aprobados.` : '';
    if (!confirm(`¿Liberar el despacho del pedido #${localPedido.value.id}?${extra}\n\nQueda registrado con tu usuario y la hora en la nota del pedido.`)) return;
    liberando.value = true;
    error.value = null;
    try {
        await api.post(`/pedidos/${localPedido.value.id}/liberar-despacho`);
        await loadData(localPedido.value.id);
    } catch (e) {
        error.value = e.response?.data?.detail || e.message || 'No se pudo liberar el despacho.';
    } finally {
        liberando.value = false;
    }
};

// Remito Actions
const tryDespachar = async (remito) => {
   if (!confirm("¿Confirmar salida física de mercadería? Esto descontará stock.")) return;
   try {
      await remitosStore.despacharRemito(remito.id);
   } catch (err) {
      // [DISENO_CIRCUITO_PR_S869.md §9.3] El backend ahora rechaza el despacho si
      // aprobado_para_despacho es false; sin este catch el error quedaba sin mostrarse.
      alert(remitosStore.error || "No se pudo despachar el remito.");
   }
};

// [Etapa 4] Pantalla de armado (D3, primera pantalla)
const openArmarModal = () => {
    armarSeleccion.value = itemsPendientes.value.map(item => ({
        pedido_item_id: item.id,
        producto_nombre: item.producto?.nombre || 'Ítem',
        cantidad_pendiente: item.cantidad_pendiente,
        cantidad: item.cantidad_pendiente,
        // [S890] neto por unidad del renglón (subtotal ya descontado, sin IVA): base del valor declarado sugerido
        neto_unitario: item.cantidad_original ? (Number(item.subtotal) || 0) / item.cantidad_original : 0,
        motivo: '',
        marcado: true, // [S887] por defecto el remito es el pedido completo; el parcial es destildar o bajar la cantidad
    }));
    // [S876] Un pedido con transporte habitual sugiere FLETE_TERCERO; sin transporte no se adivina
    // nada: hay que elegir (mostrador, moto, transporte propio...). Es el hecho de esta entrega.
    armarMetodo.value = localPedido.value?.transporte_id ? 'FLETE_TERCERO' : '';
    armarTransporteId.value = localPedido.value?.transporte_id || '';
    armarDomicilioId.value = '';
    showArmarModal.value = true;
};

const cancelArmar = () => {
    showArmarModal.value = false;
    armarSeleccion.value = [];
    armarMetodo.value = '';
    armarTransporteId.value = '';
    armarDomicilioId.value = '';
};

// [S887] Un remito recién armado se imprime abriendo su PDF (el servidor lo numera con el próximo 0015). Si el navegador bloquea la ventana, se descarga.
const imprimirArmado = (remito) => {
    const ventana = window.open(`/remitos/${remito.id}/pdf`, '_blank');
    if (!ventana) downloadLegalPDF(remito);
    else if (localPedido.value?.id) setTimeout(() => remitosStore.fetchRemitos(localPedido.value.id), 1500);   // [S891] número e IMPRESO
};

const confirmArmar = async (imprimir = false) => {
    const elegidos = armarSeleccion.value.filter(s => s.marcado);
    if (elegidos.length === 0) return;
    if (!armarMetodo.value) { alert('Elegí cómo sale la entrega.'); return; }
    if (armarMetodo.value === 'FLETE_TERCERO' && !armarTransporteId.value) { alert('Elegí el transporte.'); return; }

    // [Etapa 4, punto 5 -- confirmación obligatoria en parciales, sin gradación por tamaño]
    // Si algún renglón elegido no completa el pendiente, no alcanza con un clic: hay que
    // escribir la cantidad pendiente para confirmar. Se corta todo el armado si cualquiera
    // de las confirmaciones se cancela o no coincide -- no se arma "lo que sí se confirmó".
    for (const sel of elegidos) {
        if (sel.cantidad < sel.cantidad_pendiente) {
            const tecleado = prompt(
                `"${sel.producto_nombre}" queda con ${sel.cantidad_pendiente - sel.cantidad} pendiente ` +
                `(de ${sel.cantidad_pendiente}). Escribí ${sel.cantidad_pendiente} para confirmar que ` +
                `hacés un remito parcial.`
            );
            if (tecleado === null || Number(tecleado) !== sel.cantidad_pendiente) {
                alert('Armado cancelado: la cantidad pendiente no coincidió.');
                return;
            }
        }
    }

    // [S890] Al terminar el remito, antes de armarlo, la ventana del valor declarado y los bultos. El valor viene sugerido:
    // el neto de lo que sale (sin impuestos); si el remito es el pedido completo, es el neto del pedido (Carlos, 21/10).
    const sugerido = netoDelRemito(elegidos);
    Object.assign(datosTransporte, { visible: true, bultos: 1, valor: sugerido ? formatoAR(sugerido) : '', sugerido, imprimir, elegidos });
};

// [S890, Carlos 21/10] «El valor declarado es siempre el del producto antes de los impuestos»: neto de los renglones que salen, con el
// descuento global del pedido prorrateado. Con el pedido completo da el neto del pedido (suma de subtotales menos el descuento global).
const netoDelRemito = (elegidos) => {
    const subtotales = (localPedido.value?.items || []).reduce((a, it) => a + (Number(it.subtotal) || 0), 0);
    const factor = subtotales > 0 ? (subtotales - (Number(localPedido.value?.descuento_global_importe) || 0)) / subtotales : 1;
    const neto = elegidos.reduce((a, s) => a + (s.neto_unitario || 0) * (Number(s.cantidad) || 0), 0) * factor;
    return neto > 0 ? Math.round(neto * 100) / 100 : null;
};
const formatoAR = (n) => n.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// [S890, Carlos 21/10] Ventana del final del armado. «Cancelar» no corta el remito: sigue con 1 bulto y el valor sugerido.
const datosTransporte = reactive({ visible: false, bultos: 1, valor: '', sugerido: null, imprimir: false, elegidos: [] });
// «2.980.000», «2980000,50» o «$ 2.980.000» -> número; vacío o inválido -> null (en blanco en el papel)
const montoAR = (texto) => {
    const limpio = String(texto ?? '').replace(/[$\s]/g, '').replace(/\./g, '').replace(',', '.');
    const n = Number(limpio);
    return limpio && isFinite(n) && n > 0 ? n : null;
};
const aceptarDatosTransporte = () => {
    const bultos = Number.isInteger(datosTransporte.bultos) && datosTransporte.bultos > 0 ? datosTransporte.bultos : 1;
    datosTransporte.visible = false;
    ejecutarArmado(datosTransporte.imprimir, datosTransporte.elegidos, bultos, montoAR(datosTransporte.valor));
};
// «Cancelar» = desestimar la ventana: sigue con lo que proponía (1 bulto y el valor sugerido; sin sugerido, en blanco).
const omitirDatosTransporte = () => {
    datosTransporte.visible = false;
    ejecutarArmado(datosTransporte.imprimir, datosTransporte.elegidos, 1, datosTransporte.sugerido);
};

const ejecutarArmado = async (imprimir, elegidos, bultos, valorDeclarado) => {
    try {
        const payload = {
            pedido_id: localPedido.value.id,
            metodo_entrega: armarMetodo.value,
            bultos,
            ...(valorDeclarado ? { valor_declarado: valorDeclarado } : {}),
            items: elegidos.map(s => ({
                pedido_item_id: s.pedido_item_id,
                cantidad: s.cantidad,
                ...(s.motivo ? { motivo_no_facturable: s.motivo } : {}),
            })),
        };
        // MOSTRADOR no manda domicilio ni transporte: el backend usa la oficina y deja el transporte vacío.
        if (armarMetodo.value !== 'MOSTRADOR') {
            if (armarDomicilioId.value) payload.domicilio_entrega_id = armarDomicilioId.value;
            if (armarMetodo.value === 'FLETE_TERCERO') payload.transporte_id = armarTransporteId.value;
        }
        const nuevo = await remitosStore.armarRemito(payload);
        cancelArmar();
        if (imprimir && nuevo?.id) imprimirArmado(nuevo);
        // La entrega (sobre todo un retiro en mostrador) cambia lo entregado del pedido: se recarga.
        await loadData(localPedido.value.id);
        // El PDF numera el remito al abrirse: se recarga otra vez para mostrar el número asignado.
        if (imprimir && nuevo?.id) setTimeout(() => loadData(localPedido.value.id), 1500);
    } catch (err) {
        alert(remitosStore.error || 'No se pudo armar el remito.');
    }
};

// [S891] Genoma del remito (bits de 64: en JS se leen con aritmética, los operadores de bits son de 32). IMPRESO = bit 44.
const impresoRemito = (remito) => Math.floor(Number(remito?.flags_estado || 0) / Math.pow(2, 44)) % 2 === 1;
const vistaPreviaRemito = (remito) => { if (remito?.id) window.open(`/remitos/${remito.id}/pdf?vista_previa=1`, '_blank'); };

// [S890, Carlos 21/10] Web del transporte para pedir el retiro (padrón: empresas_transporte.web_retiro, migrate_064).
const transporteElegido = computed(() => logisticaStore.empresas.find(e => e.id === armarTransporteId.value) || null);
const webRetiroDe = (transporteId) => (logisticaStore.empresas.find(e => e.id === transporteId) || {}).web_retiro || '';
const urlWeb = (url) => /^https?:\/\//i.test(url || '') ? url : `https://${url}`;
const webCopiada = ref(false);
const copiarWebRetiro = async () => {
    try { await navigator.clipboard.writeText(urlWeb(transporteElegido.value?.web_retiro)); webCopiada.value = true; setTimeout(() => { webCopiada.value = false; }, 1500); }
    catch (e) { prompt('Copiá la dirección:', urlWeb(transporteElegido.value?.web_retiro)); }
};
const abrirPadronTransportes = () => window.open(router.resolve({ name: 'Transportes' }).href, '_blank');

// [S876] Etiquetas del remito. Un remito de mostrador apunta a la oficina, que no figura entre los
// domicilios del cliente; y uno sin transporte dice cómo salió en vez de "Transporte...".
const remitoDireccionLabel = (remito) =>
    remito.metodo_entrega === 'MOSTRADOR' ? ETIQUETA_OFICINA : getAddressLabel(remito.domicilio_entrega_id);

const remitoTransporteLabel = (remito) =>
    remito.transporte_id ? getTransportLabel(remito.transporte_id) : (metodoCorto(remito.metodo_entrega) || 'Sin transporte');

// [S876] Resolver un renglón que salió sin ser venta firme: FACTURAR lo devuelve al camino normal.
// La otra salida (devolver la mercadería) es "Registrar Devolución", un PR de cantidad negativa.
const resolverFacturar = async (rItem) => {
    const que = `${getProductName(rItem.pedido_item_id)} (${motivoLabel(rItem.motivo_no_facturable)})`;
    if (!confirm(`"${que}" deja de ser "sin venta firme" y pasa a facturable. Sigue el camino normal de facturación.\n\n` +
                 `Si en cambio vuelve la mercadería, usá "Registrar Devolución". ¿Lo facturás?`)) return;
    try {
        await remitosStore.resolverNoFacturable(rItem.id, localPedido.value.id);
    } catch (err) {
        alert(remitosStore.error || 'No se pudo resolver el renglón.');
    }
};

// [S893, Carlos 26/10] La devolución se fundió con la corrección «Volvió»: se elige de qué remito (con número, no anulado y que no es una corrección) y se abre su ficha con la ventana de corrección.
const esCorreccion = (remito) => (remito.items || []).some((i) => i.corrige_item_id !== null && i.corrige_item_id !== undefined);
const remitosParaDevolver = computed(() => (remitos.value || []).filter((r) => r.numero_legal && r.estado !== 'ANULADO' && !esCorreccion(r) && (r.items || []).some((i) => i.cantidad > 0)));
const referenciaRemito = (r) => (r.numero_legal && /^\d{4}-\d{8}$/.test(r.numero_legal)) ? r.numero_legal : r.id;
const resumenRemito = (r) => (r.items || []).filter((i) => i.cantidad > 0).map((i) => `${i.cantidad} x ${getProductName(i.pedido_item_id)}`).join('; ');
const irADevolver = (r) => { showElegirRemito.value = false; router.push({ name: 'RemitoFicha', params: { ref: referenciaRemito(r) }, query: { corregir: 'VOLVIO' } }); };
const abrirDevolucion = () => {
    const c = remitosParaDevolver.value;
    if (c.length === 1) return irADevolver(c[0]);
    if (c.length > 1) showElegirRemito.value = true;
};
// [S893] «Ver el remito»: el documento verdadero (la imagen de lo impreso, o una vista con su número si salió sin papel), sin imprimir ni dejar nota.
const verRemito = (remito) => { if (remito?.id) window.open(`/remitos/${remito.id}/pdf?ver=1`, '_blank'); };

// Drag & Drop Logic
const onDragStart = (evt, item) => {
   dragItem.value = item;
   evt.dataTransfer.effectAllowed = 'move';
};

const onDrop = (evt, remito) => {
   if (remito.estado !== 'BORRADOR') return; // Bloquear drops en remitos cerrados
   targetRemito.value = remito;
   addItemAmount.value = dragItem.value.cantidad_pendiente;
   showAddItemModal.value = true;
};

const confirmDrop = async () => {
   if(!dragItem.value || !targetRemito.value) return;
   
   loading.value = true;
   try {
      await api.post(`/remitos/${targetRemito.value.id}/items`, {
         pedido_item_id: dragItem.value.id,
         cantidad: addItemAmount.value
      });
      // Refresh
      await remitosStore.fetchRemitos(localPedido.value.id); // Assuming localPedido.value.id is available
      showAddItemModal.value = false;
      addItemAmount.value = 0;
   } catch (e) {
      console.error(e);
      error.value = "Error al agregar ítem";
   } finally {
      loading.value = false;
      dragItem.value = null;
      targetRemito.value = null;
   }
};

const cancelDrop = () => {
    showAddItemModal.value = false;
    dragItem.value = null;
    targetRemito.value = null;
};

// [V5] Download Legal PDF
const downloadLegalPDF = async (remito) => {
    try {
        const response = await api.get(`/remitos/${remito.id}/pdf`, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `remito_legal_${remito.numero_legal || remito.id}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        // [S891] el primer papel le da número y la marca IMPRESO: se recarga para que el botón pase a «Reimprimir»
        if (!impresoRemito(remito) && localPedido.value?.id) await remitosStore.fetchRemitos(localPedido.value.id);
    } catch (e) {
        console.error("Error downloading PDF", e);
        alert("Error generando PDF Legal: " + (e.response?.data?.detail || e.message));
    }
};

</script>

<style scoped>
/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #1e293b; 
}
::-webkit-scrollbar-thumb {
  background: #475569; 
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #64748b; 
}
</style>
