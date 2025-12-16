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
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-emerald-500/70 mb-1.5 ml-1">Tipo de Comprobante</label>
                    <div class="flex bg-[#051f15] rounded-lg p-1 border border-emerald-900/30">
                        <button 
                            @click="updateTipo('FISCAL')"
                            class="flex-1 py-1.5 rounded text-xs font-bold transition-all"
                            :class="modelValue.tipo_comprobante === 'FISCAL' ? 'bg-emerald-600 text-white shadow-lg' : 'text-white/30 hover:text-white/50'"
                        >
                            FISCAL (A/B)
                        </button>
                        <button 
                            @click="updateTipo('X')"
                            class="flex-1 py-1.5 rounded text-xs font-bold transition-all"
                            :class="modelValue.tipo_comprobante === 'X' ? 'bg-purple-600/80 text-white shadow-lg' : 'text-white/30 hover:text-white/50'"
                        >
                            PRESUPUESTO X
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
                            <option value="BORRADOR" class="text-gray-400 font-bold bg-white">BORRADOR (Trabajo en Progreso)</option>
                            <option value="PRESUPUESTO" class="text-purple-600 font-bold bg-white">PRESUPUESTO (Cotización)</option>
                            <option value="PENDIENTE" class="text-emerald-600 bg-white font-bold">PENDIENTE (Aprobado/En Curso)</option>
                            <option value="CUMPLIDO" class="text-blue-600 bg-white font-bold">CUMPLIDO (Entregado)</option>
                            <option value="ANULADO" class="text-red-600 bg-white font-bold">ANULADO</option>
                        </select>
                        <i class="fas fa-chevron-down absolute right-4 top-1/2 -translate-y-1/2 text-white/30 pointer-events-none"></i>
                    </div>
                </div>

                <!-- Add Item Section -->
                <div class="bg-emerald-900/5 p-4 rounded-lg border border-emerald-900/10 mb-4">
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-emerald-500/70 mb-2">Agregar Item</label>
                     <div class="flex gap-2 mb-2">
                        <div class="flex-1">
                            <SmartSelect
                                :modelValue="newItem.producto_id"
                                @update:modelValue="newItem.producto_id = $event"
                                :options="productOptions"
                                placeholder="Buscar producto..."
                                :allowCreate="false"
                                class="smart-select-container"
                            />
                        </div>
                        <div class="w-16">
                            <input 
                                type="number" 
                                v-model.number="newItem.cantidad" 
                                min="1"
                                class="w-full bg-white text-black border border-gray-300 rounded px-2 py-2 text-sm text-center font-bold focus:outline-none focus:border-emerald-500"
                            />
                        </div>
                     </div>
                     <button 
                        @click="addItem"
                        :disabled="!newItem.producto_id || newItem.cantidad < 1"
                        class="w-full py-1.5 bg-emerald-600/20 hover:bg-emerald-600 text-emerald-400 hover:text-white rounded text-xs font-bold uppercase tracking-wider transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                     >
                        <i class="fas fa-plus mr-1"></i> Agregar
                     </button>
                </div>

                <!-- Items List -->
                <div>
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-emerald-500/70 mb-2 ml-1">Items del Pedido ({{ modelValue.items.length }})</label>
                    <div class="space-y-2">
                        <div 
                            v-for="item in modelValue.items" 
                            :key="item.id"
                            class="flex justify-between items-start p-3 bg-emerald-900/5 rounded border border-emerald-900/10 group/item hover:bg-emerald-900/10 transition-colors"
                        >
                            <div class="flex-1 pr-4">
                                <p class="text-xs text-white font-medium mb-1">{{ item.producto?.nombre || 'Producto' }}</p>
                                <div class="flex items-center gap-2">
                                    <input 
                                        type="number" 
                                        v-model.number="item.cantidad"
                                        @change="updateItem(item)"
                                        class="w-12 bg-emerald-900/30 text-emerald-100 border border-emerald-500/30 rounded px-1 py-0.5 text-[10px] text-center focus:outline-none focus:border-emerald-400 no-spinner"
                                        min="1"
                                    />
                                    <span class="text-[10px] text-white/40">x</span>
                                    <div class="relative">
                                        <span class="absolute left-1.5 top-1/2 -translate-y-1/2 text-[10px] text-emerald-500/50">$</span>
                                        <input 
                                            type="number" 
                                            v-model.number="item.precio_unitario"
                                            @change="updateItem(item)"
                                            class="w-20 bg-emerald-900/30 text-emerald-100 border border-emerald-500/30 rounded pl-4 pr-1 py-0.5 text-[10px] text-right focus:outline-none focus:border-emerald-400 no-spinner"
                                            min="0"
                                            step="0.01"
                                        />
                                    </div>
                                </div>
                            </div>
                            <div class="text-right flex items-center gap-3">
                                <p class="text-xs font-bold text-emerald-200">{{ formatCurrency(item.cantidad * item.precio_unitario) }}</p>
                                <button 
                                    @click="deleteItem(item.id)"
                                    class="text-red-500/30 hover:text-red-400 opacity-0 group-hover/item:opacity-100 transition-all"
                                    title="Eliminar Item"
                                >
                                    <i class="fas fa-trash"></i>
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
import SmartSelect from '@/components/ui/SmartSelect.vue'
import clientesService from '@/services/clientes'
import productosService from '@/services/productosApi' // Corrected path
import { usePedidosStore } from '@/stores/pedidos' // Need store actions direct access
import { useNotificationStore } from '@/stores/notification'

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
                tipo_comprobante: newType 
            })
            // Manual optimistic update
            props.modelValue.estado = 'PENDIENTE'
            props.modelValue.tipo_comprobante = newType
            
            notification.add(`Activado como ${newType === 'FISCAL' ? 'FISCAL' : 'INTERNO (X)'}`, 'success')
        } catch(e) {
            notification.add('Error actualizando pedido', 'error')
        }
        return
    }

    // Normal change for other statuses (Borrador, Presupuesto, etc)
    // Optimistic update
    props.modelValue.estado = newStatus
    emit('update-status', props.modelValue, newStatus)
}

const updateTipo = async (tipo) => {
    if (tipo === props.modelValue.tipo_comprobante) return
    try {
        await store.updatePedido(props.modelValue.id, { tipo_comprobante: tipo })
        props.modelValue.tipo_comprobante = tipo 
        notification.add(`Tipo actualizado a ${tipo}`, 'success')
    } catch (e) {
        notification.add('Error al cambiar tipo', 'error')
    }
}

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

// Close (Simply close, auto-save happens on input blur/change)
const handleClose = () => {
    emit('close')
}


// Handlers
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
         case 'PENDIENTE': return 'text-white'
         case 'CUMPLIDO': return 'text-yellow-400' 
         case 'ANULADO': return 'text-red-400'
         case 'PRESUPUESTO': return 'text-purple-300'
         case 'BORRADOR': return 'text-gray-400'
         case 'CLONADO': return 'text-pink-500' // Legacy support
         case 'INTERNO': return 'text-purple-300' // Legacy support
         default: return 'text-white'
    }
}
</script>
