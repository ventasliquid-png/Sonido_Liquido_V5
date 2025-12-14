<template>
    <div class="flex flex-col h-full font-sans bg-[#0b211f] text-emerald-50 transition-colors duration-500 ease-in-out">
        
        <!-- === ZONA A: CABECERA (CONTEXTO) === -->
        <header 
            class="flex flex-col px-4 py-3 border-b shrink-0 z-30 shadow-lg transition-colors"
            :class="headerThemeClass"
        >
            <div class="flex items-start justify-between gap-4">
                
                <!-- A1. IDENTIDAD PEDIDO -->
                <div class="flex flex-col gap-1 w-32 shrink-0">
                    <div class="text-[10px] uppercase opacity-70 font-bold tracking-widest">DOCUMENTO #</div>
                    <div class="text-xl font-bold leading-none tracking-tighter opacity-90">
                        {{ form.numero_manual || sugeridoId || 'NUEVO' }}
                    </div>
                    <input 
                        type="date" 
                        class="bg-transparent text-xs opacity-80 focus:outline-none cursor-pointer mt-1 font-mono font-bold" 
                        v-model="form.fecha"
                    >
                </div>

                <!-- A2. CLIENTE (INPUT CONTEXTUAL) -->
                <div class="flex-1 relative group">
                    <label 
                        class="block text-[10px] uppercase font-bold opacity-60 mb-1 tracking-wider cursor-pointer hover:opacity-100 transition-opacity flex justify-between" 
                        @click="focusClient"
                    >
                        <span>Cliente (F2)</span>
                        <span 
                            v-if="clienteStatus" 
                            :class="clienteStatus.color"
                            :title="clienteStatus.title"
                            class="cursor-help"
                            @click.stop="clienteStatus.missing.length > 0 ? showMissingFieldsAlert(clienteStatus.missing) : null"
                        >
                            ● {{ clienteStatus.text }}
                        </span>
                    </label>
                    
                    <div class="relative">
                        <input 
                            ref="clientInput"
                            type="text" 
                            class="w-full text-lg bg-black/20 border-b-2 border-emerald-900/30 focus:border-emerald-500 rounded-t px-3 py-1 outline-none placeholder-emerald-800/50 transition-all font-mono text-emerald-100"
                            :class="{'bg-[#0d2623] border-emerald-500 shadow-lg': focusedZone === 'CLIENT'}"
                            placeholder="Buscar Cliente / Razón Social (F4 para Nuevo)..."
                            v-model="clientQuery"
                            @focus="focusedZone = 'CLIENT'"
                            @keydown="handleClientKeydown"
                            @contextmenu.prevent="handleInputContextMenu"
                        >
                        <!-- RESULTADOS CLIENTE -->
                        <!-- RESULTADOS CLIENTE -->
                        <div v-if="showClientResults" 
                             class="absolute top-full left-0 w-full bg-[#0d2623] text-emerald-100 shadow-xl rounded-b z-50 max-h-64 overflow-y-auto border border-emerald-900">
                             <div 
                                v-for="(c, idx) in filteredClients" :key="c.id"
                                class="px-4 py-2 border-b border-emerald-900/30 hover:bg-emerald-900/50 cursor-pointer flex justify-between items-center group relative select-none"
                                :class="{'bg-emerald-900/50': idx === selectedClientIdx}"
                                @mousedown.left="selectClient(c)"
                                @contextmenu.prevent="openClientContextMenu($event, c)"
                             >
                                <div>
                                    <span class="font-bold text-sm block" :class="!c.activo ? 'line-through text-slate-500' : 'text-emerald-100'">{{ c.razon_social }}</span>
                                    <span class="text-xs opacity-50 font-mono flex items-center gap-2 text-emerald-400">
                                        {{ c.cuit }}
                                        <span v-if="!c.activo" class="bg-red-900 text-red-100 px-1 rounded text-[9px] uppercase font-bold">INACTIVO</span>
                                    </span>
                                </div>
                                <div class="flex items-center gap-2">
                                     <div v-if="c.domicilios?.length > 1" class="text-[10px] bg-amber-900/50 text-amber-500 px-2 py-0.5 rounded-full border border-amber-900">
                                        Multi-Sede
                                    </div>
                                    <i class="fas fa-ellipsis-v text-emerald-800 group-hover:text-emerald-500 px-2"></i>
                                </div>
                             </div>
                             
                             <!-- Empty State / Create New -->
                             <div v-if="filteredClients.length === 0" class="p-4 text-center text-xs opacity-50 italic">
                                 <p>No hay coincidencias.</p>
                                 <p class="font-bold cursor-pointer text-blue-500 hover:underline mt-1" @mousedown="openInspectorNew">
                                     (F4) Crear Nuevo Cliente
                                 </p>
                             </div>
                        </div>
                    </div>
                </div>

                <!-- A3. ORDEN DE COMPRA & TIPO -->
                <div class="flex flex-col gap-2 w-48 shrink-0 items-end">
                    <div class="flex items-center gap-1 bg-black/5 rounded p-1">
                        <button 
                            v-for="type in ['PEDIDO', 'PRESUPUESTO']" 
                            :key="type"
                            class="px-3 py-1 rounded text-[10px] font-bold uppercase transition-all"
                            :class="form.tipo === type ? activeTypeClass(type) : 'text-slate-400 hover:text-slate-600'"
                            @click="form.tipo = type"
                            tabindex="-1"
                        >
                            {{ type.slice(0,3) }}.
                        </button>
                    </div>
                    <input 
                        type="text" 
                        class="w-full bg-transparent border-b border-black/10 text-right text-xs px-2 py-1 outline-none focus:border-black/30 placeholder-black/20 font-mono"
                        placeholder="O.C. Cliente (Opcional)"
                        v-model="form.oc"
                    >
                </div>

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
                <div class="w-24 text-right">Unitario</div>
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
                        <input 
                            type="number" 
                            v-model.number="item.cantidad" 
                            class="w-16 text-center bg-transparent hover:bg-white/10 focus:bg-black/20 rounded outline-none focus:ring-1 focus:ring-emerald-500 font-mono font-bold text-white"
                            min="0"
                            @focus="focusedRow = index"
                        >
                    </div>
                    
                    <div class="w-12 text-center text-[10px] text-emerald-600 uppercase select-none">{{ item.unidad || 'UN' }}</div>
                    
                    <div class="w-24 text-right font-mono">
                        <input 
                            type="number" 
                            v-model.number="item.precio_unitario" 
                            class="w-20 text-right bg-transparent hover:bg-white/10 focus:bg-black/20 outline-none focus:ring-1 focus:ring-emerald-500 rounded px-1 text-emerald-300 text-xs"
                            step="0.01"
                            @focus="focusedRow = index"
                        >
                    </div>
                    
                    <div class="w-24 text-right font-bold font-mono text-emerald-100 text-sm">
                        {{ formatCurrency(item.cantidad * item.precio_unitario) }}
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
                    <div class="w-10 text-center text-xs text-emerald-800 font-bold">+</div>
                    <div class="flex-1 relative">
                        <input 
                            ref="productInput"
                            type="text" 
                            class="w-full bg-transparent outline-none placeholder-emerald-800 font-bold text-emerald-100"
                            :placeholder="productPlaceholder"
                            v-model="productQuery"
                            @focus="focusedZone = 'PRODUCT'"
                            @keydown="handleProductKeydown"
                        >
                        <!-- POPUP RESULTADOS PRODUCTO -->
                        <div v-if="showProductResults" 
                             class="absolute bottom-full left-0 mb-3 w-full bg-[#0d2623] text-emerald-100 shadow-2xl rounded-lg border border-emerald-900 z-50 overflow-hidden">
                            <div class="px-3 py-1.5 bg-black/30 backdrop-blur text-[10px] text-emerald-400 uppercase tracking-wider flex justify-between border-b border-emerald-900/30">
                                <span>Coincidencias ({{ filteredProducts.length }}) <span class="text-emerald-500 ml-2">Use Flechas y Enter</span></span>
                                <span class="text-xs font-bold text-amber-400">ESC para cerrar</span>
                            </div>
                            <div class="max-h-80 overflow-y-auto">
                                <div 
                                    v-for="(p, idx) in filteredProducts" :key="p.id"
                                    class="px-4 py-2 border-b border-emerald-900/10 cursor-pointer flex justify-between items-center transition-colors gap-4 group"
                                    :class="idx === selectedProdIdx ? 'bg-emerald-600 text-white' : 'hover:bg-white/5'"
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
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- === ZONA C: PIE (LIQUIDACIÓN) === -->
        <footer 
            class=" relative z-40 px-6 py-4 border-t border-emerald-900/30 shadow-[0_-4px_20px_rgba(0,0,0,0.2)] transition-colors"
            :class="form.tipo === 'PEDIDO' ? 'bg-[#061816]' : 'bg-[#0f0a1e]'"
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
                        class="w-full h-12 bg-white border border-slate-200 rounded-lg p-2 text-xs outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 resize-none placeholder-slate-400 transition-all shadow-inner"
                        placeholder="Notas internas, instrucciones de entrega o comentarios del pedido..."
                        v-model="form.nota"
                    ></textarea>
                </div>

                <!-- TOTALES -->
                <div class="flex gap-8 items-end pb-1">
                    <div class="text-right space-y-0.5">
                        <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Subtotal</div>
                        <div class="font-mono text-slate-500 text-sm">{{ formatCurrency(totals.neto) }}</div>
                    </div>
                    
                    <div class="text-right space-y-0.5" v-if="totals.iva > 0">
                        <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">IVA (21%)</div>
                        <div class="font-mono text-slate-500 text-sm">{{ formatCurrency(totals.iva) }}</div>
                    </div>

                    <div class="text-right pl-6 border-l border-slate-200">
                        <div class="text-[10px] uppercase font-bold tracking-wider mb-0.5" :class="form.tipo === 'PEDIDO' ? 'text-emerald-600' : 'text-purple-600'">Total Final</div>
                        <div class="text-3xl font-bold font-mono leading-none tracking-tight text-slate-800">
                            {{ formatCurrency(totals.final) }}
                        </div>
                    </div>
                </div>

                <!-- BOTON PROCESAR -->
                <button 
                    class="h-12 px-6 rounded-lg shadow-lg font-bold tracking-wider flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95 text-white ml-auto"
                    :class="form.tipo === 'PEDIDO' ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-200' : 'bg-purple-600 hover:bg-purple-500 shadow-purple-200'"
                    @click="handleSubmit"
                >
                    <span v-if="isSubmitting" class="animate-spin"><i class="fa-solid fa-circle-notch"></i></span>
                    <span v-else class="flex items-center gap-2">
                        <span>GUARDAR</span>
                        <span class="bg-white/20 px-1.5 py-0.5 rounded text-[10px] font-mono opacity-80">F10</span>
                    </span>
                </button>
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
                <div class="w-full max-w-2xl h-full shadow-2xl overflow-y-auto transform transition-transform duration-300">
                    <ClienteInspector 
                        :modelValue="clienteForInspector"
                        :isNew="isInspectorNew"
                        @close="closeInspector"
                        @save="handleInspectorSave"
                        @delete="handleInspectorDelete"
                        @switch-client="switchToClient"
                    />
                </div>
            </div>
        </Teleport>

    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useClientesStore } from '@/stores/clientes';
import { useProductosStore } from '@/stores/productos';
import { usePedidosStore } from '@/stores/pedidos';
import apiClient from '@/services/api';
import ContextMenu from '@/components/common/ContextMenu.vue';
import ClientHistoryPopover from '@/components/common/ClientHistoryPopover.vue';
import ClienteInspector from '../Hawe/components/ClienteInspector.vue';

// STORES
const clientesStore = useClientesStore();
const productosStore = useProductosStore(); 
const pedidosStore = usePedidosStore();

// UI STATE
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

// HISTORY POPOVER
const historyPopover = ref({
    show: false,
    x: 0,
    y: 0,
    orders: []
});

const isSubmitting = ref(false);
const draftId = ref(null);

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

// DATA STATE
const form = ref({
    cliente_id: null,
    fecha: new Date().toISOString().split('T')[0],
    nota: '',
    tipo: 'PEDIDO', // PEDIDO | COTIZACION
    numero_manual: '' // Visual suggestion from backend
});

const sugeridoId = ref(0); // To store valid next ID

const selectedClient = ref(null);
const items = ref([]);


// --- COMPUTED STYLES ---

const headerThemeClass = computed(() => {
    if (form.value.tipo === 'COTIZACION') return 'bg-[#1a0b1e] border-purple-900 text-purple-400'; // Lilac/Purple Theme
    if (form.value.tipo === 'PEDIDO') return 'bg-[#061816] border-emerald-900 text-emerald-400';
    return 'bg-[#0f0a1e] border-purple-900 text-purple-400'; // Default?
});

const mainThemeClass = computed(() => {
    if (form.value.tipo === 'COTIZACION') return 'bg-[#2d1b36]'; // Lilac bg
    return 'bg-[#0b211f]'; // Green bg
});

const activeTypeClass = (type) => {
    if (type === 'PEDIDO') return 'bg-emerald-500 text-white shadow-sm';
    return 'bg-purple-500 text-white shadow-sm';
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
            const name = normalizeText(c.razon_social);
            const cuit = c.cuit || "";
            return name.includes(q) || cuit.includes(q);
        })
        .sort((a, b) => {
            // Sort: Actives first, then Exact Match
            if (a.activo && !b.activo) return -1;
            if (!a.activo && b.activo) return 1;
            
            const nameA = normalizeText(a.razon_social);
            const nameB = normalizeText(b.razon_social);

            if (nameA.startsWith(q) && !nameB.startsWith(q)) return -1;
            if (!nameA.startsWith(q) && nameB.startsWith(q)) return 1;
            return 0;
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
        .slice(0, 50);
});

const showProductResults = computed(() => {
    return focusedZone.value === 'PRODUCT' && filteredProducts.value.length > 0;
});

const productPlaceholder = computed(() => {
    const count = productosStore.productos.length;
    return count > 0 ? `+ Agregar Producto (F3 para buscar en ${count} ítems)` : 'Cargando catálogo...';
});

// Totals
const totals = computed(() => {
    const neto = items.value.reduce((sum, item) => sum + (item.cantidad * item.precio_unitario), 0);
    const iva = form.value.tipo === 'PEDIDO' ? neto * 0.21 : 0;
    return { neto, iva, final: neto + iva };
});


// --- METHODS ---

const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(val);
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

onMounted(() => {
    focusedZone.value = 'CLIENT';
    setTimeout(() => clientInput.value?.focus(), 100);
    fetchNextId();
});

onUnmounted(() => {
    // cleanup
});

const createEmptyRow = () => ({
    _ui_id: Date.now() + Math.random(),
    sku: '',
    nombre: '',
    cantidad: 1,
    precio_unitario: 0,
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
    } else if (e.key === 'Escape') {
        showClientResults.value = false;
        clientInput.value?.blur();
    } else if (e.key === 'F4') {
        e.preventDefault();
        openInspectorNew();
    } else {
        showClientResults.value = true;
        selectedClientIdx.value = 0; 
    }
};

const selectClient = (client) => {
    selectedClient.value = client;
    clientQuery.value = client.razon_social;
    showClientResults.value = false;
    focusProductSearch();
};

// --- INSPECTOR LOGIC ---

const openInspectorNew = () => {
    clienteForInspector.value = null;
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
    }
};

const addProduct = (p) => {
    items.value.push({
        _ui_id: Date.now() + Math.random(), 
        id: p.id,
        sku: p.sku || 'N/A',
        nombre: p.nombre,
        unidad: p.unidad_venta || 'UN',
        cantidad: 1,
        precio_unitario: p.precio_sugerido || 0 
    });
    
    productQuery.value = '';
    selectedProdIdx.value = 0;
    
    nextTick(() => {
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
    if (items.value.length === 0) return alert('El pedido está vacío.');
    
    isSubmitting.value = true;
    try {
        const payload = {
            cliente_id: selectedClient.value.id,
            fecha: form.value.fecha,
            nota: form.value.nota,
            oc: form.value.oc,
            items: items.value.map(i => ({
                producto_id: i.id,
                cantidad: i.cantidad,
                precio_unitario: i.precio_unitario
            }))
        };
        
        await pedidosStore.createPedidoTactico(payload);
        
        if(confirm('Pedido generado con éxito. ¿Limpiar?')) {
            items.value = [];
            form.value.nota = '';
            form.value.oc = '';
            // Reset client? Depends on user workflow. Usually yes.
            selectedClient.value = null;
            clientQuery.value = '';
            focusClient();
        }
    } catch (e) {
        alert('Error al guardar: ' + e.message);
    } finally {
        isSubmitting.value = false;
    }
};


// Lifecycle
const handleGlobalKeys = (e) => {
    if (e.key === 'F2') {
        e.preventDefault();
        focusClient();
    } else if (e.key === 'F3') {
        e.preventDefault();
        focusProductSearch();
    } else if (e.key === 'F10') {
        e.preventDefault();
        if (!showInspector.value) handleSubmit(); // Don't submit grid if inspector open
    } else if (e.key === 'F4') {
        if (focusedZone.value === 'CLIENT') {
            e.preventDefault();
            openInspectorNew();
        }
    }
};

onMounted(async () => {
    window.addEventListener('keydown', handleGlobalKeys);
    
    // Load Catalogs
    if (clientesStore.clientes.length === 0) await clientesStore.fetchClientes();
    if (productosStore.productos.length === 0) await productosStore.fetchProductos();
    
    focusClient();
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeys);
});

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.5); border-radius: 4px; border: 2px solid transparent; background-clip: content-box; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background-color: rgba(148, 163, 184, 0.8); }
</style>
