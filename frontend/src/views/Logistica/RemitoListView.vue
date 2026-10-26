// [IDENTIDAD] - frontend\src\views\Logistica\RemitoListView.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans tokyo-bg neon-orange rounded-2xl border-2 border-orange-500 shadow-[0_0_30px_rgba(249,115,22,0.4)] p-6">
    
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative min-w-0">
      
      <!-- Top Bar -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-orange-900/20 bg-black/20 px-6 backdrop-blur-sm shrink-0">
        <!-- Title -->
        <div>
            <h1 class="font-outfit text-xl font-semibold text-white">
                Logística: Remitos Emitidos
            </h1>
            <p class="text-xs text-orange-400/50 font-medium uppercase tracking-wider">Control de Despachos</p>
        </div>

        <!-- Search & Tools -->
        <div class="flex items-center gap-4">
          <div class="relative">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-orange-500/50"></i>
            <!-- [S893, Carlos 26/10] Buscar por número de remito, OC, cliente o pedido (F3). Enter abre la ficha si hay uno solo o si el número es exacto. -->
            <input
              ref="cajaBusqueda"
              v-model="searchQuery"
              type="text"
              data-campo="buscar-remito"
              placeholder="Buscar por número, OC, cliente o pedido (F3)..."
              @keydown.enter.prevent="buscarYAbrir"
              class="h-9 w-80 rounded-full border border-orange-900/30 bg-[#02050f] pl-10 pr-4 text-sm text-orange-100 placeholder-orange-900/50 focus:border-orange-500 focus:outline-none focus:ring-1 focus:ring-orange-500"
            />
          </div>

          <!-- [S893] Los atajos (F3, F4) tienen su botón a la vista: la tecla es memoria muscular, el botón es lo que ve quien no la tiene -->
          <button @click="enfocarBusqueda" data-accion="buscar" class="h-9 px-3 whitespace-nowrap rounded-full border border-orange-900/30 text-xs font-bold text-orange-200 hover:text-white hover:border-orange-500/50 transition-colors" title="Buscar (F3)">
            <i class="fas fa-search mr-1"></i> Buscar (F3)
          </button>
          <button @click="nuevoRemito" data-accion="nuevo-remito" class="h-9 px-3 whitespace-nowrap rounded-full bg-orange-600 hover:bg-orange-500 text-xs font-bold text-white transition-colors" title="Nuevo remito (F4)">
            <i class="fas fa-plus mr-1"></i> Nuevo remito (F4)
          </button>

          <button
            @click="refresh"
            class="p-2 text-orange-500 hover:text-orange-300 transition-colors"
            title="Recargar"
          >
            <i class="fas fa-sync-alt" :class="{ 'animate-spin': store.loading }"></i>
          </button>
        </div>
      </header>

      <!-- Content List -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-orange-900/10 scrollbar-thumb-orange-900/30">
        
        <!-- List View -->
        <div class="flex flex-col gap-2">
            <!-- Header Row -->
             <div class="flex items-center justify-between px-4 py-3 text-[11px] font-black uppercase tracking-widest select-none text-white border-b border-orange-500/10 mb-2">
                <!-- Columna Numero -->
                <div class="w-32 cursor-pointer hover:text-orange-300 transition-colors flex items-center gap-2 group/h" @click="toggleSort('numero')">
                    Número
                    <div class="flex flex-col text-[7px] -space-y-0.5">
                        <i class="fas fa-chevron-up" :class="sortKey === 'numero' && sortOrder === 'asc' ? 'text-orange-400' : 'text-orange-900/40'"></i>
                        <i class="fas fa-chevron-down" :class="sortKey === 'numero' && sortOrder === 'desc' ? 'text-orange-400' : 'text-orange-900/40'"></i>
                    </div>
                </div>

                <!-- [S887] Columna Pedido: el Nº del pedido al que pertenece el remito -->
                <div class="w-16 text-center cursor-pointer hover:text-orange-300 transition-colors flex items-center justify-center gap-2 group/h" @click="toggleSort('pedido')">
                    Pedido
                    <div class="flex flex-col text-[7px] -space-y-0.5">
                        <i class="fas fa-chevron-up" :class="sortKey === 'pedido' && sortOrder === 'asc' ? 'text-orange-400' : 'text-orange-900/40'"></i>
                        <i class="fas fa-chevron-down" :class="sortKey === 'pedido' && sortOrder === 'desc' ? 'text-orange-400' : 'text-orange-900/40'"></i>
                    </div>
                </div>

                <!-- Columna Fecha -->
                <div class="w-24 text-center cursor-pointer hover:text-orange-300 transition-colors flex items-center justify-center gap-2 group/h" @click="toggleSort('fecha')">
                    Fecha
                    <div class="flex flex-col text-[7px] -space-y-0.5">
                        <i class="fas fa-chevron-up" :class="sortKey === 'fecha' && sortOrder === 'asc' ? 'text-orange-400' : 'text-orange-900/40'"></i>
                        <i class="fas fa-chevron-down" :class="sortKey === 'fecha' && sortOrder === 'desc' ? 'text-orange-400' : 'text-orange-900/40'"></i>
                    </div>
                </div>

                <!-- Columna Cliente -->
                <div class="flex-1 px-4 cursor-pointer hover:text-orange-300 transition-colors flex items-center gap-2 group/h" @click="toggleSort('cliente')">
                    Cliente
                    <div class="flex flex-col text-[7px] -space-y-0.5">
                        <i class="fas fa-chevron-up" :class="sortKey === 'cliente' && sortOrder === 'asc' ? 'text-orange-400' : 'text-orange-900/40'"></i>
                        <i class="fas fa-chevron-down" :class="sortKey === 'cliente' && sortOrder === 'desc' ? 'text-orange-400' : 'text-orange-900/40'"></i>
                    </div>
                </div>

                <div class="w-28 text-center text-orange-200/40">Factura</div>

                <!-- Columna Estado -->
                <div class="w-28 text-center cursor-pointer hover:text-orange-300 transition-colors flex items-center justify-center gap-2 group/h" @click="toggleSort('estado')">
                    Estado
                    <div class="flex flex-col text-[7px] -space-y-0.5">
                        <i class="fas fa-chevron-up" :class="sortKey === 'estado' && sortOrder === 'asc' ? 'text-orange-400' : 'text-orange-900/40'"></i>
                        <i class="fas fa-chevron-down" :class="sortKey === 'estado' && sortOrder === 'desc' ? 'text-orange-400' : 'text-orange-900/40'"></i>
                    </div>
                </div>

                <div class="w-14 text-right text-orange-200/40">Items</div>
                <div class="w-40"></div>
            </div>

            <div 
                v-for="remito in sortedRemitos" 
                :key="remito.id"
                @click="abrirFicha(remito)"
                data-fila-remito
                class="group flex items-center justify-between p-4 mb-2 rounded-xl border transition-all relative overflow-hidden bg-[#070d24] border-orange-900/20 hover:bg-[#0a1435] hover:border-orange-500/30 shadow-md cursor-pointer"
            >
                <!-- Numero -->
                <div class="w-32 font-mono text-orange-400 font-bold text-sm">
                    {{ remito.numero_legal || (esCorreccion(remito) ? 'CORRECCIÓN' : 'BORRADOR') }}
                    <!-- [S893] corrige lo que quedó de un renglón de otro remito: no tiene papel ni número -->
                    <span v-if="esCorreccion(remito)" data-marca="correccion" class="block text-[9px] font-sans font-bold uppercase tracking-wider text-amber-300/80">baja lo que quedó</span>
                    <!-- [S892, Nike bit 46] un 0015 de un pedido Rosa (lo despacha un transporte): no se factura -->
                    <span v-if="tieneBit(remito.flags_estado, 46)" data-marca="rosa-no-facturable" title="Remito de un pedido Rosa: no se factura"
                          class="block text-[9px] font-sans font-bold uppercase tracking-wider text-pink-300/80">Rosa · no se factura</span>
                </div>

                <!-- Pedido [S887]: columna propia; el clic abre la pantalla de entregas de ese pedido -->
                <div class="w-16 text-center">
                    <button
                        @click.stop="viewPedido(remito.pedido_id)"
                        class="font-mono text-xs font-bold text-orange-200 hover:text-white hover:underline"
                        :title="`Ver el pedido ${remito.pedido_id}`"
                    >#{{ remito.pedido_id }}</button>
                </div>

                <!-- Fecha -->
                <!-- [S890, S891] La fecha del remito es la de emisión (el día en que tomó número); sin número, la de armado.
                     El lápiz la cambia con motivo (queda una nota [SISTEMA]). -->
                <div class="w-24 text-center flex items-center justify-center gap-1 leading-tight group/fecha">
                    <span class="text-xs text-orange-100 font-bold" data-fecha-remito>{{ formatDate(fechaRemito(remito)).split(' ')[0] }}</span>
                    <button v-if="remito.numero_legal && remito.estado !== 'ANULADO'" @click.stop="abrirCambioFecha(remito)" data-accion="cambiar-fecha"
                            class="text-[10px] text-orange-500/40 hover:text-orange-300 opacity-0 group-hover/fecha:opacity-100 transition-opacity"
                            title="Cambiar la fecha del remito (con motivo)"><i class="fas fa-pen"></i></button>
                </div>

                <!-- Cliente -->
                <div class="flex items-center gap-3 flex-1 min-w-0 px-4">
                    <div class="min-w-0 flex-1">
                        <h3 class="font-bold text-orange-50 text-sm truncate group-hover:text-orange-300 transition-colors">{{ remito.razon_social || 'Desconocido' }}</h3>
                    </div>
                </div>

                <!-- Factura vinculada [S868: el remito no tiene CAE; se muestra la factura que lo ampara, si existe] -->
                <div class="w-28 text-center font-mono text-[11px] text-orange-200/60">
                    {{ remito.factura_vinculada || '-' }}
                </div>
                
                <!-- Status Badge -->
                <div class="w-28 flex flex-col items-center justify-center">
                    <span 
                        class="px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider border transition-all"
                        :class="getStatusClass(remito.estado)"
                    >
                        {{ remito.estado }}
                    </span>
                    <!-- [S892] impreso (o sin papel) pero todavía en el depósito, esperando que lo retire el transporte -->
                    <span v-if="enDeposito(remito)" data-marca="en-deposito" class="block mt-1 text-[9px] font-bold uppercase tracking-wider text-amber-300/80">en depósito</span>
                </div>

                <!-- Items Count -->
                <div class="w-14 text-right font-mono text-orange-100 font-bold">
                    {{ remito.items?.length || 0 }}
                </div>

                <!-- Actions -->
                <div class="w-40 flex justify-end gap-1">
                    <!-- [S891] Vista previa: solo un remito SIN número; no gasta el número ni queda guardada -->
                    <button v-if="!remito.numero_legal && remito.estado !== 'ANULADO' && !esCorreccion(remito)" @click.stop="vistaPrevia(remito)" data-accion="vista-previa"
                        class="p-2 text-orange-300/70 hover:text-white transition-colors" title="Vista previa (sin número: no gasta el número)">
                        <i class="fas fa-eye"></i>
                    </button>
                    <!-- [S887] Imprimir directo, sin entrar a la ficha. [S891] Una vez impreso es «Reimprimir»: la misma imagen guardada -->
                    <button
                        @click.stop="imprimirRemito(remito)"
                        :disabled="remito.estado === 'ANULADO' || esCorreccion(remito)"
                        :data-accion="impreso(remito) ? 'reimprimir' : 'imprimir'"
                        class="p-2 text-orange-300 hover:text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                        :title="remito.estado === 'ANULADO' ? 'Remito anulado: no se imprime' : (impreso(remito) ? 'Reimprimir (la misma imagen de lo impreso)' : (remito.numero_legal ? 'Imprimir el remito (PDF)' : 'Imprimir el remito: se le asigna el próximo número 0015'))"
                    >
                        <i :class="impreso(remito) ? 'fas fa-copy' : 'fas fa-print'"></i>
                    </button>
                    <!-- [S892] Salió sin papel: toma el número sin imprimir (si después lo piden, se imprime con ese número) -->
                    <button v-if="!remito.numero_legal && remito.estado !== 'ANULADO' && !esCorreccion(remito)" @click.stop="abrirAccionFecha(remito, 'sin-papel')" data-accion="sin-papel"
                        class="p-2 text-cyan-300/70 hover:text-white transition-colors" title="Salió sin papel (toma el número sin imprimir)">
                        <i class="fas fa-file-circle-xmark"></i>
                    </button>
                    <!-- [S892] Queda en depósito / Retiró el transporte (caso Rizobacter: impreso y todavía en el depósito) -->
                    <button v-if="remito.numero_legal && remito.estado === 'BORRADOR' && !enDeposito(remito)" @click.stop="marcarEnDeposito(remito)" data-accion="en-deposito"
                        class="p-2 text-amber-300/60 hover:text-amber-200 transition-colors" title="Queda en depósito (todavía no lo retiró el transporte)">
                        <i class="fas fa-warehouse"></i>
                    </button>
                    <button v-if="enDeposito(remito)" @click.stop="abrirAccionFecha(remito, 'retiro')" data-accion="retiro"
                        class="p-2 text-amber-300 hover:text-white transition-colors" title="Retiró el transporte (registra la salida)">
                        <i class="fas fa-truck-ramp-box"></i>
                    </button>
                    <!-- [S891] Un remito con número no se borra: se anula (con motivo) y se puede deshacer si nadie cubrió esas cantidades -->
                    <button v-if="remito.numero_legal && remito.estado !== 'ANULADO'" @click.stop="abrirAnulacion(remito, 'anular')" data-accion="anular"
                        class="p-2 text-red-400/60 hover:text-red-300 transition-colors" title="Anular el remito (el número queda usado)">
                        <i class="fas fa-ban"></i>
                    </button>
                    <!-- [S893] Una corrección mal cargada se deshace con motivo (no tiene número: no pasa por «anular») -->
                    <button v-if="esCorreccion(remito) && remito.estado !== 'ANULADO'" @click.stop="abrirAnulacion(remito, 'deshacer-correccion')" data-accion="deshacer-correccion"
                        class="p-2 text-amber-400/70 hover:text-amber-300 transition-colors" title="Deshacer la corrección (el renglón vuelve a lo que tenía)">
                        <i class="fas fa-rotate-left"></i>
                    </button>
                    <button v-if="remito.estado === 'ANULADO' && !esCorreccion(remito)" @click.stop="abrirAnulacion(remito, 'deshacer')" data-accion="deshacer-anulacion"
                        class="p-2 text-amber-400/70 hover:text-amber-300 transition-colors" title="Deshacer la anulación">
                        <i class="fas fa-rotate-left"></i>
                    </button>
                    <button
                        @click.stop="viewPedido(remito.pedido_id)"
                        class="p-2 text-orange-500/50 hover:text-orange-400 transition-colors"
                        title="Ver Pedido"
                    >
                        <i class="fas fa-external-link-alt"></i>
                    </button>
                </div>
            </div>

            <!-- Empty State -->
            <div v-if="sortedRemitos.length === 0 && !store.loading" class="flex flex-col items-center justify-center py-20 text-orange-900/40">
                <i class="fas fa-truck-loading text-4xl mb-4"></i>
                <p>No se encontraron remitos</p>
            </div>
            
             <!-- Loading State -->
            <div v-if="store.loading" class="flex flex-col items-center justify-center py-20 text-orange-500">
                <i class="fas fa-spinner fa-spin text-4xl mb-4"></i>
                <p>Cargando remitos...</p>
            </div>
        </div>
      </div>

      <!-- EDIT MODAL -->
      <div v-if="showEditModal" class="fixed inset-0 bg-black/90 backdrop-blur-xl flex items-center justify-center z-[100] p-4">
         <div class="bg-[#0f172a] border-2 border-orange-500/50 rounded-3xl w-full max-w-4xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <header class="bg-orange-600/10 p-6 border-b border-orange-500/20 flex justify-between items-center shrink-0">
                <div>
                    <h3 class="text-xl font-bold text-white tracking-tight uppercase">Soberanía Total: Editar Remito</h3>
                    <p class="text-[10px] text-orange-400 font-bold tracking-widest uppercase italic">Estado: BORRADOR • ID: {{ editingRemito?.id }}</p>
                </div>
                <div class="flex items-center gap-6">
                    <button 
                        @click="printRemito(editingRemito)" 
                        title="Imprimir Remito Oficial PDF"
                        class="group flex items-center justify-center w-10 h-10 rounded-full bg-slate-800/80 border border-slate-700 hover:bg-orange-600 hover:border-orange-500 transition-all shadow-lg"
                    >
                        <i class="fas fa-print text-slate-300 group-hover:text-white"></i>
                    </button>
                    <button @click="closeEditModal" class="text-gray-500 hover:text-white transition-colors">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
            </header>

            <div class="p-8 space-y-8 overflow-y-auto custom-scrollbar flex-1">
                <!-- SECTION: CLIENTE & LOGISTICA -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <!-- Client Selector -->
                    <div class="space-y-4">
                        <label class="text-[10px] font-bold text-orange-400 uppercase tracking-widest">Destinatario</label>
                        <SmartSelect
                            v-model="editForm.cliente_id"
                            :options="clientesOptions"
                            :initial-label="editingRemito?.razon_social"
                            placeholder="Buscar cliente..."
                            @update:modelValue="onClientChanged"
                        />
                    </div>

                    <!-- Logistics -->
                    <div class="space-y-4">
                        <label class="text-[10px] font-bold text-orange-400 uppercase tracking-widest">Transporte / Expreso</label>
                        <select 
                            v-model="editForm.transporte_id" 
                            class="w-full bg-slate-900 border border-orange-900/40 rounded-xl px-4 py-3 text-sm text-white focus:border-orange-500 outline-none transition-all appearance-none"
                        >
                            <option v-for="t in maestrosStore.transportes" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                        </select>
                    </div>
                </div>

                <!-- SECTION: O.C. (Editable, mismo patrón que PedidoInspector) -->
                <div class="bg-orange-500/5 border-l-2 border-orange-500/30 p-3 rounded-r relative group/oc">
                    <label class="block text-[10px] font-bold text-orange-400/70 uppercase tracking-widest mb-1">
                        Orden de Compra (O.C.) — Pedido #{{ editingRemito?.pedido_id }}
                    </label>

                    <div v-if="!isEditingOC" class="flex justify-between items-start">
                        <p class="text-xs font-mono tracking-wide text-orange-100/80 min-h-[1.5rem]">
                            {{ pedidoOC || '-' }}
                        </p>
                        <button
                            @click="startEditingOC"
                            class="text-orange-500/30 hover:text-orange-400 opacity-0 group-hover/oc:opacity-100 transition-opacity"
                            title="Editar O.C."
                        >
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                    </div>

                    <div v-else>
                        <input
                            type="text"
                            v-model="tempOC"
                            class="w-full bg-slate-900 text-orange-100 border border-orange-500/30 rounded-lg px-4 py-3 text-xs font-mono font-bold focus:outline-none focus:border-orange-500"
                            placeholder="Nro Orden Compra..."
                        >
                        <div class="flex justify-end gap-2 mt-2">
                            <button @click="cancelEditOC" class="text-xs text-white/50 hover:text-white">Cancelar</button>
                            <button @click="saveOC" class="text-xs bg-orange-600/50 hover:bg-orange-600 text-white px-2 py-1 rounded font-bold">Guardar</button>
                        </div>
                    </div>
                </div>

                <!-- SECTION: DIRECCIÓN -->
                <div class="bg-orange-900/10 border border-orange-500/20 rounded-2xl p-6 space-y-4">
                    <div class="flex justify-between items-center">
                        <label class="text-[10px] font-bold text-orange-400 uppercase tracking-widest">Punto de Entrega</label>
                        <button 
                            @click="isForcingAddress = !isForcingAddress"
                            class="text-[10px] font-bold uppercase tracking-widest py-1 px-3 rounded-full border transition-all"
                            :class="isForcingAddress ? 'bg-amber-500/20 text-amber-500 border-amber-500/50' : 'bg-orange-500/10 text-orange-400 border-orange-900/50'"
                        >
                            {{ isForcingAddress ? 'Cancelar Forzado' : 'Forzar Dirección Nueva' }}
                        </button>
                    </div>

                    <div v-if="!isForcingAddress" class="space-y-1">
                        <select 
                            v-model="editForm.domicilio_entrega_id" 
                            class="w-full bg-slate-900 border border-orange-900/40 rounded-xl px-4 py-3 text-sm text-white focus:border-orange-500 outline-none transition-all appearance-none"
                        >
                            <option v-for="d in clientAddresses" :key="d.id" :value="d.id">{{ d.calle }} {{ d.numero }} ({{ d.localidad }})</option>
                        </select>
                    </div>

                    <div v-else class="grid grid-cols-12 gap-4 animate-in slide-in-from-top-2">
                        <div class="col-span-12 md:col-span-6">
                            <input v-model="editForm.nuevo_domicilio.calle" placeholder="Calle / Dirección" class="w-full bg-slate-900 border border-amber-500/30 rounded-xl px-4 py-3 text-sm text-white focus:border-amber-500 outline-none" />
                        </div>
                        <div class="col-span-6 md:col-span-2">
                            <input v-model="editForm.nuevo_domicilio.numero" placeholder="N°" class="w-full bg-slate-900 border border-amber-500/30 rounded-xl px-4 py-3 text-sm text-white focus:border-amber-500 outline-none" />
                        </div>
                        <div class="col-span-6 md:col-span-4">
                            <input v-model="editForm.nuevo_domicilio.localidad" placeholder="Localidad" class="w-full bg-slate-900 border border-amber-500/30 rounded-xl px-4 py-3 text-sm text-white focus:border-amber-500 outline-none" />
                        </div>
                    </div>
                </div>

                <!-- SECTION: ITEMS (GRID) -->
                <div class="space-y-4">
                    <div class="flex justify-between items-end">
                        <label class="text-[10px] font-bold text-orange-400 uppercase tracking-widest">Cuerpo del Remito (Items)</label>
                        <button @click="addItem" class="text-[10px] font-bold text-emerald-400 hover:text-emerald-300 transition-colors uppercase tracking-widest flex items-center gap-1">
                            <i class="fas fa-plus-circle"></i> Agregar Línea
                        </button>
                    </div>

                    <div class="bg-black/40 rounded-2xl border border-orange-900/20 overflow-hidden">
                        <div class="grid grid-cols-12 bg-orange-900/20 px-4 py-2 text-[9px] font-black uppercase text-orange-400/50">
                            <div class="col-span-9">Descripción</div>
                            <div class="col-span-3 text-right">Cantidad</div>
                        </div>
                        <div class="divide-y divide-orange-900/10">
                            <div v-for="(item, index) in editForm.items" :key="index" class="grid grid-cols-12 px-4 py-2 gap-4 items-center group">
                                <div class="col-span-9">
                                    <input v-model="item.descripcion" class="w-full bg-transparent border-none text-white text-sm focus:outline-none" placeholder="Descripción del ítem..." />
                                </div>
                                <div class="col-span-3 flex items-center justify-end gap-3">
                                    <input v-model.number="item.cantidad" type="number" class="w-16 bg-orange-500/5 border border-orange-500/10 rounded-lg px-2 py-1 text-right text-orange-300 font-bold text-sm focus:border-orange-500 outline-none" />
                                    <button @click="removeItem(index)" class="text-orange-900/50 hover:text-red-500 transition-colors">
                                        <i class="fas fa-times text-xs"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- SECTION: LEGAL & AFIP -->
                <!-- [S868] Sin CAE editable: un CAE tipeado en un remito es un CAE inventado -->
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="space-y-1 col-span-2">
                        <label class="text-[10px] font-bold text-orange-400 uppercase tracking-widest">Número</label>
                        <input v-model="editForm.numero_legal" readonly class="w-full bg-slate-900/50 border border-orange-900/40 rounded-xl px-4 py-3 text-xs text-slate-300 font-mono" />
                    </div>
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-orange-400 uppercase tracking-widest">Bultos</label>
                        <input v-model.number="editForm.bultos" type="number" class="w-full bg-slate-900 border border-orange-900/40 rounded-xl px-4 py-3 text-sm text-white" />
                    </div>
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-orange-400 uppercase tracking-widest">Valor Decl.</label>
                        <input v-model.number="editForm.valor_declarado" type="number" class="w-full bg-slate-900 border border-orange-900/40 rounded-xl px-4 py-3 text-sm text-white" />
                    </div>
                </div>
            </div>

            <footer class="bg-orange-600/5 p-6 border-t border-orange-500/20 flex flex-wrap justify-between gap-4 shrink-0">
                <div class="flex gap-2">
                    <button 
                        v-if="!editingRemito?.numero_legal" @click="deleteRemito(editingRemito)" 
                        title="Descartar el remito (no tiene número)"
                        class="px-4 py-2 bg-red-900/50 hover:bg-red-500 text-red-200 hover:text-white font-bold rounded-xl shadow-lg transition-all"
                    >
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
                <div class="flex gap-4">
                    <button @click="closeEditModal" class="px-6 py-2 text-sm font-bold text-slate-400 hover:text-white transition-colors">Cancelar</button>
                <button 
                    @click="saveEdition" 
                    :disabled="isSaving"
                    class="px-8 py-2 bg-orange-600 hover:bg-orange-500 disabled:bg-slate-800 text-white font-bold rounded-xl shadow-lg transition-all"
                >
                    <i v-if="isSaving" class="fas fa-spinner fa-spin mr-2"></i>
                    Guardar Cambios Totales
                </button>
                </div>
            </footer>
         </div>
      </div>

      <!-- [S893, Carlos 26/10] «Nuevo remito» (F4): el Remito Manual se retiró, un remito se arma SIEMPRE desde un pedido. Se elige el pedido (por número, OC o
           cliente) y se sigue por «Imprimir remito» de su pantalla de entregas, con el cuadro ya abierto. -->
      <div v-if="elegirPedido.visible" data-modal="elegir-pedido" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[110] p-4" @click.self="cerrarElegirPedido">
        <div class="bg-[#0b1220] border border-orange-500/40 rounded-2xl w-full max-w-2xl p-6 shadow-2xl">
          <h3 class="text-white font-bold text-lg mb-1">Nuevo remito: ¿de qué pedido?</h3>
          <p class="text-xs text-orange-300/70 mb-4">El remito se arma siempre desde un pedido. Buscá por número, OC o cliente; salen los pedidos que todavía tienen algo por remitir.</p>
          <input ref="cajaElegirPedido" v-model="elegirPedido.q" @input="buscarPedidosPorRemitar" @keydown.enter.prevent="armarDesde(elegirPedido.lista[0])" type="text" data-campo="buscar-pedido"
                 placeholder="Número de pedido, OC o cliente..." class="w-full bg-black/30 border border-orange-900/40 rounded-lg px-3 py-2 text-sm text-white placeholder-white/30 focus:border-orange-500/60 focus:outline-none mb-3" />
          <ul class="max-h-72 overflow-y-auto divide-y divide-white/5 rounded-lg border border-white/10">
            <li v-for="p in elegirPedido.lista" :key="p.pedido_id" data-pedido-por-remitar class="flex items-center gap-3 px-3 py-2 hover:bg-orange-500/5">
              <span class="font-mono text-xs font-bold text-orange-300 w-12 shrink-0">#{{ p.pedido_id }}</span>
              <div class="min-w-0 flex-1">
                <div class="text-sm text-white truncate">{{ p.cliente }} <span v-if="p.oc" class="text-[10px] text-gray-500 font-mono ml-1">OC {{ p.oc }}</span></div>
                <div class="text-[11px] text-gray-400 truncate">{{ p.resumen }}</div>
              </div>
              <button @click="armarDesde(p)" data-accion="armar-desde-pedido" class="px-3 py-1 rounded-md text-[11px] font-bold text-white bg-orange-600 hover:bg-orange-500 whitespace-nowrap">Armar remito</button>
            </li>
            <li v-if="!elegirPedido.lista.length" class="px-3 py-6 text-center text-sm text-gray-500">{{ elegirPedido.cargando ? 'Buscando…' : 'Ningún pedido abierto con algo por remitir coincide.' }}</li>
          </ul>
          <div class="flex justify-end mt-4">
            <button @click="cerrarElegirPedido" data-accion="cancelar-elegir-pedido" class="px-4 py-2 rounded-lg text-sm text-orange-300 hover:text-white">Cancelar (ESC)</button>
          </div>
        </div>
      </div>

      <!-- [S892] «Salió sin papel» (la fecha es la de la asignación del número: ahora; Carlos 23/10) y «Retiró el transporte» (fecha del retiro, hoy por defecto, nunca a futuro) -->
      <div v-if="accionFecha.visible" data-modal="accion-fecha" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[110] p-4" @click.self="cerrarAccionFecha">
        <div class="bg-[#0b1220] border border-cyan-500/40 rounded-2xl w-full max-w-md p-6 shadow-2xl">
          <h3 class="text-white font-bold text-lg mb-1">{{ accionFecha.modo === 'sin-papel' ? 'Salió sin papel' : 'Retiró el transporte' }}</h3>
          <p class="text-xs text-orange-300/70 mb-4" v-if="accionFecha.modo === 'sin-papel'">Pedido #{{ accionFecha.remito?.pedido_id }} · {{ accionFecha.remito?.razon_social }}. El remito toma el próximo número 0015 sin imprimirse, con la fecha de hoy (si hace falta otra, después se cambia con el lápiz). Si después lo piden, se imprime con ese mismo número.</p>
          <p class="text-xs text-orange-300/70 mb-4" v-else>{{ accionFecha.remito?.numero_legal }} · {{ accionFecha.remito?.razon_social }}. Registra el día en que salió del depósito.</p>
          <template v-if="accionFecha.modo === 'retiro'">
            <label class="block text-[10px] uppercase tracking-widest text-orange-400 font-bold mb-1">Fecha del retiro</label>
            <input type="date" v-model="accionFecha.fecha" :max="hoyISO()" data-campo="fecha-accion" class="w-full bg-black/30 border border-orange-900/40 rounded-lg px-3 py-2 text-sm text-white mb-4" />
          </template>
          <template v-if="accionFecha.modo === 'sin-papel'">
            <label class="block text-[10px] uppercase tracking-widest text-orange-400 font-bold mb-1">Motivo (opcional)</label>
            <textarea v-model="accionFecha.motivo" rows="2" data-campo="motivo-accion" placeholder="Ej.: salió con la factura" class="w-full bg-black/30 border border-orange-900/40 rounded-lg px-3 py-2 text-sm text-white mb-5"></textarea>
          </template>
          <div class="flex justify-end gap-2">
            <button @click="cerrarAccionFecha" class="px-4 py-2 rounded-lg text-sm text-orange-300 hover:text-white">Cancelar</button>
            <button @click="confirmarAccionFecha" :disabled="accionFecha.guardando || (accionFecha.modo === 'retiro' && !accionFecha.fecha)" data-accion="confirmar-accion-fecha"
                    class="px-4 py-2 rounded-lg text-sm font-bold text-white bg-cyan-700 hover:bg-cyan-600 disabled:opacity-40 disabled:cursor-not-allowed">
              <i v-if="accionFecha.guardando" class="fas fa-spinner fa-spin mr-1"></i> Confirmar
            </button>
          </div>
        </div>
      </div>

      <!-- [S891] Anular un remito (con número) o deshacer su anulación: siempre con motivo; queda una nota [SISTEMA] -->
      <div v-if="anulacion.visible" data-modal="anulacion" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[110] p-4" @click.self="cerrarAnulacion">
        <div class="bg-[#0b1220] border border-red-500/40 rounded-2xl w-full max-w-md p-6 shadow-2xl">
          <h3 class="text-white font-bold text-lg mb-1">{{ anulacion.modo === 'anular' ? 'Anular el remito' : (anulacion.modo === 'deshacer-correccion' ? 'Deshacer la corrección' : 'Deshacer la anulación') }}</h3>
          <p class="text-xs text-orange-300/70 mb-4" v-if="anulacion.modo === 'anular'">{{ anulacion.remito?.numero_legal }} · {{ anulacion.remito?.razon_social }}. El número queda usado (no se vuelve a dar) y las cantidades vuelven a quedar pendientes en el pedido. Si ya se facturó, primero va la nota de crédito.</p>
          <p class="text-xs text-orange-300/70 mb-4" v-else-if="anulacion.modo === 'deshacer-correccion'">Corrección del pedido #{{ anulacion.remito?.pedido_id }} · {{ anulacion.remito?.razon_social }}. El renglón vuelve a lo que tenía antes de la corrección y el pedido deja de deber esa diferencia. No se puede volver a activar: si hace falta, se hace otra.</p>
          <p class="text-xs text-orange-300/70 mb-4" v-else>{{ anulacion.remito?.numero_legal }} · {{ anulacion.remito?.razon_social }}. Vuelve al estado que tenía. No se puede si otro remito ya cubrió esas cantidades.</p>
          <label class="block text-[10px] uppercase tracking-widest text-orange-400 font-bold mb-1">Motivo</label>
          <textarea v-model="anulacion.motivo" rows="2" data-campo="motivo-anulacion" placeholder="Por qué" class="w-full bg-black/30 border border-orange-900/40 rounded-lg px-3 py-2 text-sm text-white mb-5"></textarea>
          <div class="flex justify-end gap-2">
            <button @click="cerrarAnulacion" class="px-4 py-2 rounded-lg text-sm text-orange-300 hover:text-white">Cancelar</button>
            <button @click="confirmarAnulacion" :disabled="anulacion.guardando || !anulacion.motivo.trim()" data-accion="confirmar-anulacion"
                    class="px-4 py-2 rounded-lg text-sm font-bold text-white disabled:opacity-40 disabled:cursor-not-allowed"
                    :class="anulacion.modo === 'anular' ? 'bg-red-600 hover:bg-red-500' : 'bg-amber-600 hover:bg-amber-500'">
              <i v-if="anulacion.guardando" class="fas fa-spinner fa-spin mr-1"></i> {{ anulacion.modo === 'anular' ? 'Anular' : 'Deshacer' }}
            </button>
          </div>
        </div>
      </div>

      <!-- [S890] Cambiar la fecha de un remito numerado: con motivo, nunca a futuro; queda una nota [SISTEMA] -->
      <div v-if="cambioFecha.visible" data-modal="cambiar-fecha" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[110] p-4" @click.self="cerrarCambioFecha">
        <div class="bg-[#0b1220] border border-orange-500/40 rounded-2xl w-full max-w-md p-6 shadow-2xl">
          <h3 class="text-white font-bold text-lg mb-1">Cambiar la fecha del remito</h3>
          <p class="text-xs text-orange-300/70 mb-4">{{ cambioFecha.remito?.numero_legal }} · {{ cambioFecha.remito?.razon_social }}. El remito no cambia: solo su fecha, y queda una nota con la fecha anterior y el motivo.</p>
          <label class="block text-[10px] uppercase tracking-widest text-orange-400 font-bold mb-1">Fecha</label>
          <input type="date" v-model="cambioFecha.fecha" :max="hoyISO()" data-campo="fecha" class="w-full bg-black/30 border border-orange-900/40 rounded-lg px-3 py-2 text-sm text-white mb-4" />
          <label class="block text-[10px] uppercase tracking-widest text-orange-400 font-bold mb-1">Motivo</label>
          <textarea v-model="cambioFecha.motivo" rows="2" data-campo="motivo" placeholder="Por qué cambia la fecha" class="w-full bg-black/30 border border-orange-900/40 rounded-lg px-3 py-2 text-sm text-white mb-5"></textarea>
          <div class="flex justify-end gap-2">
            <button @click="cerrarCambioFecha" class="px-4 py-2 rounded-lg text-sm text-orange-300 hover:text-white">Cancelar</button>
            <button @click="guardarCambioFecha" :disabled="cambioFecha.guardando || !cambioFecha.fecha || !cambioFecha.motivo.trim()" data-accion="guardar-fecha"
                    class="px-4 py-2 rounded-lg text-sm font-bold bg-orange-600 hover:bg-orange-500 text-white disabled:opacity-40 disabled:cursor-not-allowed">
              <i v-if="cambioFecha.guardando" class="fas fa-spinner fa-spin mr-1"></i> Guardar
            </button>
          </div>
        </div>
      </div>

    </main>

    <!-- [S893] La ficha del remito: ruta propia (/logistica/remitos/:ref) para que «volver atrás» y ESC la cierren y dejen la lista como estaba -->
    <router-view />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, reactive, provide, nextTick } from 'vue'
import { normalizarBusqueda } from '@/utils/texto'
import { useRouter, useRoute } from 'vue-router'
import { useRemitosStore } from '@/stores/remitos'
import { useMaestrosStore } from '@/stores/maestros'
import { useClientesStore } from '@/stores/clientes'
import { usePedidosStore } from '@/stores/pedidos'
import { useNotificationStore } from '@/stores/notification'
import SmartSelect from '@/components/ui/SmartSelect.vue'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const store = useRemitosStore()
const maestrosStore = useMaestrosStore()
const clientesStore = useClientesStore()
const pedidosStore = usePedidosStore()
const notification = useNotificationStore()

const searchQuery = ref('')
const isForcingAddress = ref(false)
const sortKey = ref('fecha')
const sortOrder = ref('desc')

// Editing State
const showEditModal = ref(false)
const isSaving = ref(false)
const editingRemito = ref(null)
const clientAddresses = ref([])
const pedidoOC = ref('')
const isEditingOC = ref(false)
const tempOC = ref('')
const editForm = reactive({
    cliente_id: null,
    numero_legal: '',
    transporte_id: null,
    domicilio_entrega_id: null,
    bultos: 1,
    valor_declarado: 0,
    items: [],
    nuevo_domicilio: {
        calle: '',
        numero: '',
        localidad: '',
        provincia_id: 'X'
    }
})

const clientesOptions = computed(() => {
    return clientesStore.clientes.map(c => ({
        id: c.id,
        nombre: c.razon_social,
        razon_social: c.razon_social,
        cuit: c.cuit
    }))
})

const onClientChanged = async (newId) => {
    if (!newId) return;
    try {
        const res = await api.get(`/clientes/${newId}`);
        clientAddresses.value = res.data.domicilios || [];
    } catch (e) {
        console.error("Error loading addresses", e);
    }
}

const addItem = () => {
    editForm.items.push({ id: null, descripcion: '', cantidad: 1 });
}

const removeItem = (index) => {
    editForm.items.splice(index, 1);
}

// [S893] `version` sube cada vez que se vuelve a leer el listado: la ficha abierta mira ese número y se relee (una acción cambió algo).
const version = ref(0)
const refresh = async () => {
    await store.fetchAllRemitos()
    version.value++
}

const openEditModal = async (remito) => {
    if (remito.estado !== 'BORRADOR') {
        notification.add('Solo se pueden editar remitos en estado BORRADOR.', 'warning');
        return;
    }
    // [S891] Un remito con número es inmortal: no se edita. Si está mal, se anula y se hace otro.
    if (remito.numero_legal) {
        notification.add(`El remito ${remito.numero_legal} ya tiene número: no se edita. Si está mal, anulalo.`, 'warning');
        return;
    }

    // Fallback robusto para asegurar el ID del cliente
    let c_id = remito.cliente_id || (remito.pedido && remito.pedido.cliente_id);
    
    editingRemito.value = { ...remito };
    editForm.cliente_id = c_id;
    editForm.numero_legal = remito.numero_legal || '';
    editForm.transporte_id = remito.transporte_id;
    editForm.domicilio_entrega_id = remito.domicilio_entrega_id;
    editForm.bultos = remito.bultos || 1;
    editForm.valor_declarado = remito.valor_declarado || 0;
    
    // Map items
    editForm.items = (remito.items || []).map(it => {
        // [V5 FIX] Priorizar descripcion_display que viene del backend auditado
        let desc = it.descripcion_display;
        if (!desc || desc === 'Ítem') {
            desc = it.pedido_item?.producto?.nombre || it.pedido_item?.nota || 'Ítem';
        }
        
        return {
            id: it.id,
            pedido_item_id: it.pedido_item_id,
            cantidad: it.cantidad,
            descripcion: desc
        };
    });

    if (editForm.cliente_id) {
        await onClientChanged(editForm.cliente_id);
    }

    isForcingAddress.value = false;
    editForm.nuevo_domicilio = { calle: '', numero: '', localidad: '', provincia_id: 'X' };

    // O.C. vive en Pedido, no en Remito — se trae aparte (mismo patrón que onClientChanged)
    isEditingOC.value = false;
    tempOC.value = '';
    pedidoOC.value = '';
    if (remito.pedido_id) {
        try {
            const res = await api.get(`/pedidos/${remito.pedido_id}`);
            pedidoOC.value = res.data.oc || '';
        } catch (e) {
            console.error("Error loading pedido OC", e);
        }
    }

    showEditModal.value = true;
}

const closeEditModal = () => {
    showEditModal.value = false;
    editingRemito.value = null;
    isEditingOC.value = false;
    tempOC.value = '';
    pedidoOC.value = '';
}

const startEditingOC = () => {
    tempOC.value = pedidoOC.value || '';
    isEditingOC.value = true;
}

const cancelEditOC = () => {
    isEditingOC.value = false;
    tempOC.value = '';
}

const saveOC = async () => {
    if (tempOC.value === pedidoOC.value) {
        cancelEditOC();
        return;
    }
    try {
        await pedidosStore.updatePedido(editingRemito.value.pedido_id, { oc: tempOC.value });
        notification.add('O.C. actualizada', 'success');
        pedidoOC.value = tempOC.value;
        isEditingOC.value = false;
    } catch (e) {
        notification.add('Error actualizando O.C.', 'error');
    }
}

const saveEdition = async () => {
    if (!editingRemito.value) return;
    
    isSaving.value = true;
    try {
        const payload = { ...editForm };
        if (!isForcingAddress.value) delete payload.nuevo_domicilio;
        
        await store.updateRemito(editingRemito.value.id, payload);
        notification.add('Remito actualizado correctamente.', 'success');
        refresh(); // Refresh list to see changes
        closeEditModal();
    } catch (e) {
        console.error(e);
        notification.add('Error al actualizar: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        isSaving.value = false;
    }
}

const printRemito = (remito) => {
    if (!remito || !remito.id) return;
    const pdfUrl = `/remitos/${remito.id}/pdf`;
    window.open(pdfUrl, '_blank');
}

// [S891] Genoma del remito (RemitoFlags, bits de 64): en JS los operadores de bits son de 32, así que se lee con aritmética.
const tieneBit = (flags, n) => Math.floor(Number(flags || 0) / Math.pow(2, n)) % 2 === 1
const esCorreccion = (remito) => (remito.items || []).some((i) => i.corrige_item_id !== null && i.corrige_item_id !== undefined)   // [S893] corrige lo que quedó de otro remito: sin papel ni número
const impreso = (remito) => tieneBit(remito.flags_estado, 44)   // IMPRESO: ya se imprimió alguna vez -> «Reimprimir»
const vistaPrevia = (remito) => { if (remito && remito.id) window.open(`/remitos/${remito.id}/pdf?vista_previa=1`, '_blank') }
const anulacion = reactive({ visible: false, modo: 'anular', remito: null, motivo: '', guardando: false })
const abrirAnulacion = (remito, modo) => Object.assign(anulacion, { visible: true, modo, remito, motivo: '', guardando: false })
const cerrarAnulacion = () => { anulacion.visible = false; anulacion.remito = null }
const confirmarAnulacion = async () => {
    if (!anulacion.remito || !anulacion.motivo.trim()) return
    anulacion.guardando = true
    const ruta = anulacion.modo === 'anular' ? 'anular' : (anulacion.modo === 'deshacer-correccion' ? 'deshacer-correccion' : 'deshacer-anulacion')
    try {
        await api.post(`/remitos/${anulacion.remito.id}/${ruta}`, { motivo: anulacion.motivo.trim() })
        notification.add(anulacion.modo === 'anular' ? `Remito ${anulacion.remito.numero_legal} anulado.` : (anulacion.modo === 'deshacer-correccion' ? 'Corrección deshecha: el renglón vuelve a lo que tenía.' : `Anulación del ${anulacion.remito.numero_legal} deshecha.`), 'success')
        cerrarAnulacion()
        refresh()
    } catch (e) {
        notification.add((anulacion.modo === 'anular' ? 'No se pudo anular: ' : 'No se pudo deshacer: ') + (e.response?.data?.detail || e.message), 'error')
    } finally {
        anulacion.guardando = false
    }
}

// [S892] Paquete 2, tramo 3: salida sin papel, queda en depósito (bit 37) y retiro del transporte
const enDeposito = (remito) => tieneBit(remito.flags_estado, 37)
const accionFecha = reactive({ visible: false, modo: 'sin-papel', remito: null, fecha: '', motivo: '', guardando: false })
const abrirAccionFecha = (remito, modo) => Object.assign(accionFecha, { visible: true, modo, remito, fecha: hoyISO(), motivo: '', guardando: false })
const cerrarAccionFecha = () => { accionFecha.visible = false; accionFecha.remito = null }
const confirmarAccionFecha = async () => {
    if (!accionFecha.remito || (accionFecha.modo === 'retiro' && !accionFecha.fecha)) return
    accionFecha.guardando = true
    const ruta = accionFecha.modo === 'sin-papel' ? 'salida-sin-papel' : 'retiro'
    try {
        const cuerpo = accionFecha.modo === 'retiro' ? { fecha: accionFecha.fecha } : { motivo: (accionFecha.motivo || '').trim() || null }
        const r = await api.post(`/remitos/${accionFecha.remito.id}/${ruta}`, cuerpo)
        notification.add(accionFecha.modo === 'sin-papel' ? `Salió sin papel: tomó el número ${r.data?.numero_legal || ''}.` : `Retiro registrado (${accionFecha.remito.numero_legal}).`, 'success')
        cerrarAccionFecha()
        refresh()
    } catch (e) {
        notification.add('No se pudo: ' + (e.response?.data?.detail || e.message), 'error')
    } finally {
        accionFecha.guardando = false
    }
}
const marcarEnDeposito = async (remito) => {
    if (!confirm(`¿El ${remito.numero_legal} queda en el depósito esperando que lo retire el transporte? Se borra la salida que se había asumido al emitirlo.`)) return
    try {
        await api.post(`/remitos/${remito.id}/en-deposito`)
        notification.add(`${remito.numero_legal}: queda en depósito.`, 'success')
        refresh()
    } catch (e) {
        notification.add('No se pudo: ' + (e.response?.data?.detail || e.message), 'error')
    }
}

// [S887] Imprimir desde el listado. El PDF numera el remito si todavía no tiene número (el 0015 es el talonario vivo), así que en ese caso se pide
// confirmación antes de gastar un número; el listado se refresca para mostrar el número asignado.
const imprimirRemito = (remito) => {
    if (!remito || !remito.id || remito.estado === 'ANULADO' || esCorreccion(remito)) return;
    const sinNumero = !remito.numero_legal;
    if (sinNumero && !confirm('Este remito todavía no tiene número. Al imprimirlo se le asigna el próximo número del talonario 0015 y queda guardada la imagen de lo impreso (si querés revisarlo antes, usá la vista previa). ¿Imprimir?')) return;
    printRemito(remito);
    if (!impreso(remito)) setTimeout(refresh, 1500);   // [S891] toma número y/o queda IMPRESO: el botón pasa a «Reimprimir»
}

const deleteRemito = async (remito) => {
    if (!remito) return;
    if (confirm(`¿Está seguro de eliminar definitivamente el remito ${remito.numero_legal || 'nuevo'} y su pedido asociado?`)) {
        try {
            await api.delete(`/remitos/${remito.id}`);
            notification.add('Remito y Pedido fantasma eliminados', 'success');
            refresh();
            closeEditModal();
        } catch (error) {
            notification.add('Error al eliminar: ' + (error.response?.data?.detail || error.message), 'error');
        }
    }
}

const toggleSort = (key) => {
    if (sortKey.value === key) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
        sortKey.value = key
        sortOrder.value = 'asc'
    }
}

const sortedRemitos = computed(() => {
    let items = [...store.remitos]
    
    if (searchQuery.value) {
        const query = normalizarBusqueda(searchQuery.value)   // [S892] sin acentos
        items = items.filter(r => {
            const numMatch = normalizarBusqueda(r.numero_legal).includes(query)
            const clientMatch = normalizarBusqueda(r.razon_social).includes(query)
            const pedidoMatch = String(r.pedido_id ?? '') === query.replace(/^#/, '').trim() // [S887] el Nº de pedido, exacto
            const ocMatch = normalizarBusqueda(r.oc).includes(query)   // [S893] la OC también (la lleva el remito)
            return numMatch || clientMatch || pedidoMatch || ocMatch
        })
    }

    return items.sort((a, b) => {
        let valA, valB
        
        switch (sortKey.value) {
            case 'numero': 
                valA = a.numero_legal || ''
                valB = b.numero_legal || ''
                break
            case 'fecha':
                valA = new Date(fechaRemito(a)).getTime()
                valB = new Date(fechaRemito(b)).getTime()
                break
            case 'cliente':
                valA = a.razon_social || ''
                valB = b.razon_social || ''
                break
            case 'pedido':
                valA = Number(a.pedido_id) || 0
                valB = Number(b.pedido_id) || 0
                break
            case 'estado':
                valA = a.estado || ''
                valB = b.estado || ''
                break
            default:
                return 0
        }
        
        if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1
        if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1
        return 0
    })
})

// [S890, S891] La fecha del remito: la de EMISIÓN (el día en que tomó número); los viejos sin ella, la de salida; sin número, la de armado.
const fechaRemito = (remito) => remito.numero_legal ? (remito.fecha_emision || remito.fecha_salida || remito.fecha_creacion) : remito.fecha_creacion
const hoyISO = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` }
const aISO = (s) => { const d = new Date(s); return isNaN(d) ? hoyISO() : `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` }
const cambioFecha = reactive({ visible: false, remito: null, fecha: '', motivo: '', guardando: false })
const abrirCambioFecha = (remito) => {
    Object.assign(cambioFecha, { visible: true, remito, fecha: aISO(fechaRemito(remito)), motivo: '', guardando: false })
}
const cerrarCambioFecha = () => { cambioFecha.visible = false; cambioFecha.remito = null }
const guardarCambioFecha = async () => {
    if (!cambioFecha.remito || !cambioFecha.fecha || !cambioFecha.motivo.trim()) return
    cambioFecha.guardando = true
    try {
        await api.patch(`/remitos/${cambioFecha.remito.id}/fecha`, { fecha: cambioFecha.fecha, motivo: cambioFecha.motivo.trim() })
        notification.add(`Fecha del remito ${cambioFecha.remito.numero_legal} cambiada.`, 'success')
        cerrarCambioFecha()
        refresh()
    } catch (e) {
        notification.add('No se pudo cambiar la fecha: ' + (e.response?.data?.detail || e.message), 'error')
    } finally {
        cambioFecha.guardando = false
    }
}

const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('es-AR', {
        day: '2-digit',
        month: '2-digit',
        year: '2-digit'
    })
}

const getStatusClass = (status) => {
    switch (status) {
        case 'BORRADOR': return 'bg-slate-500/20 text-slate-400 border-slate-500/50'
        case 'EN_CAMINO': return 'bg-blue-500/20 text-blue-400 border-blue-500/50'
        case 'ENTREGADO': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50'
        case 'ANULADO': return 'bg-red-500/20 text-red-400 border-red-500/50'
        default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
    }
}

const viewPedido = (id) => {
    router.push({ name: 'PedidoLogistica', params: { id } })
}

// [S893, Carlos 26/10] La FICHA del remito (ruta /logistica/remitos/:ref). Se llega por clic en la fila, por F3 + tipear (número, OC o cliente) o por
// el vínculo de otro remito del pedido. En la dirección va el número (0015-00003031) cuando es el de siempre; si no, el UUID.
const referenciaDe = (remito) => (remito.numero_legal && /^\d{4}-\d{8}$/.test(remito.numero_legal)) ? remito.numero_legal : remito.id
const abrirFicha = (remito) => router.push({ name: 'RemitoFicha', params: { ref: referenciaDe(remito) } })
const cajaBusqueda = ref(null)
const fichaAbierta = () => route.name === 'RemitoFicha'
const enfocarBusqueda = async () => {
    if (fichaAbierta()) await router.push({ name: 'RemitoList' })
    await nextTick()
    if (cajaBusqueda.value) { cajaBusqueda.value.focus(); cajaBusqueda.value.select() }
}
// Enter en el buscador: si el servidor encuentra UN remito (o el número exacto), se abre su ficha; si hay varios, quedan filtrados en la lista.
const buscarYAbrir = async () => {
    const q = searchQuery.value.trim()
    if (!q) return
    const enLista = sortedRemitos.value
    if (enLista.length === 1) return abrirFicha(enLista[0])
    try {
        const { data } = await api.get('/remitos/buscar', { params: { q } })
        if (data.exacto) return abrirFicha(data.resultados.find((x) => x.id === data.exacto) || data.resultados[0])
        if (data.total === 1) return abrirFicha(data.resultados[0])
        if (data.total === 0) notification.add(`Ningún remito coincide con «${q}».`, 'warning')
        else notification.add(`${data.total} remitos coinciden con «${q}»: elegí uno de la lista.`, 'info')
    } catch (e) {
        notification.add('No se pudo buscar: ' + (e.response?.data?.detail || e.message), 'error')
    }
}
// Alta: el Remito Manual se retiró; «Nuevo remito» (F4) elige el PEDIDO y sigue por su armado («Imprimir remito», con el cuadro abierto).
const elegirPedido = reactive({ visible: false, q: '', lista: [], cargando: false })
const cajaElegirPedido = ref(null)
let demoraBusquedaPedido = null
const buscarPedidosPorRemitar = () => {
    clearTimeout(demoraBusquedaPedido)
    demoraBusquedaPedido = setTimeout(async () => {
        elegirPedido.cargando = true
        try {
            const { data } = await api.get('/remitos/pedidos-por-remitar', { params: { q: elegirPedido.q } })
            elegirPedido.lista = data.pedidos || []
        } catch (e) {
            elegirPedido.lista = []
            notification.add('No se pudo buscar pedidos: ' + (e.response?.data?.detail || e.message), 'error')
        } finally {
            elegirPedido.cargando = false
        }
    }, 220)
}
const nuevoRemito = async () => {
    if (fichaAbierta()) await router.push({ name: 'RemitoList' })
    Object.assign(elegirPedido, { visible: true, q: '', lista: [], cargando: false })
    buscarPedidosPorRemitar()
    await nextTick()
    if (cajaElegirPedido.value) cajaElegirPedido.value.focus()
}
const cerrarElegirPedido = () => { clearTimeout(demoraBusquedaPedido); elegirPedido.visible = false }
const armarDesde = (p) => {
    if (!p) return
    cerrarElegirPedido()
    router.push({ name: 'PedidoLogistica', params: { id: p.pedido_id }, query: { armar: 1 } })
}
const hayModalAbierto = () => !!(showEditModal.value || accionFecha.visible || anulacion.visible || cambioFecha.visible || elegirPedido.visible)
// [S893, Carlos 26/10] F4 es ALTA del campo donde estás parado: si el campo ya la atiende (un selector de cliente, de producto…) el evento llega con defaultPrevented y la lista no hace nada;
// tampoco mientras haya una ventana abierta. Solo si no estás en un campo con alta, F4 es el alta del nodo: un remito nuevo (se elige el pedido).
const onKeyLista = (e) => {
    if ((e.key === 'F3' || e.key === 'F4') && (e.defaultPrevented || hayModalAbierto())) return
    if (e.key === 'F3') { e.preventDefault(); enfocarBusqueda() }
    else if (e.key === 'F4') { e.preventDefault(); nuevoRemito() }
    else if (e.key === 'Escape' && hayModalAbierto()) {
        // ESC cierra la ventana de arriba (las de acción primero); no llega a la ficha que está debajo
        e.stopImmediatePropagation()
        if (elegirPedido.visible) cerrarElegirPedido()
        else if (cambioFecha.visible) cerrarCambioFecha()
        else if (anulacion.visible) cerrarAnulacion()
        else if (accionFecha.visible) cerrarAccionFecha()
        else if (showEditModal.value) closeEditModal()
    }
}

// Las acciones del listado, para que la ficha las use sin duplicarlas (anular, fecha, depósito, retiro, sin papel, imprimir, editar).
// La ficha las llama con lo que ella sabe del remito; la fila del listado (con sus renglones y ids) tiene prioridad si está cargada.
const filaDe = (r) => store.remitos.find((x) => x.id === r.id) || r
provide('remitosAcciones', {
    version,
    refresh,
    hayModalAbierto,
    abrirAnulacion: (r, modo) => abrirAnulacion(filaDe(r), modo),
    abrirCambioFecha: (r) => abrirCambioFecha(filaDe(r)),
    abrirAccionFecha: (r, modo) => abrirAccionFecha(filaDe(r), modo),
    marcarEnDeposito: (r) => marcarEnDeposito(filaDe(r)),
    imprimirRemito: (r) => imprimirRemito(filaDe(r)),
    vistaPrevia: (r) => vistaPrevia(filaDe(r)),
    openEditModal: (r) => openEditModal(filaDe(r)),
})

onMounted(async () => {
    window.addEventListener('keydown', onKeyLista)
    refresh()
    if (maestrosStore.transportes.length === 0) maestrosStore.fetchTransportes()
    if (clientesStore.clientes.length === 0) await clientesStore.fetchClientes()
})
onUnmounted(() => window.removeEventListener('keydown', onKeyLista))
</script>

<style scoped>
.tokyo-bg {
    background: radial-gradient(circle at top right, rgba(249, 115, 22, 0.05), transparent),
                radial-gradient(circle at bottom left, rgba(234, 88, 12, 0.05), transparent);
}
.neon-orange {
    box-shadow: 0 0 20px rgba(249, 115, 22, 0.1), inset 0 0 20px rgba(249, 115, 22, 0.05);
}
</style>
