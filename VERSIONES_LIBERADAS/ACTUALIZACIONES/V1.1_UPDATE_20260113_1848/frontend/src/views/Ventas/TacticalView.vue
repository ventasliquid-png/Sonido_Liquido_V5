<template>
    <div 
        class="flex flex-col h-full font-sans transition-colors duration-500 ease-in-out font-mono"
        :class="bgThemeClass"
        @click="handleBackgroundClick"
    >
        
        <!-- === ZONA A: CABECERA (CONTEXTO) === -->
        <header class="flex flex-col px-4 py-3 border-b shrink-0 z-30 shadow-sm"
            :class="headerThemeClass"
        >
            <div class="flex items-start justify-between gap-4">
                
                <!-- A1. IDENTIDAD PEDIDO -->
                <div class="flex flex-col gap-1 w-32 shrink-0">
                    <div class="text-[10px] uppercase opacity-70 font-bold tracking-widest">PEDIDO #</div>
                    <div class="text-xl font-bold leading-none tracking-tighter">0001-000045</div>
                    <input type="date" class="bg-transparent text-xs opacity-80 focus:outline-none cursor-pointer mt-1" v-model="form.fecha">
                </div>

                <!-- A2. CLIENTE (INPUT CONTEXTUAL) -->
                <div class="flex-1 relative group">
                    <label class="block text-[10px] uppercase font-bold opacity-60 mb-1 tracking-wider cursor-pointer hover:text-white transition-colors" @click="focusClient">
                        Cliente (F2)
                    </label>
                    <div class="relative">
                        <input 
                            ref="clientInput"
                            type="text" 
                            class="w-full text-lg bg-black/20 border-b-2 border-white/10 focus:border-white/50 rounded-t px-3 py-1 outline-none placeholder-white/20 transition-all font-mono"
                            :class="{'bg-black/40 border-white/80': focusedZone === 'CLIENT'}"
                            placeholder="Buscar Cliente / Razón Social..."
                            v-model="clientQuery"
                            @focus="focusedZone = 'CLIENT'"
                        >
                        <!-- RESULTADOS CLIENTE -->
                        <div v-if="filteredClients.length && focusedZone === 'CLIENT' && clientQuery" 
                             class="absolute top-full left-0 w-full bg-slate-800 text-slate-200 shadow-xl rounded-b z-50 max-h-64 overflow-y-auto border border-slate-600">
                             <div 
                                v-for="c in filteredClients" :key="c.id"
                                class="px-4 py-2 border-b border-slate-700 hover:bg-slate-700 cursor-pointer flex justify-between"
                                @mousedown="selectClient(c)"
                             >
                                <span>{{ c.razon_social }}</span>
                                <span class="text-xs opacity-50 font-mono">{{ c.cuit }}</span>
                             </div>
                        </div>
                    </div>
                </div>

                <!-- A3. ORDEN DE COMPRA & TIPO -->
                <div class="flex flex-col gap-2 w-48 shrink-0 items-end">
                    <div class="flex items-center gap-2 bg-black/20 rounded p-1">
                        <button 
                            class="px-3 py-1 rounded text-[10px] font-bold uppercase transition-all"
                            :class="form.tipo === 'PEDIDO' ? 'bg-emerald-500 text-white shadow-lg' : 'text-white/40 hover:text-white'"
                            @click="form.tipo = 'PEDIDO'"
                        >
                            Pedido
                        </button>
                        <button 
                            class="px-3 py-1 rounded text-[10px] font-bold uppercase transition-all"
                            :class="form.tipo === 'PRESUPUESTO' ? 'bg-purple-500 text-white shadow-lg' : 'text-white/40 hover:text-white'"
                            @click="form.tipo = 'PRESUPUESTO'"
                        >
                            Presup.
                        </button>
                    </div>
                    <input 
                        type="text" 
                        class="w-full bg-black/10 border-b border-white/10 text-right text-xs px-2 py-1 outline-none focus:bg-black/20 placeholder-white/30 rounded"
                        placeholder="O.C. Cliente (Opcional)"
                        v-model="form.oc"
                    >
                </div>

            </div>
        </header>




        <!-- === ZONA B: CUERPO (GRILLA) === -->
        <main class="flex-1 relative flex flex-col overflow-hidden">
            
            <!-- ENCABEZADOS TABLA -->
            <div class="flex px-4 py-2 text-[10px] font-bold uppercase tracking-widest opacity-60 border-b border-black/10 shrink-0">
                <div class="w-12 text-center">#</div>
                <div class="w-32">SKU</div>
                <div class="flex-1">Descripción</div>
                <div class="w-20 text-center">Cant.</div>
                <div class="w-16 text-center">Unid.</div>
                <div class="w-32 text-right">Unitario</div>
                <div class="w-32 text-right">Subtotal</div>
                <div class="w-8"></div>
            </div>

            <!-- SCROLLABLE ROWS -->
            <div class="flex-1 overflow-y-auto custom-scrollbar relative px-4 py-2 space-y-0.5">
                
                <!-- RENGLONES -->
                <div 
                    v-for="(item, index) in orderItems" 
                    :key="index"
                    class="flex items-center py-1.5 border-b border-black/5 hover:bg-black/5 group transition-colors text-sm"
                >
                    <div class="w-12 text-center opacity-50 text-xs">{{ index + 1 }}</div>
                    <div class="w-32 font-bold opacity-80">{{ item.sku }}</div>
                    <div class="flex-1 font-medium">{{ item.nombre }}</div>
                    
                    <!-- EDITABLE CANTIDAD -->
                    <div class="w-20 text-center">
                        <input type="number" v-model.number="item.cantidad" class="w-16 text-center bg-black/5 rounded outline-none focus:bg-white/20 focus:font-bold">
                    </div>
                    
                    <div class="w-16 text-center text-xs opacity-60">{{ item.unidad }}</div>
                    
                    <!-- EDITABLE PRECIO -->
                    <div class="w-32 text-right font-mono">
                        <input type="number" v-model.number="item.precio" class="w-24 text-right bg-transparent outline-none focus:bg-white/20 rounded px-1">
                    </div>
                    
                    <div class="w-32 text-right font-bold font-mono">{{ formatCurrency(item.cantidad * item.precio) }}</div>
                    
                    <div class="w-8 text-center opacity-0 group-hover:opacity-100 cursor-pointer text-red-400 hover:text-red-600" @click="removeItem(index)">
                        <i class="fa-solid fa-times"></i>
                    </div>
                </div>

                <!-- INPUT LINE (SIEMPRE AL FINAL) -->
                <div 
                    class="flex items-center py-2 mt-2 bg-black/5 border border-black/10 rounded px-2"
                    :class="{'ring-2 ring-white/50 bg-black/10': focusedZone === 'PRODUCT'}"
                    @click.stop
                >
                    <div class="w-12 text-center text-xs opacity-40">+</div>
                    <div class="flex-1 relative">
                        <input 
                            ref="productInput"
                            type="text" 
                            class="w-full bg-transparent outline-none placeholder-black/30 font-bold"
                            :placeholder="productPlaceholder"
                            v-model="productQuery"
                            @focus="focusedZone = 'PRODUCT'"
                            @keydown.enter.prevent="tryAddProduct"
                            @keydown.down.prevent="navProdResults(1)"
                            @keydown.up.prevent="navProdResults(-1)"
                            @keydown.esc="productQuery = ''"
                        >
                        <!-- POPUP RESULTADOS PRODUCTO -->
                        <div v-if="filteredProducts.length && focusedZone === 'PRODUCT'" 
                             class="absolute bottom-full left-0 mb-2 w-full bg-slate-800 text-slate-200 shadow-2xl rounded border border-slate-600 z-50 overflow-hidden">
                            <div class="px-2 py-1 bg-slate-900 text-[10px] text-slate-400 uppercase tracking-wider flex justify-between">
                                <span>Coincidencias ({{ filteredProducts.length }})</span>
                                <span>ENTER para seleccionar</span>
                            </div>
                            <div class="max-h-60 overflow-y-auto">
                                <div 
                                    v-for="(p, idx) in filteredProducts" :key="p.id"
                                    class="px-3 py-2 border-b border-slate-700 cursor-pointer flex justify-between items-center transition-colors lg:gap-4"
                                    :class="[
                                        idx === selectedProdIdx ? 'bg-slate-700' : 'hover:bg-slate-700/50',
                                        // Semáforo Visual (Borde Izquierdo)
                                        p._audit?.color === 'bg-emerald-500' ? 'border-l-4 border-l-emerald-500' :
                                        p._audit?.color === 'bg-rose-500' ? 'border-l-4 border-l-rose-500' :
                                        p._audit?.color === 'bg-gray-500' ? 'border-l-4 border-l-gray-500 opacity-60' : 'border-l-4 border-l-slate-500'
                                    ]"
                                    @click="addProduct(p)"
                                >
                                    <div class="flex-1">
                                        <div class="font-bold text-sm flex items-center gap-2">
                                            {{ p.nombre }}
                                            <!-- Icono de Estado -->
                                            <i v-if="p._audit?.icon" :class="p._audit.icon" class="text-[10px] opacity-70"></i>
                                        </div>
                                        <div class="text-xs opacity-60 font-mono flex gap-2">
                                            <span>{{ p.sku }}</span>
                                            <span v-if="p._audit?.reasons?.length" class="text-rose-400 text-[10px]">
                                                ({{ p._audit.reasons.join(', ') }})
                                            </span>
                                        </div>
                                    </div>
                                    <div class="font-mono text-emerald-400 font-bold">
                                        {{ formatCurrency(p.precio_costo * 1.5) }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

        </main>


        <!-- === ZONA C: PIE (LIQUIDACIÓN) === -->
        <footer class="bg-slate-900 border-t border-slate-700 text-slate-300 px-6 py-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)] z-40 relative">
            
            <!-- OVERRIDE LOGISTICA -->
            <div class="absolute -top-3 left-6">
                <div class="bg-slate-800 border border-slate-600 text-[10px] px-3 py-1 rounded-full shadow cursor-pointer hover:bg-slate-700 flex items-center gap-2">
                    <i class="fa-solid fa-truck text-emerald-500"></i>
                    <span>Logística: <b>{{ selectedClient?.transporte_nombre || 'Retiro en Local' }}</b></span>
                    <i class="fa-solid fa-chevron-down opacity-50"></i>
                </div>
            </div>

            <div class="flex items-end justify-between">
                
                <!-- COMENTARIOS / ACCIONES -->
                <div class="w-1/3 flex flex-col gap-2">
                    <textarea 
                        class="w-full h-16 bg-slate-800 border border-slate-700 rounded p-2 text-xs outline-none focus:border-slate-500 resize-none placeholder-slate-600"
                        placeholder="Comentarios internos, notas de entrega, instrucciones especiales..."
                    ></textarea>
                </div>

                <!-- TOTALES -->
                <div class="flex gap-8 items-end">
                    <div class="text-right space-y-1">
                        <div class="text-xs text-slate-500 uppercase font-bold tracking-wider">Subtotal Neto</div>
                        <div class="font-mono text-slate-300">{{ formatCurrency(totals.neto) }}</div>
                    </div>
                    
                    <div class="text-right space-y-1">
                        <div class="text-xs text-slate-500 uppercase font-bold tracking-wider">IVA (21%)</div>
                        <div class="font-mono text-slate-300">{{ formatCurrency(totals.iva) }}</div>
                    </div>

                    <div class="text-right pl-6 border-l border-slate-700">
                        <div class="text-xs text-emerald-500 uppercase font-bold tracking-wider mb-1">Total Final</div>
                        <div class="text-3xl font-bold font-mono text-white leading-none tracking-tight">
                            {{ formatCurrency(totals.final) }}
                        </div>
                    </div>
                </div>

                <!-- BOTON PROCESAR -->
                <button class="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-3 rounded shadow-lg font-bold tracking-wider flex items-center gap-2 transition-all transform hover:scale-105 ml-6">
                    <span>PROCESAR</span>
                    <i class="fa-solid fa-check"></i>
                </button>

            </div>
        </footer>

    </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useClientesStore } from '@/stores/clientes';
import { useProductosStore } from '@/stores/productos';
import { useAuditSemaphore } from '@/composables/useAuditSemaphore';

// STORES
const clientesStore = useClientesStore();
const productosStore = useProductosStore(); 
const { evaluateProducto } = useAuditSemaphore();

// STATE REFS
const focusedZone = ref('CLIENT'); // 'CLIENT' | 'PRODUCT'
const form = ref({
    fecha: new Date().toISOString().slice(0, 10),
    tipo: 'PEDIDO', // 'PEDIDO' | 'PRESUPUESTO'
    oc: ''
});

const clientQuery = ref('');
const productQuery = ref('');
const selectedClient = ref(null);
const orderItems = ref([]);
const selectedProdIdx = ref(0);

// REFS DOM
const clientInput = ref(null);
const productInput = ref(null);

// --- THEME LOGIC ---
const bgThemeClass = computed(() => {
    // Fondos MUY suaves según tipo
    if (form.value.tipo === 'PEDIDO') return 'bg-[#ecfdf5] text-slate-800'; // Verde muy suave (emerald-50)
    if (form.value.tipo === 'PRESUPUESTO') return 'bg-[#faf5ff] text-slate-800'; // Lila muy suave (purple-50)
    return 'bg-white text-slate-800';
});

const headerThemeClass = computed(() => {
    if (form.value.tipo === 'PEDIDO') return 'bg-[#10b981] text-white border-emerald-600';
    if (form.value.tipo === 'PRESUPUESTO') return 'bg-[#a855f7] text-white border-purple-600';
    return 'bg-slate-200';
});


// --- FILTER LOGIC ---
const filteredClients = computed(() => {
    if (clientQuery.value.length < 2) return [];
    const q = clientQuery.value.toLowerCase();
    return clientesStore.clientes.filter(c => 
        c.razon_social?.toLowerCase().includes(q) || c.cuit?.includes(q)
    ).slice(0, 10);
});

// Computed Products (Grid Search) + Default Base
const productPlaceholder = computed(() => {
    const count = productosStore.productos.length;
    return count > 0 ? `Agregar Producto (F3)... [${count} Disp.]` : 'Cargando Productos...';
});

const filteredProducts = computed(() => {
    const q = productQuery.value.toLowerCase();
    
    // Si no hay query, mostrar los primeros 20 para que se vea que "hay base"
    if (!q) {
         return productosStore.productos.slice(0, 20);
    }

    return productosStore.productos
        .filter(p => (p.nombre && p.nombre.toLowerCase().includes(q)) || (p.sku && p.sku.toLowerCase().includes(q)))
        .slice(0, 50);
});

const totals = computed(() => {
    const neto = orderItems.value.reduce((sum, item) => sum + (item.cantidad * item.precio), 0);
    const iva = form.value.tipo === 'PEDIDO' ? neto * 0.21 : 0; // Simple logic for now
    return {
        neto,
        iva,
        final: neto + iva
    };
});

// --- ACTIONS ---
const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(val);
};

const focusClient = () => {
    focusedZone.value = 'CLIENT';
    clientInput.value?.focus();
};

const selectClient = (client) => {
    selectedClient.value = client;
    clientQuery.value = client.razon_social;
    // Auto-jump to product
    focusedZone.value = 'PRODUCT';
    nextTick(() => productInput.value?.focus());
};

const addProduct = (product) => {
    orderItems.value.push({
        id: product.id,
        sku: product.sku || 'SKU-000',
        nombre: product.nombre,
        cantidad: 1,
        unidad: 'UN',
        precio: parseFloat(product.precio_costo) * 1.5 || 1000 // Mock Formula
    });
    productQuery.value = '';
    selectedProdIdx.value = 0;
    // Keep focus on input for rapid fire
    nextTick(() => productInput.value?.focus());
};

const tryAddProduct = () => {
    if (filteredProducts.value.length > 0) {
        addProduct(filteredProducts.value[selectedProdIdx.value]);
    }
};

const removeItem = (index) => {
    orderItems.value.splice(index, 1);
};

const navProdResults = (delta) => {
    const max = filteredProducts.value.length;
    if (max === 0) return;
    const newIdx = selectedProdIdx.value + delta;
    if (newIdx >= 0 && newIdx < max) selectedProdIdx.value = newIdx;
};

// --- SHORTCUTS ---
const handleKeydown = (e) => {
    if (e.key === 'F2') {
        e.preventDefault();
        focusClient();
    }
    if (e.key === 'F3') {
        e.preventDefault();
        focusedZone.value = 'PRODUCT';
        productInput.value?.focus();
    }
};

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
    // Init Store (Mock or real)
    if (clientesStore.clientes.length === 0) clientesStore.fetchClientes();
    if (productosStore.productos.length === 0) productosStore.fetchProductos();
});

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.2); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.4); }
</style>
