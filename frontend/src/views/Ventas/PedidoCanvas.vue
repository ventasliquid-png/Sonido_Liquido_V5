<template>
    <div class="min-h-screen w-full bg-[#0f172a] p-2 flex justify-center items-start">
        <div class="w-full max-w-[98%] bg-[#0f172a] rounded-2xl border-2 border-emerald-500 shadow-[0_0_40px_-10px_rgba(16,185,129,0.5)] overflow-hidden relative flex flex-col h-screen">
            <!-- HEADER (User Provided Style) -->
            <!-- HEADER (Compact Mode) -->
            <div class="w-full bg-emerald-950/30 border-b border-emerald-500/20 py-2 px-4 flex justify-between items-center backdrop-blur-sm shrink-0">
                <div class="flex items-center gap-4">
                    <button @click="$router.push({ name: 'PedidoList' })" class="text-emerald-500/50 hover:text-emerald-400 transition-colors">
                        <i class="fas fa-arrow-left"></i>
                    </button>
                    <h1 class="text-lg font-bold text-emerald-400 tracking-wider flex items-center gap-3">
                        <i class="fas fa-file-invoice"></i> NUEVO PEDIDO
                    </h1>
                </div>
                <div class="flex gap-3">
                     <button @click="resetPedido" class="text-emerald-500 hover:text-emerald-400 font-bold flex items-center gap-2 transition-colors uppercase tracking-wider text-xs">
                        <i class="fas fa-plus-circle"></i> Resetear
                    </button>
                </div>
            </div>

            <!-- BODY (Existing Content) -->
            <div class="flex-1 flex flex-col overflow-hidden relative min-h-0">
                <!-- Inner content wrapper to maintain existing flex behavior -->
                 <div class="flex-1 flex flex-col min-h-0 overflow-hidden transition-all duration-300 ease-in-out"
                     :class="showCostDrawer ? 'mr-96' : ''">

            <!-- SECTION 1: HEADER (Refinado: Dense Mode) -->
            <header class="shrink-0 p-5 border-b border-white/10 bg-black/10 backdrop-blur-md relative z-10 space-y-4">
                
                <!-- ROW 1: PRIMARY DATA -->
                <div class="grid grid-cols-12 gap-4 items-center">
                    
                    <!-- 1. ID -->
                    <div class="col-span-1">
                         <label class="block text-[10px] font-bold uppercase tracking-widest text-emerald-500/50 mb-1">ID</label>
                         <div class="bg-emerald-500/10 text-emerald-400 px-2 py-2 rounded-lg font-mono font-bold text-lg border border-emerald-500/20 text-center">
                            {{ nroPedido }}
                        </div>
                    </div>

                    <!-- 2. FECHA -->
                    <div class="col-span-2">
                         <label class="block text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1">Fecha Pedido</label>
                         <input type="date" 
                            v-model="fechaPedido" 
                            class="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white font-bold focus:border-emerald-500 focus:outline-none transition-colors"
                            style="color-scheme: dark;"
                        >
                    </div>

                    <!-- 3. CLIENTE (Search) -->
                    <div class="col-span-4">
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1">Cliente</label>
                        <div class="relative group" @contextmenu.prevent="handleContextMenu($event)">
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <i class="fas fa-user-circle text-gray-500 group-focus-within:text-emerald-400 text-lg"></i>
                            </div>
                            <input type="text" 
                                ref="clientInputRef"
                                v-model="busquedaCliente"
                                @focus="handleInputFocus"
                                @keydown.down.prevent="navigateResults(1)"
                                @keydown.up.prevent="navigateResults(-1)"
                                @keydown.enter.prevent="selectHighlighted"
                                placeholder="Buscar Cliente..." 
                                :class="[
                                    'w-full bg-black/50 border rounded-xl py-2 pl-10 pr-4 text-base font-medium placeholder-gray-600 focus:outline-none transition-all',
                                    clienteSeleccionado && !clientValidation.valid 
                                        ? 'border-amber-500/50 text-amber-500 focus:border-amber-500 focus:ring-1 focus:ring-amber-500/50' 
                                        : 'border-white/10 text-white focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50'
                                ]"
                            >
                            <!-- Validation Warning -->
                            <div v-if="clienteSeleccionado && !clientValidation.valid" class="absolute -top-3 right-0 bg-amber-900/90 border border-amber-500 text-amber-500 text-[10px] px-2 py-0.5 rounded uppercase font-bold tracking-wider animate-pulse flex items-center gap-2 shadow-lg z-10">
                                <i class="fas fa-exclamation-triangle"></i> DATOS FALTANTES
                            </div>
                            
                            <!-- Context Menu Teleport -->
                            <Teleport to="body">
                                <div v-if="showContextMenu" class="fixed inset-0 z-[9998]" @click="showContextMenu = false" @contextmenu.prevent></div>
                                <div v-if="showContextMenu"
                                     :style="{ top: contextMenuY + 'px', left: contextMenuX + 'px' }"
                                     class="fixed z-[9999] bg-[#2b2b2b] border border-[#454545] shadow-lg py-1 w-64 select-none flex flex-col text-[13px] font-sans rounded-none"
                                     @click.stop
                                     @mousedown.stop
                                     @contextmenu.prevent>
                                    <div class="flex justify-between items-center px-2 pb-1 mb-1 border-b border-[#454545] text-xs text-gray-500">
                                        <span class="font-bold">Acciones</span>
                                        <i @click="showContextMenu = false" class="fas fa-times hover:text-white cursor-pointer p-1"></i>
                                    </div>
                                    <div v-if="clienteSeleccionado && (clienteSeleccionado.id || clienteSeleccionado._id)"
                                         @click="irAFicha"
                                         class="px-3 py-1.5 hover:bg-[#414141] cursor-default flex items-center gap-3 text-white transition-colors">
                                        <i class="fas fa-external-link-alt text-gray-400 text-xs"></i>
                                        <span>Ir a Ficha de Cliente</span>
                                    </div>
                                    <div v-else class="px-3 py-1.5 text-gray-400 italic cursor-default">
                                        Sin cliente seleccionado
                                    </div>
                                </div>
                            </Teleport>

                             <!-- Results List -->
                             <div v-if="showClienteResults && filteredClientes.length > 0" 
                                  class="absolute top-full left-0 w-full mt-1 bg-[#151515] border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden max-h-60 overflow-y-auto">
                                 <div v-for="(cliente, index) in filteredClientes" 
                                      :key="cliente.id"
                                      @click="selectCliente(cliente)"
                                      :class="{'bg-emerald-600 text-white': index === selectedIndex, 'hover:bg-emerald-500/10 hover:text-emerald-400': index !== selectedIndex}"
                                      class="px-4 py-2 cursor-pointer border-b border-white/5 last:border-0 transition-colors flex justify-between items-center text-sm">
                                     <span class="font-medium">{{ cliente.razon_social }}</span>
                                     <span class="text-xs font-mono text-gray-400 ml-2" :class="{'text-emerald-200': index === selectedIndex}">{{ cliente.cuit }}</span>
                                 </div>
                             </div>
                        </div>
                    </div>

                    <!-- 4. CUIT -->
                    <div class="col-span-2">
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1">CUIT</label>
                        <input type="text" 
                             :value="clienteSeleccionado?.cuit || '---'"
                             readonly
                             class="w-full bg-white/5 border border-white/10 rounded-lg py-2 px-3 text-base font-mono text-gray-300 text-center cursor-default"
                        >
                    </div>

                    <!-- 5. OC -->
                    <div class="col-span-1">
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1">O. Compra</label>
                        <input type="text" 
                            v-model="nroOC"
                            placeholder="---" 
                            class="w-full bg-transparent border-b border-white/10 focus:border-emerald-500/50 text-white text-base py-2 focus:outline-none transition-colors placeholder-white/10 text-center"
                        >
                    </div>

                    <!-- 6. ENTREGA -->
                    <div class="col-span-2">
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-green-600 mb-1">Entrega Est.</label>
                        <input type="date" 
                            v-model="fechaEntrega"
                            class="w-full bg-transparent border-b border-white/10 focus:border-green-500/50 text-gray-300 text-base py-2 focus:outline-none transition-colors"
                            style="color-scheme: dark;"
                        >
                    </div>
                </div>

                <!-- ROW 2: LOGISTICS (Symmetric Windows) -->
                <div class="grid grid-cols-12 gap-4 items-start border-t border-white/5 pt-4">
                    
                    <!-- 1. FISCAL (Left) -->
                    <div class="col-span-4">
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-emerald-500/40 mb-2 flex items-center gap-2">
                            <i class="fas fa-map-pin"></i> Domicilio Fiscal
                        </label>
                        <div class="bg-black/20 border border-white/5 rounded-lg p-3 h-20 overflow-y-auto">
                            <p class="text-xs text-white font-mono leading-relaxed" v-if="clienteSeleccionado">
                                {{ clientLogistics.address }}
                            </p>
                            <p class="text-xs text-gray-600 italic" v-else>Seleccione un cliente...</p>
                        </div>
                    </div>

                    <!-- 2. ENTREGA (Center) -->
                    <div class="col-span-4">
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-blue-400/40 mb-2 flex items-center gap-2">
                            <i class="fas fa-shipping-fast"></i> Dirección de Entrega
                        </label>
                        <div class="relative">
                            <select 
                                v-model="selectedDomicilioId" 
                                class="w-full bg-blue-900/10 border border-blue-500/20 text-blue-100/90 text-sm rounded-lg p-3 pr-8 focus:outline-none focus:border-blue-500/50 appearance-none h-20"
                                :disabled="!clienteSeleccionado"
                            >
                                <option :value="null">Definir entrega...</option>
                                <option v-for="dom in clientAddresses" :key="dom.id" :value="dom.id">
                                    {{ dom.calle }} {{ dom.numero }} ({{ dom.localidad }})
                                </option>
                            </select>
                             <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                                <i class="fas fa-chevron-down text-blue-500/50"></i>
                            </div>
                        </div>
                    </div>

                    <!-- 3. TRANSPORTE (Right) -->
                    <div class="col-span-4">
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-purple-400/40 mb-2 flex items-center gap-2">
                            <i class="fas fa-truck"></i> Transporte Asignado
                        </label>
                        <div class="relative">
                             <select 
                                v-model="selectedTransporteId" 
                                class="w-full bg-purple-900/10 border border-purple-500/20 text-purple-100/90 text-sm rounded-lg p-3 pr-8 focus:outline-none focus:border-purple-500/50 appearance-none h-20"
                                :disabled="!clienteSeleccionado"
                            >
                                <option :value="null">Gestionar Logística...</option>
                                <option v-for="t in availableTransportes" :key="t.id" :value="t.id">
                                    {{ t.nombre }}
                                </option>
                            </select>
                             <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                                <i class="fas fa-chevron-down text-purple-500/50"></i>
                            </div>
                        </div>
                    </div>
                </div>

            </header>

            <!-- SECTION 2: BODY (Grid Productos) -->
            <main class="flex-1 overflow-hidden p-2 flex flex-col">
                <div class="bg-black/30 rounded-xl border border-white/5 overflow-hidden flex-1 flex flex-col relative">
                    
                    <!-- Table Header -->
                    <div class="shrink-0 grid grid-cols-12 bg-white/5 px-4 py-3 gap-2 border-b border-white/5 text-[10px] font-bold uppercase tracking-widest text-gray-400">
                        <div class="col-span-1 text-center">#</div>
                        <div class="col-span-1">SKU</div>
                        <div class="col-span-4">Descripción</div>
                        <div class="col-span-1 text-center">Cant.</div>
                        <div class="col-span-1 text-right">Precio</div>
                        <div class="col-span-1 text-right">Desc %</div>
                        <div class="col-span-1 text-right">Desc $</div>
                        <div class="col-span-2 text-right">Subtotal</div>
                    </div>

                    <!-- Table Rows -->
                    <div ref="itemsContainerRef" class="overflow-y-auto flex-1 p-2 space-y-1">
                        
                        <!-- INLINE ENTRY ROW (Always Visible at Top) -->
                        <div class="grid grid-cols-12 px-4 py-4 gap-2 bg-emerald-500/5 rounded-lg items-center border border-emerald-500/20 shadow-lg relative z-30 min-h-[70px]">
                            
                            <!-- Index Placeholder -->
                            <div class="col-span-1 text-center font-bold text-emerald-500/50 text-xs">
                                <i class="fas fa-plus"></i>
                            </div>

                            <!-- SKU Input -->
                            <div class="col-span-1 relative">
                                <input type="text"
                                    ref="inputSkuRef"
                                    v-model="newItem.sku"
                                    @input="activateSearch('sku')"
                                    @keydown.down.prevent="navigateProductResults(1)"
                                    @keydown.up.prevent="navigateProductResults(-1)"
                                    @keydown.enter.prevent="selectProductHighlighted"
                                    placeholder="SKU"
                                    class="w-full bg-transparent border-b border-emerald-500/30 text-white font-mono text-xs focus:outline-none focus:border-emerald-500"
                                >
                            </div>

                            <!-- Descripción Input -->
                            <div class="col-span-4 relative">
                                <input type="text"
                                    ref="inputDescRef"
                                    v-model="newItem.descripcion"
                                    @input="activateSearch('description')"
                                    @keydown.down.prevent="navigateProductResults(1)"
                                    @keydown.up.prevent="navigateProductResults(-1)"
                                    @keydown.enter.prevent="selectProductHighlighted"
                                    placeholder="Buscar producto..."
                                    class="w-full bg-transparent border-none text-white placeholder-gray-600 focus:outline-none font-medium"
                                >
                                <!-- DROPDOWN RESULTS (Keep existing dropdown) -->
                                <div v-if="(showProductResults && (filteredProductos.length > 0 || productCanteraResults.length > 0 || isSearchingCanteraProduct))" 
                                     class="absolute top-full left-0 w-[400px] mt-2 bg-[#151515] border border-white/10 rounded-xl shadow-2xl max-h-80 overflow-y-auto z-50">
                                    <div v-for="(prod, index) in filteredProductos" :key="prod.id"
                                         @click="selectProduct(prod)"
                                         :class="{'bg-emerald-500/20 text-emerald-400': index === selectedProductIndex, 'hover:bg-emerald-500/10 hover:text-emerald-400': index !== selectedProductIndex}"
                                         class="px-4 py-2 cursor-pointer border-b border-white/5 last:border-0 transition-colors flex justify-between items-center">
                                        <div class="flex flex-col">
                                            <span class="font-medium text-sm">{{ prod.nombre }}</span>
                                            <span class="text-[10px] text-gray-500">{{ prod.sku }}</span>
                                        </div>
                                        <span class="font-mono text-xs text-emerald-400 font-bold">$ {{ (prod.precio_sugerido || prod.precio_lista || 0).toLocaleString('es-AR') }}</span>
                                    </div>

                                    <!-- CANTERA RESULTS SECTION -->
                                    <div v-if="productCanteraResults.length > 0" class="bg-black/40 border-t border-emerald-500/30">
                                        <div class="px-4 py-1 flex items-center justify-between text-[9px] uppercase font-bold tracking-widest text-emerald-600 bg-black/60">
                                            <span>Cantera de Maestros (Nube)</span>
                                            <i v-if="isSearchingCanteraProduct" class="fas fa-spinner fa-spin"></i>
                                        </div>
                                        <div v-for="item in productCanteraResults" :key="item.id"
                                             @click="importAndAddProduct(item)"
                                             class="px-4 py-2 cursor-pointer border-b border-white/5 last:border-0 hover:bg-indigo-900/30 transition-colors flex justify-between items-center group">
                                            <div class="flex flex-col min-w-0">
                                                <span class="font-medium text-sm text-indigo-200 group-hover:text-indigo-100 flex items-center gap-2">
                                                    {{ item.nombre }}
                                                    <i class="fas fa-cloud-download-alt text-[10px] opacity-50"></i>
                                                </span>
                                                <span class="text-[10px] text-indigo-400/50">{{ item.sku || 'Sin SKU' }}</span>
                                            </div>
                                            <div class="flex items-center gap-2">
                                                 <span class="text-[9px] bg-indigo-500/20 text-indigo-300 px-1.5 py-0.5 rounded border border-indigo-500/30">IMPORTAR</span>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <!-- LOADING STATE -->
                                    <div v-if="filteredProductos.length === 0 && productCanteraResults.length === 0 && isSearchingCanteraProduct" class="px-4 py-3 text-center">
                                        <span class="text-xs text-emerald-500/70 animate-pulse">Buscando en catálogo global...</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Cantidad -->
                            <div class="col-span-1">
                                <input type="number" 
                                    ref="inputQtyRef"
                                    v-model.number="newItem.cantidad" 
                                    @input="updateRowTotal"
                                    @keydown.enter.prevent="commitRow"
                                    class="w-full bg-transparent border-b border-emerald-500/30 text-emerald-400 font-bold text-center focus:outline-none focus:border-emerald-500"
                                >
                            </div>

                            <!-- Precio Unit. -->
                            <div class="col-span-1 text-right">
                                <input type="number" 
                                    v-model.number="newItem.precio" 
                                    @input="updateRowTotal"
                                    @keydown.enter.prevent="commitRow"
                                    class="w-full bg-transparent border-b border-emerald-500/30 text-gray-300 font-mono text-right focus:outline-none focus:border-emerald-500"
                                >
                            </div>

                            <!-- Descuento % -->
                            <div class="col-span-1 text-right">
                                <input type="number" 
                                    v-model.number="newItem.descuento_porcentaje" 
                                    @input="updateRowDescPct"
                                    @keydown.enter.prevent="commitRow"
                                    placeholder="%"
                                    class="w-full bg-transparent border-b border-emerald-500/30 text-yellow-500 font-mono text-right focus:outline-none focus:border-emerald-500"
                                >
                            </div>
                            <!-- Descuento $ (Restored) -->
                            <div class="col-span-1 text-right">
                                <input type="number" 
                                    v-model.number="newItem.descuento_valor" 
                                    @input="updateRowDescVal"
                                    @keydown.enter.prevent="commitRow"
                                    placeholder="$"
                                    class="w-full bg-transparent border-b border-emerald-500/30 text-yellow-500 font-mono text-right focus:outline-none focus:border-emerald-500"
                                >
                            </div>
                            
                            <!-- Subtotal (Replaces Desc $ + Total) -->
                            <div class="col-span-2 text-right">
                                <span class="font-mono font-bold text-white text-lg">$ {{ newItem.total.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</span>
                            </div>

                        </div>

                        <!-- SAVED ROWS -->
                        <div v-for="(item, index) in items" :key="item.sku || index" :class="{'bg-white/10': expandedRows.has(index)}">
                            <div class="grid grid-cols-12 px-4 py-3 gap-2 bg-white/[0.02] hover:bg-white/5 rounded-lg items-center group transition-colors border border-transparent hover:border-white/5 relative">
                            
                                <!-- Index -->
                                <div class="col-span-1 text-center font-mono text-gray-500 text-xs select-none">
                                    {{ index + 1 }}
                                </div>

                                <!-- SKU (Editable) -->
                                <div class="col-span-1">
                                    <input type="text" v-model="item.sku" 
                                        class="w-full bg-transparent border-none text-gray-400 font-mono text-xs focus:text-white focus:outline-none truncate">
                                </div>
                                
                                <!-- Descripcion (Editable) + Chevron -->
                                <div class="col-span-4 flex items-center gap-2">
                                     <button @click="toggleDetails(index)" class="text-gray-500 hover:text-white transition-colors focus:outline-none z-10 p-1">
                                        <i class="fas" :class="expandedRows.has(index) ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
                                    </button>
                                    <input type="text" v-model="item.descripcion" 
                                        class="w-full bg-transparent border-none text-gray-300 font-medium text-sm focus:text-white focus:outline-none truncate">
                                    
                                    <div v-if="item.producto_obj?.costos?.costo_reposicion === 0" class="shrink-0" title="ALERTA: Costo de Reposición Cero">
                                        <i class="fas fa-exclamation-triangle text-orange-500 animate-pulse"></i>
                                    </div>
                                </div>
                                
                                <!-- Cantidad (Editable) -->
                                <div class="col-span-1">
                                    <input type="number" 
                                        v-model.number="item.cantidad"
                                        @input="updateItemTotal(item)"
                                        class="w-full bg-transparent border-b border-transparent hover:border-white/20 focus:border-emerald-500 text-center font-bold text-white text-sm focus:outline-none transition-colors"
                                    >
                                </div>

                                <!-- Precio (Editable) -->
                                <div class="col-span-1 text-right relative">
                                    <span class="absolute left-0 text-gray-600 font-mono text-xs">$</span>
                                    <input type="number" 
                                        v-model.number="item.precio" 
                                        @input="updateItemTotal(item)"
                                        class="w-full bg-transparent border-b border-transparent hover:border-white/20 focus:border-emerald-500 text-right font-mono text-gray-300 text-sm focus:outline-none transition-colors"
                                    >
                                </div>

                               <!-- Descuento % (Editable) -->
                                <div class="col-span-1 text-right">
                                    <input type="number" 
                                        :value="item.descuento_porcentaje" 
                                        @input="(e) => { item.descuento_porcentaje = parseFloat(e.target.value); updateItemDescPct(item); }"
                                        class="w-full bg-transparent border-b border-transparent hover:border-white/20 focus:border-emerald-500 text-right font-mono text-yellow-500 text-sm focus:outline-none transition-colors"
                                        step="0.01"
                                    >
                                </div>

                                <!-- Descuento $ (Editable - Restored) -->
                                <div class="col-span-1 text-right">
                                    <input type="number" 
                                        v-model.number="item.descuento_valor" 
                                        @input="updateItemDescVal(item)"
                                        class="w-full bg-transparent border-b border-transparent hover:border-white/20 focus:border-emerald-500 text-right font-mono text-yellow-500 text-sm focus:outline-none transition-colors"
                                    >
                                </div>
                                
                                <!-- Total -->
                                <div class="col-span-2 text-right font-mono font-semibold text-white text-sm">
                                    $ {{ item.total.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}
                                </div>

                                <!-- Actions (Floating) -->
                                <div class="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/80 px-2 py-1 rounded-lg border border-white/10 shadow-xl z-20">
                                    <button @click="editItem(index)" class="text-blue-500 hover:text-blue-300 transition-colors" title="Editar">
                                        <i class="fas fa-pencil-alt"></i>
                                    </button>
                                    <button @click="removeItem(index)" class="text-red-500 hover:text-red-400 transition-colors" title="Eliminar">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                            
                            <!-- DETAILS ROW (Rentabilidad) -->
                            <div v-if="expandedRows.has(index)" class="px-4 py-2 bg-black/40 border-b border-white/5 text-xs text-gray-400 font-mono flex gap-8 pl-12">
                                <div>
                                    <span class="text-gray-600 block text-[9px] uppercase">Costo Unit.</span>
                                    <span>$ {{ (item.producto_obj?.costo || 0).toLocaleString('es-AR') }}</span>
                                </div>
                                 <div class="text-xs">
                                     <span class="text-gray-600 block text-[9px] uppercase">Rentabilidad</span>
                                     <span :class="(item.precio - (item.producto_obj?.costo || 0) * (1 - item.descuento_porcentaje/100)) > 0 ? 'text-green-500' : 'text-red-500'">
                                         {{ (((item.precio * (1 - item.descuento_porcentaje/100)) / (item.producto_obj?.costo || 1)) - 1).toLocaleString(undefined, {style: 'percent', minimumFractionDigits: 1}) }}
                                     </span>
                                 </div>
                            </div>
                        </div>

                    </div>
                </div>
            </main>
            </div> <!-- End of overflow-hidden relative wrapper -->

            <!-- SECTION 3: FOOTER -->
            <footer class="shrink-0 bg-[#0e0e0e] border-t border-white/10 p-4 relative z-40">
                
                <!-- NOTES WIDGET (Bottom Left) -->
                <div class="absolute left-6 bottom-6 z-50">
                    <!-- Toggle Button -->
                    <button @click="showNotes = !showNotes" 
                            class="flex items-center gap-2 px-3 py-2 rounded-lg border transition-all text-xs font-bold uppercase tracking-widest bg-[#1a1b26] shadow-lg"
                            :class="hasNotes ? 'text-orange-500 border-orange-500/50' : 'text-gray-500 border-white/10'">
                        <i class="fas fa-sticky-note" :class="hasNotes ? 'text-orange-500' : 'text-gray-600'"></i>
                        Notas
                    </button>

                    <!-- Notes Popup -->
                    <transition name="fade-slide-up">
                        <div v-if="showNotes" class="absolute bottom-full left-0 mb-2 w-80 bg-[#151515] border border-white/20 rounded-xl shadow-2xl p-3 flex flex-col gap-2 z-[60]">
                             <div class="flex justify-between items-center pb-2 border-b border-white/5">
                                <span class="text-[10px] font-bold uppercase text-gray-400">Instrucciones / Observaciones</span>
                                <button @click="showNotes = false" class="text-gray-500 hover:text-white"><i class="fas fa-times"></i></button>
                             </div>
                             <textarea 
                                v-model="notas"
                                placeholder="Escribe aquí instrucciones..." 
                                class="w-full h-32 bg-black/50 border border-white/10 rounded-lg p-2 text-sm text-white focus:border-orange-500/50 focus:outline-none resize-none placeholder-gray-700"
                             ></textarea>
                        </div>
                    </transition>
                </div>

                <div class="flex justify-end items-end gap-6">
                    
                    <div class="text-right">
                        <div class="text-[10px] font-bold uppercase tracking-widest text-gray-500">Subtotal Neto</div>
                        <div class="font-mono text-gray-300">$ {{ subtotal.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</div>
                    </div>

                    <!-- Global Discount Block -->
                     <div class="text-right flex flex-col items-end">
                        <div class="text-[10px] font-bold uppercase tracking-widest text-yellow-600 mb-1">Descuento Gral.</div>
                        <div class="flex items-center gap-2">
                             <div class="relative w-16">
                                <input type="number" v-model.number="descuentoGlobalPorcentaje" @input="updateGlobalDescPct" class="w-full bg-transparent border-b border-white/10 text-right font-mono text-sm text-yellow-500 focus:outline-none focus:border-yellow-500" placeholder="%">
                                <span class="absolute right-0 top-0 text-[10px] text-gray-600 pointer-events-none">%</span>
                             </div>
                             <div class="relative w-20">
                                <input type="number" v-model.number="descuentoGlobalValor" @input="updateGlobalDescVal" class="w-full bg-transparent border-b border-white/10 text-right font-mono text-sm text-yellow-500 focus:outline-none focus:border-yellow-500" placeholder="$">
                                <span class="absolute left-0 top-0 text-[10px] text-gray-600 pointer-events-none">$</span>
                             </div>
                        </div>
                    </div>

                    <div class="text-right">
                        <div class="text-[10px] font-bold uppercase tracking-widest text-gray-500">IVA (21%)</div>
                        <div class="font-mono text-gray-300">$ {{ ((subtotal - descuentoGlobalValor) * 0.21).toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</div>
                    </div>


                    
                    <!-- SAVE BUTTON BLOCK -->
                    <div class="text-right pl-6 border-l border-white/10 flex flex-col justify-end gap-2">
                         <div class="text-xs font-bold uppercase tracking-widest text-emerald-500 mb-1">Total Final</div>
                         <div class="flex items-baseline gap-2 justify-end mb-2">
                              <span class="text-sm text-gray-500 font-bold">ARS</span>
                              <span class="font-outfit text-3xl font-bold text-white tracking-tight">$ {{ totalFinal.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</span>
                         </div>
                         <button @click="savePedido" 
                                 :disabled="isSaving || items.length === 0 || !clienteSeleccionado"
                                 class="bg-emerald-500 hover:bg-emerald-400 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:shadow-emerald-500/20 transition-all flex items-center justify-center gap-2 uppercase tracking-wider text-sm">
                            <i v-if="isSaving" class="fas fa-spinner fa-spin"></i>
                            <i v-else class="fas fa-save"></i>
                            {{ isSaving ? 'Guardando...' : 'Guardar Pedido' }}
                         </button>
                    </div>
                </div>

            </footer>
            
            </div> <!-- End of Parent -->
            
            <div class="w-full bg-[#0b1120] border-t border-emerald-900/50 p-2 text-center text-xs text-emerald-500/30 font-mono shrink-0 relative z-50">
                SISTEMA TÁCTICO DE PEDIDOS V5 - OPERACIÓN SEGURA
            </div>
        </div>
        
        <!-- RENTABILIDAD PANEL (Moving to Root for Fixed Positioning Safety) -->
        <RentabilidadPanel v-model="showCostDrawer" />
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useClientesStore } from '../../stores/clientes';
import { useProductosStore } from '../../stores/productos';
import { useMaestrosStore } from '../../stores/maestros';
import RentabilidadPanel from './components/RentabilidadPanel.vue';
import api from '../../services/api'; // Import API service
import _ from 'lodash';
import canteraService from '@/services/canteraService';
import { useNotificationStore } from '@/stores/notification';

import { useRoute } from 'vue-router'; // Add useRoute

// --- STORES & ROUTER ---
const route = useRoute();
const notificationStore = useNotificationStore();
const clientesStore = useClientesStore();
const productosStore = useProductosStore();
const maestrosStore = useMaestrosStore();

// --- LIFECYCLE ---
onMounted(async () => {
    // 1. Check for Edit Mode
    if (route.params.id) {
        await loadPedido(route.params.id);
    } else {
        // New Order Mode: Fetch Suggestion ID
        try {
            const res = await api.get('/pedidos/sugerir_id');
            // Endpoint returns plain integer
            nroPedido.value = res.data;
        } catch (e) {
            console.error('Error fetching Suggestion ID:', e);
            // Fallback or leave as ---
        }
    }

    // 2. Ensure Clients are Loaded
    if (clientesStore.clientes.length === 0) {
        await clientesStore.fetchClientes();
    }

    // 3. Ensure Products are Loaded
    if (productosStore.productos.length === 0) {
        productosStore.fetchProductos();
    }
    
    // 4. Ensure Maestros (e.g., Transportes) are Loaded
    if (maestrosStore.transportes.length === 0) {
        await maestrosStore.fetchTransportes();
    }
    
    // 5. Global Keys
    window.addEventListener('keydown', handleGlobalKeys);
    
    // 6. Auto-Sync on Focus (Satellite Return)
    window.addEventListener('focus', checkClientSync);
});

const checkClientSync = async () => {
    // If we have a client selected, re-fetch to ensure data is fresh (e.g. edited in Satellite)
    if (clienteSeleccionado.value && (clienteSeleccionado.value.id || clienteSeleccionado.value._id)) {
        try {
            console.log("Syncing client data...");
            const id = clienteSeleccionado.value.id || clienteSeleccionado.value._id;
            const fresh = await clientesStore.fetchClienteById(id);
            if (fresh) {
                 clienteSeleccionado.value = fresh;
                 console.log("Client synced.");
            }
        } catch(e) {
            console.warn("Sync failed", e);
        }
    }
};

const loadPedido = async (id) => {
    try {
        notificationStore.add('Cargando pedido...', 'info');
        const res = await api.get(`/pedidos/${id}`);
        const p = res.data;

        // Hydrate Header
        nroPedido.value = p.id;
        fechaPedido.value = p.fecha ? p.fecha.split('T')[0] : new Date().toISOString().split('T')[0];
        notas.value = p.nota || '';
        // TODO: Handle Order Status specifically if needed (locked state?)

        // Hydrate Client
        // Ensure client list is loaded first (handled in onMounted)
        // We might need to handle "Client not in list" if it's external, but for now try find
        const foundCliente = clientesStore.clientes.find(c => c.id === p.cliente_id);
        if (foundCliente) {
            selectCliente(foundCliente);
        } else if (p.cliente) {
             // Fallback: use embedded client data if available
             selectCliente(p.cliente);
        }

        // Hydrate Items
        items.value = p.items.map(i => ({
            id: i.producto_id, // Use product ID or item ID? Local uses Prod ID usually.
            sku: i.producto?.sku || '???',
            descripcion: i.producto?.nombre || 'Producto Desconocido',
            cantidad: Number(i.cantidad),
            precio: Number(i.precio_unitario),
            descuento_porcentaje: 0, // Backend output format dependent
            descuento_valor: 0, // Backend output format dependent
            total: Number(i.total),
            producto_obj: i.producto
        }));
        
        // TODO: Backend 'items' usually don't carry discount breakdown per line in simple schemas.
        // If V5 schema supports line discounts, map them here. 
        // Assuming simple migration for now.

        notificationStore.add('Pedido cargado para edición.', 'success');

    } catch (e) {
        console.error(e);
        notificationStore.add('Error cargando pedido: ' + e.message, 'error');
    }
};

onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeys);
    window.removeEventListener('focus', checkClientSync);
});

// --- STATE: UI ---
const showCostDrawer = ref(false);
const showNotes = ref(false); // Toggle for Notes Widget

// --- STATE: PEDIDO ---
// --- STATE: PEDIDO ---
// --- STATE: PEDIDO ---
const nroPedido = ref('---');
const fechaPedido = ref(new Date().toISOString().split('T')[0]);
const fechaEntrega = ref('');
const nroOC = ref('');
const notas = ref('');
const expandedRows = ref(new Set());
const toggleDetails = (index) => {
    const newSet = new Set(expandedRows.value);
    if (newSet.has(index)) {
        newSet.delete(index);
    } else {
        newSet.add(index);
    }
    expandedRows.value = newSet;
};

// --- LOGISTICA STATE ---
const clienteSeleccionado = ref(null);

const clientLogistics = computed(() => {
    if (!clienteSeleccionado.value) return { address: '---', transport: '---' };
    
    const c = clienteSeleccionado.value;
    const doms = c.domicilios || [];
    
    // 1. Fiscal or First
    const fiscal = doms.find(d => d.es_fiscal);
    const targetDom = fiscal || doms[0];
    
    let address = 'Sin dirección cargada';
    let transport = 'Sin transporte';

    if (targetDom) {
        address = `${targetDom.calle || ''} ${targetDom.numero || ''}, ${targetDom.localidad || ''}`;
        if (targetDom.transporte?.nombre) {
            transport = targetDom.transporte.nombre;
        } else if (targetDom.transporte_nombre) {
             transport = targetDom.transporte_nombre;
        }
    }

    return { address, transport };
});

const selectedDomicilioId = ref(null);
const selectedTransporteId = ref(null);

const clientAddresses = computed(() => {
    return clienteSeleccionado.value?.domicilios || [];
});

const availableTransportes = computed(() => {
    return maestrosStore.transportes || [];
});

// Watch for client change to set defaults
watch(clienteSeleccionado, (newVal) => {
   if (newVal) {
       const doms = newVal.domicilios || [];
       const fiscal = doms.find(d => d.es_fiscal);
       const target = fiscal || doms[0];
       
       if (target) {
           selectedDomicilioId.value = target.id;
           // Trigger transport update logic handled by watcher next/manual
           if (target.transporte_id) selectedTransporteId.value = target.transporte_id;
           else if (target.transporte?.id) selectedTransporteId.value = target.transporte.id;
           else selectedTransporteId.value = null;
       } else {
           selectedDomicilioId.value = null;
           selectedTransporteId.value = null;
       }
   } else {
       selectedDomicilioId.value = null;
       selectedTransporteId.value = null;
   }
});

// Watch for domicile change to update transport
watch(selectedDomicilioId, (newId) => {
    if (!newId || !clienteSeleccionado.value) return;
    const dom = clienteSeleccionado.value.domicilios?.find(d => d.id === newId);
    if (dom) {
        if (dom.transporte_id) selectedTransporteId.value = dom.transporte_id;
        else if (dom.transporte?.id) selectedTransporteId.value = dom.transporte.id;
    }
});

// --- LÓGICA CONTEXTUAL (FIXED) ---
const router = useRouter(); // Ensure router is available
const showContextMenu = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);

const handleInputFocus = () => {
    // ANTI-REBOTE: Solo mostrar resultados si el menú NO está activo
    if (!showContextMenu.value) {
        showClienteResults.value = true;
    }
};

const handleContextMenu = (event) => {
    // 1. IMPORTANTE: Matar el rebote del buscador
    showClienteResults.value = false;

    // 2. Capturar coordenadas
    contextMenuX.value = event.clientX;
    contextMenuY.value = event.clientY;

    // 3. Abrir menú
    showContextMenu.value = true;
};

const irAFicha = () => {
    const c = clienteSeleccionado.value;
    const id = c?.id || c?._id;
    
    if (id) {
        console.log("Abriendo ficha en ventana satélite:", c.razon_social);
        
        // 1. Resolve URL securely using Vue Router
        const { href } = router.resolve({ 
            name: 'HaweClientCanvas', 
            params: { id: id },
            query: { mode: 'satellite' }
        });

        // 2. Window Dimensions
        const width = 1700;
        const height = 900;

        // 3. Center Calculation
        const left = (window.screen.width - width) / 2;
        const top = (window.screen.height - height) / 2;

        // 4. Clean Window Configuration (App-like)
        const features = `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes,status=no,menubar=no,toolbar=no,location=no`;

        // 5. Open Satellite Window
        window.open(href, 'EdicionCliente', features);
        
        showContextMenu.value = false;
    }
};

// Deprecated: contextMenu object removed in favor of flat refs
// Deprecated: openMenu removed
// Deprecated: contextMenu object removed in favor of flat refs
// Deprecated: openMenu removed
const clientInputRef = ref(null);
const inputQtyRef = ref(null);
const itemsContainerRef = ref(null); // Ref for auto-scroll
// Deprecated: clientEditUrl removed in favor of irAFicha method


const descuentoGlobalPorcentaje = ref('');
const descuentoGlobalValor = ref('');





const clientValidation = computed(() => {
    if (!clienteSeleccionado.value) return { valid: true, missing: [] };
    const c = clienteSeleccionado.value;
    const missing = [];
    
    if (!c.condicion_iva_id || c.condicion_iva_id === 'null') missing.push('Condición IVA');
    if (!c.segmento_id) missing.push('Segmento');
    if (!c.domicilios || c.domicilios.length === 0) missing.push('Domicilio');
    // Basic CUIT check
    if (!c.cuit || c.cuit.length < 5) missing.push('CUIT');

    return {
        valid: missing.length === 0,
        missing
    };
});
const busquedaCliente = ref('');
const showClienteResults = ref(false);

const items = ref([]); 

// --- STATE: INLINE ENTRY ---
const newItem = ref({
    sku: '',
    descripcion: '', 
    cantidad: 1,
    precio: '',
    descuento_porcentaje: '',
    descuento_valor: '',
    total: 0,
    producto_obj: null
});
const showProductResults = ref(false);
const inputSkuRef = ref(null);
const inputDescRef = ref(null);
const activeSearchField = ref('description'); 
const selectedProductIndex = ref(0);

// --- CANTERA STATE ---
const productCanteraResults = ref([]);
const isSearchingCanteraProduct = ref(false);

const handleProductCanteraSearch = _.debounce(async (val) => {
    if (!val || val.length < 3) {
        productCanteraResults.value = [];
        return;
    }
    isSearchingCanteraProduct.value = true;
    try {
        const res = await canteraService.searchProductos(val);
        // Deduplicación por ID (Database Key) para evitar SKUs nulos o repetidos
        const localIds = new Set(productosStore.productos.map(p => String(p.id)));
        productCanteraResults.value = res.data.filter(p => !localIds.has(String(p.id)));
    } catch (e) {
        console.error("Error buscando en Cantera:", e);
    } finally {
        isSearchingCanteraProduct.value = false;
    }
}, 400);

const importAndAddProduct = async (item) => {
    try {
        notificationStore.add('Importando producto de Cantera...', 'info');
        await canteraService.importProducto(item.id); 
        await productosStore.fetchProductos();
        
        // Buscar el producto recién importado en el store local
        const imported = productosStore.productos.find(p => String(p.id) === String(item.id));
        
        if (imported) {
            selectProduct(imported);
            notificationStore.add('Producto importado y seleccionado.', 'success');
        } else {
            notificationStore.add('Producto importado, pero no se pudo seleccionar automáticamente.', 'warning');
        }
        
        productCanteraResults.value = [];
    } catch (e) {
        console.error(e);
        notificationStore.add('Error crítico al importar producto.', 'error');
    }
};

// Watchers para disparar búsqueda en Cantera (Unified)
watch(() => newItem.value.sku, (val) => {
    if (activeSearchField.value === 'sku') handleProductCanteraSearch(val);
});
watch(() => newItem.value.descripcion, (val) => {
    if (activeSearchField.value === 'description') handleProductCanteraSearch(val);
});


// --- SEARCH LOGIC (CLIENTS) ---
const selectedIndex = ref(-1); // Start at -1 as requested

const filteredClientes = computed(() => {
    if (!busquedaCliente.value || busquedaCliente.value.length < 2) {
        selectedIndex.value = -1; // Reset selection on new search
        return [];
    }
    
    const normalize = (str) => str ? str.toString().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") : '';
    const term = normalize(busquedaCliente.value);
    
    const results = clientesStore.clientes.filter(c => {
        const nombre = normalize(c.razon_social);
        const fantasia = normalize(c.nombre_fantasia);
        const cuit = c.cuit ? c.cuit.toString() : ''; 
        return nombre.includes(term) || fantasia.includes(term) || cuit.includes(term);
    }).slice(0, 10);

    return results;
});


// --- SEARCH LOGIC (PRODUCTS) ---
const filteredProductos = computed(() => {
    // Unified Search Term: Determines what to search for based on active field
    let term = '';
    if (activeSearchField.value === 'sku') {
        term = String(newItem.value.sku || '').toLowerCase().trim();
    } else {
        term = String(newItem.value.descripcion || '').toLowerCase().trim();
    }

    if (productosStore.productos.length === 0) return [];
    if (term.length < 1) return []; // Allow 1 char for SKU search? Or keep it > 1? User wants instant feedback.

    const normalize = (str) => str ? str.toString().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") : '';
    const termNorm = normalize(term);

    return productosStore.productos.filter(p => {
        const pSku = normalize(p.sku);
        const pNombre = normalize(p.nombre || p.descripcion); 

        // Unified Logic: Search in BOTH SKU and Name regardless of which input is used
        // This fulfills: "en cualquiera de los dos lugares que se empiece a tipear aparezca el valor a elegir"
        return pSku.includes(termNorm) || pNombre.includes(termNorm);
    }).slice(0, 50);
});

// --- COMPUTED TOTALS ---
const saldoDeudor = computed(() => clienteSeleccionado.value?.saldo_actual || 0);

// Sum of line totals (which already have line discounts deducted)
const subtotal = computed(() => items.value.reduce((sum, item) => sum + item.total, 0));

// Global Discount Calculation
const totalFinal = computed(() => {
    const base = subtotal.value;
    const globalDesc = Number(descuentoGlobalValor.value) || 0;
    const taxable = Math.max(0, base - globalDesc);
    return taxable * 1.21; // Assuming IVA is applied ON TOP of the net after global discount? Or is global discount gross? Usually Net.
});

const hasNotes = computed(() => notas.value.trim().length > 0);

// --- NAVIGATION (CLIENTS/PRODUCTS) ---
const navigateResults = (direction) => {
    if (!filteredClientes.value.length) return;
    
    let newIndex = selectedIndex.value + direction;
    
    // Bounds check
    if (newIndex < 0) newIndex = 0;
    if (newIndex >= filteredClientes.value.length) newIndex = filteredClientes.value.length - 1;
    
    selectedIndex.value = newIndex;
    
    // Auto-Scroll
    const list = document.querySelector('.client-results-list'); 
    if (list) {
         const item = list.children[selectedIndex.value];
         if (item) item.scrollIntoView({ block: 'nearest' });
    }
    
    // Keep Focus
    clientInputRef.value?.focus();
};
const selectHighlighted = () => {
    if (filteredClientes.value.length && showClienteResults.value && selectedIndex.value >= 0) {
        selectCliente(filteredClientes.value[selectedIndex.value]);
    } else {
        // Trigger search or other action if needed
    }
};

const navigateProductResults = (direction) => {
    if (!filteredProductos.value.length) return;
    selectedProductIndex.value += direction;
    if (selectedProductIndex.value < 0) selectedProductIndex.value = filteredProductos.value.length - 1;
    if (selectedProductIndex.value >= filteredProductos.value.length) selectedProductIndex.value = 0;
};

const selectProductHighlighted = () => {
    if (filteredProductos.value.length) {
        selectProduct(filteredProductos.value[selectedProductIndex.value]);
    } else {
        // Fallback for manual entry: Move focus to Quantity
        inputQtyRef.value?.focus();
    }
};

// --- METHODS ---
const selectCliente = async (cliente) => {
    // 1. Initial set for instant UI feedback
    clienteSeleccionado.value = cliente;
    busquedaCliente.value = cliente.razon_social;
    showClienteResults.value = false;
    selectedIndex.value = -1; // Reset

    // 2. Lazy Load Full Data (Critical for Validation of nested arrays like domicilios)
    try {
        // Only fetch if we assume the list object is lightweight
        // We use the store action which handles caching if implemented, or just hits API
        const fullClient = await clientesStore.fetchClienteById(cliente.id);
        if (fullClient) {
            clienteSeleccionado.value = fullClient;
        }
    } catch(e) {
        console.warn("Could not load full client details, running with partial data", e);
    }

    setTimeout(() => inputSkuRef.value?.focus(), 100);
};

const activateSearch = (field) => {
    activeSearchField.value = field;
    showProductResults.value = true;
    selectedProductIndex.value = 0;
};

const selectProduct = (prod) => {
    newItem.value.producto_obj = prod;
    newItem.value.sku = prod.sku;
    newItem.value.descripcion = prod.nombre;
    const price = prod.precio_sugerido || prod.precio_lista || 0;
    newItem.value.precio = price || ''; // Handle 0 prices as empty for cleaner UI? Or keep 0 if it's real price? User said "no lo pongamos". Let's try keeping real price if > 0.
    newItem.value.cantidad = 1;
    
    // Reset discounts
    newItem.value.descuento_porcentaje = '';
    newItem.value.descuento_valor = '';
    
    newItem.value.total = price;
    showProductResults.value = false;
    
    // Auto-focus Quantity for speed
    setTimeout(() => {
        inputQtyRef.value?.focus();
        inputQtyRef.value?.select();
    }, 50);
};

// --- INLINE ROW DISCOUNT HANDLERS ---
const updateRowDescPct = () => {
    const gross = (Number(newItem.value.cantidad) || 0) * (Number(newItem.value.precio) || 0);
    const pct = Number(newItem.value.descuento_porcentaje) || 0;
    newItem.value.descuento_valor = (gross * pct) / 100;
    if (newItem.value.descuento_valor === 0) newItem.value.descuento_valor = ''; // Keep UI Clean
    updateRowTotal();
};

const updateRowDescVal = () => {
    const gross = (Number(newItem.value.cantidad) || 0) * (Number(newItem.value.precio) || 0);
    const val = Number(newItem.value.descuento_valor) || 0;
    if (gross > 0) {
        newItem.value.descuento_porcentaje = (val / gross) * 100;
    } else {
        newItem.value.descuento_porcentaje = '';
    }
    updateRowTotal();
};

const updateRowTotal = () => {
    const gross = (Number(newItem.value.cantidad) || 0) * (Number(newItem.value.precio) || 0);
    const desc = Number(newItem.value.descuento_valor) || 0;
    newItem.value.total = Math.max(0, gross - desc);
};

// --- SAVED ROW DISCOUNT HANDLERS ---
const updateItemDescPct = (item) => {
    const gross = item.cantidad * item.precio;
    const pct = item.descuento_porcentaje;
    item.descuento_valor = (gross * pct) / 100;
    updateItemTotal(item);
};

const updateItemDescVal = (item) => {
    const gross = item.cantidad * item.precio;
    const val = item.descuento_valor;
    if (gross > 0) {
        item.descuento_porcentaje = (val / gross) * 100;
    } else {
        item.descuento_porcentaje = 0;
    }
    updateItemTotal(item);
};

const updateItemTotal = (item) => {
    const gross = Number(item.cantidad) * Number(item.precio);
    const desc = Number(item.descuento_valor || 0);
    item.total = Math.max(0, gross - desc);
    // Recalculate percentage just in case price/qty changed but value stayed same?
    // User preference often: keep % constant or keep $ constant?
    // Let's keep $ constant for now unless explicitly changed, but update % visualization.
    if (gross > 0) {
         item.descuento_porcentaje = (desc / gross) * 100;
    }
};

// --- GLOBAL FOOTER DISCOUNT HANDLERS ---
// --- GLOBAL FOOTER DISCOUNT HANDLERS ---
const updateGlobalDescPct = () => {
    const base = subtotal.value;
    const pct = Number(descuentoGlobalPorcentaje.value) || 0;
    descuentoGlobalValor.value = (base * pct) / 100;
    if (descuentoGlobalValor.value === 0) descuentoGlobalValor.value = '';
};

const updateGlobalDescVal = () => {
    const base = subtotal.value;
    const val = Number(descuentoGlobalValor.value) || 0;
    if (base > 0) {
        descuentoGlobalPorcentaje.value = (val / base) * 100;
    } else {
        descuentoGlobalPorcentaje.value = '';
    }
};


const commitRow = () => {
    if (!newItem.value.producto_obj && !newItem.value.descripcion) return;

    // Validation: Must have product object (prevents empty/ghost rows)
    if (!newItem.value.producto_obj) {
        notificationStore.add('Seleccione un producto válido.', 'warning');
        return;
    }

    if (newItem.value.cantidad <= 0) {
        notificationStore.add('La cantidad debe ser mayor a 0.', 'warning');
        return;
    }

    // Use PUSH instead of UNSHIFT per user request
    items.value.push({ 
        ...newItem.value,
        id: newItem.value.producto_obj?.id || Date.now(), // Ensure a unique ID for the item in the list
        cantidad: Number(newItem.value.cantidad),
        precio: Number(newItem.value.precio),
        descuento_porcentaje: Number(newItem.value.descuento_porcentaje || 0),
        descuento_valor: Number(newItem.value.descuento_valor || 0),
        total: Number(newItem.value.total)
    }); 
    
    // Reset but keep some logical defaults if needed
    newItem.value = {
        sku: '',
        descripcion: '',
        cantidad: 1,
        precio: 0,
        descuento_porcentaje: 0,
        descuento_valor: 0,
        total: 0,
        producto_obj: null
    };
    showProductResults.value = false;
    
    // Focus back to Desc or SKU? User flow usually SKU -> Desc -> Qty -> Enter -> New SKU
    // Let's focus SKU
    // Focus back to Desc or SKU? User flow usually SKU -> Desc -> Qty -> Enter -> New SKU
    // Let's focus SKU
    setTimeout(() => {
        inputSkuRef.value?.focus();
        
        // Auto-scroll to bottom to show new item
        if (itemsContainerRef.value) {
            itemsContainerRef.value.scrollTop = itemsContainerRef.value.scrollHeight;
        }
    }, 50);
};


const editItem = async (index) => {
    // 1. Get item safely
    const item = items.value[index];
    if (!item) return;

    // 2. Clone data to avoid reactivity issues with splice
    const itemData = JSON.parse(JSON.stringify(item));

    // 3. Remove from list (Move to "workbench")
    items.value.splice(index, 1);
    
    // 4. Update newItem state after DOM update to prevent race conditions
    // (Though strictly not necessary for state, good for finding inputs)
    newItem.value = {
        ...itemData,
        // Ensure numbers are reactive/correct types
        cantidad: Number(itemData.cantidad),
        precio: Number(itemData.precio),
        // Use empty string for 0 to keep UI clean
        descuento_porcentaje: itemData.descuento_porcentaje || '',
        descuento_valor: itemData.descuento_valor || '',
        producto_obj: itemData.producto_obj || null
    };

    // 5. Build/Focus
    showProductResults.value = false; // Hide dropdown if it pops up
    // Ensure the input actually receives the value before focus triggers selection logic
    setTimeout(() => {
        if (inputSkuRef.value) {
            inputSkuRef.value.focus();
            inputSkuRef.value.select(); // Select text for easy replacement
        }
    }, 100);
};

const removeItem = (index) => {
    items.value.splice(index, 1);
};

// Global Shortcuts
const handleGlobalKeys = (e) => {
    if (e.key === 'F3') {
        e.preventDefault();
        inputDescRef.value?.focus();
    }
};

const resetPedido = async () => {
    if (items.value.length > 0) {
        if (!confirm('¿Descartar pedido actual y comenzar uno nuevo?')) return;
    }
    
    // Reset State
    nroPedido.value = '---';
    fechaPedido.value = new Date().toISOString().split('T')[0];
    clienteSeleccionado.value = null;
    busquedaCliente.value = '';
    items.value = [];
    notas.value = '';
    descuentoGlobalPorcentaje.value = '';
    descuentoGlobalValor.value = '';
    
    // Fetch new ID
    try {
        const res = await api.get('/pedidos/sugerir_id');
        nroPedido.value = res.data;
    } catch (e) {
        console.error('Error Resetting:', e);
    }
    
    setTimeout(() => {
        // Focus client search
        const clientInput = document.querySelector('input[placeholder="Buscar Cliente..."]');
        if (clientInput) clientInput.focus();
    }, 100);
};

const isSaving = ref(false);

const savePedido = async () => {
    if (!clienteSeleccionado.value) return notificationStore.add('Seleccione un cliente.', 'error');
    if (items.value.length === 0) return notificationStore.add('Agregue al menos un producto.', 'error');

    isSaving.value = true;
    try {
        const payload = {
            cliente_id: clienteSeleccionado.value.id || clienteSeleccionado.value._id,
            fecha: new Date(fechaPedido.value).toISOString(),
            items: items.value.map(i => ({
                producto_id: i.id || i.producto_obj?.id,
                cantidad: i.cantidad,
                precio_unitario: i.precio,
                total: i.total
                // TODO: Add discounts to backend schema if needed
            })),
            nota: notas.value,
            descuento_global_porcentaje: descuentoGlobalPorcentaje.value || 0,
            domicilio_id: selectedDomicilioId.value,
            transporte_id: selectedTransporteId.value
        };

        // Check if editing existing or new
        // Ideally we use POST for new, PUT for edit.
        // Assuming simple POST for now based on instructions "Logic: Guardar Pedido -> POST"
        
        await api.post('/pedidos/', payload);
        
        notificationStore.add('Pedido guardado exitosamente.', 'success');
        
        // Reset or Redirect
        setTimeout(() => {
             // resetPedido(); 
             // Or redirect to list
             router.push({ name: 'PedidoList' });
        }, 1000);

    } catch (e) {
        console.error(e);
        notificationStore.add('Error al guardar pedido: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        isSaving.value = false;
    }
};

</script>

<style scoped>
.fade-slide-up-enter-active,
.fade-slide-up-leave-active {
  transition: all 0.2s ease-out;
}

.fade-slide-up-enter-from,
.fade-slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>


