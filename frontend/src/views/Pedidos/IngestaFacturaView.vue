// [IDENTIDAD] - frontend\src\views\Pedidos\IngestaFacturaView.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans tokyo-bg neon-blue rounded-2xl border-2 border-blue-500/50 shadow-[0_0_30px_rgba(59,130,246,0.3)] p-6">
    
    <div class="flex-1 flex flex-col min-w-0">
        <!-- Header -->
        <header class="flex justify-between items-center mb-6 border-b border-blue-900/30 pb-4">
            <div>
                <h1 class="font-outfit text-2xl font-bold text-white flex items-center gap-3">
                    <i class="fas fa-robot text-blue-400"></i>
                    Ingesta Automática de Facturas
                </h1>
                <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider mt-1">
                    Conversión Inteligente: PDF AFIP <i class="fas fa-arrow-right mx-1"></i> Remito V5
                </p>
            </div>
        </header>

        <div class="grid grid-cols-12 gap-6 h-full overflow-hidden">
            
            <!-- LEFT: DROP ZONE -->
            <div class="col-span-5 flex flex-col gap-4">
                <div 
                    class="flex-1 border-2 border-dashed border-blue-500/30 bg-blue-900/10 rounded-2xl flex flex-col items-center justify-center p-8 transition-all duration-300 relative overflow-hidden group"
                    :class="{'border-blue-400 bg-blue-900/20 scale-[1.01]': isDragging, 'border-red-500/50': error}"
                    @dragover.prevent="isDragging = true"
                    @dragleave.prevent="isDragging = false"
                    @drop.prevent="handleDrop"
                    @click="triggerFileInput"
                >
                    <input type="file" ref="fileInput" class="hidden" accept=".pdf" @change="handleFileSelect">
                    
                    <div v-if="loading" class="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-20">
                        <div class="text-center">
                            <i class="fas fa-circle-notch fa-spin text-4xl text-blue-400 mb-4"></i>
                            <p class="text-blue-200 font-bold animate-pulse">Analizando Documento...</p>
                        </div>
                    </div>

                    <div class="text-center relative z-10 pointer-events-none">
                        <div class="w-20 h-20 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                            <i class="fas fa-file-pdf text-4xl text-blue-400"></i>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Arrastre su Factura Aquí</h3>
                        <p class="text-sm text-blue-300/60 mb-6 max-w-xs mx-auto">
                            Soporta Facturas de Crédito Electrónicas MiPyME (FCE) y Facturas B estándar de AFIP.
                        </p>
                        <button class="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold shadow-lg shadow-blue-900/50 transition-all pointer-events-auto">
                            O seleccione archivo
                        </button>
                    </div>
                </div>

                <!-- Instructions -->
                <div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50 text-xs text-slate-400">
                    <h4 class="font-bold text-slate-300 mb-2 uppercase"><i class="fas fa-info-circle mr-1"></i> Cómo funciona</h4>
                    <ol class="list-decimal list-inside space-y-1">
                        <li>Suba el PDF original descargado de AFIP.</li>
                        <li>El sistema extraerá Cliente, CUIT e Ítems.</li>
                        <li>Verifique los datos en el panel derecho.</li>
                        <li>Confirme para generar el Remito automáticamente.</li>
                    </ol>
                </div>
            </div>

            <!-- RIGHT: PREVIEW & ACTIONS -->
            <div class="col-span-7 flex flex-col bg-slate-900/50 rounded-2xl border border-slate-700/50 overflow-hidden relative">
                
                <!-- EMPTY STATE -->
                <div v-if="!parsedData" class="absolute inset-0 flex items-center justify-center text-slate-600 flex-col pointer-events-none">
                    <i class="fas fa-arrow-left text-4xl mb-4 opacity-20"></i>
                    <p class="font-bold opacity-30">Esperando documento...</p>
                </div>

                <!-- CONTENT -->
                <div v-else class="flex flex-col h-full">
                    <!-- Invoice & Client Header (EDITABLE) -->
                    <div class="p-6 bg-slate-800/80 border-b border-slate-700 space-y-6">
                        <div class="flex justify-between items-start">
                            <div class="flex-1 mr-4">
                                 <label class="text-[10px] uppercase font-bold text-blue-400 tracking-wider block mb-1">Nro. Factura / Remito</label>
                                 <input 
                                    v-model="parsedData.factura.numero" 
                                    class="text-2xl font-bold text-white bg-transparent border-none focus:ring-0 p-0 w-full"
                                    placeholder="0000-00000000"
                                 />
                                 <p class="text-[10px] text-blue-500/50 font-mono italic mt-1">Soberanía Total: Edite si el OCR falló.</p>
                                 <div class="mt-3 p-2 bg-blue-500/5 border border-blue-500/20 rounded-lg animate-pulse" v-if="parsedData.factura.numero">
                                     <span class="text-[9px] uppercase font-bold text-blue-400/50 block mb-1">Remito Resultante (Serie 0016)</span>
                                     <span class="text-lg font-mono font-black text-emerald-400">0016-{{ (parsedData.factura.numero.split('-')[1] || parsedData.factura.numero.split(' ')[1] || parsedData.factura.numero).trim().padStart(8, '0') }}</span>
                                 </div>
                            </div>
                            <div class="text-right flex flex-col items-end gap-2">
                                <div class="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/20 text-xs font-bold uppercase">
                                    <i class="fas" :class="auditLog?.confidence >= 80 ? 'fa-check-circle' : 'fa-info-circle'"></i> 
                                    {{ auditLog?.confidence >= 80 ? 'Validado' : 'Revisión Sugerida' }}
                                </div>
                                <div v-if="auditLog" class="text-[10px] font-mono flex items-center gap-2">
                                    <span class="text-slate-500 uppercase">Confianza Conserje:</span>
                                    <span :class="auditLog.confidence >= 80 ? 'text-emerald-400' : 'text-amber-400'">{{ auditLog.confidence }}%</span>
                                </div>
                                <div class="flex items-center gap-4">
                                    <div class="flex flex-col items-end">
                                        <span class="text-[9px] uppercase font-bold text-slate-500">Confianza Sabueso</span>
                                        <div class="w-16 h-1 bg-slate-800 rounded-full overflow-hidden">
                                            <div class="h-full transition-all duration-1000" :class="auditLog.confidence >= 80 ? 'bg-emerald-500' : 'bg-amber-500'" :style="{width: auditLog.confidence + '%'}"></div>
                                        </div>
                                    </div>
                                    <div class="h-8 w-px bg-slate-800 mx-2"></div>
                                    <!-- [NUEVO] VINCULACION STATUS -->
                                    <div class="flex flex-col">
                                        <span class="text-[9px] uppercase font-bold text-slate-500">Estado de Vínculo</span>
                                        <div class="flex items-center gap-2 mt-0.5">
                                            <span v-if="!selectedPedidoId" class="px-2 py-0.5 rounded-full bg-red-500/10 text-red-500 text-[10px] font-bold border border-red-500/20 flex items-center gap-1">
                                                <i class="fas fa-unlink"></i> SIN PEDIDO
                                            </span>
                                            <span v-else class="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 text-[10px] font-bold border border-emerald-500/20 flex items-center gap-1">
                                                <i class="fas fa-link"></i> VINCULADO #{{ selectedPedidoId }}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <!-- CLIENT BOX -->
                            <div class="bg-slate-900 p-4 rounded-xl border border-blue-500/20 shadow-inner group transition-all hover:border-blue-500/40">
                                <label class="text-[10px] uppercase text-blue-500 font-black block mb-2 tracking-widest">Cliente Destinatario</label>
                                <input 
                                    v-model="parsedData.cliente.razon_social" 
                                    class="font-bold text-white bg-transparent border-none focus:ring-0 w-full px-0 mb-1"
                                    placeholder="Razón Social..."
                                />
                                <div class="flex items-center gap-2 text-xs text-slate-400">
                                    <span class="font-mono text-blue-400/50">CUIT:</span>
                                    <input 
                                        v-model="parsedData.cliente.cuit" 
                                        class="bg-transparent border-none focus:ring-0 p-0 text-slate-300 w-full font-mono"
                                        placeholder="00-00000000-0"
                                    />
                                </div>
                            </div>

                            <!-- FISCAL DATA BOX -->
                            <div class="bg-slate-900 p-4 rounded-xl border border-slate-700/50">
                                <label class="text-[10px] uppercase text-slate-500 font-bold block mb-2">Comprobante AFIP</label>
                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <p class="text-[9px] uppercase text-slate-600 font-bold mb-1">CAE</p>
                                        <input 
                                            v-model="parsedData.factura.cae" 
                                            class="font-mono font-bold text-white bg-transparent border-none focus:ring-0 p-0 w-full text-sm"
                                            placeholder="CAE..."
                                        />
                                    </div>
                                    <div class="text-right">
                                        <p class="text-[9px] uppercase text-slate-600 font-bold mb-1">Vencimiento</p>
                                        <input 
                                            v-model="parsedData.factura.vto_cae" 
                                            class="font-mono font-bold text-white bg-transparent border-none focus:ring-0 p-0 w-full text-sm text-right"
                                            placeholder="DD/MM/YYYY"
                                        />
                                    </div>
                                 </div>
                            </div>
                        </div>

                        <!-- LOGISTICS BOX -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                             <div class="space-y-1">
                                <label class="text-[10px] uppercase text-blue-500 font-black block mb-1 tracking-widest">Empresa Logística</label>
                                <select 
                                    v-model="selectedTransportId" 
                                    class="w-full bg-slate-950 border border-blue-900/30 rounded-lg px-3 py-2 text-xs text-white focus:border-blue-500 outline-none transition-all appearance-none"
                                >
                                    <option v-for="t in maestrosStore.transportes" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                                </select>
                             </div>
                    <!-- LOGISTICS EXTENSION: COSTOS Y BULTOS -->
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 pb-4">
                        <div class="md:col-span-2 space-y-1" v-if="clientAddresses.length > 0">
                            <label class="text-[10px] uppercase text-blue-500 font-black block mb-1 tracking-widest flex items-center justify-between">
                                <span>Sede de Entrega (Padrón)</span>
                                <span v-if="addressAmbiguity" class="text-amber-500 animate-pulse flex items-center gap-1">
                                    <i class="fas fa-exclamation-triangle text-[8px]"></i> AMBIGÜEDAD: CONFIRME SEDE
                                </span>
                            </label>
                            <div class="relative group">
                                <select 
                                    v-model="selectedAddressId" 
                                    @change="onAddressSelectChange"
                                    class="w-full bg-slate-950 border rounded-lg px-3 py-2 text-xs text-white focus:border-blue-500 outline-none transition-all appearance-none pr-8"
                                    :class="[
                                        addressAmbiguity && !manualAddressChange ? 'border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.2)]' : 'border-blue-900/30',
                                        isSuggestedSelected ? 'border-emerald-500/50 shadow-[0_0_10px_rgba(16,185,129,0.2)]' : ''
                                    ]"
                                >
                                    <!-- Options from DB -->
                                    <option v-for="d in clientAddresses" :key="d.id" :value="d.id">
                                        {{ d.is_suggested ? '🪄' : (d.es_entrega ? '🚛' : '🏠') }} 
                                        {{ d.alias || (d.calle + ' ' + (d.numero || '')) }} 
                                        {{ d.is_suggested ? '(SUGERIDO)' : (d.es_fiscal ? '(FISCAL)' : '') }}
                                    </option>
                                    
                                    <!-- Management Options -->
                                    <option value="ADD_NEW" class="text-blue-400 font-bold">➕ AGREGAR NUEVA DIRECCIÓN...</option>
                                </select>
                                <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 group-hover:text-blue-400">
                                    <i class="fas" :class="isSuggestedSelected ? 'fa-magic text-emerald-400' : 'fa-chevron-down'"></i>
                                </div>
                            </div>
                        </div>
                        
                        <!-- NEW ADDRESS MINI-FORM -->
                        <div v-if="selectedAddressId === 'ADD_NEW'" class="md:col-span-4 bg-blue-500/5 border border-blue-500/20 rounded-xl p-4 mt-2 animate-in fade-in slide-in-from-top-4 duration-300">
                            <div class="flex items-center gap-2 mb-3">
                                <i class="fas fa-plus-circle text-blue-400"></i>
                                <span class="text-[10px] uppercase font-bold text-blue-200 tracking-wider">Alta de Nueva Sede de Entrega</span>
                            </div>
                            <div class="grid grid-cols-12 gap-3">
                                <div class="col-span-8">
                                    <label class="text-[8px] uppercase text-blue-400/50 font-bold block mb-1">Calle</label>
                                    <input v-model="newAddress.calle" type="text" class="w-full bg-slate-950 border border-blue-900/40 rounded px-2 py-1 text-xs text-white focus:border-blue-500 outline-none" placeholder="Calle..." />
                                </div>
                                <div class="col-span-4">
                                    <label class="text-[8px] uppercase text-blue-400/50 font-bold block mb-1">Número</label>
                                    <input v-model="newAddress.numero" type="text" class="w-full bg-slate-950 border border-blue-900/40 rounded px-2 py-1 text-xs text-white focus:border-blue-500 outline-none" placeholder="Nro..." />
                                </div>
                                <div class="col-span-6">
                                    <label class="text-[8px] uppercase text-blue-400/50 font-bold block mb-1">Localidad</label>
                                    <input v-model="newAddress.localidad" type="text" class="w-full bg-slate-950 border border-blue-900/40 rounded px-2 py-1 text-xs text-white focus:border-blue-500 outline-none" placeholder="Localidad..." />
                                </div>
                                <div class="col-span-6">
                                    <label class="text-[8px] uppercase text-blue-400/50 font-bold block mb-1">Provincia (ID)</label>
                                    <input v-model="newAddress.provincia_id" type="text" class="w-full bg-slate-950 border border-blue-900/40 rounded px-2 py-1 text-xs text-white focus:border-blue-500 outline-none uppercase" placeholder="B / X / C..." />
                                </div>
                            </div>
                            <p class="text-[9px] text-blue-400/40 italic mt-3 flex items-center gap-1">
                                <i class="fas fa-info-circle"></i> Al confirmar, esta sede se guardará permanentemente en la ficha del cliente.
                            </p>
                        </div>
                        <div class="space-y-1">
                            <label class="text-[10px] uppercase text-blue-500 font-black block mb-1 tracking-widest">Bultos</label>
                            <input type="number" v-model.number="bultos" class="w-full bg-slate-950 border border-blue-900/30 rounded-lg px-3 py-2 text-xs text-white focus:border-blue-500 outline-none transition-all text-center" />
                        </div>
                        <div class="space-y-1">
                            <label class="text-[10px] uppercase text-blue-500 font-black block mb-1 tracking-widest">Valor Decl.</label>
                            <input type="number" v-model.number="valor_declarado" class="w-full bg-slate-950 border border-blue-900/30 rounded-lg px-3 py-2 text-xs text-white focus:border-blue-500 outline-none transition-all text-center" />
                        </div>
                    </div>
                </div>
            </div>

                    <!-- Items List -->
                    <div class="flex-1 overflow-y-auto p-4 bg-slate-900/30">
                        <table class="w-full text-left border-collapse">
                            <thead class="text-xs uppercase text-slate-500 font-bold border-b border-slate-700">
                                <tr>
                                    <th class="py-2 pl-2">Descripción</th>
                                    <th class="py-2 text-right w-24">Cant.</th>
                                    <th class="py-2 w-10"></th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-800">
                                <tr v-for="(item, idx) in parsedData.items" :key="idx" class="group hover:bg-slate-800/50">
                                    <td class="py-2 pl-2">
                                        <input 
                                            v-model="item.descripcion" 
                                            type="text" 
                                            class="w-full bg-transparent border-none text-sm text-slate-300 group-hover:text-white focus:outline-none focus:ring-1 focus:ring-blue-500/50 rounded px-1 transition-all"
                                            placeholder="Descripción del ítem..."
                                        />
                                    </td>
                                    <td class="py-2 text-right">
                                        <input 
                                            v-model.number="item.cantidad" 
                                            type="number" 
                                            class="w-20 bg-blue-500/10 border border-blue-500/20 rounded px-2 py-1 text-right text-sm font-mono font-bold text-blue-300 focus:outline-none focus:border-blue-500 transition-all"
                                        />
                                    </td>
                                    <td class="py-2 text-center">
                                        <button @click="removeItem(idx)" class="text-slate-600 hover:text-red-500 transition-colors">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </td>
                                </tr>
                                
                                <!-- Add Item Row -->
                                <tr class="bg-blue-500/5">
                                    <td colspan="3" class="py-3 text-center">
                                        <button @click="addItem" class="text-[10px] font-bold text-blue-400 hover:text-blue-300 transition-all uppercase tracking-widest flex items-center justify-center w-full gap-2">
                                            <i class="fas fa-plus-circle"></i> Agregar Ítem Manual
                                        </button>
                                    </td>
                                </tr>

                                <tr v-if="parsedData.items.length === 0">
                                    <td colspan="3" class="py-8 text-center text-slate-500 italic">
                                        No hay ítems cargados.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Actions -->
                    <div class="p-4 bg-slate-800 border-t border-slate-700 flex justify-end gap-3 transition-all">
                        <button @click="reset" class="px-4 py-2 text-slate-400 hover:text-white transition">
                            Descartar
                        </button>
                        <!-- PREVIEW NATIVO REMOVIDO -->
                        <button 
                            @click="confirmIngesta"
                            :disabled="loading"
                            class="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-lg shadow-lg shadow-blue-900/30 flex items-center gap-2"
                        >
                            <i v-if="loading" class="fas fa-circle-notch fa-spin"></i>
                            <span>{{ loading ? 'Procesando...' : 'Generar Remito' }}</span>
                            <i v-if="!loading" class="fas fa-file-import"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- SE ELIMINÓ EL MODAL PREVIEW DE VUE -->

    <!-- CLIENT ABM MODAL (SABUESO INTERVENTION) -->
    <Teleport to="body">
        <div v-if="showClientAbm" class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 lg:p-12">
            <div class="border-2 border-cyan-500/50 rounded-2xl w-full max-w-5xl h-full max-h-[90vh] flex flex-col overflow-hidden shadow-[0_0_50px_rgba(6,182,212,0.2)] bg-[#0f172a]">
                <!-- V5 HUD Border Wrapper for Inspector -->
                <div class="flex-1 overflow-hidden relative">
                     <ClientCanvas
                         :isModal="true"
                         id="new"
                         :initialData="parsedData?.cliente"
                         @close="closeClientAbm"
                         @save="onClientSaved"
                     />
                </div>
            </div>
        </div>
    </Teleport>

    <!-- 409 NO PEDIDO MODAL -->
    <Teleport to="body">
        <div v-if="show409Modal" class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" @keydown.esc="close409Modal">
            <div class="bg-slate-900 border-2 border-amber-500/50 rounded-2xl w-full max-w-2xl shadow-[0_0_50px_rgba(217,119,6,0.2)] overflow-hidden">
                <!-- Header -->
                <div class="bg-gradient-to-r from-amber-900/30 to-orange-900/30 border-b border-amber-500/30 p-6">
                    <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                        <i class="fas fa-exclamation-triangle text-amber-400"></i>
                        Factura sin Pedido Vinculado
                    </h2>
                    <p class="text-sm text-amber-200/60 mt-2">
                        Esta factura requiere un pedido asociado para generar el remito. Elija una opción:
                    </p>
                </div>

                <!-- Options -->
                <div class="p-6 space-y-3">
                    <!-- Opción 1: Asignar pedido existente -->
                    <button
                        v-if="pendingPedidos.length > 0"
                        @click="selectedPedidoId && retryWithPedido(selectedPedidoId)"
                        :disabled="!selectedPedidoId"
                        class="w-full p-4 bg-blue-900/30 border border-blue-500/50 hover:border-blue-400 hover:bg-blue-900/50 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-all text-left"
                    >
                        <div class="flex items-start gap-3">
                            <i class="fas fa-link text-blue-400 mt-1"></i>
                            <div class="flex-1">
                                <p class="font-bold text-white">Asignar Pedido Existente</p>
                                <select
                                    v-model="selectedPedidoId"
                                    @click.stop
                                    class="mt-2 w-full bg-slate-950 border border-blue-500/30 rounded px-3 py-2 text-sm text-white focus:border-blue-400 outline-none"
                                >
                                    <option :value="null">-- Seleccione un pedido --</option>
                                    <option v-for="p in pendingPedidos" :key="p.id" :value="p.id">
                                        #{{ p.id }} — {{ p.cliente.razon_social }} ({{ p.fecha }})
                                    </option>
                                </select>
                            </div>
                        </div>
                    </button>

                    <!-- Opción 2: Dar de alta pedido nuevo -->
                    <button
                        @click="goToNewPedido"
                        class="w-full p-4 bg-emerald-900/30 border border-emerald-500/50 hover:border-emerald-400 hover:bg-emerald-900/50 rounded-lg transition-all text-left flex items-start gap-3"
                    >
                        <i class="fas fa-plus-circle text-emerald-400 mt-1"></i>
                        <div>
                            <p class="font-bold text-white">Dar de Alta Pedido Nuevo</p>
                            <p class="text-xs text-emerald-200/60 mt-1">Abre el formulario de nuevo pedido</p>
                        </div>
                    </button>

                    <button
                        @click="goToNewPedidoAndPrint"
                        class="w-full p-4 bg-indigo-900/30 border border-indigo-500/50 hover:border-indigo-400 hover:bg-indigo-900/50 rounded-lg transition-all text-left flex items-start gap-3 mt-2"
                    >
                        <i class="fas fa-print text-indigo-400 mt-1"></i>
                        <div>
                            <p class="font-bold text-white">Alta Pedido Nuevo + Imprimir</p>
                            <p class="text-xs text-indigo-200/60 mt-1">Crea el pedido y dispara impresión de remito al guardar</p>
                        </div>
                    </button>

                    <!-- Opción 3: Continuar sin pedido (Cuarentena) -->
                    <button
                        @click="retryInCuarentena"
                        class="w-full p-4 bg-orange-900/30 border border-orange-500/50 hover:border-orange-400 hover:bg-orange-900/50 rounded-lg transition-all text-left flex items-start gap-3"
                    >
                        <i class="fas fa-pause-circle text-orange-400 mt-1"></i>
                        <div>
                            <p class="font-bold text-white">Continuar en Cuarentena</p>
                            <p class="text-xs text-orange-200/60 mt-1">Genera remito requiere revisión supervisor</p>
                        </div>
                    </button>
                </div>

                <!-- Footer -->
                <div class="bg-slate-950 border-t border-slate-700 p-4 flex justify-end">
                    <button
                        @click="close409Modal"
                        class="px-4 py-2 text-slate-400 hover:text-white transition font-bold"
                    >
                        Salir
                    </button>
                </div>
            </div>
        </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import remitosService from '@/services/remitos';
import ingestaService from '@/services/ingesta';
import { useNotificationStore } from '@/stores/notification';
import { useMaestrosStore } from '@/stores/maestros';
import { useClientesStore } from '@/stores/clientes';
import { usePedidosStore } from '@/stores/pedidos';
import ClientCanvas from '../Hawe/ClientCanvas.vue';
import SmartSelect from '@/components/ui/SmartSelect.vue';
import api from '@/services/api';

const router = useRouter();
const notification = useNotificationStore();
const maestrosStore = useMaestrosStore();
const clientesStore = useClientesStore();

const isDragging = ref(false);
const loading = ref(false);
const error = ref(null);
const parsedData = ref(null);
const fileInput = ref(null);
const showPreview = ref(false);

const showClientAbm = ref(false);
const clientAddresses = ref([]);
const selectedTransportId = ref(null);
const selectedAddressId = ref(null);
const bultos = ref(1);
const valor_declarado = ref(0.0);
const auditLog = ref(null);
const currentRawId = ref(null);
const addressAmbiguity = ref(false);
const manualAddressChange = ref(false);

// 409 Modal State
const show409Modal = ref(false);
const pendingPedidos = ref([]);
const selectedPedidoId = ref(null);
const isSuggestedSelected = computed(() => {
    const selected = clientAddresses.value.find(d => d.id === selectedAddressId.value);
    return selected?.is_suggested || false;
});

const newAddress = ref({
    calle: '',
    numero: '',
    localidad: '',
    provincia_id: 'X'
});

// SE ELIMINARON MOCKS DE VISTA PREVIA

const triggerFileInput = () => {
    if (fileInput.value) {
        fileInput.value.click();
    } else {
        console.warn("[V5-UI] fileInput ref is not ready.");
    }
};

const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (file) await processFile(file);
};

const handleDrop = async (e) => {
    isDragging.value = false;
    const file = e.dataTransfer.files[0];
    if (file) await processFile(file);
};

const processFile = async (file) => {
    if (file.type !== 'application/pdf') {
        notification.add('Solo se admiten archivos PDF', 'error');
        return;
    }

    loading.value = true;
    error.value = null;

    try {
        const formData = new FormData();
        formData.append('file', file);
        
        // [V2] Upload Raw
        const uploadRes = await ingestaService.uploadRaw(formData);
        const rawId = uploadRes.data.id;
        currentRawId.value = rawId;

        // [V2] Get Preview & Audit
        const previewRes = await ingestaService.getPreview(rawId);
        const previewData = previewRes.data;
        
        parsedData.value = previewData.parsed_data;
        auditLog.value = previewData.audit_log;

        // [V5.6 FIX] Sincronizar resolución del Conserje con el modelo de vista
        if (auditLog.value?.client_resolution) {
            parsedData.value.cliente.db_status = auditLog.value.client_resolution.db_status;
            parsedData.value.cliente.flags_estado = auditLog.value.client_resolution.flags_estado;
            parsedData.value.cliente.id = auditLog.value.client_resolution.id;
            
            if (auditLog.value.client_resolution.razon_social) {
                parsedData.value.cliente.razon_social = auditLog.value.client_resolution.razon_social;
            }
        }
        
        notification.add('Factura analizada por Conserje V2', 'success');
        
        // Auto-load client details and scoring
        if (auditLog.value?.client_resolution?.id) {
            await loadClientDetails(auditLog.value.client_resolution.id);
            // Overwrite suggested addresses with Conserje scoring
            if (auditLog.value.domicilios_scoring?.length > 0) {
                clientAddresses.value = clientAddresses.value.map(d => {
                    const audit = auditLog.value.domicilios_scoring.find(as => as.id === d.id);
                    return audit ? { ...d, is_suggested: audit.is_suggested, score: audit.score } : d;
                });
                autoSelectAddress();
            }
        }

    } catch (e) {
        console.error(e);
        error.value = e.message;
        notification.add('Error en Ingesta V2: ' + e.message, 'error');
    } finally {
        loading.value = false;
    }
};

const reset = () => {
    parsedData.value = null;
    bultos.value = 1;
    valor_declarado.value = 0.0;
    if (fileInput.value) fileInput.value.value = '';
};

const addItem = () => {
    if (!parsedData.value) return;
    if (!parsedData.value.items) parsedData.value.items = [];
    parsedData.value.items.push({
        descripcion: '',
        cantidad: 1,
        precio_unitario: 0.0,
        codigo: null
    });
};

const removeItem = (index) => {
    if (parsedData.value && parsedData.value.items) {
        parsedData.value.items.splice(index, 1);
    }
};

const checkClientStatus = () => {
    if (!parsedData.value) return false;
    
    const status = parsedData.value.cliente.db_status;
    const flags = parsedData.value.cliente.flags_estado || 0;
    
    // Level 13 = Existence (1) | GOLD_ARCA (4) | V14_STRUCT (8)
    const BIT_EXISTENCE = 1;
    const BIT_GOLD_ARCA = 4;
    
    // Si no existe, o si no cumple con ser "Blanco" básico (1 y 4)
    if (status === 'NO_EXISTE' || !(flags & BIT_EXISTENCE) || !(flags & BIT_GOLD_ARCA)) {
        return false;
    }
    
    return true;
};

const closeClientAbm = () => {
    showClientAbm.value = false;
};

const onClientSaved = async (savedClient) => {
    showClientAbm.value = false;
    notification.add('Cliente consistido. Procediendo a generar remito...', 'success');
    
    // Update local data with the new verified status
    if (parsedData.value && savedClient) {
        parsedData.value.cliente.db_status = 'EXISTE';
        parsedData.value.cliente.flags_estado = savedClient.flags_estado;
        parsedData.value.cliente.razon_social = savedClient.razon_social;
        parsedData.value.cliente.id = savedClient.id; // Guarda el ID real devuelto por la DB
        
        await loadClientDetails(savedClient.id);
    }
    
    // Auto-resume formulation  
    confirmIngesta();
};

const loadClientDetails = async (clientId) => {
    try {
        const res = await api.get(`/clientes/${clientId}`);
        clientAddresses.value = res.data.domicilios || [];
        autoSelectAddress();
    } catch (e) {
        console.error("[V5] No se pudieron cargar domicilios del cliente", e);
    }
}

const onAddressSelectChange = () => {
    manualAddressChange.value = true;
    if (selectedAddressId.value === 'ADD_NEW') {
        const extracted = parsedData.value?.cliente?.domicilio || '';
        // Heurística básica de limpieza para el formulario
        const clean = extracted.replace('[EXTRACTED] ', '').replace('SIN DOMICILIO FISCAL', '').trim();
        
        // Intentar separar Calle y Número (Simple split por último espacio que sea número?)
        // Por ahora lo ponemos todo en calle y el usuario separa en el mini-form
        newAddress.value.calle = clean;
        newAddress.value.numero = '';
        newAddress.value.localidad = 'CABA'; // Default situational
        newAddress.value.provincia_id = 'C';
    }
}

const autoSelectAddress = () => {
    if (clientAddresses.value.length === 0) return;
    
    manualAddressChange.value = false;
    addressAmbiguity.value = false;
    
    // Logic V15.8 (Carlos Policy):
    // 1. [V15.8.5 GOLD] Priorizar Sugerencia Heurística (Magic Wand)
    const suggested = clientAddresses.value.find(d => d.is_suggested);
    if (suggested) {
        selectedAddressId.value = suggested.id;
        return;
    }

    // 2. Find all "Entrega" addresses
    const deliveryAddresses = clientAddresses.value.filter(d => d.es_entrega);
    
    if (deliveryAddresses.length === 1) {
        // Correct unique delivery address
        selectedAddressId.value = deliveryAddresses[0].id;
    } else if (deliveryAddresses.length > 1) {
        // Ambiguedad: multiple delivery
        selectedAddressId.value = deliveryAddresses[0].id; // Suggest first
        addressAmbiguity.value = true;
        notification.add('Atención: El cliente tiene múltiples sedes de entrega. Verifique cuál corresponde.', 'warning');
    } else {
        // Fallback: Fiscal
        const fiscal = clientAddresses.value.find(d => d.es_fiscal);
        selectedAddressId.value = fiscal ? fiscal.id : clientAddresses.value[0].id;
    }
}

const confirmIngesta = async () => {
    if (!parsedData.value) return;

    // [V5] Interception Check (ABM Workflow)
    if (!checkClientStatus()) {
        notification.add('El cliente no existe o requiere consistencia AFIP. Complete la ficha técnica.', 'warning');
        showClientAbm.value = true;
        return;
    }

    try {
        loading.value = true;
        
        // Prepare Payload based on schema
        // Ensure numbers are floats/ints as expected
        const payload = {
            cliente: {
                id: parsedData.value.cliente.id || null,
                cuit: parsedData.value.cliente.cuit,
                razon_social: parsedData.value.cliente.razon_social
            },
            factura: {
                numero: parsedData.value.factura.numero,
                cae: parsedData.value.factura.cae,
                vto_cae: parsedData.value.factura.vto_cae
            },
            items: parsedData.value.items.map(item => ({
                descripcion: item.descripcion,
                cantidad: parseFloat(item.cantidad),
                precio_unitario: parseFloat(item.precio_unitario || 0.0),
                codigo: item.codigo || null
            })),
            transporte_id: selectedTransportId.value,
            bultos: bultos.value,
            valor_declarado: valor_declarado.value,
            nuevo_domicilio: selectedAddressId.value === 'ADD_NEW' ? newAddress.value : null,
            audit_log: auditLog.value
        };

        if (selectedAddressId.value && selectedAddressId.value !== 'ADD_NEW') {
            payload.domicilio_id = selectedAddressId.value;
        }

        // [V2] Approve via IngestaService
        const res = await ingestaService.approve(currentRawId.value, payload);
        
        if (res.data && res.data.id) {
            notification.add('Ingesta Procesada y Sellada (Bit 22)', 'success');
            
            // In V2, we might need to get the Remito ID from the procesada response
            // For now, let's assume approve returns {id: proc_id, remito_id: rem_id}
            // I'll update the backend service to return remito_id.
            const remitoId = res.data.remito_id;
            if (remitoId) {
                const pdfUrl = `/remitos/${remitoId}/pdf`;
                window.open(pdfUrl, '_blank');
            }
            
            reset();
        }

    } catch (e) {
        console.error(e);

        // Handle 409 Conflict: Factura sin pedido vinculado OR Duplicada
        if (e.response?.status === 409) {
            loading.value = false;
            const detail = e.response.data.detail || '';
            
            if (detail.includes('FACTURA_DUPLICADA')) {
                notification.add(detail.replace('FACTURA_DUPLICADA: ', ''), 'error');
                // Alerta Visual Persistente
                error.value = detail.replace('FACTURA_DUPLICADA: ', '');
                return;
            }

            notification.add('Se requiere vinculación de pedido para continuar', 'warning');
            await handle409NoPedido();
            return;
        }

        notification.add('Error al generar remito: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        loading.value = false;
    }
};
const handle409NoPedido = async () => {
    // Check for pending pedidos with this CUIT
    const cuit = parsedData.value?.cliente?.cuit;
    if (cuit) {
        try {
            const res = await api.get('/pedidos/', { params: { cliente_cuit: cuit, estado: 'PENDIENTE' } });
            pendingPedidos.value = res.data || [];
        } catch (e) {
            console.error("[V5] No se pudieron cargar pedidos pendientes", e);
            pendingPedidos.value = [];
        }
    }
    show409Modal.value = true;
};

const retryWithPedido = async (pedidoId) => {
    if (!parsedData.value) return;

    try {
        loading.value = true;
        show409Modal.value = false;

        const payload = {
            cliente: {
                id: parsedData.value.cliente.id || null,
                cuit: parsedData.value.cliente.cuit,
                razon_social: parsedData.value.cliente.razon_social
            },
            factura: {
                numero: parsedData.value.factura.numero,
                cae: parsedData.value.factura.cae,
                vto_cae: parsedData.value.factura.vto_cae
            },
            items: parsedData.value.items.map(item => ({
                descripcion: item.descripcion,
                cantidad: parseFloat(item.cantidad),
                precio_unitario: parseFloat(item.precio_unitario || 0.0),
                codigo: item.codigo || null
            })),
            transporte_id: selectedTransportId.value,
            bultos: bultos.value,
            valor_declarado: valor_declarado.value,
            nuevo_domicilio: selectedAddressId.value === 'ADD_NEW' ? newAddress.value : null,
            modo_ingesta: 'VINCULAR_EXISTENTE',
            pedido_id_vinculado: pedidoId
        };

        if (selectedAddressId.value && selectedAddressId.value !== 'ADD_NEW') {
            payload.domicilio_id = selectedAddressId.value;
        }

        const res = await remitosService.confirmIngesta(payload);

        if (res.data && res.data.id) {
            notification.add('Remito generado con éxito', 'success');
            const pdfUrl = `/remitos/${res.data.id}/pdf`;
            window.open(pdfUrl, '_blank');
            reset();
        }
    } catch (e) {
        console.error(e);
        notification.add('Error al generar remito: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        loading.value = false;
    }
};

const goToNewPedido = () => {
    show409Modal.value = false;
    const pedidosStore = usePedidosStore();
    pedidosStore.setIngestaData(parsedData.value);
    pedidosStore.set409Context({
        parsedData: parsedData.value,
        pendingPedidos: pendingPedidos.value
    });
    router.push({ name: 'PedidoCanvas' });
};

const goToNewPedidoAndPrint = () => {
    const pedidosStore = usePedidosStore();
    pedidosStore.setAutoPrint(true);
    goToNewPedido();
};

const retryInCuarentena = async () => {
    if (!parsedData.value) return;

    try {
        loading.value = true;
        show409Modal.value = false;

        const payload = {
            cliente: {
                id: parsedData.value.cliente.id || null,
                cuit: parsedData.value.cliente.cuit,
                razon_social: parsedData.value.cliente.razon_social
            },
            factura: {
                numero: parsedData.value.factura.numero,
                cae: parsedData.value.factura.cae,
                vto_cae: parsedData.value.factura.vto_cae
            },
            items: parsedData.value.items.map(item => ({
                descripcion: item.descripcion,
                cantidad: parseFloat(item.cantidad),
                precio_unitario: parseFloat(item.precio_unitario || 0.0),
                codigo: item.codigo || null
            })),
            transporte_id: selectedTransportId.value,
            bultos: bultos.value,
            valor_declarado: valor_declarado.value,
            nuevo_domicilio: selectedAddressId.value === 'ADD_NEW' ? newAddress.value : null,
            modo_cuarentena: true
        };

        if (selectedAddressId.value && selectedAddressId.value !== 'ADD_NEW') {
            payload.domicilio_id = selectedAddressId.value;
        }

        const res = await remitosService.confirmIngesta(payload);

        if (res.data && res.data.id) {
            notification.add('Remito en cuarentena generado. Requiere revisión supervisor.', 'warning');
            const pdfUrl = `/remitos/${res.data.id}/pdf`;
            window.open(pdfUrl, '_blank');
            reset();
        }
    } catch (e) {
        console.error(e);
        notification.add('Error: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        loading.value = false;
    }
};

const close409Modal = () => {
    show409Modal.value = false;
};

import { onMounted } from 'vue';
onMounted(async () => {
    if (maestrosStore.transportes.length === 0) {
        maestrosStore.fetchTransportes();
    }

    const pedidosStore = usePedidosStore();
    if (pedidosStore.pending409Context) {
        const ctx = pedidosStore.pending409Context;
        parsedData.value = ctx.parsedData;
        pendingPedidos.value = ctx.pendingPedidos || [];
        show409Modal.value = true;
        pedidosStore.clear409Context();

        if (ctx.parsedData?.cliente?.id) {
            await loadClientDetails(ctx.parsedData.cliente.id);
        }
    }
});
</script>

<style scoped>
.tokyo-bg {
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(37, 99, 235, 0.05) 0%, transparent 20%),
        radial-gradient(circle at 90% 80%, rgba(59, 130, 246, 0.05) 0%, transparent 20%);
}
</style>
