<template>
    <div class="h-full flex flex-col bg-[#021812] border-l border-emerald-900/30">
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
                <button 
                    @click="handleClose" 
                    class="h-8 w-8 rounded-full flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all"
                    title="Cerrar (ESC)"
                >
                    <i class="fas fa-times"></i>
                </button>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-emerald-900/30 hover:scrollbar-thumb-emerald-900/50">
                
                <!-- Client Card (Editable) -->
                <div class="bg-emerald-900/10 p-4 rounded-lg border border-emerald-900/20 relative group/client">
                    <div v-if="!isEditingClient" class="flex items-center justify-between">
                         <div class="flex items-center gap-3">
                             <div class="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-900 to-green-900 flex items-center justify-center text-white font-bold text-sm border border-emerald-500/20 shrink-0">
                                {{ getInitials(modelValue.cliente?.razon_social) }}
                            </div>
                            <div>
                                 <h3 class="font-bold text-emerald-100 text-sm">{{ modelValue.cliente?.razon_social }}</h3>
                                 <p class="text-xs text-emerald-500/50">ID: {{ modelValue.cliente?.id }}</p>
                            </div>
                        </div>
                        <button 
                            @click="startEditingClient"
                            class="text-emerald-500/30 hover:text-emerald-400 transition-colors opacity-0 group-hover/client:opacity-100"
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

                <!-- Tipo Comprobante Toggle -->
                <div class="mb-4">
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-emerald-500/70 mb-1.5 ml-1">Tipo de Comprobante / Modo</label>
                    <div class="grid grid-cols-2 gap-2 bg-[#051f15] rounded-lg p-2 border border-emerald-900/30">
                        <button 
                            @click="updateTipo('FISCAL')"
                            class="py-1.5 rounded text-[10px] font-bold transition-all border border-transparent"
                            :class="modelValue.tipo_facturacion === 'FISCAL' || modelValue.tipo_facturacion === 'B' || modelValue.tipo_facturacion === 'A' ? 'bg-emerald-600 text-white shadow-lg border-emerald-400' : 'text-white/30 hover:text-white/50 bg-emerald-950/30'"
                        >
                            <i class="fas fa-file-invoice-dollar mr-1"></i> FISCAL (A/B)
                        </button>
                        <button 
                            @click="updateTipo('X')"
                            class="py-1.5 rounded text-[10px] font-bold transition-all border border-transparent"
                            :class="modelValue.tipo_facturacion === 'X' && modelValue.estado === 'PRESUPUESTO' ? 'bg-purple-600/80 text-white shadow-lg border-purple-400' : 'text-white/30 hover:text-white/50 bg-emerald-950/30'"
                        >
                            <i class="fas fa-calculator mr-1"></i> PRESUPUESTO X
                        </button>
                        <button 
                            @click="updateTipo('INT')"
                            class="py-1.5 rounded text-[10px] font-bold transition-all border border-transparent"
                            :class="modelValue.estado === 'INTERNO' ? 'bg-cyan-600/80 text-white shadow-lg border-cyan-400' : 'text-white/30 hover:text-white/50 bg-emerald-950/30'"
                        >
                            <i class="fas fa-microchip mr-1"></i> INTERNO (INT)
                        </button>
                        <button 
                            @click="updateTipo('ANULADO')"
                            class="py-1.5 rounded text-[10px] font-bold transition-all border border-transparent"
                            :class="modelValue.estado === 'ANULADO' ? 'bg-red-600/80 text-white shadow-lg border-red-400' : 'text-white/30 hover:text-white/50 bg-emerald-950/30'"
                        >
                            <i class="fas fa-ban mr-1"></i> ANULADO
                        </button>
                    </div>
                </div>

                <!-- Status Selector -->
                <div class="group relative">
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

                <!-- QUICK EDIT ITEMS BUTTON -->
                <div class="pt-2">
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
                            class="flex justify-between items-start p-3 bg-emerald-900/5 rounded border border-emerald-900/10 group/item hover:bg-emerald-900/10 transition-colors"
                        >
                            <div class="flex-1 pr-4">
                                <p class="text-xs text-white font-medium mb-1">{{ item.producto?.nombre || 'Producto' }}</p>
                                <div class="flex items-center gap-2">
                                     <span class="text-[10px] text-emerald-400 font-bold">{{ item.cantidad }}</span>
                                     <span class="text-[10px] text-white/40">x</span>
                                     <span class="text-[10px] text-white/60">{{ formatCurrency(item.precio_unitario) }}</span>
                                </div>
                            </div>
                            <div class="text-right">
                                <p class="text-xs font-bold text-emerald-200">{{ formatCurrency(item.cantidad * item.precio_unitario) }}</p>
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
                            class="text-yellow-500/30 hover:text-yellow-400 opacity-0 group-hover/nota:opacity-100 transition-opacity"
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
                            class="text-blue-500/30 hover:text-blue-400 opacity-0 group-hover/oc:opacity-100 transition-opacity"
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
                
                <div class="flex gap-2">
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
                        <i class="fas fa-check mr-1"></i> Aceptar (F10)
                    </button>
                </div>
            </div>
        </div>
    </div>
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
</style>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import SmartSelect from '@/components/ui/SmartSelect.vue'
import clientesService from '@/services/clientes'
import productosService from '@/services/productosApi' // Corrected path
import { usePedidosStore } from '@/stores/pedidos' // Need store actions direct access
import { useNotificationStore } from '@/stores/notification'
import canteraService from '@/services/canteraService'

const router = useRouter()

const props = defineProps({
    modelValue: {
        type: Object,
        default: null
    }
})

const emit = defineEmits(['close', 'update-status', 'delete-item', 'clone'])

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

const newItem = ref({
    producto_id: null,
    cantidad: 1
})

// Lifecycle
onMounted(() => {
    loadOptions()
    window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

// Load Data
const loadOptions = async () => {
    try {
        const [clientesRes, productosRes] = await Promise.all([
            clientesService.getAll({ type: 'simple' }), // Assuming simple returns id/name
            productosService.getAll({ limit: 1000 }) // Or search on demand? For now load all if small
        ])
        clientOptions.value = clientesRes.data || []
        
        // Map products for SmartSelect (needs id, nombre)
        // Check structure of productsRes.data
        const prods = productosRes.data || []
        productOptions.value = prods.map(p => ({
            id: p.id,
            nombre: `${p.nombre} ($${p.precio_mayorista})`, // Show price in name
             // Other fields for SmartSelect filtering if needed
        }))

    } catch (e) {
        console.error("Error loading inspector options", e)
    }
}

// Watchers
watch(() => props.modelValue, (newVal) => {
    // Reset edit states when switching orders
    isEditingClient.value = false
    newItem.value = { producto_id: null, cantidad: 1 }
})

// Methods
const handleStatusChange = async (newStatus) => {
    // Intercept PENDIENTE to ask for Type
    if (newStatus === 'PENDIENTE') {
        const confirmComp = confirm("DISCRECIÓN REQUERIDA:\n\n¿Tipo de Operación para Reservar Stock?\n\n[ACEPTAR] = Con Factura A/B (FISCAL)\n[CANCELAR] = Solo Reserva Interna (X)")
        
        const newType = confirmComp ? 'FISCAL' : 'X'
        
        try {
            await store.updatePedido(props.modelValue.id, { 
                estado: 'PENDIENTE', 
                tipo_facturacion: newType 
            })
            // Manual optimistic update
            props.modelValue.estado = 'PENDIENTE'
            props.modelValue.tipo_facturacion = newType
            
            notification.add(`Activado como ${newType === 'FISCAL' ? 'FISCAL' : 'INTERNO (X)'}`, 'success')
        } catch(e) {
            notification.add('Error actualizando pedido', 'error')
        }
        return
    }

    // Normal change for other statuses (Borrador, Presupuesto, etc)
    try {
        await store.updatePedido(props.modelValue.id, { estado: newStatus })
        props.modelValue.estado = newStatus
        emit('update-status', props.modelValue, newStatus)
        notification.add(`Estado: ${newStatus}`, 'success')
    } catch (e) {
        notification.add('Error al cambiar estado', 'error')
    }
}

const updateTipo = async (mode) => {
    let updateData = {}
    
    if (mode === 'FISCAL') {
        updateData = { tipo_facturacion: 'FISCAL', estado: 'PENDIENTE' }
    } else if (mode === 'X') {
        updateData = { tipo_facturacion: 'X', estado: 'PRESUPUESTO' }
    } else if (mode === 'INT') {
        updateData = { tipo_facturacion: 'X', estado: 'INTERNO' }
    } else if (mode === 'ANULADO') {
        updateData = { estado: 'ANULADO' }
    }

    try {
        await store.updatePedido(props.modelValue.id, updateData)
        // Optimistic update
        Object.assign(props.modelValue, updateData)
        notification.add(`Modo actualizado a ${mode}`, 'success')
    } catch (e) {
        notification.add('Error al cambiar modo', 'error')
    }
}

const handleCanteraSelect = async (item) => {
    try {
        notification.add({
            title: 'Resiembra Táctica',
            message: `Importando ${item.razon_social} desde Cantera...`,
            type: 'info'
        });
        
        await canteraService.importCliente(item.id);
        
        // Recargar opciones para que el nuevo cliente aparezca en el select
        await loadOptions();
        
        // Asignar el nuevo ID importado (coincide con el del mirror)
        tempClientId.value = item.id;
        
        notification.add({
            title: 'Éxito',
            message: 'Cliente importado y listo para usar.',
            type: 'success'
        });
    } catch (e) {
        console.error("Error importing from cantera", e);
        notification.add({
            title: 'Error de Importación',
            message: 'No se pudo importar el maestro.',
            type: 'error'
        });
    }
};

const handleProductCanteraSelect = async (item) => {
    try {
        notification.add({
            title: 'Resiembra Táctica',
            message: `Importando ${item.nombre} desde Cantera...`,
            type: 'info'
        });
        
        await canteraService.importProducto(item.id);
        
        // Recargar opciones
        await loadOptions();
        
        // Asignar el nuevo ID importado al item que se está agregando
        newItem.value.producto_id = item.id;
        
        notification.add({
            title: 'Éxito',
            message: 'Producto importado y listo para agregar.',
            type: 'success'
        });
    } catch (e) {
        console.error("Error importing product from cantera", e);
        notification.add({
            title: 'Error de Importación',
            message: 'No se pudo importar el producto maestro.',
            type: 'error'
        });
    }
};

// Client Change Logic
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

// Note Edit Logic
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

// OC Edit Logic
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
        props.modelValue.oc = tempOC.value // Optimistic update
        isEditingOC.value = false
        hasChanges.value = true
    } catch (e) {
        notification.add('Error actualizando O.C.', 'error')
    }
}

// Add Item Logic
const addItem = async () => {
    if (!newItem.value.producto_id) return
    
    try {
        await store.addPedidoItem(props.modelValue.id, {
            producto_id: newItem.value.producto_id,
            cantidad: newItem.value.cantidad,
            precio_unitario: 0 
        })
        notification.add('Item agregado', 'success')
        newItem.value = { producto_id: null, cantidad: 1 }
        hasChanges.value = true
        // Force reactivity since we are modifying a prop object via store that updates array
        // We rely on parent using the same object reference from store.
    } catch (e) {
        notification.add('Error agregando item', 'error')
    }
}

const updateItem = async (item) => {
    try {
        await store.updatePedidoItem(props.modelValue.id, item.id, {
            cantidad: item.cantidad,
            precio_unitario: item.precio_unitario
        })
        hasChanges.value = true
    } catch (e) {
        notification.add('Error actualizando item', 'error')
    }
}

// Delete Item Logic
const deleteItem = async (itemId) => {
    const isLastItem = props.modelValue.items.length <= 1
    
    let confirmMsg = '¿Eliminar este item?'
    if (isLastItem) {
        confirmMsg = '⚠️ CUIDADO: Al eliminar el último item, el pedido quedará vacío y pasará a estado ANULADO. ¿Continuar?'
    }
    
    if (!confirm(confirmMsg)) return

    try {
        await store.deletePedidoItem(props.modelValue.id, itemId)
        
        if (isLastItem) {
            await store.updatePedido(props.modelValue.id, { estado: 'ANULADO' })
            notification.add('Pedido ANULADO por falta de items', 'warning')
        } else {
            notification.add('Item eliminado', 'success')
        }
        hasChanges.value = true
    } catch (e) {
        notification.add('Error eliminando item', 'error')
    }
}

const editInGrid = () => {
    router.push({
        path: '/hawe/tactico',
        query: { edit: props.modelValue.id }
    })
}

// Close (Simply close, auto-save happens on input blur/change)
const handleClose = () => {
    emit('close')
}


// Handlers
const handleKeydown = (e) => {
    // F10 - Save/Close
    if (e.key === 'F10') {
        e.preventDefault()
        handleClose()
    }
    // Escape - Close
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
