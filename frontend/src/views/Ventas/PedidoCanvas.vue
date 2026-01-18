<template>
    <div class="flex h-full w-full bg-[#1a1b26] text-white overflow-hidden font-outfit relative shadow-[inset_0_0_20px_rgba(16,185,129,0.2)] border-2 border-emerald-500/30">
        
        <!-- MAIN CONTENT (Shrinks when drawer opens) -->
        <div class="flex-1 flex flex-col transition-all duration-300 ease-in-out"
             :class="showCostDrawer ? 'mr-96' : ''">
             
            <!-- TOP TOOLBAR: Navigation & Actions -->
            <div class="bg-[#111] border-b border-white/5 px-5 py-2 flex justify-between items-center text-xs relative z-20">
                <button @click="$router.push({ name: 'PedidoList' })" class="text-gray-400 hover:text-white flex items-center gap-2 transition-colors">
                    <i class="fas fa-arrow-left"></i> Volver a Tablero de Pedidos
                </button>
                <div class="flex gap-3">
                    <button @click="resetPedido" class="text-emerald-500 hover:text-emerald-400 font-bold flex items-center gap-2 transition-colors uppercase tracking-wider">
                        <i class="fas fa-plus-circle"></i> Nuevo Pedido
                    </button>
                </div>
            </div>

            <!-- SECTION 1: HEADER (Refinado: Pedido / Fecha / Cliente) -->
            <header class="shrink-0 p-5 border-b border-white/10 bg-[#111] grid grid-cols-12 gap-6 items-start relative z-10">
                
                <!-- Group 1: Identificadores (Lo más importante) -->
                <div class="col-span-3 flex flex-col gap-3">
                    <div class="flex items-center gap-3">
                        <div class="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-lg font-mono font-bold text-xl border border-emerald-500/30">
                            #{{ nroPedido }}
                        </div>
                        <div class="flex flex-col">
                            <span class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Fecha Pedido</span>
                            <!-- Editable Date Input -->
                            <input type="date" 
                                v-model="fechaPedido" 
                                class="bg-transparent border-b border-white/10 hover:border-emerald-500/50 focus:border-emerald-500 text-white font-bold text-lg w-full focus:outline-none transition-colors cursor-pointer"
                                title="Doble click para calendario completo"
                                style="color-scheme: dark;"
                            >
                        </div>
                    </div>
                </div>

                <!-- Group 2: Cliente & CUIT -->
                <div class="col-span-5 grid grid-cols-12 gap-3">
                    <div class="col-span-8">
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1">Cliente</label>
                        <div class="relative group">
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <i class="fas fa-user-circle text-gray-500 group-focus-within:text-emerald-400 text-lg"></i>
                            </div>
                            <input type="text" 
                            v-model="busquedaCliente"
                            @focus="showClienteResults = true"
                            @keydown.down.prevent="navigateResults(1)"
                            @keydown.up.prevent="navigateResults(-1)"
                            @keydown.enter.prevent="selectHighlighted"
                            placeholder="Buscar Cliente..." 
                            class="w-full bg-black/50 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-lg font-medium text-white placeholder-gray-600 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 focus:outline-none transition-all"
                        >
                        <!-- Client Results Dropdown -->
                        <div v-if="showClienteResults && filteredClientes.length > 0" 
                             class="absolute top-full left-0 w-full mt-1 bg-[#151515] border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden max-h-60 overflow-y-auto">
                            <div v-for="(cliente, index) in filteredClientes" 
                                 :key="cliente.id"
                                 @click="selectCliente(cliente)"
                                 :class="{'bg-emerald-500/20 text-emerald-400': index === selectedIndex, 'hover:bg-emerald-500/10 hover:text-emerald-400': index !== selectedIndex}"
                                 class="px-4 py-3 cursor-pointer border-b border-white/5 last:border-0 transition-colors flex justify-between items-center group/item">
                                <span class="font-medium text-sm">{{ cliente.razon_social }}</span>
                                <span class="text-xs font-mono text-gray-500 group-hover/item:text-emerald-500/70">{{ cliente.cuit }}</span>
                            </div>
                        </div>    
                        </div>
                    </div>
                    <div class="col-span-4">
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1">CUIT (ARCA)</label>
                        <div class="relative group">
                             <input type="text" 
                                :value="clienteSeleccionado?.cuit || '---'"
                                readonly
                                class="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-3 text-lg font-mono text-gray-300 focus:border-emerald-500/50 focus:outline-none text-center cursor-pointer hover:bg-white/10 hover:text-emerald-400 transition-colors selection:bg-emerald-500/30 selection:text-white"
                                title="Click para copiar (Pendiente)"
                            >
                            <i class="fas fa-copy absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-600 group-hover:text-emerald-500 pointer-events-none"></i>
                        </div>
                    </div>
                </div>

                <!-- Group 3: Contexto (OC, Entrega) -->
                <div class="col-span-2 flex flex-col gap-2">
                     <div>
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-gray-500">Orden de Compra</label>
                        <input type="text" placeholder="---" class="bg-transparent border-b border-white/10 focus:border-emerald-500 text-sm w-full py-1 text-white focus:outline-none">
                     </div>
                     <div>
                        <label class="block text-[10px] font-bold uppercase tracking-widest text-green-600">Entrega Estimada</label>
                        <input type="date" style="color-scheme: dark;" class="bg-transparent border-b border-white/10 focus:border-emerald-500 text-sm w-full py-1 text-gray-300 focus:outline-none">
                     </div>
                </div>

                 <!-- Group 4: Saldo / Toggle Drawer -->
                 <div class="col-span-2 flex justify-end items-center gap-2">
                    <div class="text-right">
                        <div class="text-[10px] text-red-500 font-bold uppercase tracking-widest">Saldo Deudor</div>
                        <div class="text-xl font-bold text-red-400 cursor-pointer hover:underline decoration-red-500/50">$ {{ saldoDeudor.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</div>
                    </div>
                 </div>

            </header>

            <!-- SECTION 2: BODY (Grid Productos) -->
            <main class="flex-1 overflow-auto p-4 flex flex-col">
                <div class="bg-black/30 rounded-xl border border-white/5 overflow-hidden flex-1 flex flex-col relative">
                    
                    <!-- Table Header -->
                    <div class="shrink-0 grid grid-cols-12 bg-white/5 px-4 py-3 gap-2 border-b border-white/5 text-[10px] font-bold uppercase tracking-widest text-gray-400">
                        <div class="col-span-1">#</div>
                        <div class="col-span-2">SKU</div>
                        <div class="col-span-2">Descripción</div>
                        <div class="col-span-1 text-center">Cant.</div>
                        <div class="col-span-2 text-right">Precio</div>
                        <div class="col-span-1 text-right">Desc %</div>
                        <div class="col-span-1 text-right">Desc $</div>
                        <div class="col-span-2 text-right">Subtotal</div>
                    </div>

                    <!-- Table Rows -->
                    <div class="overflow-y-auto flex-1 p-2 space-y-1">
                        
                        <!-- INLINE ENTRY ROW (Always Visible at Top) -->
                        <div class="grid grid-cols-12 px-4 py-2 gap-2 bg-emerald-500/5 rounded-lg items-center border border-emerald-500/20 shadow-lg relative z-30">
                            
                            <!-- Row Number / Status -->
                            <div class="col-span-1 flex items-center justify-center">
                                <span class="text-[10px] font-bold bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded border border-emerald-500/30">NUEVO</span>
                            </div>

                            <!-- SKU Input -->
                            <div class="col-span-2 relative">
                                <input type="text"
                                    ref="inputSkuRef"
                                    v-model="newItem.sku"
                                    @focus="activateSearch('sku')"
                                    @input="activateSearch('sku')"
                                    @keydown.down.prevent="navigateProductResults(1)"
                                    @keydown.up.prevent="navigateProductResults(-1)"
                                    @keydown.enter.prevent="selectProductHighlighted"
                                    placeholder="SKU"
                                    class="w-full bg-transparent border-b border-emerald-500/30 text-white font-mono text-xs focus:outline-none focus:border-emerald-500"
                                >
                            </div>

                            <!-- Descripción Input -->
                            <div class="col-span-2 relative">
                                <input type="text"
                                    ref="inputDescRef"
                                    v-model="newItem.descripcion"
                                    @focus="activateSearch('description')"
                                    @input="activateSearch('description')"
                                    @keydown.down.prevent="navigateProductResults(1)"
                                    @keydown.up.prevent="navigateProductResults(-1)"
                                    @keydown.enter.prevent="selectProductHighlighted"
                                    placeholder="Buscar producto..."
                                    class="w-full bg-transparent border-none text-white placeholder-gray-600 focus:outline-none font-medium"
                                >
                                <!-- DROPDOWN RESULTADOS (Shared Position) -->
                                <div v-if="showProductResults && filteredProductos.length > 0" 
                                     class="absolute top-full left-0 w-[400px] mt-2 bg-[#151515] border border-white/10 rounded-xl shadow-2xl max-h-60 overflow-y-auto z-50">
                                    <div v-for="(prod, index) in filteredProductos" :key="prod.id"
                                         @click="selectProduct(prod)"
                                         :class="{'bg-emerald-500/20 text-emerald-400': index === selectedProductIndex, 'hover:bg-emerald-500/10 hover:text-emerald-400': index !== selectedProductIndex}"
                                         class="px-4 py-2 cursor-pointer border-b border-white/5 last:border-0 transition-colors flex justify-between items-center">
                                        <div class="flex flex-col">
                                            <span class="font-medium text-sm">{{ prod.nombre }}</span>
                                            <span class="text-[10px] text-gray-500">{{ prod.sku }}</span>
                                        </div>
                                        <span class="font-mono text-xs text-emerald-400 font-bold">$ {{ (prod.precio_sugerido || prod.precio_lista).toLocaleString('es-AR') }}</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Cantidad -->
                            <div class="col-span-1">
                                <input type="number" 
                                    v-model.number="newItem.cantidad" 
                                    @input="updateRowTotal"
                                    class="w-full bg-transparent border-b border-emerald-500/30 text-emerald-400 font-bold text-center focus:outline-none focus:border-emerald-500"
                                >
                            </div>

                            <!-- Precio Unit. -->
                            <div class="col-span-2 text-right">
                                <input type="number" 
                                    v-model.number="newItem.precio" 
                                    @input="updateRowTotal"
                                    class="w-full bg-transparent border-b border-emerald-500/30 text-gray-300 font-mono text-right focus:outline-none focus:border-emerald-500"
                                >
                            </div>

                            <!-- Descuento % -->
                            <div class="col-span-1 text-right">
                                <input type="number" 
                                    v-model.number="newItem.descuento_porcentaje" 
                                    @input="updateRowDescPct"
                                    placeholder="%"
                                    class="w-full bg-transparent border-b border-emerald-500/30 text-yellow-500 font-mono text-right focus:outline-none focus:border-emerald-500 text-xs"
                                >
                            </div>
                            <!-- Descuento $ -->
                            <div class="col-span-1 text-right">
                                <input type="number" 
                                    v-model.number="newItem.descuento_valor" 
                                    @input="updateRowDescVal"
                                    @keydown.enter="commitRow"
                                    placeholder="$"
                                    class="w-full bg-transparent border-b border-emerald-500/30 text-yellow-500 font-mono text-right focus:outline-none focus:border-emerald-500 text-xs"
                                >
                            </div>

                            <!-- Total -->
                            <div class="col-span-2 text-right">
                                <span class="font-mono font-bold text-white text-lg">$ {{ newItem.total.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</span>
                            </div>

                        </div>

                        <!-- SAVED ROWS -->
                        <div v-for="(item, index) in items" :key="item.sku || index" 
                             class="grid grid-cols-12 px-4 py-3 gap-2 bg-white/[0.02] hover:bg-white/5 rounded-lg items-center group transition-colors border border-transparent hover:border-white/5">
                            
                            <!-- Actions / Index -->
                            <div class="col-span-1 flex justify-center text-gray-600 font-mono text-xs relative group/actions">
                                <span class="group-hover/actions:hidden">{{ items.length - index }}</span>
                                <button @click="removeItem(index)" class="hidden group-hover/actions:block text-red-500 hover:text-red-400">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>

                            <!-- SKU (Editable) -->
                            <div class="col-span-2">
                                <input type="text" v-model="item.sku" 
                                    class="w-full bg-transparent border-none text-gray-400 font-mono text-xs focus:text-white focus:outline-none truncate">
                            </div>
                            
                            <!-- Descripcion (Editable) -->
                            <div class="col-span-2">
                                <input type="text" v-model="item.descripcion" 
                                    class="w-full bg-transparent border-none text-gray-300 font-medium text-sm focus:text-white focus:outline-none truncate">
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
                            <div class="col-span-2 text-right">
                                <input type="number" 
                                    v-model.number="item.precio" 
                                    @input="updateItemTotal(item)"
                                    class="w-full bg-transparent border-b border-transparent hover:border-white/20 focus:border-emerald-500 text-right font-mono text-gray-300 text-sm focus:outline-none transition-colors"
                                >
                            </div>

                           <!-- Descuento % (Editable) -->
                            <div class="col-span-1 text-right">
                                <input type="number" 
                                    v-model.number="item.descuento_porcentaje" 
                                    @input="updateItemDescPct(item)"
                                    class="w-full bg-transparent border-b border-transparent hover:border-white/20 focus:border-emerald-500 text-right font-mono text-yellow-500 text-sm focus:outline-none transition-colors"
                                >
                            </div>
                            <!-- Descuento $ (Editable) -->
                            <div class="col-span-1 text-right">
                                <input type="number" 
                                    v-model.number="item.descuento_valor" 
                                    @input="updateItemDescVal(item)"
                                    class="w-full bg-transparent border-b border-transparent hover:border-white/20 focus:border-emerald-500 text-right font-mono text-yellow-500 text-sm focus:outline-none transition-colors"
                                >
                            </div>
                            
                            <!-- Total -->
                            <div class="col-span-2 text-right font-mono font-bold text-white text-lg">
                                $ {{ item.total.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}
                            </div>
                        </div>

                    </div>
                </div>
            </main>

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

                    <div class="text-right pl-6 border-l border-white/10">
                        <div class="text-xs font-bold uppercase tracking-widest text-emerald-500 mb-1">Total Final</div>
                        <div class="flex items-baseline gap-2 justify-end">
                             <span class="text-sm text-gray-500 font-bold">ARS</span>
                             <span class="font-outfit text-3xl font-bold text-white tracking-tight">$ {{ totalFinal.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</span>
                        </div>
                    </div>
                </div>
            </footer>
        </div>



        <!-- RENTABILIDAD PANEL (Extracted Component) -->
        <RentabilidadPanel v-model="showCostDrawer" />

    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useClientesStore } from '../../stores/clientes';
import { useProductosStore } from '../../stores/productos';
import RentabilidadPanel from './components/RentabilidadPanel.vue';
import api from '../../services/api'; // Import API service

// --- STORES ---
const clientesStore = useClientesStore();
const productosStore = useProductosStore();

// --- LIFECYCLE ---
onMounted(async () => {
    // 1. Fetch Suggestion ID
    try {
        const res = await api.get('/pedidos/sugerir_id');
        nroPedido.value = res.data.id;
    } catch (e) {
        console.error('Error fetching Suggestion ID:', e);
        nroPedido.value = 'ERR';
    }

    // 2. Ensure Clients are Loaded
    if (clientesStore.clientes.length === 0) {
        clientesStore.fetchClientes();
    }

    // 3. Ensure Products are Loaded
    productosStore.fetchProductos();
    
    // 4. Global Keys
    window.addEventListener('keydown', handleGlobalKeys);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeys);
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

// Global Discount State
const descuentoGlobalPorcentaje = ref(0);
const descuentoGlobalValor = ref(0);

const clienteSeleccionado = ref(null);
const busquedaCliente = ref('');
const showClienteResults = ref(false);

const items = ref([]); 

// --- STATE: INLINE ENTRY ---
const newItem = ref({
    sku: '',
    descripcion: '', 
    cantidad: 1,
    precio: 0,
    descuento_porcentaje: 0,
    descuento_valor: 0,
    total: 0,
    producto_obj: null
});
const showProductResults = ref(false);
const inputSkuRef = ref(null);
const inputDescRef = ref(null);
const activeSearchField = ref('description'); 
const selectedProductIndex = ref(0);

// --- SEARCH LOGIC (CLIENTS) ---
const selectedIndex = ref(0); 

const filteredClientes = computed(() => {
    if (!busquedaCliente.value || busquedaCliente.value.length < 2) return [];
    
    const normalize = (str) => str ? str.toString().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") : '';
    const term = normalize(busquedaCliente.value);
    
    return clientesStore.clientes.filter(c => {
        const nombre = normalize(c.razon_social);
        const fantasia = normalize(c.nombre_fantasia);
        const cuit = c.cuit ? c.cuit.toString() : ''; 
        return nombre.includes(term) || fantasia.includes(term) || cuit.includes(term);
    }).slice(0, 10);
});

// --- SEARCH LOGIC (PRODUCTS) ---
const filteredProductos = computed(() => {
    const termSku = (newItem.value.sku || '').toLowerCase().trim();
    const termDesc = (newItem.value.descripcion || '').toLowerCase().trim();
    
    if (productosStore.productos.length === 0) return [];

    const normalize = (str) => str ? str.toString().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") : '';
    
    const termSkuNorm = normalize(termSku);
    const termDescNorm = normalize(termDesc);

    if (termSku.length < 1 && termDesc.length < 2) return [];

    return productosStore.productos.filter(p => {
        const pSku = normalize(p.sku);
        const pNombre = normalize(p.nombre || p.descripcion); // Check both if ambiguous

        // 1. SKU Search
        if (termSku.length >= 1) {
            if (pSku.includes(termSkuNorm)) return true;
        }

        // 2. Description Search
        if (termDesc.length >= 2) {
            if (pNombre.includes(termDescNorm) || pSku.includes(termDescNorm)) return true;
        }
        
        return false;
    }).slice(0, 50);
});

// --- COMPUTED TOTALS ---
const saldoDeudor = computed(() => clienteSeleccionado.value?.saldo_actual || 0);

// Sum of line totals (which already have line discounts deducted)
const subtotal = computed(() => items.value.reduce((sum, item) => sum + item.total, 0));

// Global Discount Calculation
const totalFinal = computed(() => {
    const base = subtotal.value;
    const globalDesc = descuentoGlobalValor.value;
    const taxable = Math.max(0, base - globalDesc);
    return taxable * 1.21; // Assuming IVA is applied ON TOP of the net after global discount? Or is global discount gross? Usually Net.
});

const hasNotes = computed(() => notas.value.trim().length > 0);

// --- NAVIGATION (CLIENTS/PRODUCTS) ---
const navigateResults = (direction) => {
    if (!filteredClientes.value.length) return;
    selectedIndex.value += direction;
    if (selectedIndex.value < 0) selectedIndex.value = filteredClientes.value.length - 1;
    if (selectedIndex.value >= filteredClientes.value.length) selectedIndex.value = 0;
};
const selectHighlighted = () => {
    if (filteredClientes.value.length && showClienteResults.value) {
        selectCliente(filteredClientes.value[selectedIndex.value]);
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
    }
};

// --- METHODS ---
const selectCliente = (cliente) => {
    clienteSeleccionado.value = cliente;
    busquedaCliente.value = cliente.razon_social;
    showClienteResults.value = false;
    selectedIndex.value = 0;
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
    newItem.value.precio = price;
    newItem.value.cantidad = 1;
    
    // Reset discounts
    newItem.value.descuento_porcentaje = 0;
    newItem.value.descuento_valor = 0;
    
    newItem.value.total = price;
    showProductResults.value = false;
};

// --- INLINE ROW DISCOUNT HANDLERS ---
const updateRowDescPct = () => {
    const gross = newItem.value.cantidad * newItem.value.precio;
    const pct = newItem.value.descuento_porcentaje;
    newItem.value.descuento_valor = (gross * pct) / 100;
    updateRowTotal();
};

const updateRowDescVal = () => {
    const gross = newItem.value.cantidad * newItem.value.precio;
    const val = newItem.value.descuento_valor;
    if (gross > 0) {
        newItem.value.descuento_porcentaje = (val / gross) * 100;
    } else {
        newItem.value.descuento_porcentaje = 0;
    }
    updateRowTotal();
};

const updateRowTotal = () => {
    const gross = Number(newItem.value.cantidad) * Number(newItem.value.precio);
    const desc = Number(newItem.value.descuento_valor || 0);
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
const updateGlobalDescPct = () => {
    const base = subtotal.value;
    const pct = descuentoGlobalPorcentaje.value;
    descuentoGlobalValor.value = (base * pct) / 100;
};

const updateGlobalDescVal = () => {
    const base = subtotal.value;
    const val = descuentoGlobalValor.value;
    if (base > 0) {
        descuentoGlobalPorcentaje.value = (val / base) * 100;
    } else {
        descuentoGlobalPorcentaje.value = 0;
    }
};


const commitRow = () => {
    if (!newItem.value.producto_obj && !newItem.value.descripcion) return;

    items.value.unshift({ 
        ...newItem.value,
        id: newItem.value.producto_obj?.id || Date.now(),
        cantidad: Number(newItem.value.cantidad),
        precio: Number(newItem.value.precio),
        descuento_porcentaje: Number(newItem.value.descuento_porcentaje || 0),
        descuento_valor: Number(newItem.value.descuento_valor || 0),
        total: Number(newItem.value.total)
     });

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
    setTimeout(() => inputSkuRef.value?.focus(), 50);
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


