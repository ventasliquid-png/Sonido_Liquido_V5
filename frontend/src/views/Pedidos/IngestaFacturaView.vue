// [IDENTIDAD] - frontend\src\views\Pedidos\IngestaFacturaView.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

<template>
    <div class="absolute inset-0 bg-[#0f172a] p-2 flex justify-center items-stretch overflow-hidden"
         @dragover.prevent="isDraggingGlobal = true"
         @dragleave.prevent="isDraggingGlobal = false"
         @drop.prevent="handleGlobalDrop">
        
        <!-- Global Drag Overlay -->
        <div v-if="isDraggingGlobal" class="absolute inset-0 bg-blue-900/80 backdrop-blur-sm z-[100] border-4 border-dashed border-blue-400 rounded-2xl flex items-center justify-center animate-fade-in pointer-events-none">
            <div class="text-center">
                <i class="fas fa-cloud-upload-alt text-7xl text-blue-300 mb-4 animate-bounce"></i>
                <h2 class="text-3xl font-black text-white tracking-widest">SOLTAR NUEVA FACTURA AQUÍ</h2>
                <p class="text-blue-200 mt-2">Reemplazará cualquier documento actual</p>
            </div>
        </div>

        <div class="w-full max-w-[98%] bg-[#0f172a] rounded-2xl border-2 border-slate-700 shadow-2xl overflow-hidden relative flex flex-col min-h-0">
    
    <div class="flex-1 flex flex-col min-w-0 min-h-0">
        <!-- Header -->
        <header class="flex justify-between items-center mb-3 border-b border-blue-900/30 pb-2">
            <div>
                <h1 class="font-outfit text-xl font-bold text-white flex items-center gap-2">
                    <i class="fas fa-robot text-blue-400"></i>
                    Ingesta Automática de Facturas
                    <span v-if="parsedData" class="ml-4 px-3 py-1 bg-amber-500/20 border border-amber-500/50 text-amber-300 text-xs font-bold rounded-full animate-pulse">
                        BORRADOR EN MEMORIA - NO GUARDADO
                    </span>
                </h1>
                <p class="text-[10px] text-blue-400/50 font-medium uppercase tracking-wider mt-0.5">
                    Conversión Inteligente: PDF AFIP <i class="fas fa-arrow-right mx-1"></i> Remito V5
                </p>
            </div>
        </header>
        <div class="grid grid-cols-12 gap-6 flex-1 min-h-0 overflow-hidden">
            
            <!-- LEFT: DROP ZONE -->
            <div class="col-span-5 flex flex-col gap-4 min-h-0">
                <div v-if="error" class="bg-red-950/40 border border-red-500/30 rounded-xl p-4 mb-4 text-red-200 text-xs flex items-center gap-3">
                  <i class="fas fa-times-circle text-red-500 text-lg"></i>
                  <div>
                    <p class="font-bold uppercase tracking-wider">Error de Procesamiento</p>
                    <p class="mt-1 font-mono text-[11px]">{{ error }}</p>
                  </div>
                </div>

                <!-- CARGANDO DETALLE DE PEDIDO -->
                <div v-if="loadingPedidoDetail" class="flex-1 flex items-center justify-center text-blue-400">
                    <i class="fas fa-circle-notch fa-spin text-3xl"></i>
                </div>

                <!-- PANEL DETALLE PEDIDO VINCULADO -->
                <div v-else-if="selectedPedidoDetail" class="flex-1 flex flex-col bg-slate-900/80 rounded-2xl border border-slate-700/50 overflow-hidden">
                    <!-- Header -->
                    <div class="p-4 bg-slate-800 border-b border-slate-700 flex justify-between items-center shrink-0">
                        <div>
                            <h3 class="font-bold text-white flex items-center gap-2 text-sm">
                                <i class="fas fa-clipboard-list text-blue-400"></i>
                                Pedido #{{ selectedPedidoDetail.id }}
                            </h3>
                            <p class="text-[10px] text-slate-400 mt-0.5">
                                {{ selectedPedidoDetail.fecha ? selectedPedidoDetail.fecha.split('T')[0] : '—' }}
                            </p>
                        </div>
                        <div class="flex items-center gap-2">
                            <span v-if="selectedPedidoDetail.oc_compra" class="text-[10px] font-mono text-slate-400 bg-slate-700 px-2 py-0.5 rounded">
                                OC: {{ selectedPedidoDetail.oc_compra }}
                            </span>
                            <span class="px-2 py-0.5 rounded-md text-[10px] font-bold border" :class="getStatusClassDetail(selectedPedidoDetail.estado)">
                                {{ selectedPedidoDetail.estado }}
                            </span>
                        </div>
                    </div>

                    <!-- Cliente -->
                    <div class="px-4 py-3 border-b border-slate-800 bg-slate-900/50 shrink-0">
                        <p class="text-[9px] uppercase text-blue-400/60 font-bold tracking-wider mb-1">Cliente</p>
                        <p class="font-bold text-white text-sm">{{ selectedPedidoDetail.cliente?.razon_social }}</p>
                        <p class="text-[11px] text-slate-400 font-mono">{{ selectedPedidoDetail.cliente?.cuit }}</p>
                    </div>

                    <!-- Tabla ítems -->
                    <div class="flex-1 overflow-y-auto">
                        <table class="w-full text-left border-collapse">
                            <thead class="sticky top-0 bg-slate-950">
                                <tr class="text-[9px] uppercase text-slate-500 font-bold border-b border-slate-800">
                                    <th class="py-2 pl-3 w-6">#</th>
                                    <th class="py-2">Descripción</th>
                                    <th class="py-2 px-2 text-right w-12">Cant.</th>
                                    <th class="py-2 px-2 text-right w-20">Precio</th>
                                    <th class="py-2 pr-3 text-right w-24">Subtotal</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-800/50">
                                <tr v-for="(item, idx) in selectedPedidoDetail.items" :key="item.id || idx" class="hover:bg-slate-800/30 text-xs">
                                    <td class="py-1.5 pl-3 text-slate-500 font-mono">{{ idx + 1 }}</td>
                                    <td class="py-1.5 text-slate-300 truncate max-w-[140px]">{{ item.producto?.nombre || '—' }}</td>
                                    <td class="py-1.5 px-2 text-right font-mono text-slate-300">{{ item.cantidad }}</td>
                                    <td class="py-1.5 px-2 text-right font-mono text-slate-400">{{ formatCurrencyDetail(item.precio_unitario) }}</td>
                                    <td class="py-1.5 pr-3 text-right font-mono text-emerald-400">{{ formatCurrencyDetail(item.cantidad * item.precio_unitario) }}</td>
                                </tr>
                                <tr v-if="!selectedPedidoDetail.items?.length">
                                    <td colspan="5" class="py-4 text-center text-slate-500 italic text-xs">Sin ítems</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- NOTAS -->
                    <div v-if="selectedPedidoDetail.nota" class="px-4 py-3 bg-amber-900/10 border-t border-amber-500/20 shrink-0">
                        <p class="text-[9px] uppercase text-amber-400/60 font-bold tracking-wider mb-1">📝 NOTAS</p>
                        <p class="text-xs text-amber-200/80 italic">{{ selectedPedidoDetail.nota }}</p>
                    </div>

                    <!-- Footer totales -->
                    <div class="px-4 py-3 bg-slate-950 border-t border-slate-800 space-y-1 shrink-0">
                        <div class="flex justify-between text-xs text-slate-400">
                            <span>Subtotal neto</span>
                            <span class="font-mono">{{ formatCurrencyDetail((selectedPedidoDetail.flags_estado & 4096) ? selectedPedidoDetail.total : selectedPedidoDetail.total / 1.21) }}</span>
                        </div>
                        <div v-if="!(selectedPedidoDetail.flags_estado & 4096)" class="flex justify-between text-xs text-slate-400">
                            <span>IVA 21%</span>
                            <span class="font-mono">{{ formatCurrencyDetail(selectedPedidoDetail.total - selectedPedidoDetail.total / 1.21) }}</span>
                        </div>
                        <div class="flex justify-between items-center pt-1.5 border-t border-slate-700">
                            <span class="text-xs font-bold text-white">TOTAL</span>
                            <span class="text-lg font-black font-mono text-emerald-300">{{ formatCurrencyDetail(selectedPedidoDetail.total) }}</span>
                        </div>
                    </div>

                    <!-- Botón desvincular -->
                    <div class="px-4 py-2 bg-slate-900 border-t border-slate-800 flex justify-end shrink-0">
                        <button
                            @click="selectedPedidoId = null"
                            class="text-[10px] text-slate-500 hover:text-red-400 transition-colors font-bold uppercase tracking-wider flex items-center gap-1"
                        >
                            <i class="fas fa-times"></i> Desvincular
                        </button>
                    </div>
                </div>

                <!-- DEFAULT: DROPZONE + INSTRUCCIONES -->
                <template v-else>
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

                        <!-- DUPLICATE WARNING OVERLAY -->
                        <div v-if="duplicadoData" class="absolute inset-0 bg-amber-950/90 backdrop-blur-md flex items-center justify-center z-30 flex-col border-4 border-amber-500 rounded-2xl p-8 text-center animate-fade-in shadow-[0_0_50px_rgba(245,158,11,0.3)]">
                            <i class="fas fa-exclamation-triangle text-amber-400 text-6xl mb-6 animate-bounce"></i>
                            <h3 class="text-2xl font-black text-white mb-2 tracking-widest">¡DOCUMENTO YA PROCESADO!</h3>
                            <p class="text-amber-200 font-medium mb-6">Esta factura ya se encuentra ingresada en el sistema.</p>
                            
                            <div class="bg-amber-900/50 border border-amber-500/50 rounded-xl p-4 w-full max-w-sm mb-6 text-left space-y-2">
                                <div class="flex justify-between border-b border-amber-500/30 pb-2">
                                    <span class="text-amber-400/80 text-xs uppercase font-bold">Comprobante</span>
                                    <span class="text-amber-100 font-mono font-bold">{{ duplicadoData.tipo_comprobante }} {{ String(duplicadoData.punto_venta).padStart(4, '0') }}-{{ String(duplicadoData.numero_comprobante).padStart(8, '0') }}</span>
                                </div>
                                <div class="flex justify-between border-b border-amber-500/30 pb-2">
                                    <span class="text-amber-400/80 text-xs uppercase font-bold">Pedido Vinculado</span>
                                    <span class="text-amber-100 font-bold">#{{ duplicadoData.pedido_id }}</span>
                                </div>
                                <div class="flex justify-between pb-1">
                                    <span class="text-amber-400/80 text-xs uppercase font-bold">Estado Remito</span>
                                    <span class="text-amber-100 font-bold">{{ duplicadoData.remito_estado }}</span>
                                </div>
                            </div>

                            <button @click="reset" class="px-8 py-3 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white rounded-xl font-bold shadow-lg shadow-amber-900/50 transition-all uppercase tracking-wider">
                                Entendido — Subir Otra Factura
                            </button>
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
                </template>
            </div>

            <!-- RIGHT: PREVIEW & ACTIONS -->
            <div class="col-span-7 flex flex-col bg-slate-900/50 rounded-2xl border border-slate-700/50 overflow-hidden relative min-h-0">
                
                <!-- EMPTY STATE -->
                <div v-if="!parsedData" class="absolute inset-0 flex items-center justify-center text-slate-600 flex-col pointer-events-none">
                    <i class="fas fa-arrow-left text-4xl mb-4 opacity-20"></i>
                    <p class="font-bold opacity-30">Esperando documento...</p>
                </div>

                <!-- CONTENT -->
                <div v-else class="flex-1 flex flex-col min-h-0">
                    <div class="flex-1 overflow-y-auto min-h-0 flex flex-col">
                        <!-- Invoice & Client Header (EDITABLE) -->
                        <div class="p-6 bg-slate-800/80 border-b border-slate-700 space-y-6 shrink-0">
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
                            </label>
                            <div class="relative group">
                                <select 
                                    v-model="selectedAddressId" 
                                    class="w-full bg-slate-950 border border-blue-900/30 rounded-lg px-3 py-2 text-xs text-white focus:border-blue-500 outline-none transition-all appearance-none pr-8"
                                >
                                    <!-- Options from DB -->
                                    <option v-for="d in clientAddresses" :key="d.id" :value="d.id">
                                        {{ d.es_entrega ? '🚛' : '🏠' }} 
                                        {{ d.alias || (d.calle + ' ' + (d.numero || '')) }} 
                                        {{ d.es_fiscal ? '(FISCAL)' : '' }}
                                    </option>
                                </select>
                                <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 group-hover:text-blue-400">
                                    <i class="fas fa-chevron-down"></i>
                                </div>
                            </div>
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
                    <div class="flex-1 p-4 bg-slate-900/30 shrink-0">
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
                    </div>

                    <!-- Vinculación de Pedido -->
                    <div class="p-4 bg-slate-950 border-t border-slate-800/80 shrink-0 relative z-10">
                        <div v-if="pendingPedidos.length > 0" class="flex flex-col gap-2">
                            <label class="text-[10px] uppercase text-blue-400 font-black block tracking-widest">
                                Vincular Pedido Existente
                            </label>
                            <select 
                                v-model="selectedPedidoId"
                                class="w-full bg-slate-900 border border-blue-900/30 rounded-lg px-3 py-2 text-xs text-white focus:border-blue-500 outline-none transition-all"
                            >
                                <option :value="null">-- Seleccione un pedido --</option>
                                <option value="NEW">🆕 Crear pedido nuevo (Redirigir a Canvas)</option>
                                <option v-for="p in pendingPedidos" :key="p.id" :value="p.id">
                                    #{{ p.id }} — {{ p.cliente.razon_social }} ({{ p.fecha ? p.fecha.split('T')[0] : '' }}) - Total: ${{ p.total }}
                                </option>
                            </select>
                        </div>
                        <div v-else class="bg-blue-500/5 border border-blue-500/10 rounded-xl p-3 flex items-center justify-between">
                            <span class="text-xs text-blue-300 font-medium flex items-center gap-2">
                                <i class="fas fa-info-circle text-blue-400"></i>
                                Sin pedidos pendientes para este cliente — se creará uno nuevo
                            </span>
                        </div>
                    </div>

                    <!-- Actions & Assistant Panel -->
                    <div class="p-4 bg-slate-800 border-t border-slate-700 flex flex-col gap-3 transition-all shrink-0 relative z-10">
                        <div v-if="selectedPedidoId === 'NEW'" class="grid grid-cols-1 xl:grid-cols-3 gap-3 w-full animate-fade-in">
                            <button @click="goToNewPedido" class="p-3 bg-emerald-900/30 border border-emerald-500/50 hover:bg-emerald-900/50 rounded-lg text-left flex items-start gap-3 transition-all">
                                <i class="fas fa-plus-circle text-emerald-400 mt-1 text-lg"></i>
                                <div>
                                    <p class="font-bold text-white text-sm">Crear Pedido Nuevo</p>
                                    <p class="text-[10px] text-emerald-200/60 mt-0.5 leading-tight">Ir al Canvas para armar el pedido</p>
                                </div>
                            </button>
                            <button @click="goToNewPedidoAndPrint" class="p-3 bg-indigo-900/30 border border-indigo-500/50 hover:bg-indigo-900/50 rounded-lg text-left flex items-start gap-3 transition-all">
                                <i class="fas fa-print text-indigo-400 mt-1 text-lg"></i>
                                <div>
                                    <p class="font-bold text-white text-sm">Crear e Imprimir</p>
                                    <p class="text-[10px] text-indigo-200/60 mt-0.5 leading-tight">Auto-imprimir remito al finalizar</p>
                                </div>
                            </button>
                            <button @click="retryInCuarentena" class="p-3 bg-orange-900/30 border border-orange-500/50 hover:bg-orange-900/50 rounded-lg text-left flex items-start gap-3 transition-all">
                                <i class="fas fa-pause-circle text-orange-400 mt-1 text-lg"></i>
                                <div>
                                    <p class="font-bold text-white text-sm">Enviar a Cuarentena</p>
                                    <p class="text-[10px] text-orange-200/60 mt-0.5 leading-tight">Generar remito sin pedido (requiere revisión)</p>
                                </div>
                            </button>
                        </div>
                        <div class="flex justify-end gap-3 w-full pt-2" :class="{'border-t border-slate-700 mt-2': selectedPedidoId === 'NEW'}">
                            <button @click="reset" class="px-4 py-2 text-slate-400 hover:text-white transition">
                                Descartar
                            </button>
                            <button 
                                v-if="selectedPedidoId !== 'NEW'"
                                @click="handleProceder"
                                :disabled="loading || !selectedPedidoId"
                                class="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-lg shadow-lg shadow-blue-900/30 flex items-center gap-2"
                            >
                                <i v-if="loading" class="fas fa-circle-notch fa-spin"></i>
                                <span>{{ loading ? 'Procesando...' : 'Vincular y Proceder' }}</span>
                                <i v-if="!loading" class="fas fa-file-import"></i>
                            </button>
                        </div>
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

    <!-- IDENTITY DISCREPANCY MODAL -->
    <Teleport to="body">
        <div v-if="showIdentityModal" class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div class="bg-slate-900 border-2 border-yellow-500/50 rounded-2xl w-full max-w-xl shadow-[0_0_50px_rgba(234,179,8,0.2)] overflow-hidden">
                <div class="bg-gradient-to-r from-yellow-900/30 to-amber-900/30 border-b border-yellow-500/30 p-6">
                    <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                        <i class="fas fa-id-card text-yellow-400"></i>
                        Discrepancia de Identidad Detectada
                    </h2>
                    <p class="text-sm text-yellow-200/60 mt-2">
                        El CUIT de la factura coincide con un cliente existente, pero la razón social es sustancialmente distinta.
                    </p>
                </div>
                <div class="p-6 space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
                            <p class="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1">Documento (AFIP)</p>
                            <p class="font-bold text-white">{{ parsedData?.cliente?.razon_social || '---' }}</p>
                        </div>
                        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
                            <p class="text-xs text-yellow-500 uppercase font-bold tracking-wider mb-1">Base de Datos</p>
                            <p class="font-bold text-yellow-400">{{ selectedPedidoObj?.cliente?.razon_social || '---' }}</p>
                        </div>
                    </div>
                    
                    <div class="flex flex-col gap-3 mt-6">
                        <button @click="ignorarIdentidad" class="w-full p-4 bg-emerald-900/30 border border-emerald-500/50 hover:bg-emerald-900/50 rounded-lg text-left flex items-start gap-3 transition">
                            <i class="fas fa-check-circle text-emerald-400 mt-1"></i>
                            <div>
                                <p class="font-bold text-white">Ignorar y Continuar</p>
                                <p class="text-xs text-emerald-200/60 mt-1">Es un error de tipeo o una dependencia vinculada correcta. Proceder a vincular ítems.</p>
                            </div>
                        </button>
                        <button @click="showIdentityModal = false" class="w-full p-4 bg-red-900/30 border border-red-500/50 hover:bg-red-900/50 rounded-lg text-left flex items-start gap-3 transition">
                            <i class="fas fa-hand-paper text-red-400 mt-1"></i>
                            <div>
                                <p class="font-bold text-white">Suspender Carga</p>
                                <p class="text-xs text-red-200/60 mt-1">Abortar ingesta para revisar manual en padrón.</p>
                            </div>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>

    <!-- INGESTA ITEM MODAL -->
    <IngestaItemModal
        v-if="showItemModal"
        :items="parsedData?.items || []"
        @resolved="onItemsResolved"
        @cancel="showItemModal = false"
    />

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import remitosService from '@/services/remitos';
import ingestaService from '@/services/ingesta';
import { useNotificationStore } from '@/stores/notification';
import { useMaestrosStore } from '@/stores/maestros';
import { useClientesStore } from '@/stores/clientes';
import { usePedidosStore } from '@/stores/pedidos';
import ClientCanvas from '../Hawe/ClientCanvas.vue';
import IngestaItemModal from '../Ventas/components/IngestaItemModal.vue';
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
const isDraggingGlobal = ref(false);
const showPreview = ref(false);
const selectedPedidoId = ref(null);
const pendingPedidos = ref([]);

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

const duplicadoData = ref(null);

// 409 Modal State
const isSuggestedSelected = computed(() => {
    const selected = clientAddresses.value.find(d => d.id === selectedAddressId.value);
    return selected?.is_suggested || false;
});

const pinVerification = ref('');

const newAddress = ref({
    calle: '',
    numero: '',
    localidad: '',
    provincia_id: 'X'
});

// Panel detalle pedido vinculado
const selectedPedidoDetail = ref(null)
const loadingPedidoDetail = ref(false)

const formatCurrencyDetail = (value) =>
    new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value || 0)

const getStatusClassDetail = (status) => {
    switch (status) {
        case 'PENDIENTE':   return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50'
        case 'CUMPLIDO':    return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/50'
        case 'ANULADO':     return 'bg-red-500/20 text-red-500 border-red-500/50'
        case 'PRESUPUESTO': return 'bg-purple-600/40 text-purple-300 border-purple-500/50'
        case 'INTERNO':     return 'bg-cyan-600/40 text-cyan-300 border-cyan-500/50'
        default:            return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
    }
}

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

const handleGlobalDrop = async (e) => {
    isDraggingGlobal.value = false;
    const file = e.dataTransfer.files[0];
    if (file) {
        reset(); // Clear previous
        await processFile(file);
    }
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

        // Check early duplicate detection response
        const dup = uploadRes.data.duplicado;
        if (dup && dup.encontrado) {
            duplicadoData.value = dup;
            loading.value = false;
            return;
        }

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
        } else {
            // [GY-FIX] Caso Fantasma: El cliente no existe en DB. Forzamos 'NEW' para habilitar el botón "Proceder"
            // y que el orquestador abra el ABM.
            selectedPedidoId.value = 'NEW';
            pendingPedidos.value = [];
        }

    } catch (e) {
        console.error(e);
        error.value = e.message;
        setTimeout(() => { error.value = ''; }, 9000);
        notification.add('Error en Ingesta V2: ' + e.message, 'error');
    } finally {
        loading.value = false;
    }
};

const reset = () => {
    parsedData.value = null;
    bultos.value = 1;
    valor_declarado.value = 0.0;
    clientAddresses.value = [];
    isDiscrepancyResolved.value = false;
    error.value = '';
    duplicadoData.value = null;

    if (fileInput.value) fileInput.value.value = '';
    selectedPedidoId.value = null;
    pendingPedidos.value = [];
    pinVerification.value = '';
};

const handleAnularYReingestar = async () => {
    if (!pinVerification.value) {
        notification.add('Por favor, ingrese el PIN de autorización.', 'warning');
        return;
    }
    
    try {
        loading.value = true;
        const res = await api.post(`/ingesta/raw/${currentRawId.value}/anular-y-reingestar`, {
            factura_id: duplicadoData.value.factura_id,
            pin: pinVerification.value
        });
        
        if (res.data && res.data.status === 'ok') {
            notification.add('Factura y remito anterior anulados con éxito.', 'success');
            
            const newRawId = res.data.raw_id_nuevo;
            currentRawId.value = newRawId;
            showComparePanel.value = false;
            duplicadoData.value = null;
            pinVerification.value = '';
            
            // Cargar preview del nuevo RAW
            const previewRes = await ingestaService.getPreview(newRawId);
            const previewData = previewRes.data;
            
            parsedData.value = previewData.parsed_data;
            auditLog.value = previewData.audit_log;
            
            if (auditLog.value?.client_resolution) {
                parsedData.value.cliente.db_status = auditLog.value.client_resolution.db_status;
                parsedData.value.cliente.flags_estado = auditLog.value.client_resolution.flags_estado;
                parsedData.value.cliente.id = auditLog.value.client_resolution.id;
                if (auditLog.value.client_resolution.razon_social) {
                    parsedData.value.cliente.razon_social = auditLog.value.client_resolution.razon_social;
                }
            }
            
            notification.add('Factura analizada por Conserje V2', 'success');
            
            if (auditLog.value?.client_resolution?.id) {
                await loadClientDetails(auditLog.value.client_resolution.id);
                if (auditLog.value.domicilios_scoring?.length > 0) {
                    clientAddresses.value = clientAddresses.value.map(d => {
                        const audit = auditLog.value.domicilios_scoring.find(as => as.id === d.id);
                        return audit ? { ...d, is_suggested: audit.is_suggested, score: audit.score } : d;
                    });
                    autoSelectAddress();
                }
            }
        }
    } catch (e) {
        console.error(e);
        notification.add('Error al anular y re-ingestar: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        loading.value = false;
    }
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
    
    // Auto-resume formulation with the new Orchestrator
    handleProceder();
};

const loadClientDetails = async (clientId) => {
    try {
        const res = await api.get(`/clientes/${clientId}`);
        clientAddresses.value = res.data.domicilios || [];
        autoSelectAddress();

        // Cargar y filtrar pedidos pendientes del cliente por CUIT
        const cuit = res.data.cuit;
        if (cuit) {
            const pedRes = await api.get('/pedidos/', { params: { estado: 'PENDIENTE' } });
            const targetCuit = String(cuit).replace(/-/g, '').trim();
            pendingPedidos.value = (pedRes.data || []).filter(p => {
                const pCuit = String(p.cliente?.cuit || '').replace(/-/g, '').trim();
                return pCuit === targetCuit;
            });
            if (pendingPedidos.value.length === 0) {
                selectedPedidoId.value = 'NEW';
            } else {
                selectedPedidoId.value = null; // Dejar que el operador seleccione
            }
        } else {
            pendingPedidos.value = [];
            selectedPedidoId.value = 'NEW';
        }
    } catch (e) {
        console.error("[V5] No se pudieron cargar domicilios o pedidos del cliente", e);
    }
}

const onAddressSelectChange = () => {
    manualAddressChange.value = true;
    addressAmbiguity.value = false;
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
        // Card #49 — Solo mostrar advertencia si no hay pedidos disponibles para vincular
        if (pendingPedidos.value.length === 0) {
            addressAmbiguity.value = true;
            notification.add('Atención: El cliente tiene múltiples sedes de entrega. Verifique cuál corresponde.', 'warning');
        }
    } else {
        // Fallback: Fiscal
        const fiscal = clientAddresses.value.find(d => d.es_fiscal);
        selectedAddressId.value = fiscal ? fiscal.id : clientAddresses.value[0].id;
    }
}

const showIdentityModal = ref(false);
const showItemModal = ref(false);
const selectedPedidoObj = ref(null);

const calculateSimilarity = (s1, s2) => {
    if (!s1 || !s2) return 0;
    const a = s1.toLowerCase().trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    const b = s2.toLowerCase().trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    if (a === b) return 1;
    if (a.includes(b) || b.includes(a)) return 0.9;
    
    // Similitud Jaccard simple
    const wordsA = new Set(a.split(/\s+/));
    const wordsB = new Set(b.split(/\s+/));
    const intersection = new Set([...wordsA].filter(x => wordsB.has(x)));
    const union = new Set([...wordsA, ...wordsB]);
    return intersection.size / (union.size || 1);
};

const handleProceder = () => {
    // [V5] Interception Check (ABM Workflow)
    if (!checkClientStatus()) {
        notification.add('El cliente no existe o requiere consistencia AFIP. Complete la ficha técnica.', 'warning');
        showClientAbm.value = true;
        return;
    }

    if (selectedPedidoId.value === 'NEW') {
        goToNewPedido();
    } else if (selectedPedidoId.value) {
        // [SEMÁFORO 1: Identidad Legal]
        const pedido = pendingPedidos.value.find(p => p.id === selectedPedidoId.value);
        if (!pedido) {
            goToVincularPedido();
            return;
        }
        selectedPedidoObj.value = pedido;
        
        const namePdf = parsedData.value?.cliente?.razon_social || '';
        const nameDb = pedido.cliente?.razon_social || '';
        
        const sim = calculateSimilarity(namePdf, nameDb);
        if (sim < 0.6) { // Umbral bajo para alertar si son muy distintos
            showIdentityModal.value = true;
        } else {
            // Identidad OK -> Abrir Modal de Ítems
            showItemModal.value = true;
        }
    }
};

const ignorarIdentidad = () => {
    showIdentityModal.value = false;
    showItemModal.value = true;
};

const onItemsResolved = async (resolvedItems) => {
    showItemModal.value = false;
    
    // [SEMÁFORO 2 y 3: Logística y Finanzas]
    const pedido = selectedPedidoObj.value;
    let isDiscrepancy = false;
    let motivo = [];
    
    // Cargar pendientes del pedido (si API no devuelve cantidad_pendiente lo calculamos simplificado)
    const pendingMap = {};
    const priceMap = {};
    for (const pItem of pedido.items || []) {
        // Asumimos cantidad como pendiente si no hay campo explícito (luego lo ajustamos en backend)
        const qty = pItem.cantidad_pendiente !== undefined ? pItem.cantidad_pendiente : pItem.cantidad;
        pendingMap[pItem.producto_id] = (pendingMap[pItem.producto_id] || 0) + parseFloat(qty);
        priceMap[pItem.producto_id] = parseFloat(pItem.precio_unitario);
    }
    
    for (const rItem of resolvedItems) {
        if (!rItem.producto_id) {
            isDiscrepancy = true;
            motivo.push('Ítems sin vincular a catálogo');
            break;
        }
        
        const pid = rItem.producto_id;
        const reqQty = parseFloat(rItem.cantidad);
        const reqPrice = parseFloat(rItem.precio);
        
        if (!pendingMap[pid] || reqQty > pendingMap[pid]) {
            isDiscrepancy = true; // Facturado > Pedido (Logística)
            motivo.push('Cantidades exceden saldo del pedido original');
            break;
        }
        if (Math.abs(reqPrice - priceMap[pid]) > 0.1) {
            isDiscrepancy = true; // Precio difiere (Finanzas)
            motivo.push('Discrepancia en precios unitarios');
            break;
        }
        
        pendingMap[pid] -= reqQty;
    }
    
    if (isDiscrepancy) {
        // RUTA ROJA (Migración)
        notification.add(`Ruta Roja: ${motivo[0]}. Migrando a Canvas...`, 'warning');
        const pedidosStore = usePedidosStore();
        // Guardamos los ítems resueltos para no perder el mapeo en el Canvas
        const data = { ...parsedData.value, items: resolvedItems, pedido_id_vinculado: selectedPedidoId.value };
        pedidosStore.setIngestaData(data);
        pedidosStore.set409Context({
            parsedData: data,
            pendingPedidos: pendingPedidos.value
        });
        router.push({ name: 'PedidoCanvas', params: { id: selectedPedidoId.value } });
    } else {
        // RUTA VERDE (Parcial / Exacto)
        notification.add('Ruta Verde Autorizada. Generando remito parcial sin alterar pedido...', 'success');
        parsedData.value.items = resolvedItems;
        // Inyectamos un flag para que confirmIngesta sepa qué hacer
        parsedData.value.modo_ingesta = 'VINCULAR_PARCIAL'; 
        await confirmIngesta();
    }
};

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
                precio_unitario: parseFloat(item.precio_unitario || item.precio || 0.0),
                codigo: item.codigo || item.sku || null,
                producto_id: item.producto_id || null
            })),
            transporte_id: selectedTransportId.value,
            bultos: bultos.value,
            valor_declarado: valor_declarado.value,
            nuevo_domicilio: selectedAddressId.value === 'ADD_NEW' ? newAddress.value : null,
            audit_log: auditLog.value,
            modo_ingesta: selectedPedidoId.value && selectedPedidoId.value !== 'NEW' ? 'VINCULAR_EXISTENTE' : null,
            pedido_id_vinculado: selectedPedidoId.value && selectedPedidoId.value !== 'NEW' ? Number(selectedPedidoId.value) : null,
            modo_cuarentena: false
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
                setTimeout(() => { error.value = ''; }, 9000);
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
            const res = await api.get('/pedidos/', { params: { estado: 'PENDIENTE' } });
            const targetCuit = cuit.replace(/-/g, '').trim();
            pendingPedidos.value = (res.data || []).filter(p => {
                const pCuit = (p.cliente?.cuit || '').replace(/-/g, '').trim();
                return pCuit === targetCuit;
            });
        } catch (e) {
            console.error("[V5] No se pudieron cargar pedidos pendientes", e);
            pendingPedidos.value = [];
        }
    }
    goToNewPedido();
};

const retryWithPedido = async (pedidoId) => {
    if (!parsedData.value) return;

    loading.value = true;
    show409Modal.value = false;
    selectedPedidoId.value = pedidoId;

    // [DOCTRINA INMUTABILIDAD] Forzamos la resolución de ítems en el Canvas
    goToVincularPedido();
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

const goToVincularPedido = () => {
    show409Modal.value = false;
    const pedidosStore = usePedidosStore();
    const data = { ...parsedData.value, pedido_id_vinculado: selectedPedidoId.value };
    pedidosStore.setIngestaData(data);
    pedidosStore.set409Context({
        parsedData: parsedData.value,
        pendingPedidos: pendingPedidos.value
    });
    router.push({ name: 'PedidoCanvas', params: { id: selectedPedidoId.value } });
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
                precio_unitario: parseFloat(item.precio_unitario || item.precio || 0.0),
                codigo: item.codigo || item.sku || null,
                producto_id: item.producto_id || null
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

        const res = await remitosService.confirmIngesta(currentRawId.value, payload);

        if (res.data && res.data.id) {
            notification.add('Remito en cuarentena generado. Requiere revisión supervisor.', 'warning');
            const remitoId = res.data.remito_id;
            if (remitoId) {
                const pdfUrl = `/remitos/${remitoId}/pdf`;
                window.open(pdfUrl, '_blank');
            }
            reset();
        }
    } catch (e) {
        console.error(e);
        notification.add('Error: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        loading.value = false;
    }
};

import { onMounted } from 'vue';
import { onBeforeRouteLeave } from 'vue-router';

onBeforeRouteLeave((to, from, next) => {
    const pedidosStore = usePedidosStore();
    pedidosStore.clearIngestaData();
    next();
});

onMounted(async () => {
    if (maestrosStore.transportes.length === 0) {
        maestrosStore.fetchTransportes();
    }

    const pedidosStore = usePedidosStore();
    if (pedidosStore.pending409Context) {
        const ctx = pedidosStore.pending409Context;
        parsedData.value = ctx.parsedData;
        pendingPedidos.value = ctx.pendingPedidos || [];
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
