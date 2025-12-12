<script setup>
import { ref, computed, onMounted } from 'vue';
import { useClientesStore } from '@/stores/clientes';
import { useProductosStore } from '@/stores/productos';
import SmartSelect from '@/components/ui/SmartSelect.vue';
import pedidosService from '@/services/pedidos';

const clientesStore = useClientesStore();
const productosStore = useProductosStore();

const fecha = ref(new Date().toISOString().split('T')[0]);
const clienteId = ref(null);
const nota = ref('');
const items = ref([]);
const isSaving = ref(false);

// Totals
const total = computed(() => {
    return items.value.reduce((acc, item) => {
        return acc + (item.cantidad * item.precio_unitario);
    }, 0);
});

// Lifecycle
onMounted(async () => {
    // Cargar maestros si no estan
    if (clientesStore.clientes.length === 0) await clientesStore.fetchClientes();
    if (productosStore.productos.length === 0) await productosStore.fetchProductos();
    
    // Iniciar con una fila vacia
    addItem();
    
    // Global Shortcuts
    window.addEventListener('keydown', handleGlobalKeydown);
});

import { onUnmounted } from 'vue';
onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeydown);
});

const handleGlobalKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault();
        saveAndExport();
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
        // Precios: Prioridad Mayorista -> Distribuidor -> Minorista (Opcional, en tactico suele ser manual)
        // Por ahora tomamos un precio base si existe, o 0.
        // Asumimos que el backend no envia precios aun en la lista simple, o si?
        // Revisaremos el store. Si no, 0.
        item.precio_unitario = prod.precio_minorista || prod.precio_sugerido || 0; 
    }
};

const saveAndExport = async () => {
    if (!clienteId.value) return alert('Seleccione un cliente');
    
    const validItems = items.value.filter(i => i.producto_id && i.cantidad > 0);
    if (validItems.length === 0) return alert('Agregue al menos un producto valido');

    try {
        isSaving.value = true;
        
        const payload = {
            cliente_id: clienteId.value,
            fecha: new Date(fecha.value), // ISO conversion handled by JSON stringify usually, but explicitly better
            nota: nota.value,
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
        const clienteNombre = clientesStore.clientes.find(c => c.id === clienteId.value)?.razon_social || 'Cliente';
        link.setAttribute('download', `Pedido_${clienteNombre}_${fecha.value}.xlsx`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        
        // Reset form? Optional.
        if (confirm('Pedido generado con éxito. ¿Limpiar formulario?')) {
            items.value = [];
            addItem();
            nota.value = '';
            // clienteId.value = null; // Keep client select for speed? No, clean.
             clienteId.value = null;
        }

    } catch (error) {
        console.error(error);
        alert('Error al generar pedido: ' + (error.response?.data?.detail || error.message));
    } finally {
        isSaving.value = false;
    }
};

// Key Handling for Grid
const handleKeydown = (e, index) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        saveAndExport();
    }
    // Si es Enter en el ultimo campo de la ultima fila, agregar nueva
    if (e.key === 'Enter' && index === items.value.length - 1) {
        // Check field? Nah, just add row if validated
        addItem();
    }
};

</script>

<template>
    <div class="h-full flex flex-col bg-[#022c22] text-gray-100 p-4 overflow-hidden">
        
        <!-- Header -->
        <header class="flex justify-between items-center mb-6 border-b border-emerald-900/50 pb-4">
            <div>
                <h1 class="text-2xl font-bold text-emerald-400">Cargador Táctico <span class="text-emerald-600/60 text-sm">v5.3</span></h1>
                <p class="text-emerald-200/50 text-xs">Entrada rápida de pedidos y generación de Excel</p>
            </div>
            <div class="flex gap-4 items-end">
                <div class="text-right">
                    <div class="text-xs text-emerald-400/70 uppercase tracking-widest">Total Pedido</div>
                    <div class="text-3xl font-mono text-emerald-400 font-bold">{{ total.toLocaleString('es-AR', {style: 'currency', currency: 'ARS'}) }}</div>
                </div>
                <button 
                    @click="saveAndExport"
                    :disabled="isSaving"
                    class="h-12 px-6 bg-emerald-600 text-white font-bold rounded hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-emerald-900/50 border border-emerald-500/30"
                >
                    <span v-if="isSaving" class="animate-spin">⏳</span>
                    <span v-else>💾 GUARDAR Y EXPORTAR (F10)</span>
                </button>
            </div>
        </header>

        <!-- Form Header -->
        <section class="grid grid-cols-12 gap-4 mb-6 bg-[#064e3b]/40 p-4 rounded-lg shadow-sm border border-emerald-500/20 backdrop-blur-sm">
            <div class="col-span-2">
                <label class="block text-xs font-bold text-emerald-500/80 mb-1">FECHA</label>
                <input type="date" v-model="fecha" class="w-full bg-[#022c22] border border-emerald-800 rounded p-2 text-emerald-100 focus:border-emerald-500 outline-none hover:border-emerald-600 transition-colors">
            </div>
            
            <div class="col-span-10 lg:col-span-5">
                 <!-- Cliente Select -->
                 <SmartSelect 
                    v-model="clienteId"
                    :options="clientesStore.clientes.map(c => ({id: c.id, nombre: c.razon_social, cuit: c.cuit}))"
                    label="CLIENTE"
                    placeholder="Buscar Cliente / CUIT..."
                    :allow-create="false"
                    :required="true"
                    class="text-gray-900" 
                 />
                 <!-- Note: SmartSelect internal input has its own bg styling, might conflict if transparent -->
            </div>

            <div class="col-span-12 lg:col-span-5">
                <label class="block text-xs font-bold text-emerald-500/80 mb-1">NOTA INTERNA / O.C.</label>
                <input 
                    type="text" 
                    v-model="nota" 
                    placeholder="Opcional: Nro Orden Compra, Entrega Jueves..." 
                    class="w-full bg-[#022c22] border border-emerald-800 rounded p-2 text-emerald-100 placeholder-emerald-800/50 focus:border-emerald-500 outline-none transition-colors"
                >
            </div>
        </section>

        <!-- Grid -->
        <section class="flex-1 overflow-auto bg-[#064e3b]/20 rounded-lg border border-emerald-900/50 relative">
            <table class="w-full text-left border-collapse">
                <thead class="bg-[#022c22] sticky top-0 z-10 text-xs uppercase text-emerald-500/80 font-bold border-b border-emerald-900">
                    <tr>
                        <th class="p-3 w-12 text-center">#</th>
                        <th class="p-3 w-6/12">Producto</th>
                        <th class="p-3 w-2/12 text-right">Cantidad</th>
                        <th class="p-3 w-2/12 text-right">Precio Unit.</th>
                        <th class="p-3 w-2/12 text-right">Subtotal</th>
                        <th class="p-3 w-12"></th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-emerald-900/30">
                    <tr v-for="(item, index) in items" :key="index" class="group hover:bg-emerald-900/20 transition-colors">
                        <td class="p-2 text-center text-emerald-700 font-mono">{{ index + 1 }}</td>
                        <td class="p-2">
                             <!-- text-gray-900 forces black text for the input inside smart select which usually has white bg -->
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
                                class="w-full bg-transparent border-b border-emerald-900/30 text-right p-1 focus:border-emerald-500 outline-none font-mono text-emerald-100 font-bold"
                                min="0.1" step="any"
                            >
                        </td>
                        <td class="p-2">
                             <input 
                                type="number" 
                                v-model.number="item.precio_unitario"
                                class="w-full bg-transparent border-b border-emerald-900/30 text-right p-1 focus:border-emerald-500 outline-none font-mono text-emerald-300"
                                min="0" step="0.01"
                                @keydown="(e) => handleKeydown(e, index)"
                            >
                        </td>
                        <td class="p-2 text-right font-mono font-bold text-white">
                            {{ (item.cantidad * item.precio_unitario).toLocaleString('es-AR', {minimumFractionDigits: 2}) }}
                        </td>
                        <td class="p-2 text-center">
                            <button @click="removeItem(index)" class="text-emerald-800 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <div class="p-4 border-t border-emerald-900/30">
                <button @click="addItem" class="text-emerald-500 text-sm font-bold hover:text-emerald-300 transition-colors flex items-center gap-2 hover:bg-emerald-900/20 px-3 py-2 rounded">
                    <i class="fa-solid fa-plus"></i> Agregar Fila (Enter)
                </button>
            </div>
        </section>

    </div>
</template>

<style scoped>
/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
input[type=number] {
  -moz-appearance: textfield;
}
</style>
