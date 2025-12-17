<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useClientesStore } from '@/stores/clientes';
import { useProductosStore } from '@/stores/productos';
import SmartSelect from '@/components/ui/SmartSelect.vue';
import pedidosService from '@/services/pedidos';

// Components
import ClientLookup from '@/components/ventas/ClientLookup.vue';
import ClienteInspector from '@/views/Hawe/components/ClienteInspector.vue';

const clientesStore = useClientesStore();
const productosStore = useProductosStore();

const fecha = ref(new Date().toISOString().split('T')[0]);
const clienteId = ref(null);
const nota = ref('');
const oc = ref('');
const items = ref([]);
const isSaving = ref(false);

// Modals State
const showLookup = ref(false);
const showInspector = ref(false);
const clienteForInspector = ref(null);

// Totals
const total = computed(() => {
    return items.value.reduce((acc, item) => {
        return acc + (item.cantidad * item.precio_unitario);
    }, 0);
});

const clienteSeleccionado = computed(() => {
    return clientesStore.clientes.find(c => c.id === clienteId.value);
});

const clienteEsVerde = computed(() => {
    const c = clienteSeleccionado.value;
    if (!c) return false;
    // Misma lógica que ClientLookup - Centralizar si es posible, por ahora replicamos
    const hasCuit = c.cuit && c.cuit.length >= 11;
    const hasAddress = c.domicilio_fiscal_resumen || (c.domicilios && c.domicilios.some(d => d.es_fiscal && d.activo));
    const hasCond = !!c.condicion_iva_id || !!c.condicion_iva;
    return hasCuit && hasAddress && hasCond;
});

// Lifecycle
onMounted(async () => {
    // Cargar maestros si no estan (o forzar refresh para tener statuses frescos)
    await Promise.all([
        clientesStore.fetchClientes(),
        productosStore.fetchProductos()
    ]);
    
    // Iniciar con una fila vacia
    addItem();
    
    // Global Shortcuts
    window.addEventListener('keydown', handleGlobalKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeydown);
});

const handleGlobalKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault();
        saveAndExport();
    }
    if (e.key === 'F3') {
        e.preventDefault();
        showLookup.value = true;
    }
};

// Actions
const addItem = () => {
    items.value.push({
        producto_id: null,
        cantidad: 1,
        precio_unitario: 0,
        subtotal: 0
    });
};

const removeItem = (index) => {
    items.value.splice(index, 1);
    if (items.value.length === 0) addItem(); // Siempre una
};

const handleProductChange = (item, newId) => {
    item.producto_id = newId;
    const prod = productosStore.productos.find(p => p.id === newId);
    if (prod) {
        item.precio_unitario = prod.precio_minorista || prod.precio_sugerido || 0; 
    }
};

const saveAndExport = async () => {
    if (!clienteId.value) return alert('Seleccione un cliente (F3)');
    if (!clienteEsVerde.value && !confirm('⚠️ El cliente seleccionado tiene datos incompletos (ROJO). ¿Desea facturar igual?')) {
        return;
    }
    
    const validItems = items.value.filter(i => i.producto_id && i.cantidad > 0);
    if (validItems.length === 0) return alert('Agregue al menos un producto valido');

    try {
        isSaving.value = true;
        
        const payload = {
            cliente_id: clienteId.value,
            fecha: new Date(fecha.value),
            nota: nota.value,
            oc: oc.value,
            items: validItems.map(i => ({
                producto_id: i.producto_id,
                cantidad: parseFloat(i.cantidad),
                precio_unitario: parseFloat(i.precio_unitario)
            }))
        };

        const blob = await pedidosService.createTactico(payload);
        
        // Trigger download
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const nombre = clienteSeleccionado.value?.razon_social || 'Cliente';
        link.setAttribute('download', `Pedido_${nombre}_${fecha.value}.xlsx`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        
        if (confirm('Pedido generado con éxito. ¿Limpiar formulario?')) {
            items.value = [];
            addItem();
            nota.value = '';
            clienteId.value = null;
        }

    } catch (error) {
        console.error(error);
        alert('Error al generar pedido: ' + (error.response?.data?.detail || error.message));
    } finally {
        isSaving.value = false;
    }
};

const openInspectorForCurrent = () => {
    if (clienteSeleccionado.value) {
        clienteForInspector.value = clienteSeleccionado.value;
        showInspector.value = true;
    }
};

// --- Lookup Handlers ---
const onLookupSelect = (cliente) => {
    clienteId.value = cliente.id;
    // Auto focus grid logic could go here
};

const onLookupEdit = (cliente) => {
    clienteForInspector.value = cliente;
    showInspector.value = true;
    // Keep lookup open? Usually better to close lookup, fix in inspector, then reopen lookup or just select.
    // User flow: "Doble click abre inspeccion... le doy ok... verde"
    // So we close lookup, open inspector.
    showLookup.value = false;
};

const onLookupDelete = async (cliente) => {
    try {
        await clientesStore.deleteCliente(cliente.id); // Soft delete
        // Toast logic here?
    } catch (e) {
        alert("Error eliminando: " + e.message);
    }
};

const onInspectorClose = async () => {
    showInspector.value = false;
    clienteForInspector.value = null;
    await clientesStore.fetchClientes(); // Refresh data to turn RED -> GREEN
    
    // If we were editing the selected client, update check
    if (clienteId.value) {
        // Computed will re-eval
    } else {
        // If we came from lookup edit, maybe reopen lookup?
        showLookup.value = true;
    }
};

</script>

<template>
    <div class="h-full flex flex-col bg-[#020617] text-gray-100 p-4 overflow-hidden font-sans">
        
        <!-- Header -->
        <header class="flex justify-between items-center mb-6 border-b border-indigo-900/50 pb-4">
            <div>
                <h1 class="text-2xl font-bold text-indigo-400">Cargador Táctico <span class="text-indigo-600/60 text-sm">v5.4</span></h1>
                <p class="text-indigo-200/50 text-xs">Entrada rápida • Auditoría integrada (F3)</p>
            </div>
            <div class="flex gap-4 items-end">
                <div class="text-right">
                    <div class="text-xs text-indigo-400/70 uppercase tracking-widest">Total Pedido</div>
                    <div class="text-3xl font-mono text-indigo-400 font-bold">{{ total.toLocaleString('es-AR', {style: 'currency', currency: 'ARS'}) }}</div>
                </div>
                <button 
                    @click="saveAndExport"
                    :disabled="isSaving"
                    class="h-12 px-6 bg-indigo-600 text-white font-bold rounded hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-indigo-900/50 border border-indigo-500/30 active:translate-y-0.5 transition-all"
                >
                    <span v-if="isSaving" class="animate-spin">⏳</span>
                    <span v-else>💾 GUARDAR (F10)</span>
                </button>
            </div>
        </header>

        <!-- Form Header -->
        <section class="grid grid-cols-12 gap-4 mb-6 bg-[#0f172a] p-4 rounded-lg shadow-sm border border-slate-800">
            <div class="col-span-2">
                <label class="block text-xs font-bold text-slate-500 mb-1">FECHA</label>
                <input type="date" v-model="fecha" class="w-full bg-[#1e293b] border border-slate-700 rounded p-2 text-white focus:border-indigo-500 outline-none">
            </div>
            
            <div class="col-span-10 lg:col-span-5 relative group">
                 <label class="block text-xs font-bold text-slate-500 mb-1 flex justify-between">
                    <span>CLIENTE (F3)</span>
                    <span v-if="clienteId" :class="clienteEsVerde ? 'text-emerald-500' : 'text-rose-500 animate-pulse'">
                        <i class="fa-solid fa-circle text-[0.6rem]"></i> {{ clienteEsVerde ? 'AUDITADO' : 'REQUIERE REVISIÓN' }}
                    </span>
                 </label>
                 
                 <!-- Input Dummy Trigger -->
                 <div 
                    @click="showLookup = true"
                    class="w-full bg-[#1e293b] border border-slate-700 rounded p-2 text-white cursor-pointer hover:border-indigo-500 flex justify-between items-center h-[42px]"
                 >
                    <span v-if="clienteSeleccionado" class="font-bold truncate">
                        {{ clienteSeleccionado.razon_social }}
                        <span class="text-slate-500 font-normal text-xs ml-2">{{ clienteSeleccionado.cuit }}</span>
                    </span>
                    <span v-else class="text-slate-500 italic">Presione F3 para buscar...</span>
                    
                    <i class="fa-solid fa-search text-slate-600"></i>
                 </div>
                 
                 <button 
                    v-if="clienteId" 
                    @click.stop="openInspectorForCurrent"
                    class="absolute top-8 right-10 text-xs text-slate-400 hover:text-white px-2 py-1"
                    title="Ver detalles"
                >
                    <i class="fa-solid fa-eye"></i>
                </button>
            </div>

            <div class="col-span-12 lg:col-span-5 flex gap-2">
                <div class="w-1/3">
                    <label class="block text-xs font-bold text-slate-500 mb-1">O.C.</label>
                    <input 
                        type="text" 
                        v-model="oc" 
                        placeholder="Orden Compra" 
                        class="w-full bg-[#1e293b] border border-slate-700 rounded p-2 text-white focus:border-indigo-500 outline-none font-bold text-center"
                    >
                </div>
                <div class="flex-1">
                    <label class="block text-xs font-bold text-slate-500 mb-1">NOTA INTERNA</label>
                    <input 
                        type="text" 
                        v-model="nota" 
                        placeholder="Observaciones..." 
                        class="w-full bg-[#1e293b] border border-slate-700 rounded p-2 text-white focus:border-indigo-500 outline-none"
                    >
                </div>
            </div>
        </section>

        <!-- Grid -->
        <section class="flex-1 overflow-auto bg-[#0f172a] rounded-lg border border-slate-800 relative">
            <table class="w-full text-left border-collapse">
                <thead class="bg-[#1e293b] sticky top-0 z-10 text-xs uppercase text-slate-400 font-bold border-b border-slate-700">
                    <tr>
                        <th class="p-3 w-12 text-center">#</th>
                        <th class="p-3 w-6/12">Producto</th>
                        <th class="p-3 w-2/12 text-right">Cantidad</th>
                        <th class="p-3 w-2/12 text-right">Precio Unit.</th>
                        <th class="p-3 w-2/12 text-right">Subtotal</th>
                        <th class="p-3 w-12"></th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-800">
                    <tr v-for="(item, index) in items" :key="index" class="group hover:bg-slate-800/50 transition-colors">
                        <td class="p-2 text-center text-slate-600 font-mono">{{ index + 1 }}</td>
                        <td class="p-2">
                            <SmartSelect 
                                v-model="item.producto_id"
                                :options="productosStore.productos.map(p => ({id: p.id, nombre: p.nombre, sku: p.sku, precio_minorista: p.precio_minorista, precio_sugerido: p.precio_sugerido}))" 
                                @update:modelValue="(val) => handleProductChange(item, val)"
                                placeholder="Buscar Producto..."
                                :allow-create="false"
                                class="w-full text-gray-900" 
                            />
                        </td>
                        <td class="p-2">
                            <input 
                                type="number" 
                                v-model.number="item.cantidad"
                                class="w-full bg-transparent border-b border-transparent hover:border-slate-600 focus:border-indigo-500 text-right p-1 outline-none font-mono text-emerald-300 font-bold"
                                min="0.1" step="any"
                            >
                        </td>
                        <td class="p-2">
                             <input 
                                type="number" 
                                v-model.number="item.precio_unitario"
                                class="w-full bg-transparent border-b border-transparent hover:border-slate-600 focus:border-indigo-500 text-right p-1 outline-none font-mono text-slate-300"
                                min="0" step="0.01"
                            >
                        </td>
                        <td class="p-2 text-right font-mono font-bold text-white">
                            {{ (item.cantidad * item.precio_unitario).toLocaleString('es-AR', {minimumFractionDigits: 2}) }}
                        </td>
                        <td class="p-2 text-center">
                            <button @click="removeItem(index)" class="text-slate-600 hover:text-rose-500 transition-colors opacity-0 group-hover:opacity-100">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <div class="p-4 border-t border-slate-800">
                <button @click="addItem" class="text-indigo-400 text-sm font-bold hover:text-indigo-300 transition-colors flex items-center gap-2 hover:bg-indigo-900/20 px-3 py-2 rounded">
                    <i class="fa-solid fa-plus"></i> Agregar Fila (Enter)
                </button>
            </div>
        </section>

        <!-- Modals -->
        <ClientLookup 
            :show="showLookup"
            :clientes="clientesStore.clientes"
            @close="showLookup = false"
            @select="onLookupSelect"
            @edit="onLookupEdit"
            @delete="onLookupDelete"
        />

        <!-- Inspector (Reusing Hawe's component) -->
        <div v-if="showInspector" class="fixed inset-0 z-[60] flex justify-end bg-black/50 backdrop-blur-sm" @click.self="onInspectorClose">
            <div class="w-full max-w-2xl h-full bg-slate-900 border-l border-slate-700 shadow-2xl overflow-y-auto transform transition-transform duration-300">
                <!-- Wrapper to ensure props match what ClienteInspector expects. 
                     Assuming ClienteInspector takes :cliente -->
                <ClienteInspector 
                    v-if="clienteForInspector"
                    :cliente="clienteForInspector" 
                    @close="onInspectorClose"
                />
            </div>
        </div>

    </div>
</template>

<style scoped>
/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type=number] {
  -moz-appearance: textfield;
}
</style>
