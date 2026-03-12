<template>
    <div ref="inspectorRef" class="h-full flex flex-col bg-[#021812] border-l border-emerald-900/30" :class="{ 'zen-active': isZenMode }" @contextmenu.prevent="handleGlobalContextMenu">
        <!-- Empty State -->
        <div v-if="!modelValue" class="flex flex-col items-center justify-center h-full text-white/30 p-6 text-center">
             <i class="fas fa-shopping-cart text-4xl mb-4 text-emerald-900/50"></i>
             <p class="text-sm">Seleccione un pedido<br>para ver sus detalles</p>
        </div>

        <!-- Order Details State -->
        <div v-else class="flex flex-col h-full w-[400px]"> <!-- Fixed width for consistency -->
            <!-- Header -->
            <div class="h-16 flex items-center justify-between px-6 border-b border-emerald-900/30 bg-[#052e1e]/50 backdrop-blur-sm shrink-0">
                <div class="flex flex-col">
                    <h2 class="font-outfit text-lg font-bold text-white tracking-wide">
                        Pedido <span class="text-emerald-400">#{{ modelValue.id }}</span>
                    </h2>
                    <span class="text-[10px] text-emerald-200/50 uppercase tracking-widest">{{ formatDate(modelValue.fecha) }}</span>
                </div>
                <div class="flex items-center">
                    <button 
                        @click="captureZen" 
                        class="h-8 w-8 rounded-full flex items-center justify-center text-emerald-400 hover:text-white hover:bg-white/10 transition-all mr-1 no-zen"
                        title="Copiar Presupuesto (Imagen)"
                    >
                        <i class="fas fa-camera"></i>
                    </button>
                    <button 
                        @click="handleClose" 
                        class="h-8 w-8 rounded-full flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all no-zen"
                        title="Cerrar (ESC)"
                    >
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-emerald-900/30 hover:scrollbar-thumb-emerald-900/50">
                
                <div 
                    class="bg-emerald-900/10 p-4 rounded-lg border border-emerald-900/20 relative group/client cursor-context-menu"
                    @contextmenu.prevent="handleClientRightClick"
                    title="Clic Derecho: Ver Ficha Cliente"
                >
                    <div v-if="!isEditingClient" class="flex items-center justify-between">
                         <div class="flex items-center gap-3">
                             <div class="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-900 to-green-900 flex items-center justify-center text-white font-bold text-sm border border-emerald-500/20 shrink-0">
                                {{ getInitials(modelValue.cliente?.razon_social) }}
                            </div>
                            <div>
                                 <h3 class="font-bold text-emerald-100 text-sm">{{ modelValue.cliente?.razon_social }}</h3>
                                 <p class="text-xs text-emerald-500/50">ID: {{ modelValue.cliente?.id }}</p>
                                 <p class="text-xs text-emerald-500/50">CUIT: {{ modelValue.cliente?.cuit || 'N/A' }}</p>
                                 <div class="flex items-center gap-1 mt-0.5">
                                    <span v-if="modelValue.cliente?.condicion_iva" class="text-[9px] px-1 bg-emerald-900/40 text-emerald-300 rounded border border-emerald-500/20 uppercase tracking-widest font-bold">
                                        {{ modelValue.cliente?.condicion_iva.nombre }}
                                    </span>
                                    <span v-if="modelValue.cliente?.segmento" class="text-[9px] px-1 bg-blue-900/40 text-blue-300 rounded border border-blue-500/20 uppercase tracking-widest font-bold">
                                        {{ modelValue.cliente?.segmento.nombre }}
                                    </span>
                                 </div>
                                 <p class="text-xs text-emerald-500/50 mt-1">{{ modelValue.cliente?.domicilio_fiscal_resumen || 'Sin dirección de entrega' }}</p>
                            </div>
                        </div>
                        <button 
                            @click="startEditingClient"
                            class="text-emerald-500/30 hover:text-emerald-400 transition-colors opacity-0 group-hover/client:opacity-100 no-zen"
                            title="Cambiar Cliente"
                        >
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                    </div>

                    <div v-else>
                         <label class="block text-[10px] uppercase tracking-wider font-bold text-emerald-500/70 mb-2">Cambiar Cliente</label>
                         <SmartSelect
                            :modelValue="tempClientId"
                            @update:modelValue="tempClientId = $event"
                            :options="clientOptions"
                            placeholder="Buscar cliente..."
                            :allowCreate="false"
                            canteraType="clientes"
                            @select-cantera="handleCanteraSelect"
                            class="mb-2"
                         />
                         <div class="flex justify-end gap-2 mt-2">
                             <button @click="cancelEditClient" class="text-xs text-white/50 hover:text-white">Cancelar</button>
                             <button @click="saveClientChange" class="text-xs bg-emerald-600 text-white px-2 py-1 rounded font-bold">Guardar</button>
                         </div>
                    </div>
                </div>

                <!-- Navigation Context Menu Helper (Invisible) -->
                <!-- We bind contextmenu directly to the card above -->
                <div v-show="false"></div>

                <!-- Tipo Comprobante Selector (ABX) -->
                <div class="mb-4 no-zen">
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-emerald-500/70 mb-1.5 ml-1">Estrategia Fiscal (ABX)</label>
                    <div class="flex items-center gap-1 bg-[#051f15] rounded-lg p-1.5 border border-emerald-900/30">
                        
                        <!-- FACTURA A -->
                        <!-- Visible: Always. Enabled: Only if Client allows A. Active: if Current Type is A or FISCAL (and resolved to A) -->
                        <button 
                            @click="setFiscalMode"
                            class="flex-1 py-2 rounded text-[10px] font-bold transition-all border flex items-center justify-center gap-1 relative"
                            :class="getFiscalButtonClass('A')"
                            :disabled="!canClientBeA"
                            :title="canClientBeA ? 'Factura A (Automático)' : 'Bloqueado: Cliente no admite A'"
                        >
                            <span class="font-mono text-xs">A</span>
                            <i v-if="!canClientBeA" class="fas fa-lock text-[8px] absolute top-1 right-1 opacity-50"></i>
                        </button>

                        <!-- FACTURA B -->
                        <button 
                            @click="setFiscalMode"
                            class="flex-1 py-2 rounded text-[10px] font-bold transition-all border flex items-center justify-center gap-1 relative"
                            :class="getFiscalButtonClass('B')"
                            :disabled="!canClientBeB"
                            :title="canClientBeB ? 'Factura B (Automático)' : 'Bloqueado: Cliente debe ser A'"
                        >
                            <span class="font-mono text-xs">B</span>
                             <i v-if="!canClientBeB" class="fas fa-lock text-[8px] absolute top-1 right-1 opacity-50"></i>
                        </button>

                        <!-- TICKET M (Hidden/Disabled for now unless relevant) -->
                        <!-- Keeping logic minimal -->

                        <div class="w-px h-4 bg-emerald-900/50 mx-1"></div>

                        <!-- X (NEGRO) -->
                        <button 
                            @click="updateTipo('X')"
                            class="flex-1 py-2 rounded text-[10px] font-bold transition-all border border-purple-900/0 flex items-center justify-center gap-1"
                            :class="modelValue.tipo_facturacion === 'X' ? 'bg-purple-600/80 text-white shadow-lg border-purple-400' : 'text-purple-500/50 hover:text-purple-300 hover:bg-purple-900/20'"
                            title="Presupuesto X (Sin IVA)"
                        >
                            <span class="font-mono text-xs">X</span>
                        </button>

                    </div>
                    <!-- Helper Text -->
                    <div v-if="clientCondition" class="mt-1 px-1">
                        <p class="text-[9px] text-emerald-500/40 uppercase tracking-widest text-right">
                            Condición: <strong class="text-emerald-400">{{ clientCondition }}</strong>
                        </p>
                    </div>
                </div>

                <!-- Status Selector -->
                <div class="group relative no-zen">
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-emerald-500/70 mb-1.5 ml-1">Estado del Flujo</label>
                    <div class="relative">
                        <select 
                            :value="modelValue.estado"
                            @change="handleStatusChange($event.target.value)"
                            class="w-full bg-[#051f15] text-white border border-emerald-900/30 rounded-lg px-4 py-2.5 focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400/50 transition-all appearance-none font-bold uppercase tracking-wide"
                            :class="getStatusColorClass(modelValue.estado)"
                        >
                            <option value="PRESUPUESTO" class="text-purple-600 font-bold bg-white">PRESUPUESTO (Cotización)</option>
                            <option value="INTERNO" class="text-cyan-600 font-bold bg-white">INTERNO (Manejo Propio)</option>
                            <option value="PENDIENTE" class="text-emerald-600 bg-white font-bold">PENDIENTE (Aprobado/En Curso)</option>
                            <option value="CUMPLIDO" class="text-yellow-600 bg-white font-bold">CUMPLIDO (Entregado)</option>
                            <option value="ANULADO" class="text-red-600 bg-white font-bold">ANULADO</option>
                        </select>
                        <i class="fas fa-chevron-down absolute right-4 top-1/2 -translate-y-1/2 text-white/30 pointer-events-none"></i>
                    </div>
                </div>

                <!-- Logistics Panel (MVP) -->
                <LogisticaPanel :modelValue="modelValue" />

                <!-- QUICK EDIT ITEMS BUTTON -->
                <div class="pt-2 no-zen">
                    <button 
                        @click="editInGrid"
                        class="w-full py-3 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500 text-emerald-400 rounded-lg font-bold text-xs uppercase tracking-widest transition-all flex items-center justify-center gap-2 group/edit"
                    >
                        <i class="fas fa-th group-hover/edit:scale-110 transition-transform"></i>
                        Editar Renglones en Grilla
                    </button>
                </div>

                <!-- Items List -->
                <div>
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-emerald-500/70 mb-2 ml-1">Items del Pedido ({{ modelValue.items.length }})</label>
                    <div class="space-y-2 max-h-[300px] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-emerald-900/30">
                        <div 
                            v-for="item in modelValue.items" 
                            :key="item.id"
                            class="flex justify-between items-start p-3 bg-emerald-900/5 rounded border border-emerald-900/10 group/item hover:bg-emerald-900/10 transition-colors cursor-context-menu"
                            @contextmenu.prevent="handleProductContextMenu($event, item)"
                            title="Clic Derecho: Ver Producto"
                        >
                            <div class="flex-1 pr-4">
                                <p class="text-xs text-white font-medium mb-1">{{ item.producto?.nombre || 'Producto' }}</p>
                                <div class="flex items-center gap-2">
                                     <span class="text-[10px] text-emerald-400 font-bold">{{ item.cantidad }}</span>
                                     <span class="text-[10px] text-white/40">x</span>
                                     <span class="text-[10px] text-white/60">{{ formatCurrency(item.precio_unitario) }}</span>
                                </div>
                            </div>
                            <div class="text-right flex items-center gap-3">
                                <p class="text-xs font-bold text-emerald-200">{{ formatCurrency(item.cantidad * item.precio_unitario) }}</p>
                                <button 
                                    @click.stop="handleProductContextMenu($event, item)"
                                    class="h-6 w-6 flex items-center justify-center rounded bg-emerald-900/40 text-emerald-400 hover:bg-emerald-800 hover:text-white transition-colors border border-emerald-500/20 no-zen"
                                    title="Más acciones"
                                >
                                    <i class="fas fa-ellipsis-v text-xs"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Nota (Editable) -->
                <div class="bg-yellow-500/5 border-l-2 border-yellow-500/30 p-3 rounded-r relative group/nota">
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-yellow-500/70 mb-1">Nota</label>
                    
                    <div v-if="!isEditingNote" class="flex justify-between items-start">
                         <p class="text-xs text-yellow-100/80 italic min-h-[1.5rem]">{{ modelValue.nota || 'Sin nota' }}</p>
                         <button 
                            @click="startEditingNote"
                            class="text-yellow-500/30 hover:text-yellow-400 opacity-0 group-hover/nota:opacity-100 transition-opacity no-zen"
                            title="Editar Nota"
                        >
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                    </div>

                    <div v-else>
                        <textarea 
                            v-model="tempNote"
                            class="w-full bg-[#051f15] text-yellow-100 border border-yellow-500/30 rounded p-2 text-xs italic focus:outline-none focus:border-yellow-500"
                            rows="3"
                        ></textarea>
                         <div class="flex justify-end gap-2 mt-2">
                             <button @click="cancelEditNote" class="text-xs text-white/50 hover:text-white">Cancelar</button>
                             <button @click="saveNote" class="text-xs bg-yellow-600/50 hover:bg-yellow-600 text-white px-2 py-1 rounded font-bold">Guardar</button>
                         </div>
                    </div>
                </div>

                <!-- O.C. (Editable) -->
                <div class="bg-blue-500/5 border-l-2 border-blue-500/30 p-3 rounded-r relative group/oc">
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-blue-500/70 mb-1">Orden de Compra (O.C.)</label>
                    
                    <div v-if="!isEditingOC" class="flex justify-between items-start">
                         <p class="text-xs text-blue-100/80 font-mono tracking-wide min-h-[1.5rem]">{{ modelValue.oc || '-' }}</p>
                         <button 
                            @click="startEditingOC"
                            class="text-blue-500/30 hover:text-blue-400 opacity-0 group-hover/oc:opacity-100 transition-opacity no-zen"
                            title="Editar O.C."
                        >
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                    </div>

                    <div v-else>
                        <input 
                            type="text"
                            v-model="tempOC"
                            class="w-full bg-[#051f15] text-blue-100 border border-blue-500/30 rounded p-2 text-xs font-mono font-bold focus:outline-none focus:border-blue-500"
                            placeholder="Nro Orden Compra..."
                        >
                         <div class="flex justify-end gap-2 mt-2">
                             <button @click="cancelEditOC" class="text-xs text-white/50 hover:text-white">Cancelar</button>
                             <button @click="saveOC" class="text-xs bg-blue-600/50 hover:bg-blue-600 text-white px-2 py-1 rounded font-bold">Guardar</button>
                         </div>
                    </div>
                </div>
            </div>

            <!-- Total Footer -->
            <div class="p-6 border-t border-emerald-900/30 bg-[#02110c] shrink-0 space-y-4">
                 <div class="flex items-center justify-between">
                    <span class="text-sm font-bold text-white/50 uppercase tracking-widest">Total Pedido</span>
                    <span class="text-2xl font-bold text-white font-mono">{{ formatCurrency(modelValue.total) }}</span>
                </div>
                
                <div class="flex gap-2 no-zen">
                    <button 
                        @click="emit('clone')"
                        class="px-4 py-3 bg-emerald-900/30 hover:bg-emerald-900/50 text-emerald-400 border border-emerald-500/20 rounded-lg font-bold transition-all text-xs uppercase"
                        title="Clonar este pedido"
                    >
                        <i class="fas fa-copy mr-1"></i> Clonar
                    </button>
                    
                    <button 
                        @click="handleClose"
                        class="flex-1 py-3 bg-gradient-to-r from-emerald-800 to-emerald-700 hover:from-emerald-700 hover:to-emerald-600 text-white rounded-lg font-bold shadow-lg shadow-black/20 hover:shadow-emerald-500/10 transition-all active:scale-[0.98] text-xs uppercase"
                        title="Cerrar / Aceptar (F10)"
                    >
                        <i class="fas fa-check mr-1"></i> Aceptar y Volver (F10)
                    </button>
                    <!-- "Volver" as explicit alias for Close, just in case user distinguishes them -->
                    <button 
                        @click="handleClose"
                        class="px-4 py-3 bg-white/5 hover:bg-white/10 text-emerald-200/50 hover:text-emerald-200 border border-white/5 hover:border-white/10 rounded-lg font-bold transition-all text-xs uppercase"
                        title="Volver (F10 / ESC)"
                    >
                        Volver
                    </button>
                </div>
            </div>
        </div>
    </div>
    <ContextMenu 
        v-model="contextMenu.show" 
        :x="contextMenu.x" 
        :y="contextMenu.y" 
        :actions="contextMenu.actions"
        @close="contextMenu.show = false"
    />
</template>

<style scoped>
/* Hide standard scrollbars but keep functionality */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: rgba(5, 46, 30, 0.5);
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: rgba(16, 185, 129, 0.2);
  border-radius: 20px;
}

/* Hide Number Spinners */
.no-spinner::-webkit-inner-spin-button, 
.no-spinner::-webkit-outer-spin-button { 
  -webkit-appearance: none; 
  margin: 0; 
}
.no-spinner {
  -moz-appearance: textfield;
}

/* Override SmartSelect input text color specifically in this component */
:deep(.smart-select-container input) {
    color: #000 !important; 
    font-weight: bold;
}

/* Zen Mode Styles - High Contrast for White Background */
.zen-active {
    background-color: white !important;
    border: none !important;
    color: black !important;
}

.zen-active * {
    border-color: #e5e7eb !important; /* gray-200 */
}

/* Force dark text for all common light text classes */
.zen-active .text-white,
.zen-active .text-white\/30,
.zen-active .text-white\/40,
.zen-active .text-white\/50,
.zen-active .text-white\/70,
.zen-active .text-emerald-200,
.zen-active .text-emerald-200\/50,
.zen-active .text-emerald-100 {
    color: #1f2937 !important; /* gray-800 */
}

/* Keep semantic colors but darken them for white background */
.zen-active .text-emerald-400,
.zen-active .text-emerald-500 {
    color: #059669 !important; /* emerald-600 (Darker Green) */
}

.zen-active .text-yellow-400 {
    color: #d97706 !important; /* amber-600 */
}

.zen-active .text-red-400 {
    color: #dc2626 !important; /* red-600 */
}

.zen-active .bg-emerald-900\/10,
.zen-active .bg-emerald-900\/20,
.zen-active .bg-emerald-900\/30, 
.zen-active .bg-\[\#052e1e\]\/50 {
    background-color: #f3f4f6 !important; /* gray-100 */
    backdrop-filter: none !important;
}

/* Header specific overrides */
.zen-active h2.font-outfit {
    color: #111827 !important;
}

/* Items specific overrides */
.zen-active .item-row {
    border-bottom: 1px solid #e5e7eb !important;
}

/* Ocultar elementos en modo Zen */
.zen-active .no-zen {
    display: none !important;
}
</style>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import SmartSelect from '@/components/ui/SmartSelect.vue'
import clientesService from '@/services/clientes'
import productosService from '@/services/productosApi'
import { usePedidosStore } from '@/stores/pedidos'
import { useNotificationStore } from '@/stores/notification'
import canteraService from '@/services/canteraService'
import ContextMenu from '@/components/common/ContextMenu.vue'
import LogisticaPanel from './components/LogisticaPanel.vue'
import html2canvas from 'html2canvas'

const router = useRouter()

const props = defineProps({
    modelValue: {
        type: Object,
        default: null
    },
    clientes: Array
})

const emit = defineEmits(['close', 'update-status', 'delete-item', 'clone', 'update:modelValue', 'save', 'refresh-orders'])

const store = usePedidosStore()
const notification = useNotificationStore()

// State
const isEditingClient = ref(false)
const isEditingNote = ref(false)
const hasChanges = ref(false)
const tempClientId = ref(null)
const tempNote = ref('')
const clientOptions = ref([])
const productOptions = ref([])

// Zen Mode & Capture
const isZenMode = ref(false)
const inspectorRef = ref(null) // Debe vincularse al div raiz

const captureZen = async () => {
    try {
        isZenMode.value = true
        await nextTick()
        await new Promise(resolve => setTimeout(resolve, 600))

        if (inspectorRef.value) {
            const canvas = await html2canvas(inspectorRef.value, {
                backgroundColor: '#ffffff',
                scale: 2,
                useCORS: true,
                logging: false,
                ignoreElements: (element) => element.classList.contains('no-zen')
            })

            canvas.toBlob(async (blob) => {
                try {
                    if (navigator.clipboard && navigator.clipboard.write) {
                        const item = new ClipboardItem({ 'image/png': blob })
                        await navigator.clipboard.write([item])
                        notification.add({
                            type: 'success',
                            title: 'Captura Copiada',
                            message: 'Imagen en portapapeles.',
                            duration: 3000
                        })
                    } else {
                        throw new Error('Clipboard API no disponible')
                    }
                } catch (clipboardErr) {
                    console.warn('Fallo portapapeles, iniciando descarga...', clipboardErr)
                    const link = document.createElement('a')
                    link.href = URL.createObjectURL(blob)
                    link.download = `Presupuesto_Pedido_${props.modelValue.id || 'Nuevo'}.png`
                    document.body.appendChild(link)
                    link.click()
                    document.body.removeChild(link)
                    notification.add({
                        type: 'info',
                        title: 'Imagen Descargada',
                        message: 'No se pudo copiar, se descargó el archivo.',
                        duration: 5000
                    })
                }
            })
        }
    } catch (err) {
        console.error('Zen Capture Error:', err)
        notification.add({
            type: 'error',
            title: 'Error de Renderizado',
            message: 'No se pudo generar la imagen.'
        })
    } finally {
        setTimeout(() => {
            isZenMode.value = false
        }, 500)
    }
}


const newItem = ref({
    producto_id: null,
    cantidad: 1
})

// Lifecycle
onMounted(() => {
    loadOptions()
    window.addEventListener('keydown', handleKeydown)
    if (props.clientes) {
        clientOptions.value = props.clientes
    }
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

// Load Data
const loadOptions = async () => {
    try {
        if (!props.clientes || props.clientes.length === 0) {
             const clientesRes = await clientesService.getAll({ type: 'simple' })
             clientOptions.value = clientesRes.data || []
        } else {
             clientOptions.value = props.clientes
        }

        const productosRes = await productosService.getAll({ limit: 1000 })
        const prods = productosRes.data || []
        productOptions.value = prods.map(p => ({
            id: p.id,
            nombre: `${p.nombre} ($${p.precio_mayorista})`,
        }))

    } catch (e) {
        console.error("Error loading inspector options", e)
    }
}

// Watchers
watch(() => props.modelValue, (newVal) => {
    isEditingClient.value = false
    newItem.value = { producto_id: null, cantidad: 1 }
}, { deep: true })

// Methods
const handleStatusChange = async (newStatus) => {
    if (newStatus === 'PENDIENTE') {
        const confirmComp = confirm("DISCRECIÓN REQUERIDA:\n\n¿Tipo de Operación para Reservar Stock?\n\n[ACEPTAR] = Con Factura A/B (FISCAL)\n[CANCELAR] = Solo Reserva Interna (X)")
        const newType = confirmComp ? 'FISCAL' : 'X'
        try {
            await store.updatePedido(props.modelValue.id, { 
                estado: 'PENDIENTE', 
                tipo_facturacion: newType 
            })
            props.modelValue.estado = 'PENDIENTE'
            props.modelValue.tipo_facturacion = newType
            notification.add(`Activado como ${newType === 'FISCAL' ? 'FISCAL' : 'INTERNO (X)'}`, 'success')
        } catch(e) {
            notification.add('Error actualizando pedido', 'error')
        }
        return
    }
    try {
        await store.updatePedido(props.modelValue.id, { estado: newStatus })
        props.modelValue.estado = newStatus
        emit('update-status', props.modelValue, newStatus)
        notification.add(`Estado: ${newStatus}`, 'success')
    } catch (e) {
        notification.add('Error al cambiar estado', 'error')
    }
}

const clientCondition = computed(() => {
    return props.modelValue.cliente?.condicion_iva?.nombre || ''
})

const canClientBeA = computed(() => {
    const c = clientCondition.value.toUpperCase()
    return c.includes('RESPONSABLE INSCRIPTO') || c.includes('MONOTRIBUTISTA')
})

const canClientBeB = computed(() => {
    return !canClientBeA.value
})

const recommendedFiscalType = computed(() => {
    return canClientBeA.value ? 'A' : 'B'
})

const getFiscalButtonClass = (btnType) => {
    const isCurrent = props.modelValue.tipo_facturacion === btnType
    const isRecommended = btnType === recommendedFiscalType.value
    
    if (props.modelValue.tipo_facturacion === 'X') {
        if (isRecommended) return 'text-emerald-500/50 hover:text-emerald-200 hover:bg-emerald-900/30 border-transparent'
        return 'text-emerald-500/20 opacity-50 cursor-not-allowed border-transparent'
    }

    if (isCurrent) {
        return 'bg-emerald-600 text-white shadow-lg border-emerald-400'
    }
    
    return 'text-emerald-500/30 opacity-50 cursor-not-allowed border-transparent'
}

const setFiscalMode = async () => {
    const target = recommendedFiscalType.value
    if (props.modelValue.tipo_facturacion === target) return
    await updateTipo(target)
}

const updateTipo = async (mode) => {
    let updateData = {}
    if (['A', 'B', 'M', 'FISCAL'].includes(mode)) {
        const finalType = mode === 'FISCAL' ? recommendedFiscalType.value : mode 
        updateData = { tipo_facturacion: finalType, estado: 'PENDIENTE' }
    } else if (mode === 'X') {
        updateData = { tipo_facturacion: 'X', estado: 'PRESUPUESTO' }
    } else if (mode === 'INT') {
        updateData = { tipo_facturacion: 'X', estado: 'INTERNO' }
    } else if (mode === 'ANULADO') {
        updateData = { estado: 'ANULADO' }
    }

    try {
        await store.updatePedido(props.modelValue.id, updateData)
        Object.assign(props.modelValue, updateData)
        notification.add(`Modo actualizado a ${mode}`, 'success')
    } catch (e) {
        notification.add('Error al cambiar modo', 'error')
    }
}

const handleCanteraSelect = async (item) => {
    try {
        notification.add({ title: 'Resiembra Táctica', message: `Importando ${item.razon_social}...`, type: 'info' });
        await canteraService.importCliente(item.id);
        await loadOptions();
        tempClientId.value = item.id;
        notification.add({ title: 'Éxito', message: 'Cliente importado.', type: 'success' });
    } catch (e) {
        console.error("Error importing from cantera", e);
        notification.add({ title: 'Error', message: 'Fallo importación.', type: 'error' });
    }
};

const handleProductCanteraSelect = async (item) => {
     // ... (Implementación idéntica a anterior si necesaria, o omitir si no se usa)
};

const startEditingClient = () => {
    tempClientId.value = props.modelValue.cliente?.id
    isEditingClient.value = true
}

const cancelEditClient = () => {
    isEditingClient.value = false
    tempClientId.value = null
}

const saveClientChange = async () => {
    if (!tempClientId.value || tempClientId.value === props.modelValue.cliente?.id) {
        cancelEditClient()
        return
    }
    try {
        await store.updatePedido(props.modelValue.id, { cliente_id: tempClientId.value })
        notification.add('Cliente actualizado', 'success')
        isEditingClient.value = false
        hasChanges.value = true
    } catch (e) {
        notification.add('Error actualizando cliente', 'error')
    }
}

const startEditingNote = () => {
    tempNote.value = props.modelValue.nota || ''
    isEditingNote.value = true
}

const cancelEditNote = () => {
    isEditingNote.value = false
    tempNote.value = ''
}

const saveNote = async () => {
    if (tempNote.value === props.modelValue.nota) {
        cancelEditNote()
        return
    }
    try {
        await store.updatePedido(props.modelValue.id, { nota: tempNote.value })
        notification.add('Nota actualizada', 'success')
        isEditingNote.value = false
        hasChanges.value = true
    } catch (e) {
        notification.add('Error actualizando nota', 'error')
    }
}

const isEditingOC = ref(false)
const tempOC = ref('')

const startEditingOC = () => {
    tempOC.value = props.modelValue.oc || ''
    isEditingOC.value = true
}

const cancelEditOC = () => {
    isEditingOC.value = false
    tempOC.value = ''
}

const saveOC = async () => {
    if (tempOC.value === props.modelValue.oc) {
        cancelEditOC()
        return
    }
    try {
        await store.updatePedido(props.modelValue.id, { oc: tempOC.value })
        notification.add('O.C. actualizada', 'success')
        props.modelValue.oc = tempOC.value 
        isEditingOC.value = false
        hasChanges.value = true
    } catch (e) {
        notification.add('Error actualizando O.C.', 'error')
    }
}

const addItem = async () => {
   // ... (Lógica agregar item)
}

const updateItem = async (item) => {
   // ... (Lógica actualizar item)
}

const deleteItem = async (itemId) => {
   // ... (Lógica eliminar item)
}

const editInGrid = () => {
    router.push({
        path: '/hawe/tactico',
        query: { edit: props.modelValue.id }
    })
}

const handleClientRightClick = () => {
    if (props.modelValue.cliente_id) {
        const returnUrl = `/hawe/tactico?edit=${props.modelValue.id}`
        router.push({ 
            name: 'HaweClientCanvas', 
            params: { id: props.modelValue.cliente_id },
            query: { returnUrl }
        })
    } else {
        notification.add('Error: Pedido sin cliente vinculado', 'error')
    }
}

const contextMenu = ref({
    show: false,
    x: 0,
    y: 0,
    actions: []
})

const handleGlobalContextMenu = (e) => {
    e.preventDefault()
    contextMenu.value.x = e.clientX
    contextMenu.value.y = e.clientY
    contextMenu.value.actions = [
        {
            label: 'Capturar Presupuesto (Zen)',
            icon: '📸',
            handler: () => captureZen()
        },
        {
            label: 'Clonar Pedido',
            icon: '📄',
            handler: () => emit('clone')
        },
        {
            label: 'Cerrar / Volver',
            icon: '❌',
            handler: () => handleClose()
        }
    ]
    contextMenu.value.show = true
}

const handleProductContextMenu = (e, item) => {
    e.preventDefault()
    e.stopPropagation() // Evitar gatillar menú global
    if (!item.producto_id) return
    contextMenu.value.x = e.clientX
    contextMenu.value.y = e.clientY
    contextMenu.value.actions = [
        {
            label: 'Ver Producto',
            icon: '📦',
            handler: () => {
                const query = item.producto?.sku || item.producto?.nombre
                if (query) {
                    router.push({ path: '/hawe/productos', query: { search: query } })
                }
            }
        },
        {
            label: 'Eliminar Item',
            icon: '🗑️',
            handler: () => emit('delete-item', item.id) 
        }
    ]
    contextMenu.value.show = true
}

const handleClose = () => {
    emit('close')
}

const handleKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault()
        handleClose()
    }
    if (e.key === 'Escape') {
        e.preventDefault()
        handleClose()
    }
}
// Utils
const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('es-AR', {
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute:'2-digit'
    })
}

const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value)
}

const getInitials = (name) => {
    if (!name) return '?'
    return name.substring(0, 1).toUpperCase()
}

const getStatusColorClass = (status) => {
    switch (status) {
         case 'PENDIENTE': return 'text-emerald-400'
         case 'CUMPLIDO': return 'text-yellow-400' 
         case 'ANULADO': return 'text-red-400'
         case 'PRESUPUESTO': return 'text-purple-300'
         case 'BORRADOR': return 'text-purple-300/50'
         case 'CLONADO': return 'text-purple-300/50' // Legacy support
         case 'INTERNO': return 'text-cyan-300'
         default: return 'text-white'
    }
}
</script>


