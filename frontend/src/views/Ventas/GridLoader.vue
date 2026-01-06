<template>
    <div class="flex flex-col h-full font-sans text-emerald-50 transition-colors duration-500 ease-in-out" :class="mainThemeClass">
        
        <!-- === ZONA A: CABECERA (CONTEXTO) === -->
        <header 
            class="grid grid-cols-[100px_1fr_120px_180px] grid-rows-2 gap-px bg-slate-800 border-b border-slate-700 shrink-0 select-none text-xs"
        >
            <!-- A1. NRO PEDIDO (Top Left) -->
            <div class="bg-[#0f172a] text-slate-400 flex flex-col justify-center px-2 py-1">
                <span class="text-[9px] uppercase font-bold tracking-widest opacity-50">PEDIDO #</span>
                <span class="text-emerald-400 font-mono font-bold text-sm leading-none">{{ form.numero_manual || sugeridoId || 'NEW' }}</span>
            </div>

            <!-- A2. CLIENTE SEARCH (F3) (Top Center - Expanded) -->
            <div class="bg-[#1e293b] relative group flex flex-col justify-center px-1">
                <div class="flex items-center justify-between pointer-events-none absolute inset-x-2 top-1 z-10">
                     <span class="text-[9px] font-bold text-slate-500">CLIENTE (F3)</span>
                     <span v-if="clienteStatus" :class="clienteStatus.color" class="text-[9px] font-bold uppercase tracking-wider flex items-center gap-1">
                        <i class="fas fa-circle text-[6px]"></i> {{ clienteStatus.text }}
                     </span>
                </div>
                
                <input 
                    ref="clientInput"
                    type="text" 
                    name="client_search_v5"
                    id="client_search_v5"
                    autocomplete="new-password"
                    spellcheck="false"
                    autocorrect="off"
                    autocapitalize="none"
                    class="w-full h-full bg-transparent pt-3 pb-0 px-1 outline-none text-emerald-100 font-bold placeholder-slate-600 focus:bg-slate-700/50 transition-colors cursor-text pr-6"
                    :class="{'bg-slate-700/50': focusedZone === 'CLIENT'}"
                    placeholder="BUSCAR CLIENTE..."
                    v-model="clientQuery"
                    @input="handleClientInput"
                    @focus="focusedZone = 'CLIENT'"
                    @keydown="handleClientKeydown"
                    @contextmenu.prevent="handleInputContextMenu"
                >
                
                <!-- Clear Button -->
                <button 
                    v-if="clientQuery"
                    @click="clearClient"
                    class="absolute right-6 top-1/2 -translate-y-0 text-slate-500 hover:text-rose-500 z-20 px-2"
                    tabindex="-1"
                >
                    <i class="fa-solid fa-times"></i>
                </button>

                <!-- History Trigger (Hover) -->
                <div 
                    v-if="selectedClient"
                    class="absolute right-1 bottom-1 text-slate-500 hover:text-emerald-400 cursor-help"
                    @mouseenter="showHistoryPreview"
                    @mouseleave="hideHistoryPreview"
                >
                    <i class="fa-solid fa-clock-rotate-left"></i>
                </div>

                <Teleport to="body">
                    <div v-if="showClientResults && focusedZone === 'CLIENT'" 
                            class="fixed bg-[#0d2623] text-emerald-100 shadow-[0_20px_80px_rgba(0,0,0,0.8)] rounded-xl z-[9999] max-h-80 overflow-y-auto border border-emerald-900 border-t-0 animate-in fade-in slide-in-from-top-2 duration-150"
                            :style="clientPopupStyle">
                        <div 
                        v-for="(c, idx) in filteredClients" :key="c.id"
                        class="px-3 py-1.5 border-b border-emerald-900/30 hover:bg-emerald-900/50 cursor-pointer flex justify-between items-center group relative select-none text-xs"
                        :class="{'bg-emerald-900/50': idx === selectedClientIdx}"
                        @mousedown.left="selectClient(c)"
                        @contextmenu.prevent="openClientContextMenu($event, c)"
                        >
                        <div>
                            <span class="font-bold block" :class="!c.activo ? 'line-through text-slate-500' : 'text-emerald-100'">{{ c.razon_social }}</span>
                            <span class="text-[10px] opacity-50 font-mono flex items-center gap-2 text-emerald-400">
                                {{ c.cuit }}
                                <span v-if="!c.activo" class="bg-red-900 text-red-100 px-1 rounded text-[8px] uppercase font-bold">INACTIVO</span>
                            </span>
                        </div>
                        <div class="flex items-center gap-2">
                                <div v-if="c.domicilios?.length > 1" class="text-[9px] bg-amber-900/50 text-amber-500 px-1.5 rounded-full border border-amber-900">
                                Multi-Sede
                            </div>
                        </div>
                        </div>
                        
                        <!-- Empty State / Create New / Cantera -->
                        <div v-if="filteredClients.length === 0 && clientCanteraResults.length === 0" class="p-3 text-center text-xs space-y-3">
                            <p class="opacity-50 italic">No hay coincidencias locales.</p>
                            <p v-if="isSearchingCanteraClient" class="text-emerald-500 animate-pulse">Buscando en maestros...</p>
                            <p class="font-bold cursor-pointer text-blue-500 hover:underline mt-1 block" @mousedown="openInspectorNew">
                                (F4) Crear Nuevo Cliente Local
                            </p>
                        </div>

                        <!-- Cantera Results list (Automatic) -->
                        <div v-if="clientCanteraResults.length > 0" class="border-t border-emerald-900/30 pt-0 text-left bg-black/10">
                            <p class="text-[9px] uppercase text-emerald-500 font-bold px-3 py-1 bg-black/40 tracking-widest flex items-center justify-between">
                                <span>Cantera de Maestros</span>
                                <i v-if="isSearchingCanteraClient" class="fas fa-spinner fa-spin"></i>
                            </p>
                            <div 
                                v-for="item in clientCanteraResults" 
                                :key="item.id"
                                @mousedown.stop="importAndSelectClient(item)"
                                class="px-3 py-2 border-b border-white/5 hover:bg-emerald-900/50 cursor-pointer flex justify-between items-center group transition-colors"
                            >
                                <div class="min-w-0 flex-1">
                                    <span class="font-bold text-emerald-100 group-hover:text-emerald-400 truncate block">{{ item.razon_social }}</span>
                                    <span class="text-[9px] text-emerald-500 opacity-50 font-mono">{{ item.cuit }}</span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <i class="fas fa-eye-slash text-red-500/50 hover:text-red-400 p-2 cursor-pointer transition-colors" 
                                       title="Inactivar en Cantera (Mover a Sobrante)"
                                       @mousedown.stop="inactivateClientCantera(item)"></i>
                                    <i class="fas fa-plus-circle text-emerald-500 opacity-0 group-hover:opacity-100 transition-opacity"></i>
                                </div>
                            </div>
                        </div>
                </div>
                </Teleport>
            </div>

            <!-- A3. FECHA (Top Right) -->
            <div class="bg-[#0f172a] flex flex-col justify-center px-2 py-1">
                <span class="text-[9px] uppercase font-bold tracking-widest text-slate-500">FECHA</span>
                <input 
                    type="date" 
                    class="bg-transparent text-xs text-emerald-100 focus:outline-none cursor-pointer font-mono font-bold w-full" 
                    v-model="form.fecha"
                >
            </div>

            <!-- A4. TOTAL (Top Right - Big) -->
            <div class="bg-[#020617] text-right flex flex-col justify-center px-3 row-span-2 border-l border-slate-700">
                <span class="text-[9px] uppercase font-bold tracking-widest text-emerald-600 mb-1">TOTAL ESTIMADO</span>
                <span class="text-2xl font-mono font-bold text-emerald-400 tracking-tight leading-none">
                    {{ formatCurrency(totals.final) }}
                </span>
                <span class="text-[10px] text-slate-600 mt-1 font-mono">
                    {{ items.length }} ITEM(S) | {{ formatCurrency(totals.iva) }} IVA
                </span>
            </div>

            <!-- B1. CUIT (Bottom Left) -->
            <div class="bg-[#0f172a] flex items-center px-2 border-t border-slate-800">
                <span class="text-[9px] font-bold text-slate-500 w-8">CUIT:</span>
                <span class="font-mono text-emerald-100/80 ml-1 select-all h-full flex items-center">
                    {{ selectedClient?.cuit || '-' }}
                </span>
            </div>

            <!-- B2. LOGISTICA + COND IVA (Bottom Center) -->
            <!-- B2. LOGISTICA + NOTAS (Bottom Center - Span 2) -->
            <!-- B2. LOGISTICA + NOTAS (Bottom Center - Span 2) -->
            <div class="bg-[#1e293b] flex items-center col-span-2 border-t border-slate-700 divide-x divide-slate-700 relative z-30">
                
                <!-- 1. Logistica (Width: Auto / Approx 40%) -->
                <div 
                    class="flex items-center gap-1 px-3 cursor-pointer hover:text-emerald-400 transition-colors h-full min-w-[30%] max-w-[40%]" 
                    title="Cambiar Logística / Domicilio"
                    @click="showLogisticaModal = true"
                >
                    <i class="fa-solid fa-truck text-[10px] text-slate-500 shrink-0"></i>
                    <div class="flex flex-col leading-none ml-1 overflow-hidden">
                        <span class="font-bold truncate text-slate-300 text-[10px]">
                            {{ logisticsLabel }}
                        </span>
                        <span class="text-[9px] text-slate-500 truncate">
                            {{ selectedClient?.domicilio_entrega || 'Sin dirección de entrega' }}
                        </span>
                    </div>
                    <i class="fa-solid fa-caret-down text-[10px] text-slate-600 ml-auto pl-2"></i>
                </div>

                <!-- 2. OC (Width: Fixed 80px) -->
                <div class="w-20 h-full bg-slate-200 relative border-r border-slate-300">
                    <input 
                        type="text" 
                        v-model="form.oc"
                        placeholder="O.C."
                        autocomplete="off"
                        class="w-full h-full px-2 text-[10px] text-slate-900 placeholder-slate-500 font-bold outline-none transition-colors text-center border-none bg-transparent"
                        title="Orden de Compra"
                    >
                </div>

                <!-- 3. Nota (Width: Flex) -->
                <div class="flex-1 h-full bg-slate-200 relative">
                    <input 
                        type="text" 
                        v-model="form.nota"
                        placeholder="Observaciones del Pedido..."
                        autocomplete="off"
                        class="w-full h-full px-3 text-[10px] text-slate-900 placeholder-slate-500 font-bold outline-none transition-colors border-none bg-transparent"
                        style="color: #0f172a !important;"
                    >
                </div>

                 <!-- 4. Cond IVA (Fixed - End) -->
                <div class="flex items-center gap-1 shrink-0 px-2 bg-[#1e293b]">
                    <span class="text-[9px] font-bold text-slate-500">IVA:</span>
                    <span class="font-bold text-slate-300 truncate max-w-[80px]" :title="selectedClient?.condicion_iva_nombre">
                         {{ selectedClient?.condicion_iva_nombre || '-' }}
                    </span>
                </div>
            </div>

             <!-- B3. NOTA/OC (Bottom Right) -->

            
            <!-- SEMÁFORO (ESTADO) -->
            <div class="h-8 flex items-center bg-[#0d1f1c] rounded-md mx-2 px-1 border border-emerald-900/40">
                <button 
                    v-for="opt in statusOptions" :key="opt.value"
                    class="px-3 h-6 text-[10px] font-bold uppercase rounded transition-all mr-1 last:mr-0 flex items-center gap-1"
                    :class="form.estado === opt.value ? opt.activeClass : 'text-slate-500 hover:text-slate-300'"
                    @click="setStatus(opt.value)"
                    :title="opt.label"
                >
                    <div class="w-2 h-2 rounded-full" :class="form.estado === opt.value ? 'bg-current' : opt.dotClass"></div>
                    {{ opt.label }}
                </button>
            </div>

        </header>

        <!-- === ZONA B: CUERPO (GRILLA) === -->
        <main class="flex-1 relative flex flex-col overflow-hidden transition-colors duration-500" :class="mainThemeClass">
            <!-- ENCABEZADOS TABLA -->
            <div class="flex px-4 py-2 text-[10px] font-bold uppercase tracking-widest text-emerald-600/60 border-b border-emerald-900/30 shrink-0 bg-[#061816]">
                <div class="w-10 text-center">#</div>
                <div class="w-24">SKU</div>
                <div class="w-64 pl-2">Descripción</div>
                <div class="flex-1 pl-2">Notas / Obs</div>
                <div class="w-20 text-center">Cant.</div>
                <div class="w-12 text-center">Unid.</div>
                <div class="w-28 text-right">Unitario (4 dec)</div>
                <div class="w-32 text-right">Descuento (%)</div>
                <div class="w-32 text-right">Descuento ($)</div>
                <div class="w-24 text-right">Subtotal</div>
                <div class="w-8"></div>
            </div>

            <!-- SCROLLABLE ROWS -->
            <div ref="gridContainer" class="flex-1 overflow-y-auto custom-scrollbar relative px-4 py-1 space-y-0.5" @click="focusProductSearch">
                <!-- EMPTY STATE -->
                <div v-if="items.length === 0" class="flex flex-col items-center justify-center h-48 opacity-30 select-none pointer-events-none">
                    <i class="fa-solid fa-keyboard text-4xl mb-2"></i>
                    <p class="text-sm">Empieza escribiendo el nombre de un producto...</p>
                </div>

                <!-- RENGLONES -->
                <div 
                    v-for="(item, index) in items" 
                    :key="item._ui_id"
                    class="flex items-center py-1 border-b border-emerald-900/30 hover:bg-white/5 group transition-colors text-sm rounded px-1"
                    :class="{'bg-[#061816] ring-1 ring-emerald-500/50': focusedRow === index}"
                    @click.stop="focusedRow = index"
                >
                    <div class="w-10 text-center text-xs text-emerald-800 font-mono select-none">{{ index + 1 }}</div>
                    <div class="w-24 font-bold text-emerald-400 text-xs truncate select-all">{{ item.sku }}</div>
                    <div class="w-64 font-medium text-emerald-100 pl-2 truncate select-all" :title="item.nombre">
                        {{ item.nombre }}
                    </div>
                    
                    <!-- NOTE INPUT -->
                    <div class="flex-1 px-2">
                        <input 
                            type="text" 
                            v-model="item.nota"
                            class="w-full bg-transparent text-xs text-emerald-200/70 placeholder-emerald-900/50 outline-none focus:text-emerald-100 focus:bg-white/5 rounded px-1"
                            placeholder="..."
                            @focus="focusedRow = index"
                        >
                    </div>

                    <div class="w-20 text-center">
                        <MagicInput 
                            v-model.number="item.cantidad" 
                            inputClass="w-16 text-center bg-transparent hover:bg-white/10 focus:bg-black/20 rounded outline-none focus:ring-1 focus:ring-emerald-500 font-mono font-bold text-white placeholder-emerald-800"
                            :decimals="0"
                            @focus="focusedRow = index"
                            @update:modelValue="recalculateItemEngine(item, 'cantidad')"
                        />
                    </div>
                    
                    <div class="w-12 text-center text-[10px] text-emerald-600 uppercase select-none">{{ item.unidad || 'UN' }}</div>
                    
                    <div class="w-28 text-right font-mono">
                        <MagicInput 
                            v-model.number="item.precio_unitario" 
                            inputClass="w-24 text-right bg-transparent hover:bg-white/10 focus:bg-black/20 outline-none focus:ring-1 focus:ring-emerald-500 rounded px-1 text-emerald-300 text-xs placeholder-emerald-800"
                            :decimals="4"
                            @focus="focusedRow = index"
                            @update:modelValue="recalculateItemEngine(item, 'precio')"
                        />
                    </div>

                    <!-- DESCUENTO PORCENTAJE -->
                    <div class="w-32 text-right font-mono">
                        <MagicInput 
                            v-model.number="item.descuento_porcentaje" 
                            inputClass="w-20 text-right bg-transparent hover:bg-white/10 focus:bg-black/20 outline-none focus:ring-1 focus:ring-emerald-500 rounded px-1 text-amber-400 text-xs"
                            :decimals="2"
                            @focus="focusedRow = index"
                            @update:modelValue="recalculateItemEngine(item, 'porcentaje')"
                        />
                    </div>

                    <!-- DESCUENTO IMPORTE -->
                    <div class="w-32 text-right font-mono">
                        <MagicInput 
                            v-model.number="item.descuento_importe" 
                            inputClass="w-24 text-right bg-transparent hover:bg-white/10 focus:bg-black/20 outline-none focus:ring-1 focus:ring-emerald-500 rounded px-1 text-amber-500 text-xs"
                            :decimals="4"
                            @focus="focusedRow = index"
                            @update:modelValue="recalculateItemEngine(item, 'importe')"
                        />
                    </div>
                    
                    <div class="w-24 text-right font-bold font-mono text-emerald-100 text-sm">
                        {{ formatCurrency(item.subtotal) }}
                    </div>
                    
                    <div class="w-8 text-center opacity-0 group-hover:opacity-100 cursor-pointer text-emerald-700 hover:text-red-400 transition-opacity" @click.stop="removeItem(index)">
                        <i class="fa-solid fa-times"></i>
                    </div>
                </div>

                <!-- INPUT LINE (SEARCH) -->
                <div 
                    class="flex items-center py-2 mt-2 bg-[#020a0f] border border-emerald-900/50 shadow-sm rounded-md px-2 sticky bottom-2 z-10"
                    :class="{'ring-1 ring-emerald-500 border-emerald-500': focusedZone === 'PRODUCT'}"
                    @click.stop
                >
                    <div class="w-10 text-center text-xs text-emerald-800 font-bold items-center flex justify-center h-full">
                        <i class="fas fa-plus scale-75"></i>
                    </div>
                    <div class="flex-1 relative">
                        <input 
                            ref="productInput"
                            type="text" 
                            name="search_product_v5"
                            id="search_product_v5"
                            autocomplete="new-password"
                            spellcheck="false"
                            autocorrect="off"
                            autocapitalize="none"
                            class="w-full bg-transparent outline-none placeholder-emerald-800 font-bold text-emerald-100"
                            :placeholder="productPlaceholder"
                            v-model="productQuery"
                            @focus="focusedZone = 'PRODUCT'"
                            @keydown="handleProductKeydown"
                        >
                            <!-- POPUP RESULTADOS PRODUCTO (Teletransportado para evitar cortes de capa) -->
                            <Teleport to="body">
                                <div v-if="(showProductResults || productCanteraResults.length > 0) && focusedZone === 'PRODUCT'" 
                                     class="fixed bg-[#112d2a] text-emerald-100 shadow-[0_30px_90px_rgba(0,0,0,0.9)] rounded-2xl border border-emerald-400/30 z-[9999] overflow-hidden backdrop-blur-3xl transition-all animate-in fade-in zoom-in-95 duration-200"
                                     :style="productPopupStyle">
                                    <div class="px-4 py-3 bg-emerald-950/80 text-[10px] text-emerald-300 uppercase tracking-widest flex items-center justify-between border-b border-white/5">
                                        <div class="flex items-center gap-3">
                                            <i class="fas fa-search text-emerald-500"></i>
                                            <span v-if="filteredProducts.length > 0" class="font-bold">Sugerencias ({{ filteredProducts.length }})</span>
                                            <span v-else class="font-bold">Buscando en Maestros...</span>
                                        </div>
                                        <div class="flex items-center gap-3">
                                            <span class="text-[9px] opacity-30 lowercase italic font-normal">ESC para cerrar</span>
                                            <button @click.stop="productQuery = ''" class="hover:bg-red-500/30 text-emerald-500 hover:text-red-400 w-7 h-7 rounded-lg flex items-center justify-center transition-all bg-white/5 border border-white/5 shadow-inner">
                                                <i class="fas fa-times text-xs"></i>
                                            </button>
                                        </div>
                                    </div>
                                <div class="max-h-80 overflow-y-auto">
                                    <!-- Local Results -->
                                    <!-- Local Results -->
                                    <div 
                                        v-for="(p, idx) in filteredProducts" :key="p.id"
                                        class="px-4 py-2 border-b border-emerald-900/10 cursor-pointer flex justify-between items-center transition-colors gap-4 group"
                                        :class="idx === selectedProdIdx && focusedZone === 'PRODUCT' ? 'bg-emerald-600 text-white' : 'hover:bg-white/5'"
                                        @mousedown="addProduct(p)"
                                        @mouseover="selectedProdIdx = idx"
                                    >
                                        <div class="flex-1 min-w-0">
                                            <div class="font-bold text-sm flex items-center gap-2 truncate">
                                                {{ p.nombre }}
                                            </div>
                                            <div class="text-[10px] opacity-60 font-mono flex gap-3 mt-0.5">
                                                <span class="bg-white/10 px-1 rounded">{{ p.sku }}</span>
                                                <span v-if="p.rubro_nombre">{{ p.rubro_nombre }}</span>
                                            </div>
                                        </div>
                                        <div class="text-right shrink-0">
                                            <div class="font-mono font-bold text-emerald-400 group-hover:text-emerald-300">
                                                {{ formatCurrency(p.precio_sugerido || 0) }}
                                            </div>
                                            <div class="text-[10px] opacity-40">Lista</div>
                                        </div>
                                    </div>

                                    <!-- Product Cantera Results (Automatic) -->
                                    <div v-if="productCanteraResults.length > 0" class="bg-black/20 border-t border-emerald-500/20">
                                         <p class="text-[9px] uppercase text-emerald-500 font-bold px-4 py-1.5 bg-black/40 tracking-widest flex items-center justify-between">
                                            <span>Cantera de Maestros</span>
                                            <i v-if="isSearchingCanteraProduct" class="fas fa-spinner fa-spin"></i>
                                        </p>
                                        <div 
                                            v-for="item in productCanteraResults" 
                                            :key="item.id"
                                            @mousedown.stop="importAndAddProduct(item)"
                                            class="px-4 py-2 border-b border-white/5 hover:bg-emerald-900/40 cursor-pointer flex justify-between items-center group transition-colors"
                                        >
                                            <div class="min-w-0 flex-1">
                                                <p class="font-bold text-emerald-100 text-sm truncate group-hover:text-emerald-400 transition-colors">{{ item.nombre }}</p>
                                                <p class="text-[9px] opacity-50 font-mono text-emerald-500">{{ item.sku }}</p>
                                            </div>
                                            <div class="flex items-center gap-3">
                                                 <i class="fas fa-eye-slash text-red-500/40 hover:text-red-400 p-2 cursor-pointer transition-colors" 
                                                   title="Inactivar en Cantera"
                                                   @mousedown.stop="inactivateProductCantera(item)"></i>
                                                <i class="fas fa-plus-circle text-emerald-500 opacity-60 group-hover:opacity-100 transition-all transform group-hover:scale-110"></i>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Empty / Loading State -->
                                    <div v-if="filteredProducts.length === 0 && productCanteraResults.length === 0" class="p-8 text-center">
                                        <p v-if="isSearchingCanteraProduct" class="text-emerald-500 animate-pulse">Consultando catálogos maestros...</p>
                                        <p v-else class="text-white/20 italic text-xs">No se encontraron productos locales ni maestros coincidencias.</p>
                                    </div>
                                </div>
                            </div>
                        </Teleport>
                    </div>
                </div>
            </div>
        </main>

        <!-- === ZONA C: PIE (LIQUIDACIÓN) === -->
        <footer 
            class=" relative z-40 px-6 py-4 border-t border-emerald-900/30 shadow-[0_-4px_20px_rgba(0,0,0,0.2)] transition-colors"
            :class="form.estado === 'PENDIENTE' ? 'bg-[#061816]' : 'bg-[#0f0a1e]'"
        >
            <!-- OVERRIDE LOGISTICA -->
            <div class="absolute -top-3 left-6">
                <div class="bg-white border border-slate-200 text-[10px] px-3 py-1 rounded-full shadow-sm cursor-pointer hover:border-blue-400 hover:text-blue-600 flex items-center gap-2 transition-all text-slate-500 font-bold tracking-tight">
                    <i class="fa-solid fa-truck"></i>
                    <span>Logística: <b class="text-slate-700">{{ selectedClient?.transporte_nombre || 'Retiro en Local' }}</b></span>
                    <i class="fa-solid fa-chevron-down opacity-50 text-[9px]"></i>
                </div>
            </div>

            <div class="flex items-end justify-between gap-8">
                <!-- COMENTARIOS -->
                <div class="flex-1 max-w-xl">
                    <textarea 
                        class="w-full h-12 bg-white border border-slate-200 rounded-lg p-2 text-xs text-slate-900 outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 resize-none placeholder-slate-400 transition-all shadow-inner"
                        placeholder="Notas internas, instrucciones de entrega o comentarios del pedido..."
                        v-model="form.nota"
                    ></textarea>
                </div>

                <!-- TOTALES -->
                <div class="flex gap-8 items-end pb-1">
                    <div class="text-right space-y-0.5">
                        <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Subtotal Bruto</div>
                        <div class="font-mono text-slate-500 text-sm">{{ formatCurrency(totals.bruto) }}</div>
                    </div>

                    <!-- DTO GLOBAL -->
                    <div class="text-right space-y-0.5 border-l border-slate-700 pl-4">
                        <div class="text-[10px] text-amber-600 uppercase font-bold tracking-wider">Dto Global (%)</div>
                        <MagicInput 
                            v-model.number="form.descuento_global_porcentaje" 
                            inputClass="w-16 text-right bg-transparent border-b border-amber-900/30 text-amber-500 text-xs outline-none focus:border-amber-500 font-mono"
                            :decimals="2"
                            @update:modelValue="handleGlobalDiscountInputEngine('porcentaje')"
                        />
                    </div>
                    <div class="text-right space-y-0.5">
                        <div class="text-[10px] text-amber-600 uppercase font-bold tracking-wider">Dto Global ($)</div>
                        <MagicInput 
                            v-model.number="form.descuento_global_importe" 
                            inputClass="w-24 text-right bg-transparent border-b border-amber-900/30 text-amber-600 text-xs outline-none focus:border-amber-600 font-mono"
                            :decimals="4"
                            @update:modelValue="handleGlobalDiscountInputEngine('importe')"
                        />
                    </div>
                    
                    <div class="text-right space-y-0.5" v-if="totals.iva > 0">
                        <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">IVA (21%)</div>
                        <div class="font-mono text-slate-500 text-sm">{{ formatCurrency(totals.iva) }}</div>
                    </div>

                    <div class="text-right pl-6 border-l border-slate-200">
                        <div class="text-[10px] uppercase font-bold tracking-wider mb-0.5" 
                             :class="form.estado === 'PENDIENTE' ? 'text-emerald-600' : 'text-purple-600'">
                           {{ totals.iva > 0 ? 'TOTAL FINAL' : 'TOTAL NETO' }}
                        </div>
                        <div class="text-3xl font-bold font-mono leading-none tracking-tight text-slate-800">
                            {{ formatCurrency(totals.final) }}
                        </div>
                    </div>
                </div>

                <!-- ACTIONS -->
                <div class="flex items-center gap-3 ml-auto">
                    <!-- TOGGLE EXCEL (Now Inline) -->
                    <div class="flex items-center gap-2 bg-[#061816]/50 px-3 py-2 rounded-lg border border-emerald-900/30 text-[10px] text-emerald-400 select-none cursor-pointer hover:bg-[#061816]/80 transition-colors" @click="downloadExcel = !downloadExcel">
                        <div class="w-3 h-3 rounded-sm border border-emerald-600 flex items-center justify-center transition-colors" :class="{'bg-emerald-600': downloadExcel}">
                            <i v-if="downloadExcel" class="fa-solid fa-check text-white text-[8px]"></i>
                        </div>
                        <span class="font-bold">Generar Excel</span>
                    </div>

                    <!-- BOTON LIMPIAR (Reset) -->
                    <button 
                        v-if="items.length > 0 || selectedClient"
                        class="h-12 px-4 rounded-lg bg-slate-800 text-slate-400 hover:text-rose-400 hover:bg-slate-700 transition-colors font-bold text-[10px] uppercase tracking-wider flex items-center gap-2 border border-slate-700 group"
                        @click="handleClearManual"
                        title="Limpiar pantalla y borrar borrador (Ctrl+Del sugerido)"
                    >
                        <i class="fa-solid fa-trash group-hover:animate-bounce"></i>
                        <span>LIMPIAR PANTALLA</span>
                    </button>

                    <!-- BOTON PROCESAR -->
                    <button 
                        class="h-12 px-6 rounded-lg font-bold tracking-wider flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95 text-white shadow-lg"
                        :class="form.tipo === 'PEDIDO' ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-900/50' : 'bg-purple-600 hover:bg-purple-500 shadow-purple-900/50'"
                        @click="handleSubmit"
                    >
                        <span v-if="isSubmitting" class="animate-spin"><i class="fa-solid fa-circle-notch"></i></span>
                        <span v-else class="flex items-center gap-2">
                            <span>GUARDAR</span>
                            <span class="bg-white/20 px-1.5 py-0.5 rounded text-[10px] font-mono opacity-80">F10</span>
                        </span>
                    </button>
                </div>
            </div>
        </footer>

        <!-- === OVERLAYS === -->
        
        <!-- Context Menu -->
        <Teleport to="body">
            <ContextMenu 
                v-if="contextMenu.show"
                v-model="contextMenu.show" 
                :x="contextMenu.x" 
                :y="contextMenu.y" 
                :actions="contextMenu.actions" 
                @close="contextMenu.show = false"
            />
            
            <ClientHistoryPopover 
                :visible="historyPopover.show"
                :x="historyPopover.x"
                :y="historyPopover.y"
                :orders="historyPopover.orders"
                @close="historyPopover.show = false"
            />
        </Teleport>

        <!-- Cliente Inspector (Overlay Mode) -->
        <Teleport to="body">
            <!-- click.self removed to prevent accidental close -->
            <div v-if="showInspector" class="fixed inset-0 z-[60] flex justify-end bg-black/50 backdrop-blur-sm">
                <div class="w-full max-w-lg h-full shadow-2xl overflow-y-auto transform transition-transform duration-300">
                    <ClienteInspector 
                        :modelValue="clienteForInspector"
                        :isNew="isInspectorNew"
                        mode="compact"
                        @close="closeInspector"
                        @save="handleInspectorSave"
                        @delete="handleInspectorDelete"
                        @switch-client="switchToClient"
                        @manage-segmentos="openSegmentoAbm"
                    />
                </div>
            </div>
        </Teleport>
        
        <!-- Product Inspector (Overlay Mode) -->
        <Teleport to="body">
            <div v-if="showProductInspector" class="fixed inset-0 z-[60] flex justify-end bg-black/50 backdrop-blur-sm">
                <div class="w-full max-w-lg h-full shadow-2xl overflow-y-auto transform transition-transform duration-300">
                    <ProductoInspector 
                        :producto="productForInspector"
                        :rubros="productosStore.rubros"
                        @close="closeProductInspector"
                        @save="handleProductInspectorSave"
                    />
                </div>
            </div>
        </Teleport>

        <!-- Segmento ABM for Tactical Mode -->
        <Teleport to="body">
            <SimpleAbmModal
                v-if="showSegmentoAbm"
                title="Administrar Segmentos"
                :items="segmentosList"
                @close="showSegmentoAbm = false"
                @create="handleCreateSegmento"
                @delete="handleDeleteSegmento"
            />
        </Teleport>
        <!-- Logistica Selector Modal -->
        <Teleport to="body">
            <div v-if="showLogisticaModal" class="fixed inset-0 z-[70] flex items-center justify-center bg-black/60 backdrop-blur-sm" @click.self="showLogisticaModal = false">
                <div class="bg-[#0f172a] w-96 rounded-lg border border-slate-700 shadow-2xl p-4">
                    <h3 class="text-emerald-400 font-bold mb-4">Seleccionar Domicilio / Transporte</h3>
                    
                    <div v-if="selectedClient && selectedClient.domicilios && selectedClient.domicilios.length > 0" class="space-y-2 max-h-[60vh] overflow-y-auto custom-scrollbar">
                        <div 
                            v-for="dom in selectedClient.domicilios" 
                            :key="dom.id"
                            class="p-2 border border-slate-700 rounded hover:bg-slate-800 cursor-pointer transition-colors"
                            @click="handleUpdateLogistica({ 
                                transporte_id: dom.transporte_id, 
                                transporte_nombre: dom.transporte?.nombre || 'Retiro Local', 
                                domicilio_entrega: dom.calle + ' ' + dom.numero + ' (' + dom.localidad + ')'
                            })"
                        >
                            <div class="font-bold text-slate-200">{{ dom.calle }} {{ dom.numero }}</div>
                            <div class="text-xs text-slate-500">{{ dom.localidad }} - {{ dom.provincia?.nombre }}</div>
                            <div class="text-[10px] text-emerald-600 mt-1">
                                <i class="fa-solid fa-truck"></i> {{ dom.transporte?.nombre || 'Retiro en Local' }}
                            </div>
                        </div>
                    </div>
                    <div v-else class="text-slate-500 text-sm italic text-center py-4">
                        El cliente no tiene domicilios registrados.
                    </div>

                    <button @click="showLogisticaModal = false" class="mt-4 w-full bg-slate-800 text-slate-400 hover:text-white py-2 rounded">
                        Cancelar
                    </button>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import _ from 'lodash';
import { useClientesStore } from '@/stores/clientes';
import { useProductosStore } from '@/stores/productos';
import { usePedidosStore } from '@/stores/pedidos';
import { useMaestrosStore } from '@/stores/maestros';
import apiClient from '@/services/api';
import ContextMenu from '@/components/common/ContextMenu.vue';
import ClientHistoryPopover from '@/components/common/ClientHistoryPopover.vue';
import ClienteInspector from '../Hawe/components/ClienteInspector.vue';
import ProductoInspector from '../Hawe/components/ProductoInspector.vue';
import SimpleAbmModal from '@/components/common/SimpleAbmModal.vue';
import MagicInput from '@/components/ui/MagicInput.vue';
import canteraService from '@/services/canteraService';
import { useNotificationStore } from '@/stores/notification';

// STORES
const notificationStore = useNotificationStore();
const clientesStore = useClientesStore();
const productosStore = useProductosStore(); 
const pedidosStore = usePedidosStore();
const route = useRoute();
const router = useRouter();

// UI STATE
const isEditing = computed(() => !!route.query.edit);
const focusedZone = ref('CLIENT'); 
const focusedRow = ref(null);
const clientInput = ref(null);
const productInput = ref(null);
const gridContainer = ref(null);

const clientQuery = ref('');
const productQuery = ref('');
const showClientResults = ref(false);
const selectedClientIdx = ref(0);
const selectedProdIdx = ref(0);

// NEW: Product Inspector State
const showProductInspector = ref(false);
const productForInspector = ref(null);
const isProductInspectorNew = ref(false);

// HISTORY POPOVER
const historyPopover = ref({
    show: false,
    x: 0,
    y: 0,
    orders: []
});

const isSubmitting = ref(false);
const draftId = ref(null);
const downloadExcel = ref(false); // Default false per user feedback, or persist? Let's default false.

// INSPECTOR & CONTEXT MENU
const showInspector = ref(false);
const clienteForInspector = ref(null);
const isInspectorNew = ref(false);

const contextMenu = ref({
    show: false,
    x: 0,
    y: 0,
    actions: []
});

// SEGMENTOS ABM (Tactical)
const showSegmentoAbm = ref(false);
const userMaestros = useMaestrosStore();
const segmentosList = computed(() => userMaestros.segmentos);

// CANTERA INTEGRATION
const clientCanteraResults = ref([]);
const productCanteraResults = ref([]);
const isSearchingCanteraClient = ref(false);
const isSearchingCanteraProduct = ref(false);

const handleClientCanteraSearch = _.debounce(async (val) => {
    if (!val || val.length < 3) {
        clientCanteraResults.value = [];
        return;
    }
    isSearchingCanteraClient.value = true;
    try {
        const res = await canteraService.searchClientes(val);
        // Deduplicación por CUIT (si ya existe localmente, no mostrar en maestros)
        const localCuits = new Set(clientesStore.clientes.filter(c => c.activo).map(c => c.cuit).filter(Boolean));
        clientCanteraResults.value = res.data.filter(c => !localCuits.has(c.cuit));
    } catch (e) {
        console.error("Cantera client search error", e);
    } finally {
        isSearchingCanteraClient.value = false;
    }
}, 400);

const handleProductCanteraSearch = _.debounce(async (val) => {
    if (!val || val.length < 3) {
        productCanteraResults.value = [];
        return;
    }
    isSearchingCanteraProduct.value = true;
    try {
        const res = await canteraService.searchProductos(val);
        // Deduplicación por SKU
        const localSkus = new Set(productosStore.productos.map(p => p.sku).filter(Boolean));
        productCanteraResults.value = res.data.filter(p => !localSkus.has(p.sku));
    } catch (e) {
        console.error("Cantera product search error", e);
    } finally {
        isSearchingCanteraProduct.value = false;
    }
}, 400);

// Auto-trigger Cantera Search
watch(clientQuery, (newVal) => {
    if (newVal.length >= 3) {
        handleClientCanteraSearch(newVal);
    } else {
        clientCanteraResults.value = [];
    }
});

watch(productQuery, (newVal) => {
    if (newVal.length >= 3) {
        handleProductCanteraSearch(newVal);
    } else {
        productCanteraResults.value = [];
    }
});

const importAndSelectClient = async (item) => {
    try {
        notificationStore.add('Importando cliente...', 'info');
        await canteraService.importCliente(item.id);
        await clientesStore.fetchClientes();
        const imported = clientesStore.clientes.find(c => c.id === item.id);
        if (imported) selectClient(imported);
        notificationStore.add('Cliente importado con éxito', 'success');
        clientCanteraResults.value = [];
    } catch (e) {
        notificationStore.add('Error al importar cliente.', 'error');
    }
};

const importAndAddProduct = async (item) => {
    try {
        notificationStore.add('Importando producto...', 'info');
        await canteraService.importProducto(item.id); 
        await productosStore.fetchProductos();
        // Force string comparison for IDs if coming from SQLite
        const imported = productosStore.productos.find(p => String(p.id) === String(item.id));
        if (imported) addProduct(imported);
        notificationStore.add('Producto importado con éxito', 'success');
        productCanteraResults.value = [];
    } catch (e) {
        notificationStore.add('Error al importar producto.', 'error');
    }
};

const inactivateClientCantera = async (item) => {
    if(!confirm(`¿Desea marcar a "${item.razon_social}" como INACTIVO en la Cantera de Maestros?`)) return;
    try {
        await canteraService.inactivateCliente(item.id);
        clientCanteraResults.value = clientCanteraResults.value.filter(c => c.id !== item.id);
        notificationStore.add('Maestro inactivado correctamente.', 'success');
    } catch(e) {
        notificationStore.add('Error al inactivar maestro.', 'error');
    }
};

const inactivateProductCantera = async (item) => {
    if(!confirm(`¿Desea marcar el producto "${item.nombre}" como INACTIVO en la Cantera de Maestros?`)) return;
    try {
        await canteraService.inactivateProducto(item.id);
        productCanteraResults.value = productCanteraResults.value.filter(p => p.id !== item.id);
        notificationStore.add('Maestro inactivado correctamente.', 'success');
    } catch(e) {
        notificationStore.add('Error al inactivar maestro.', 'error');
    }
};

const openSegmentoAbm = () => {
    showSegmentoAbm.value = true;
};

const handleCreateSegmento = async (name) => {
    try {
        await userMaestros.createSegmento({ nombre: name });
    } catch(e) { alert(e.message) }
};

const handleDeleteSegmento = async (id) => {
    try {
        await userMaestros.deleteSegmento(id);
    } catch(e) { alert("No se puede eliminar: " + e.message) }
};

// DATA STATE
const form = ref({
    fecha: new Date().toISOString().split('T')[0],
    oc: '',
    nota: '',
    estado: 'PENDIENTE', // PENDIENTE (Pedido) | PRESUPUESTO
    tipo_facturacion: 'B', // Default Fiscal (A/B) para coincidir con PENDIENTE
    numero_manual: '',
    descuento_global_porcentaje: 0,
    descuento_global_importe: 0
});

const statusOptions = [
    { value: 'PRESUPUESTO', label: 'PRESUPUESTO', activeClass: 'bg-indigo-900/50 text-indigo-300 border border-indigo-500/50 shadow-sm', dotClass: 'bg-indigo-800' },
    { value: 'PENDIENTE', label: 'PEDIDO FIRME', activeClass: 'bg-emerald-900/50 text-emerald-300 border border-emerald-500/50 shadow-sm', dotClass: 'bg-emerald-800' },
    { value: 'CUMPLIDO', label: 'CUMPLIDO', activeClass: 'bg-yellow-900/50 text-yellow-300 border border-yellow-500/50 shadow-sm', dotClass: 'bg-yellow-800' },
    { value: 'INTERNO', label: 'INTERNO / SIN IVA', activeClass: 'bg-pink-900/50 text-pink-300 border border-pink-500/50 shadow-sm', dotClass: 'bg-pink-600' },
    { value: 'ANULADO', label: 'ANULADO', activeClass: 'bg-red-900/50 text-red-300 border border-red-500/50 shadow-sm', dotClass: 'bg-red-600' }
];

const sugeridoId = ref(0); // To store valid next ID

const showLogisticaModal = ref(false); // [GY-MOD] Logistica Selection


const selectedClient = ref(null);
const items = ref([]);


// --- COMPUTED STYLES ---

const headerThemeClass = computed(() => {
    if (form.value.estado === 'PRESUPUESTO') return 'bg-[#1a0b1e] border-purple-900 text-purple-400';
    if (form.value.estado === 'PENDIENTE') return 'bg-[#061816] border-emerald-900 text-emerald-400';
    if (form.value.estado === 'CUMPLIDO') return 'bg-[#1d1d05] border-yellow-900 text-yellow-500';
    if (form.value.estado === 'INTERNO') return 'bg-[#2b0515] border-pink-800 text-pink-400'; // Vibrant Pink
    if (form.value.estado === 'ANULADO') return 'bg-[#2a0505] border-red-900 text-red-400'; // Red Theme
    return 'bg-[#0f0a1e] border-purple-900 text-purple-400';
});

const mainThemeClass = computed(() => {
    if (form.value.estado === 'PRESUPUESTO') return 'bg-[#2d1b36]';
    if (form.value.estado === 'PENDIENTE') return 'bg-[#0b211f]';
    if (form.value.estado === 'CUMPLIDO') return 'bg-[#1d1d0b]';
    if (form.value.estado === 'INTERNO') return 'bg-[#2b0515]'; // Vibrant Pink
    if (form.value.estado === 'ANULADO') return 'bg-[#1f0505]'; // Red Theme
    return 'bg-[#0b211f]';
});

const activeTypeClass = (type) => {
    if (type === 'PENDIENTE') return 'bg-emerald-500 text-white shadow-sm';
    if (type === 'CUMPLIDO') return 'bg-yellow-500 text-black shadow-sm';
    if (type === 'PRESUPUESTO') return 'bg-purple-500 text-white shadow-sm';
    if (type === 'INTERNO') return 'bg-pink-600 text-white shadow-sm';
    if (type === 'ANULADO') return 'bg-red-600 text-white shadow-sm';
    return 'bg-slate-500 text-white shadow-sm';
};

// --- DATA LOGIC ---

// Clients Lookup
const filteredClients = computed(() => {
    if (clientQuery.value.length < 2) return [];
    
    const normalizeText = (text) => {
        return text
            ? text.toString().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
            : "";
    };

    const q = normalizeText(clientQuery.value);
    
    return clientesStore.clientes
        .filter(c => {
            if (!c.activo) return false;
            const name = normalizeText(c.razon_social);
            const cuit = c.cuit || "";
            const id = c.id ? c.id.toString() : "";
            return name.includes(q) || cuit.includes(q) || id.includes(q);
        })
        .sort((a, b) => {
            const nameA = normalizeText(a.razon_social);
            const nameB = normalizeText(b.razon_social);
            const cuitA = a.cuit || "";
            const cuitB = b.cuit || "";
            
            // 1. Prioridad: Empieza con el texto buscado
            const startsA = nameA.startsWith(q) || cuitA.startsWith(q);
            const startsB = nameB.startsWith(q) || cuitB.startsWith(q);
            if (startsA && !startsB) return -1;
            if (!startsA && startsB) return 1;

            // 2. Orden alfabético por Razón Social
            return nameA.localeCompare(nameB);
        })
        .slice(0, 15);
});

const clienteStatus = computed(() => {
    if (!selectedClient.value) return null;
    const c = selectedClient.value;
    
    // EXCEPTION: Consumidor Final is always valid
    if (c.razon_social === 'CONSUMIDOR FINAL' || c.cuit === '00-00000000-0') {
        return { color: 'text-emerald-500', text: 'Auditado (CF)', missing: [] };
    }
    
    // Explicit checks for mandatory fields
    const missing = [];
    if (!c.cuit) missing.push('CUIT');
    if (!c.domicilio_fiscal_resumen) missing.push('Domicilio Fiscal');
    
    // Fix: Check ID, as the object might not be hydrated in the list view
    if (!c.condicion_iva_id && !c.condicion_iva) missing.push('Condición IVA');
    
    if (!c.segmento_id && !c.segmento) missing.push('Segmento'); // Optional per logic but good practice

    if (missing.length === 0) {
        return { color: 'text-emerald-500', text: 'Auditado', missing: [] };
    } else {
        return { 
            color: 'text-amber-500', 
            text: 'Datos Incompletos', 
            missing: missing,
            title: 'Faltan: ' + missing.join(', ')
        };
    }
});

// Products Lookup
const filteredProducts = computed(() => {
    const normalizeText = (text) => {
        return text
            ? text.toString().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
            : "";
    };

    const q = normalizeText(productQuery.value);
    if (!q) return []; 
    
    return productosStore.productos
        .filter(p => {
            const name = normalizeText(p.nombre);
            const sku = normalizeText(p.sku);
            return name.includes(q) || sku.includes(q);
        })
        .sort((a, b) => {
            const skuA = normalizeText(a.sku);
            const skuB = normalizeText(b.sku);
            const nameA = normalizeText(a.nombre);
            const nameB = normalizeText(b.nombre);

            // 1. Prioridad: SKU exacto o que empieza con q
            if (skuA.startsWith(q) && !skuB.startsWith(q)) return -1;
            if (!skuA.startsWith(q) && skuB.startsWith(q)) return 1;

            // 2. Prioridad: Nombre que empieza con q
            if (nameA.startsWith(q) && !nameB.startsWith(q)) return -1;
            if (!nameA.startsWith(q) && nameB.startsWith(q)) return 1;

            // 3. Orden por SKU
            return skuA.localeCompare(skuB);
        })
        .slice(0, 50);
});

const showProductResults = computed(() => {
    return focusedZone.value === 'PRODUCT' && filteredProducts.value.length > 0;
});

const productPlaceholder = computed(() => {
    const count = productosStore.productos.length;
    return count > 0 ? `+ Agregar Producto (F3 para buscar en ${count} ítems)` : 'Cargando catálogo...';
});

const productPopupStyle = computed(() => {
    if (!productInput.value) return {};
    const rect = productInput.value.getBoundingClientRect();
    return {
        left: `${rect.left}px`,
        bottom: `${window.innerHeight - rect.top + 8}px`,
        width: `${rect.width * 1.5}px`,
        minWidth: '500px'
    };
});

const totals = computed(() => {
    const bruto = items.value.reduce((sum, item) => sum + (item.subtotal || 0), 0);
    const neto = bruto - (form.value.descuento_global_importe || 0);
    
    // IVA Logic synchronized with backend:
    // PENDIENTE/PRESUPUESTO with Fiscal mode (A/B) -> +21%
    const applyIva = (form.value.estado === 'PENDIENTE' || form.value.estado === 'PRESUPUESTO') && 
                     (form.value.tipo_facturacion === 'A' || form.value.tipo_facturacion === 'B' || form.value.tipo_facturacion === 'FISCAL');
    
    const iva = applyIva ? neto * 0.21 : 0;
    return { bruto, neto, iva, final: neto + iva };
});

const clientPopupStyle = computed(() => {
    if (!clientInput.value) return {};
    const rect = clientInput.value.getBoundingClientRect();
    return {
        top: `${rect.bottom}px`,
        left: `${rect.left}px`,
        width: `${rect.width}px`
    };
});

const logisticsLabel = computed(() => {
    if (!selectedClient.value) return 'Retiro en Local';
    const hasAddress = !!selectedClient.value.domicilio_entrega;
    const transportName = selectedClient.value.transporte_nombre;
    
    // Explicit transport set
    if (transportName && transportName !== 'Retiro Local') return transportName;
    
    // Fallback: If has address -> "Envío a Domicilio", else "Retira Local"
    return hasAddress ? 'Envío a Domicilio' : 'Retira en Local';
});

const handleUpdateLogistica = (data) => {
    // data: { transporte_id, transporte_nombre, domicilio_entrega }
    if(selectedClient.value) {
        selectedClient.value.transporte_id = data.transporte_id;
        selectedClient.value.transporte_nombre = data.transporte_nombre;
        selectedClient.value.domicilio_entrega = data.domicilio_entrega;
    }
    showLogisticaModal.value = false;
};



// --- METHODS ---

const handleClearManual = () => {
    if(confirm('¿Borrar todo y limpiar pantalla localmente?')) {
        // Force reset
        items.value = [];
        selectedClient.value = null;
        form.value.nota = '';
        form.value.oc = '';
        form.value.estado = 'PENDIENTE';
        clientQuery.value = '';
        form.value.descuento_global_porcentaje = 0;
        form.value.descuento_global_importe = 0;
        localStorage.removeItem('tactical_draft');
        
        // Remove edit from query if present
        if (route.query.edit) {
            router.replace({ path: route.path, query: {} });
        }

        // Ensure UI updates
        createEmptyRow(); 
        fetchNextId();
        
        // Small delay to ensure focus works
        setTimeout(() => focusClient(), 100);
    }
};

const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(val);
};

const setStatus = (newStatus) => {
    form.value.estado = newStatus;
    
    // Doctrina Táctica v6.5: 
    // Al cambiar a PENDIENTE (Verde) o PRESUPUESTO (Púrpura), 
    // activamos modo FISCAL (B) por defecto si estaba en X.
    if ((newStatus === 'PENDIENTE' || newStatus === 'PRESUPUESTO') && form.value.tipo_facturacion === 'X') {
        form.value.tipo_facturacion = 'B'; 
    }
    
    // Si el usuario elige explícitamente INTERNO o ANULADO, forzamos modo X (Sin IVA)
    if (newStatus === 'INTERNO' || newStatus === 'ANULADO') {
        form.value.tipo_facturacion = 'X';
    }
};

const fetchNextId = async () => {
    try {
        const res = await apiClient.get('/pedidos/sugerir_id');
        sugeridoId.value = res.data;
        form.value.numero_manual = res.data;
    } catch (e) {
        console.error("Error fetching next ID", e);
    }
}

const autosaveDraft = () => {
    const draft = {
        items: items.value,
        form: form.value,
        selectedClient: selectedClient.value,
        timestamp: Date.now()
    };
    localStorage.setItem('tactical_draft', JSON.stringify(draft));
};

// Clear draft on successful submit
const clearDraft = () => {
    localStorage.removeItem('tactical_draft');
    items.value = [];
    form.value.nota = '';
    form.value.oc = '';
    form.value.estado = 'PENDIENTE';
    form.value.cliente_id = null;
    selectedClient.value = null;
    clientQuery.value = '';
    
    // Remove edit from query if present
    if (route.query.edit) {
        router.replace({ path: route.path, query: {} });
    }

    createEmptyRow(); // Reset UI
};

const resetAndFetchPedido = async (id) => {
    if (!id) return;
    try {
        console.log(`[GridLoader] Intentando cargar pedido #${id} para edición...`);
        notificationStore.add('Cargando pedido...', 'info');
        
        // Limpiamos estado previo para evitar mezclas
        items.value = [];
        selectedClient.value = null;
        form.value.numero_manual = ''; 

        const pedido = await pedidosStore.getPedidoById(id);
        
        if (pedido) {
            console.log(`[GridLoader] Pedido cargado:`, pedido);
            
            // 1. Populate Form
            form.value.fecha = pedido.fecha ? pedido.fecha.split('T')[0] : new Date().toISOString().split('T')[0];
            form.value.oc = pedido.oc || '';
            form.value.nota = pedido.nota || '';
            form.value.estado = pedido.estado || 'PENDIENTE';
            form.value.numero_manual = pedido.id;
            form.value.descuento_global_porcentaje = pedido.descuento_global_porcentaje || 0;
            form.value.descuento_global_importe = pedido.descuento_global_importe || 0;
            
            // Lógica de recuperación de Tipo Facturación (Doctrina Táctica v6.6)
            // Auto-heal: Si es PENDIENTE/PRESUPUESTO, debe ser Fiscal (B) por defecto.
            if (pedido.tipo_facturacion) {
                form.value.tipo_facturacion = pedido.tipo_facturacion;
                // PATCH: Si encontramos inconsistencia (PENDIENTE pero Facturacion X/Null), corregimos a B
                if (['PENDIENTE', 'PRESUPUESTO'].includes(pedido.estado) && !['A', 'B', 'FISCAL'].includes(pedido.tipo_facturacion)) {
                     form.value.tipo_facturacion = 'B';
                }
            } else {
                form.value.tipo_facturacion = (pedido.estado === 'PENDIENTE' || pedido.estado === 'PRESUPUESTO') ? 'B' : 'X';
            }

            // 2. Populate Client
            if (pedido.cliente) {
                selectedClient.value = pedido.cliente;
                clientQuery.value = pedido.cliente.razon_social || '';
            }
            
            // 3. Populate Items
            if (pedido.items && pedido.items.length > 0) {
                items.value = pedido.items.map(i => ({
                    _ui_id: Date.now() + Math.random() + (i.id || 0),
                    id: i.id,
                    producto_id: i.producto_id,
                    sku: i.producto?.sku || '?',
                    nombre: i.producto?.nombre || '?',
                    unidad: i.producto?.unidad_medida || 'UN',
                    cantidad: i.cantidad,
                    precio_unitario: i.precio_unitario,
                    descuento_porcentaje: i.descuento_porcentaje || 0,
                    descuento_importe: i.descuento_importe || 0,
                    subtotal: (i.cantidad * i.precio_unitario) - (i.descuento_importe || 0),
                    nota: i.nota || ''
                }));
            } else {
                items.value = [];
                createEmptyRow();
            }
            
            notificationStore.add(`Pedido #${pedido.id} cargado.`, 'success');
            setTimeout(() => focusProductSearch(), 300);
        } else {
            throw new Error("El pedido no existe o vino vacío.");
        }
    } catch (e) {
        console.error("[GridLoader] Error crítico al cargar pedido:", e);
        notificationStore.add('Error al cargar pedido. Iniciando modo NUEVO.', 'error');
        // Fallback a nuevo pedido para no dejar la pantalla en el limbo "NEW"
        router.replace({ path: route.path, query: {} }); // Limpia ?edit=XX
        // El watcher de route.query se encargará de resetear, pero por seguridad:
        resetToNewOrder();
    }
}

const resetToNewOrder = async () => {
    console.log("[GridLoader] Reseteando a NUEVO PEDIDO");
    items.value = [];
    selectedClient.value = null;
    form.value.nota = '';
    form.value.oc = '';
    form.value.estado = 'PENDIENTE';
    form.value.tipo_facturacion = 'B'; // Default Fiscal
    form.value.numero_manual = '';
    form.value.descuento_global_porcentaje = 0;
    form.value.descuento_global_importe = 0;
    clientQuery.value = '';
    createEmptyRow();
    await fetchNextId();
};

onMounted(async () => {
    // 1. Listeners Globales
    window.addEventListener('keydown', handleGlobalKeydown);
    window.addEventListener('keydown', handleGlobalKeys);

    // 2. Carga de Datos Maestros
    try {
        await Promise.all([
            clientesStore.fetchClientes(),
            productosStore.fetchProductos(),
            useMaestrosStore().fetchAll()
        ]);
    } catch (e) {
        console.error("Error cargando maestros:", e);
    }

    // 3. Determinar Modo (Edición vs Nuevo)
    // Usamos nextTick para asegurar que el router esté estabilizado
    await nextTick();
    const editId = route.query.edit;

    if (editId) {
        console.log("[GridLoader] Modo EDICIÓN detectado ID:", editId);
        await resetAndFetchPedido(editId);
    } else {
        console.log("[GridLoader] Modo NUEVO detectado.");
        // Intentar restaurar borrador
        const saved = localStorage.getItem('tactical_draft');
        let restored = false;
        if (saved) {
            try {
                const draft = JSON.parse(saved);
                if (Date.now() - draft.timestamp < 24 * 60 * 60 * 1000) { // 24h validez
                    if (draft.items?.length > 0 || draft.selectedClient) {
                        items.value = draft.items || [];
                        form.value = { ...form.value, ...draft.form };
                        selectedClient.value = draft.selectedClient;
                        clientQuery.value = draft.selectedClient?.razon_social || '';
                        restored = true;
                        notificationStore.add('Borrador restaurado', 'info');
                    }
                }
            } catch (e) { console.error("Error draft restore", e); }
        }
        
        if (!restored) {
            await fetchNextId();
        } else {
             // Si restauramos borrador, también necesitamos un ID nuevo si no tenía
             if (!form.value.numero_manual) await fetchNextId();
        }
    }

    setTimeout(() => clientInput.value?.focus(), 100);
});

// Watch para cambios en URL (Navegación dentro de la misma vista)
watch(() => route.query.edit, async (newId, oldId) => {
    if (newId === oldId) return; // Evitar disparos redundantes
    if (newId) {
        await resetAndFetchPedido(newId);
    } else {
        // Si se quita el query param, asumimos "Nuevo Pedido"
        await resetToNewOrder();
    }
});

// Autosave Draft (solo si no estamos editando un pedido existente guardado, o sea, si es nuevo)
// OJO: Quizás queramos guardar draft de edición también? Por ahora solo para nuevos para no sobrescribir logic compleja
watch([items, () => form.value, selectedClient], () => {
    // Solo guardamos draft si NO estamos en modo edición (para no pisar trabajo de edición con borrador local sucio)
    if (!route.query.edit && (items.value.length > 0 || selectedClient.value)) {
        autosaveDraft();
    }
}, { deep: true });

onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeydown);
    window.removeEventListener('keydown', handleGlobalKeys);
});

const createEmptyRow = () => ({
    _ui_id: Date.now() + Math.random(),
    sku: '',
    nombre: '',
    cantidad: 1,
    precio_unitario: 0,
    descuento_porcentaje: 0,
    descuento_importe: 0,
    subtotal: 0,
    unidad: '',
    nota: ''
});

// Client Actions
const focusClient = () => {
    focusedZone.value = 'CLIENT';
    clientInput.value?.focus();
    clientInput.value?.select();
    showClientResults.value = true;
};

const handleClientKeydown = (e) => {
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedClientIdx.value = Math.min(selectedClientIdx.value + 1, filteredClients.value.length - 1);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedClientIdx.value = Math.max(selectedClientIdx.value - 1, 0);
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredClients.value.length > 0) {
            selectClient(filteredClients.value[selectedClientIdx.value]);
        }
        showClientResults.value = false;
        clientInput.value?.blur();
    } else if (e.key === 'F4') {
        e.preventDefault();
        openInspectorNew();
    } else {
        // Default behavior: typing
        showClientResults.value = true;
        // Reset index if typing new query
        // selectedClientIdx.value = 0; // handled by watcher/computed usually
    }
};

const handleGlobalKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault();
        handleSubmit();
    } else if (e.key === 'Escape') {
        // [GY-UX] Return to Order List if not in a critical input
        if (focusedZone.value === 'CLIENT' || focusedZone.value === 'PRODUCT') {
            router.push('/hawe/pedidos');
        }
    }
};

const handleClientInput = () => {
    // If user clears input, reset selection
    if (clientQuery.value === '') {
        selectedClient.value = null;
    }
    // Open results if typing
    showClientResults.value = true;
};

const clearClient = () => {
    clientQuery.value = '';
    selectedClient.value = null;
    showClientResults.value = false;
    clientInput.value?.focus();
};

const selectClient = async (client) => {
    selectedClient.value = client;
    clientQuery.value = client.razon_social;
    showClientResults.value = false;
    
    // [GY-FIX] Fetch full details (Domicilios/Transportes)
    try {
        const fullClient = await clientesStore.fetchClienteById(client.id);
        if (fullClient) selectedClient.value = fullClient;
    } catch (e) {
        console.error("Error fetching client details", e);
    }

    focusProductSearch();
};

// --- INSPECTOR LOGIC ---

const openInspectorNew = () => {
    // [GY-UX] Pass current search query as initial data
    clienteForInspector.value = { 
        razon_social: clientQuery.value || '',
        cuit: '',
        activo: true // Defaults
    };
    isInspectorNew.value = true;
    showInspector.value = true;
    showClientResults.value = false;
};

const openInspectorEdit = (client) => {
    clienteForInspector.value = client;
    isInspectorNew.value = false;
    showInspector.value = true;
    showClientResults.value = false;
};

const closeInspector = () => {
    showInspector.value = false;
    // Return focus if needed
    if (!selectedClient.value) {
        focusClient();
    }
};

const handleInspectorSave = async (clientData) => {
    // Process save/create
    try {
        let savedClient;
        if (isInspectorNew.value) {
            savedClient = await clientesStore.createCliente(clientData);
        } else {
            savedClient = await clientesStore.updateCliente(clientData.id, clientData);
        }
        
        // Auto-select the saved client
        selectClient(savedClient);
        closeInspector();
        
    } catch (e) {
        console.error(e);
        alert('Error al guardar cliente: ' + e.message);
    }
};

const handleInspectorDelete = async (clientData) => {
   // Already handled by component soft delete logic usually, but here we can force purge
   try {
       await clientesStore.deleteCliente(clientData.id);
       closeInspector();
       // Refresh search if query exists
       if (clientQuery.value) clientesStore.fetchClientes();
   } catch(e) {
       console.error(e);
   }
};

const switchToClient = (id) => {
    // Used when inspector switches context (e.g. duplicate detected)
    const client = clientesStore.clientes.find(c => c.id === id);
    if(client) openInspectorEdit(client);
};

// --- PRODUCT INSPECTOR LOGIC ---

const openProductInspectorNew = () => {
    productForInspector.value = {
        nombre: productQuery.value || '',
        sku: 'AUTO',
        activo: true,
        costos: {
            costo_reposicion: 0,
            margen_mayorista: 30,
            iva_alicuota: 21
        }
    };
    isProductInspectorNew.value = true;
    showProductInspector.value = true;
};

const closeProductInspector = () => {
    showProductInspector.value = false;
    productForInspector.value = null;
    focusProductSearch();
};

const handleProductInspectorSave = async (productData) => {
    try {
        let savedProduct;
        if (isProductInspectorNew.value) {
            savedProduct = await productosStore.createProducto(productData);
            notificationStore.add('Producto creado y clonado correctamente', 'success');
        } else {
            savedProduct = await productosStore.updateProducto(productData.id, productData);
            notificationStore.add('Producto actualizado', 'success');
        }
        
        // Auto-add the saved product to the grid
        addProduct(savedProduct);
        closeProductInspector();
        
    } catch (e) {
        console.error(e);
        alert('Error al guardar producto: ' + e.message);
    }
};

// --- CONTEXT MENU LOGIC ---

const openClientContextMenu = (e, client) => {
    // If a client is passed, standard list context menu
    // If e is from input, use selectedClient
    const targetClient = client || selectedClient.value;
    if (!targetClient) return;

    contextMenu.value = {
        show: true,
        x: e.clientX,
        y: e.clientY,
        actions: [
            { 
                label: 'Ver Historial (Últ. 5)', 
                iconClass: 'fas fa-history',
                handler: async () => {
                    historyPopover.value.x = e.clientX;
                    historyPopover.value.y = e.clientY; 
                    historyPopover.value.orders = await pedidosStore.getHistorialCliente(targetClient.id);
                    historyPopover.value.show = true;
                }
            },
            { 
                label: 'Editar Cliente', 
                iconClass: 'fas fa-edit', 
                handler: () => openInspectorEdit(targetClient) 
            },
            { 
                label: 'Eliminar Cliente', 
                iconClass: 'fas fa-trash', 
                handler: () => markForDeletion(targetClient),
                class: 'text-red-400 hover:text-red-300'
            }
        ]
    };
};

const handleInputContextMenu = (e) => {
    if (selectedClient.value) {
        openClientContextMenu(e, selectedClient.value);
    }
};

const showMissingFieldsAlert = (missing) => {
    alert('Faltan los siguientes datos obligatorios para este cliente:\n\n- ' + missing.join('\n- '));
};

const markForDeletion = async (client) => {
    if(!confirm(`¿Marcar a "${client.razon_social}" para eliminación (Baja)?`)) return;
    try {
        await clientesStore.deleteCliente(client.id); // Soft Delete
        // The list filteredClients will auto-update because of the .filter(c.activo) or sort logic
    } catch(e) {
        alert("Error al eliminar: " + e.message);
    }
};


// Product Actions
const focusProductSearch = () => {
    focusedZone.value = 'PRODUCT';
    productInput.value?.focus();
};

const handleProductKeydown = (e) => {
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (showProductResults.value) {
            selectedProdIdx.value = Math.min(selectedProdIdx.value + 1, filteredProducts.value.length - 1);
        }
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (showProductResults.value) {
            selectedProdIdx.value = Math.max(selectedProdIdx.value - 1, 0);
        }
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (showProductResults.value && filteredProducts.value.length > 0) {
            addProduct(filteredProducts.value[selectedProdIdx.value]);
        }
    } else if (e.key === 'Escape') {
        productQuery.value = '';
        productInput.value?.blur();
    } else if (e.key === 'F4') {
        e.preventDefault();
        openProductInspectorNew();
    }
};

const addProduct = async (product) => {
    // 1. Determine Initial Price (Default to stored list price)
    let unitPrice = product.precio_sugerido || 0;
    let note = '';
    
    // Add version number for user visibility (as requested in PedidoTacticoView before)
    // Actually, let's keep it clean since GridLoader doesn't have a version placeholder yet.


    // 2. Intelligence: Quote with Backend if Client is selected
    if (selectedClient.value && selectedClient.value.id) {
        try {
            const res = await apiClient.post('/pedidos/cotizar', {
                cliente_id: selectedClient.value.id,
                producto_id: product.id,
                cantidad: 1
            });
            
            if (res.data) {
                // Use the Final Target Price from the Engine
                unitPrice = res.data.precio_final_sugerido;
                
                // Optional: Add a subtle note if it's a special strategy?
                // note = res.data.estrategia === 'MAYORISTA_FISCAL' ? '' : `(${res.data.estrategia})`;
            }
        } catch (e) {
            console.warn("Pricing Engine Quote Failed, falling back to basic price", e);
        }
    }

    const newItem = {
        _ui_id: Date.now() + Math.random(), // Temp UI ID
        producto_id: product.id,
        sku: product.sku,
        nombre: product.nombre,
        unidad: product.unidad_medida || 'UN',
        cantidad: 1,
        precio_unitario: unitPrice,
        descuento_porcentaje: 0,
        descuento_importe: 0,
        subtotal: unitPrice, // Initial subtotal (1 * unitPrice - 0)
        nota: note
    };

    items.value.push(newItem);
    
    // Reset Search
    productQuery.value = '';
    
    // Focus logic
    nextTick(() => {
        focusedRow.value = items.value.length - 1;
        if (gridContainer.value) {
            gridContainer.value.scrollTop = gridContainer.value.scrollHeight;
        }
        productInput.value?.focus();
    });
};

const removeItem = (idx) => {
    items.value.splice(idx, 1);
};


// Main Submit
const handleSubmit = async () => {
    if (!selectedClient.value) return alert('Por favor seleccione un cliente.');
    
    // Sync Fiscal Mode: PENDIENTE should be FISCAL by default
    if (form.value.estado === 'PENDIENTE' && form.value.tipo_facturacion === 'X') {
        form.value.tipo_facturacion = 'B'; 
    }

    // Special Logic: Zero items -> Annul?
    if (items.value.length === 0) {
        if (isEditing.value) {
            if (confirm('El pedido no tiene renglones. ¿Desea ANULAR este pedido?')) {
                try {
                    isSubmitting.value = true;
                    await pedidosStore.updatePedido(route.query.edit, { estado: 'ANULADO' });
                    notificationStore.add('Pedido ANULADO correctamente', 'success');
                    clearDraft();
                    focusClient();
                    return;
                } catch (e) {
                    alert('Error al anular: ' + e.message);
                    return;
                } finally {
                    isSubmitting.value = false;
                }
            } else {
                return; // User cancelled annulment but can't save zero items
            }
        } else {
            return alert('El pedido está vacío.');
        }
    }
    
    isSubmitting.value = true;
    try {
        const payload = {
            cliente_id: selectedClient.value.id,
            fecha: form.value.fecha,
            nota: form.value.nota,
            oc: form.value.oc,
            estado: form.value.estado,
             items: items.value.map(i => ({
                producto_id: i.producto_id,
                cantidad: parseFloat(i.cantidad),
                precio_unitario: parseFloat(i.precio_unitario),
                descuento_porcentaje: parseFloat(i.descuento_porcentaje || 0),
                descuento_importe: parseFloat(i.descuento_importe || 0),
                nota: i.nota || ''
            })),
            tipo_facturacion: form.value.tipo_facturacion,
            descuento_global_porcentaje: parseFloat(form.value.descuento_global_porcentaje || 0),
            descuento_global_importe: parseFloat(form.value.descuento_global_importe || 0)
        };
        
        let result;
        if (isEditing.value) {
            // Re-use updatePedido but with tactical payload structure if backend supports it
            // Or better yet, create a dedicated updatePedidoTactico if needed.
            // For now, let's use a generic PATCH /pedidos/{id} which should handle items if configured.
            // Wait, the backend update_pedido might not handle items list replacement in a simple PATCH.
            // I'll check the router.py again.
            result = await pedidosStore.updatePedido(route.query.edit, payload);
        } else {
            result = await pedidosStore.createPedidoTactico(payload);
        }
        
        if (downloadExcel.value) {
            const filename = `Pedido_${result.id}_${selectedClient.value.razon_social.substring(0, 15)}.xlsx`;
            await pedidosStore.downloadExcel(result.id, filename);
        }

        isSubmitting.value = false; // Reset before alert to stop spinner

        notificationStore.add(isEditing.value ? 'Pedido actualizado' : 'Pedido generado', 'success');

        if(confirm(`Pedido #${result.id} ${isEditing.value ? 'actualizado' : 'generado'} con éxito.\n¿Limpiar pantalla?`)) {
            clearDraft();
            focusClient();
            fetchNextId();
        }
    } catch (e) {
        isSubmitting.value = false;
        alert('Error al guardar: ' + (e.response?.data?.detail || e.message));
    } finally {
        // isSubmitting already set to false above for better UX
    }
};


// Lifecycle
const showHistoryPreview = async (e) => {
    if (!selectedClient.value) return;
    historyPopover.value.x = e.clientX;
    historyPopover.value.y = e.clientY + 20; // Offset
    historyPopover.value.orders = await pedidosStore.getHistorialCliente(selectedClient.value.id);
    historyPopover.value.show = true;
};

const hideHistoryPreview = () => {
    historyPopover.value.show = false;
};



// Watch for bruto changes to update global discount amount if percentage is fixed
watch(() => totals.value.bruto, (newBruto) => {
    if (form.value.descuento_global_porcentaje > 0) {
        form.value.descuento_global_importe = _.round(newBruto * (form.value.descuento_global_porcentaje / 100), 4);
    }
});

// --- CALCULATIONS ENGINE ---

const recalculateItemEngine = (item, trigger) => {
    const cantidad = parseFloat(item.cantidad || 0);
    const precio = parseFloat(item.precio_unitario || 0);
    const base = cantidad * precio;
    
    if (trigger === 'porcentaje') {
        const pct = parseFloat(item.descuento_porcentaje || 0);
        item.descuento_importe = _.round(base * (pct / 100), 4);
    } else if (trigger === 'importe') {
        const imp = parseFloat(item.descuento_importe || 0);
        item.descuento_porcentaje = base > 0 ? _.round((imp / base) * 100, 2) : 0;
    }
    
    // Re-verify importe if base changed
    if (trigger === 'cantidad' || trigger === 'precio') {
        const pct = parseFloat(item.descuento_porcentaje || 0);
        item.descuento_importe = _.round(base * (pct / 100), 4);
    }
    
    const impFinal = parseFloat(item.descuento_importe || 0);
    item.subtotal = _.round(base - impFinal, 4);
};

const handleGlobalDiscountInputEngine = (trigger) => {
    const bruto = totals.value.bruto || 0;
    if (trigger === 'porcentaje') {
        const pct = parseFloat(form.value.descuento_global_porcentaje || 0);
        form.value.descuento_global_importe = _.round(bruto * (pct / 100), 4);
    } else if (trigger === 'importe') {
        const imp = parseFloat(form.value.descuento_global_importe || 0);
        form.value.descuento_global_porcentaje = bruto > 0 ? _.round((imp / bruto) * 100, 2) : 0;
    }
};

// Lifecycle
const handleGlobalKeys = (e) => {
    // F3: BÚSQUEDA GLOBAL (CLIENTES) - DOCTRINA DEOU
    if (e.key === 'F3') {
        e.preventDefault();
        focusClient();
    } 
    // F2: BÚSQUEDA PRODUCTO (SECUNDARIO)
    else if (e.key === 'F2') {
        e.preventDefault();
        focusProductSearch();
    } 
    else if (e.key === 'F10') {
        e.preventDefault();
        if (!showInspector.value) handleSubmit(); 
    } 
    else if (e.key === 'F4') {
        if (focusedZone.value === 'CLIENT') {
            e.preventDefault();
            openInspectorNew();
        }
    }
};

// Lifecycle handlers removed. Consolidated into setup.

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.5); border-radius: 4px; border: 2px solid transparent; background-clip: content-box; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.5); border-radius: 4px; border: 2px solid transparent; background-clip: content-box; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background-color: rgba(148, 163, 184, 0.8); }

.force-dark-input {
    background-color: #0f172a !important; /* Force dark background */
    color: #d1fae5 !important; /* Force emerald-100 text */
    -webkit-text-fill-color: #d1fae5 !important; /* Safari/Chrome override */
}
.force-dark-input:-webkit-autofill,
.force-dark-input:-webkit-autofill:hover, 
.force-dark-input:-webkit-autofill:focus, 
.force-dark-input:-webkit-autofill:active{
    -webkit-box-shadow: 0 0 0 30px #0f172a inset !important;
    -webkit-text-fill-color: #d1fae5 !important;
    transition: background-color 5000s ease-in-out 0s;
}
</style>
