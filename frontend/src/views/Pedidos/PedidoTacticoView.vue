<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useClientesStore } from '@/stores/clientes';
import { useProductosStore } from '@/stores/productos';
import SmartSelect from '@/components/ui/SmartSelect.vue';
import pedidosService from '@/services/pedidos';

const clientesStore = useClientesStore();
const productosStore = useProductosStore();

const fecha = ref(new Date().toISOString().split('T')[0]);
const clienteId = ref(null);
const nota = ref('');
const oc = ref('');
const items = ref([]);
const isSaving = ref(false);
const isCalculatingPrice = ref(false);

// Descuento Global
const descuentoGlobalPorcentaje = ref(0);
const descuentoGlobalImporte = ref(0);

const evaluateExpression = (expr) => {
    if (typeof expr !== 'string') return expr;
    try {
        if (/[^0-9+\-*/().\s]/.test(expr)) return parseFloat(expr) || 0;
        return Function(`'use strict'; return (${expr})`)();
    } catch (e) {
        return parseFloat(expr) || 0;
    }
};

// Modals State
const showLookup = ref(false);
const showInspector = ref(false);
const clienteForInspector = ref(null);

// --- Totals Logic ---
const subtotalBruto = computed(() => {
    return items.value.reduce((acc, item) => acc + (item.subtotal || 0), 0);
});

const totalNeto = computed(() => {
    return Math.max(0, subtotalBruto.value - descuentoGlobalImporte.value);
});

const clienteSeleccionado = computed(() => {
    return clientesStore.clientes.find(c => c.id === clienteId.value);
});

const clienteEsVerde = computed(() => {
    const c = clienteSeleccionado.value;
    if (!c) return false;
    const hasCuit = c.cuit && c.cuit.length >= 11;
    const hasAddress = c.domicilio_fiscal_resumen || (c.domicilios && c.domicilios.some(d => d.es_fiscal && d.activo));
    const hasCond = !!c.condicion_iva_id || !!c.condicion_iva;
    return hasCuit && hasAddress && hasCond;
});

// Lifecycle
onMounted(async () => {
    await Promise.all([
        clientesStore.fetchClientes(),
        productosStore.fetchProductos()
    ]);
    addItem();
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
        descuento_porcentaje: 0,
        descuento_importe: 0,
        subtotal: 0
    });
};

const removeItem = (index) => {
    items.value.splice(index, 1);
    if (items.value.length === 0) addItem();
};

const handleProductChange = async (item, newId) => {
    item.producto_id = newId;
    if (!newId || !clienteId.value) return;

    try {
        isCalculatingPrice.value = true;
        const res = await pedidosService.cotizar({
            cliente_id: clienteId.value,
            producto_id: newId,
            cantidad: item.cantidad || 1
        });
        
        if (res.precio_final_sugerido !== undefined) {
            item.precio_unitario = res.precio_final_sugerido;
            item.info_precio = res.info_debug;
        } else {
            const prod = productosStore.productos.find(p => p.id === newId);
            if (prod) item.precio_unitario = prod.precio_minorista || 0;
        }
        recalculateItem(item);
    } catch (e) {
        console.error("Error cotizando:", e);
    } finally {
        isCalculatingPrice.value = false;
    }
};

const recalculateItem = (item, source = 'price') => {
    const qty = parseFloat(item.cantidad) || 0;
    const price = parseFloat(item.precio_unitario) || 0;
    const bruto = qty * price;

    if (source === 'percent') {
        item.descuento_importe = Number((bruto * (item.descuento_porcentaje / 100)).toFixed(4));
    } else if (source === 'amount') {
        item.descuento_porcentaje = bruto !== 0 ? Number(((item.descuento_importe / bruto) * 100).toFixed(4)) : 0;
    } else if (source === 'price' || source === 'qty') {
        // Al cambiar precio/cant, mantenemos el porcentaje y actualizamos el importe
        item.descuento_importe = Number((bruto * (item.descuento_porcentaje / 100)).toFixed(4));
    }

    item.subtotal = Number((bruto - item.descuento_importe).toFixed(4));
};

const handleNumericInput = (item, field, value) => {
    const evaluated = evaluateExpression(value);
    item[field] = evaluated;
    
    let source = 'price';
    if (field === 'descuento_porcentaje') source = 'percent';
    if (field === 'descuento_importe') source = 'amount';
    if (field === 'cantidad') source = 'qty';
    
    recalculateItem(item, source);
};

// --- Global Discount Logic ---
const handleGlobalDiscountInput = (field, value) => {
    const val = evaluateExpression(value);
    if (field === 'percent') {
        descuentoGlobalPorcentaje.value = val;
        descuentoGlobalImporte.value = Number((subtotalBruto.value * (val / 100)).toFixed(4));
    } else {
        descuentoGlobalImporte.value = val;
        descuentoGlobalPorcentaje.value = subtotalBruto.value !== 0 ? Number(((val / subtotalBruto.value) * 100).toFixed(4)) : 0;
    }
};

// Recalcular importe global si cambia el bruto (ej: agregar/quitar items)
watch(subtotalBruto, (newBruto) => {
    descuentoGlobalImporte.value = Number((newBruto * (descuentoGlobalPorcentaje.value / 100)).toFixed(4));
});

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
            descuento_global_porcentaje: descuentoGlobalPorcentaje.value,
            descuento_global_importe: descuentoGlobalImporte.value,
            items: validItems.map(i => ({
                producto_id: i.producto_id,
                cantidad: parseFloat(i.cantidad),
                precio_unitario: parseFloat(i.precio_unitario),
                descuento_porcentaje: parseFloat(i.descuento_porcentaje),
                descuento_importe: parseFloat(i.descuento_importe)
            }))
        };

        const blob = await pedidosService.createTactico(payload);
        
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
            oc.value = '';
            clienteId.value = null;
            descuentoGlobalPorcentaje.value = 0;
            descuentoGlobalImporte.value = 0;
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

// Lookup Handlers
const onLookupSelect = (cliente) => {
    clienteId.value = cliente.id;
};

const onLookupEdit = (cliente) => {
    clienteForInspector.value = cliente;
    showInspector.value = true;
    showLookup.value = false;
};

const onLookupDelete = async (cliente) => {
    try {
        await clientesStore.deleteCliente(cliente.id);
    } catch (e) {
        alert("Error eliminando: " + e.message);
    }
};

const onLookupRefreshAndSelect = async (newId) => {
    await clientesStore.fetchClientes();
    const cliente = clientesStore.clientes.find(c => c.id === newId);
    if (cliente) {
        onLookupSelect(cliente);
        showLookup.value = false;
    }
};

const onInspectorSave = (result) => {
    // [GY-UX] If we saved a client, select it immediately to reflect changes
    if (result && result.id) {
        clienteId.value = result.id;
    }
};

const onInspectorClose = async () => {
    showInspector.value = false;
    clienteForInspector.value = null;
    // [GY-FIX] Removed redundant fetchClientes() which was overwriting updated store data with stale cache
    // await clientesStore.fetchClientes();
    if (!clienteId.value) showLookup.value = true;
};
</script>

<template>
    <div class="h-full flex flex-col bg-[#020617] text-gray-100 p-4 overflow-hidden font-sans">
        
        <!-- Header -->
        <header class="flex justify-between items-center mb-6 border-b border-indigo-900/50 pb-4">
            <div>
                <h1 class="text-2xl font-bold text-indigo-400">Cargador Táctico <span class="text-indigo-600/60 text-sm">v5.5</span></h1>
                <p class="text-indigo-200/50 text-xs">Precisión 4 decimales • Descuentos Globales (F3)</p>
            </div>
            <div class="flex gap-4 items-end">
                <div class="text-right">
                    <div class="text-xs text-indigo-400/70 uppercase tracking-widest">Total Neto</div>
                    <div class="text-3xl font-mono text-emerald-400 font-bold">{{ totalNeto.toLocaleString('es-AR', {style: 'currency', currency: 'ARS'}) }}</div>
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
                 
                 <button v-if="clienteId" @click.stop="openInspectorForCurrent" class="absolute top-8 right-10 text-xs text-slate-400 hover:text-white px-2 py-1">
                    <i class="fa-solid fa-eye"></i>
                </button>
            </div>

            <div class="col-span-12 lg:col-span-5 flex gap-2">
                <div class="w-1/3">
                    <label class="block text-xs font-bold text-slate-500 mb-1">O.C.</label>
                    <input type="text" v-model="oc" placeholder="Orden Compra" class="w-full bg-[#1e293b] border border-slate-700 rounded p-2 text-white focus:border-indigo-500 outline-none font-bold text-center">
                </div>
                <div class="flex-1">
                    <label class="block text-xs font-bold text-slate-500 mb-1">NOTA INTERNA</label>
                    <input type="text" v-model="nota" placeholder="Observaciones..." class="w-full bg-[#1e293b] border border-slate-700 rounded p-2 text-white focus:border-indigo-500 outline-none">
                </div>
            </div>
        </section>

        <!-- Grid -->
        <section class="flex-1 overflow-auto bg-[#0f172a] rounded-lg border border-slate-800 relative mb-4">
            <table class="w-full text-left border-collapse">
                <thead class="bg-[#1e293b] sticky top-0 z-10 text-xs uppercase text-slate-400 font-bold border-b border-slate-700">
                    <tr>
                        <th class="p-3 w-10 text-center">#</th>
                        <th class="p-3 w-5/12">Producto</th>
                        <th class="p-3 w-32 text-right">Cantidad</th>
                        <th class="p-3 w-40 text-right">Precio Unit. (4 dec)</th>
                        <th class="p-3 w-44 text-right">Descuento (% / $)</th>
                        <th class="p-3 w-32 text-right">Subtotal</th>
                        <th class="p-3 w-10"></th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-800">
                    <tr v-for="(item, index) in items" :key="index" class="group hover:bg-slate-800/50 transition-colors">
                        <td class="p-2 text-center text-slate-600 font-mono">{{ index + 1 }}</td>
                        <td class="p-2">
                            <SmartSelect 
                                v-model="item.producto_id"
                                :options="productosStore.productos.map(p => ({id: p.id, nombre: p.nombre, sku: p.sku}))" 
                                @update:modelValue="(val) => handleProductChange(item, val)"
                                placeholder="Producto..."
                                :allow-create="false"
                                class="w-full text-gray-900" 
                            />
                        </td>
                        <td class="p-2">
                             <input type="text" :value="item.cantidad" @change="(e) => handleNumericInput(item, 'cantidad', e.target.value)" class="w-full bg-transparent border-b border-transparent hover:border-slate-600 focus:border-indigo-500 text-right p-1 outline-none font-mono text-emerald-300 font-bold" placeholder="0">
                        </td>
                        <td class="p-2">
                              <input type="text" :value="item.precio_unitario" @change="(e) => handleNumericInput(item, 'precio_unitario', e.target.value)" class="w-full bg-transparent border-b border-transparent hover:border-slate-600 focus:border-indigo-500 text-right p-1 outline-none font-mono text-indigo-300" placeholder="0.0000">
                              <div v-if="item.info_precio" class="text-[0.6rem] text-slate-500 text-right truncate" :title="item.info_precio">{{ item.info_precio }}</div>
                        </td>
                        <td class="p-2">
                            <div class="flex gap-1 items-center">
                                <input type="text" :value="item.descuento_porcentaje" @change="(e) => handleNumericInput(item, 'descuento_porcentaje', e.target.value)" class="w-16 bg-slate-900/50 border border-slate-700/50 rounded text-right p-1 outline-none font-mono text-rose-400 text-xs" placeholder="0%">
                                <span class="text-slate-700">/</span>
                                <input type="text" :value="item.descuento_importe" @change="(e) => handleNumericInput(item, 'descuento_importe', e.target.value)" class="flex-1 bg-slate-900/50 border border-slate-700/50 rounded text-right p-1 outline-none font-mono text-rose-300 text-xs" placeholder="$ 0">
                            </div>
                        </td>
                        <td class="p-2 text-right font-mono font-bold text-white">
                            {{ (item.subtotal || 0).toLocaleString('es-AR', {minimumFractionDigits: 2}) }}
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
                    <i class="fa-solid fa-plus"></i> Agregar Fila
                </button>
            </div>
        </section>

        <!-- Footer / Totales -->
        <section class="grid grid-cols-12 gap-4 bg-[#0f172a] p-6 rounded-lg border border-slate-800 shadow-xl">
            <div class="col-span-8 flex flex-col justify-center">
                <div class="text-xs text-slate-500 italic">
                    * Todos los precios e importes mantienen hasta 4 decimales internos para asegurar paridad con facturación.
                </div>
            </div>
            <div class="col-span-4 space-y-3">
                <div class="flex justify-between items-center text-slate-400">
                    <span class="text-xs uppercase font-bold tracking-wider">Subtotal Bruto</span>
                    <span class="font-mono">{{ subtotalBruto.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</span>
                </div>
                
                <div class="flex justify-between items-center bg-rose-900/10 p-2 rounded border border-rose-900/20">
                    <span class="text-xs uppercase font-bold text-rose-400">Descuento Global</span>
                    <div class="flex gap-2 items-center">
                        <input type="text" :value="descuentoGlobalPorcentaje" @change="(e) => handleGlobalDiscountInput('percent', e.target.value)" class="w-16 bg-slate-900 border border-slate-700 rounded text-right p-1 outline-none font-mono text-rose-400 text-sm" placeholder="0%">
                        <input type="text" :value="descuentoGlobalImporte" @change="(e) => handleGlobalDiscountInput('amount', e.target.value)" class="w-28 bg-slate-900 border border-slate-700 rounded text-right p-1 outline-none font-mono text-rose-300 text-sm" placeholder="$ 0">
                    </div>
                </div>

                <div class="flex justify-between items-center border-t border-slate-700 pt-3">
                    <span class="text-lg font-bold text-indigo-400">TOTAL NETO</span>
                    <span class="text-2xl font-mono font-bold text-emerald-400">{{ totalNeto.toLocaleString('es-AR', {style: 'currency', currency: 'ARS'}) }}</span>
                </div>
            </div>
        </section>

        <!-- Modals -->
        <ClientLookup :show="showLookup" :clientes="clientesStore.clientes" @close="showLookup = false" @select="onLookupSelect" @edit="onLookupEdit" @delete="onLookupDelete" @refresh-and-select="onLookupRefreshAndSelect" />
        <div v-if="showInspector" class="fixed inset-0 z-[60] flex justify-end bg-black/50 backdrop-blur-sm" @click.self="onInspectorClose">
            <div class="w-full max-w-2xl h-full bg-slate-900 border-l border-slate-700 shadow-2xl overflow-y-auto">
                <ClienteInspector v-if="clienteForInspector" :cliente="clienteForInspector" @close="onInspectorClose" @save="onInspectorSave" />
            </div>
        </div>
    </div>
</template>

<style scoped>
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type=number] {
  -moz-appearance: textfield;
}
</style>
