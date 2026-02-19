<template>
  <div class="fixed inset-0 z-[99999] bg-white flex flex-col overflow-hidden" v-if="propRemito">
    <!-- Toolbar (No-Print) -->
    <div class="bg-slate-800 text-white p-4 flex justify-between items-center print:hidden shrink-0 shadow-xl">
      <div class="flex items-center gap-4">
          <h2 class="font-bold text-lg"><i class="fas fa-print mr-2"></i> Vista de Impresión</h2>
          <span class="text-xs bg-blue-600 px-2 py-1 rounded">Remito #{{ propRemito.numero_legal || 'BORRADOR' }}</span>
      </div>
      <div class="flex gap-3">
        <button @click="$emit('close')" class="px-4 py-2 hover:bg-slate-700 rounded text-slate-300 transition">
            Cerrar
        </button>
        <button @click="print" class="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded font-bold shadow-lg transition">
            <i class="fas fa-print mr-2"></i> Imprimir
        </button>
      </div>
    </div>

    <!-- DOCUMENT CANVAS (A4) -->
    <div class="flex-1 overflow-auto bg-slate-200 p-8 flex justify-center print:p-0 print:bg-white print:overflow-visible">
        <div class="bg-white w-[210mm] min-h-[297mm] p-[10mm] shadow-2xl print:shadow-none print:w-full print:min-h-0 text flex flex-col text-slate-900 font-sans relative">
            
            <!-- WATERMARK: BORRADOR -->
            <div v-if="propRemito.estado === 'BORRADOR'" class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.05] print:opacity-[0.05]">
                <span class="text-[150px] font-black -rotate-45 uppercase select-none text-slate-900">BORRADOR</span>
            </div>

            <!-- HEADER -->
            <header class="border-b-2 border-slate-900 pb-4 mb-6 flex justify-between items-start">
                <div>
                   <!-- LOGO PLACEHOLDER -->
                   <div class="h-16 w-48 bg-slate-900 text-white flex items-center justify-center font-black tracking-tighter text-2xl mb-2">
                       SONIDO LIQUIDO
                   </div>
                   <p class="text-xs font-bold uppercase tracking-widest text-slate-500">Módulo de Logística</p>
                   <p class="text-sm mt-2 font-medium">Av. Siempreviva 123, Córdoba</p>
                   <p class="text-sm text-slate-600">IVA Responsable Inscripto</p>
                </div>
                <div class="text-right">
                    <div class="border border-slate-900 px-4 py-2 rounded mb-2 inline-block">
                        <h1 class="text-2xl font-black uppercase tracking-widest">{{ isMasked ? 'DOC. TRANSPORTE' : 'REMITO' }}</h1>
                        <p class="text-center text-xs font-bold">{{ isMasked ? 'VINCULADO A FACTURA' : 'DOCUMENTO NO VÁLIDO COMO FACTURA' }}</p>
                    </div>
                    <div class="text-sm space-y-1 mt-2">
                        <p><span class="font-bold">N°:</span> {{ propRemito.numero_legal || '------' }}</p>
                        <p><span class="font-bold">Fecha Emisión:</span> {{ formatDate(propRemito.fecha_salida || new Date()) }}</p>
                        <p><span class="font-bold">Ref. Pedido:</span> #{{ pedido?.id }} (OC: {{ pedido?.oc || 'S/D' }})</p>
                        <p v-if="propRemito.cae" class="text-xs mt-1 font-mono">
                           CAE: {{ propRemito.cae }} <br> 
                           Vto: {{ formatDate(propRemito.vto_cae) }}
                        </p>
                    </div>
                </div>
                
                <!-- LABEL X -->
                <div class="absolute top-[10mm] left-1/2 -translate-x-1/2 border border-slate-900 bg-white w-10 h-10 flex items-center justify-center text-xl font-bold rounded">
                    X
                </div>
            </header>

            <!-- INFO CLIENTE / ENTREGA -->
            <div class="grid grid-cols-2 gap-8 mb-8 text-sm">
                <div class="border rounded p-3">
                    <h3 class="font-bold uppercase text-xs text-slate-500 mb-2 border-b pb-1">Destinatario</h3>
                    <p class="font-bold text-lg leading-tight mb-1">{{ pedido?.cliente?.razon_social || 'Consumidor Final' }}</p>
                    <p class="text-slate-600">CUIT: {{ pedido?.cliente?.cuit || '---' }}</p>
                    <p class="text-slate-600">{{ getFiscalAddress(pedido?.cliente) }}</p>
                </div>
                <div class="border rounded p-3 bg-slate-50">
                    <h3 class="font-bold uppercase text-xs text-slate-500 mb-2 border-b pb-1">Lugar de Entrega & Transporte</h3>
                    <p class="font-bold text-base mb-1"><i class="fas fa-map-marker-alt text-slate-400 mr-1"></i> {{ getDeliveryAddress(propRemito.domicilio_entrega_id) }}</p>
                    <p class="mt-2 text-slate-700">
                        <span class="font-bold text-xs uppercase text-slate-500 block">Transportista</span>
                        {{ getTransportName(propRemito.transporte_id) }}
                    </p>
                </div>
            </div>

            <!-- ITEMS TABLE -->
            <div class="flex-1">
                <table class="w-full text-sm border-collapse">
                    <thead>
                        <tr class="bg-slate-900 text-white uppercase text-xs tracking-widest">
                            <th class="py-2 px-3 text-left w-16">Cant.</th>
                            <th class="py-2 px-3 text-left">SKU</th>
                            <th class="py-2 px-3 text-left">Descripción</th>
                            <th class="py-2 px-3 text-center w-24">Bultos</th>
                            <th class="py-2 px-3 text-left w-24">Control</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-300">
                        <tr v-for="item in propRemito.items" :key="item.id" class="border-b border-slate-200">
                            <td class="py-3 px-3 font-bold font-mono text-base">{{ item.cantidad }}</td>
                            <td class="py-3 px-3 text-slate-600 font-mono text-xs">{{ getProductSku(item.pedido_item_id) }}</td>
                            <td class="py-3 px-3 uppercase text-slate-800 font-medium">{{ getProductName(item.pedido_item_id) }}</td>
                            <td class="py-3 px-3 border-l border-slate-200"></td>
                            <td class="py-3 px-3 border-l border-slate-200"></td>
                        </tr>
                        <!-- Empty rows filler -->
                        <tr v-for="n in Math.max(0, 10 - propRemito.items.length)" :key="'fill_'+n" class="h-10">
                             <td class="border-l border-slate-100"></td>
                             <td></td><td></td>
                             <td class="border-l border-slate-100"></td>
                             <td class="border-l border-slate-100"></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- FOOTER FIRMAS -->
            <div class="mt-8 border-t-2 border-slate-900 pt-4 grid grid-cols-2 gap-10">
               <div>
                  <div class="h-24 border border-dashed border-slate-400 rounded bg-slate-50 mb-1"></div>
                  <p class="text-center text-xs uppercase font-bold text-slate-500">Recibí Conforme (Firma y Aclaración)</p>
               </div>
               <div class="text-xs text-slate-500 space-y-1 text-right">
                  <p>C.A.I. N°: XXXXXXXXXXXXXX</p>
                  <p>Fecha Vto: XX/XX/XXXX</p>
                  <p>Original: Blanco / Duplicado: Color</p>
               </div>
            </div>

        </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
    propRemito: Object,
    pedido: Object,
    logisticaStore: Object, // To resolve names
    clientDomicilios: Array,
    pedidoItems: Array
});

const emit = defineEmits(['close']);

const isMasked = computed(() => {
    const num = props.propRemito?.numero_legal || '';
    return num.toUpperCase().includes('FACTURA');
});

// --- HELPERS ---
const formatDate = (dateStr) => {
    if(!dateStr) return '---';
    return new Date(dateStr).toLocaleDateString();
};

const getFiscalAddress = (cliente) => {
    if (!cliente || !cliente.domicilios) return '---';
    const fiscal = cliente.domicilios.find(d => d.tipo === 'FISCAL') || cliente.domicilios[0];
    return fiscal ? `${fiscal.direccion} - ${fiscal.localidad} (${fiscal.provincia})` : '---';
};

const getDeliveryAddress = (id) => {
    const d = props.clientDomicilios.find(addr => addr.id === id);
    return d ? `${d.direccion}, ${d.localidad}` : 'Dirección Desconocida';
};

const getTransportName = (id) => {
    const t = props.logisticaStore.transportOptions.find(opt => opt.id === id);
    return t ? t.nombre : '---';
};

const getProductName = (pItemId) => {
    const pItem = props.pedidoItems.find(i => i.id === pItemId);
    return pItem?.producto?.nombre || 'Item Desconocido';
};

const getProductSku = (pItemId) => {
    const pItem = props.pedidoItems.find(i => i.id === pItemId);
    return pItem?.producto?.sku || '---';
};

const print = () => {
    window.print();
};
</script>

<style>
@media print {
  @page { margin: 0; size: A4; }
  body { background: white; }
}
</style>
