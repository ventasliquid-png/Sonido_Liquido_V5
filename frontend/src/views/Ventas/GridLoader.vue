<template>
    <div class="flex flex-col h-full font-sans bg-[#0b211f] text-emerald-50 transition-colors duration-500 ease-in-out">
        
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

                <!-- RESULTADOS CLIENTE -->
                <div v-if="showClientResults" 
                        class="absolute top-full left-0 w-full bg-[#0d2623] text-emerald-100 shadow-xl rounded-b z-50 max-h-80 overflow-y-auto border border-emerald-900 border-t-0">
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
                        
                        <!-- Empty State / Create New -->
                        <div v-if="filteredClients.length === 0" class="p-2 text-center text-xs opacity-50 italic">
                            <p>No hay coincidencias.</p>
                            <p class="font-bold cursor-pointer text-blue-500 hover:underline mt-1" @mousedown="openInspectorNew">
                                (F4) Crear Nuevo Cliente
                            </p>
                        </div>
                </div>
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
            <div class="bg-[#1e293b] flex items-center px-2 gap-4 border-t border-slate-700">
                <!-- Logistica Dropdown Simulation -->
                <div class="flex items-center gap-1 flex-1 cursor-pointer hover:text-emerald-400 transition-colors" title="Cambiar Logística / Domicilio">
                    <i class="fa-solid fa-truck text-[10px] text-slate-500"></i>
                    <span class="font-bold truncate text-slate-300">
                        {{ selectedClient?.transporte_nombre || 'Retiro en Local' }}
                    </span>
                    <span class="text-[9px] text-slate-500 truncate ml-1">
                        ({{ selectedClient?.domicilio_entrega || 'Sin dirección de entrega' }})
                    </span>
                    <i class="fa-solid fa-caret-down text-[10px] text-slate-600 ml-auto"></i>
                </div>

                <div class="w-px h-3/4 bg-slate-700"></div>

                 <!-- Cond IVA -->
                <div class="flex items-center gap-1 shrink-0">
                    <span class="text-[9px] font-bold text-slate-500">IVA:</span>
                    <span class="font-bold text-slate-300 truncate max-w-[100px]" :title="selectedClient?.condicion_iva_nombre">
                         {{ selectedClient?.condicion_iva_nombre || '-' }}
                    </span>
                </div>
            </div>

             <!-- B3. NOTA/OC (Bottom Right) -->
            <div class="bg-[#0f172a] border-t border-slate-800">
                 <input 
                    type="text" 
                    v-model="form.oc"
                    placeholder="O.C. / NOTA INTERNA..."
                    class="w-full h-full bg-transparent px-2 text-[10px] text-emerald-100 placeholder-slate-600 outline-none focus:bg-slate-800 transition-colors"
                >
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
            <!-- TOGGLE EXCEL -->
            <div class="absolute bottom-16 right-6 flex items-center gap-2 bg-[#061816]/90 backdrop-blur px-3 py-1 rounded-full border border-emerald-900/50 shadow text-[10px] text-emerald-400 select-none cursor-pointer" @click="downloadExcel = !downloadExcel">
                 <div class="w-2.5 h-2.5 rounded-sm border border-emerald-600 flex items-center justify-center transition-colors" :class="{'bg-emerald-600': downloadExcel}">
                     <i v-if="downloadExcel" class="fa-solid fa-check text-white text-[8px]"></i>
                 </div>
                 <span class="font-bold">Generar Comprobante (Excel)</span>
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
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useClientesStore } from '@/stores/clientes';
import { useProductosStore } from '@/stores/productos';
import { usePedidosStore } from '@/stores/pedidos';
import { useMaestrosStore } from '@/stores/maestros';
import apiClient from '@/services/api';
import ContextMenu from '@/components/common/ContextMenu.vue';
import ClientHistoryPopover from '@/components/common/ClientHistoryPopover.vue';
import ClienteInspector from '../Hawe/components/ClienteInspector.vue';
import SimpleAbmModal from '@/components/common/SimpleAbmModal.vue';

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
            if (!c.activo) return false;
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
    form.value.cliente_id = null;
    selectedClient.value = null;
    createEmptyRow(); // Reset UI
};

onMounted(async () => {
    focusedZone.value = 'CLIENT';
    
    // Restore Draft
    const saved = localStorage.getItem('tactical_draft');
    if (saved) {
        try {
            const draft = JSON.parse(saved);
            // Valid for 24 hours
            if (Date.now() - draft.timestamp < 24 * 60 * 60 * 1000) {
                if (draft.items?.length > 0 || draft.selectedClient) {
                    items.value = draft.items || [];
                    form.value = { ...form.value, ...draft.form }; // Merge safely
                    selectedClient.value = draft.selectedClient;
                    clientQuery.value = draft.selectedClient?.razon_social || '';
                }
            }
        } catch (e) {
            console.error("Error restoring draft", e);
        }
    }

    setTimeout(() => clientInput.value?.focus(), 100);
    
    // Parallel data loading
    Promise.all([
        clientesStore.fetchClientes(),
        productosStore.fetchProductos(),
        useMaestrosStore().fetchAll(), 
        fetchNextId()
    ]);
});

// Watch for changes to autosave
watch([items, () => form.value, selectedClient], () => {
    if (items.value.length > 0 || selectedClient.value) {
        autosaveDraft();
    }
}, { deep: true });

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
        
        await pedidosStore.createPedidoTactico(payload, downloadExcel.value);
        
        if(confirm('Pedido generado con éxito. ¿Limpiar?')) {
            clearDraft();
            // Reset client if needed, clearDraft does it mostly but selectedClient check logic might vary
            // clearDraft resets selectedClient too.
            focusClient();
        }
    } catch (e) {
        alert('Error al guardar: ' + e.message);
    } finally {
        isSubmitting.value = false;
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
