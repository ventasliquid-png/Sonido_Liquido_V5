<template>
  <div class="h-full flex flex-col bg-gray-900 text-gray-100 overflow-hidden">
    <!-- Header -->
    <header class="bg-gray-800 border-b border-gray-700 px-6 py-4 flex justify-between items-center shrink-0">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
          <i class="fas fa-file-invoice-dollar text-xl"></i>
        </div>
        <div>
          <h1 class="text-xl font-bold font-display tracking-tight text-white">Centro de Liquidación</h1>
          <p class="text-xs text-gray-400">Asistente Fiscal V5 - Modo Espejo ARCA</p>
        </div>
      </div>
      <div>
        <span class="px-3 py-1 bg-yellow-500/10 border border-yellow-500/30 text-yellow-500 rounded text-xs animate-pulse">
          <i class="fas fa-exclamation-triangle mr-1"></i> WSFEv1 Offline (Por Carga Manual)
        </span>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <!-- SIDEBAR: Listado de Facturas / Borradores -->
      <aside class="w-80 border-r border-gray-800 flex flex-col bg-gray-900 shrink-0">
        <div class="p-4 border-b border-gray-800">
          <h2 class="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-3">Comprobantes</h2>
          <!-- Could add a search input here -->
        </div>
        <div class="flex-1 overflow-y-auto p-2 space-y-1">
          <div 
            v-for="fact in facturas" :key="fact.id"
            @click="selectFactura(fact)"
            class="p-3 rounded-lg border cursor-pointer transition-colors"
            :class="selectedFactura?.id === fact.id ? 'bg-indigo-500/10 border-indigo-500 text-indigo-100' : 'bg-gray-800 border-transparent hover:bg-gray-700 text-gray-300'"
          >
            <div class="flex justify-between items-start mb-1">
              <span class="text-xs font-mono px-1.5 py-0.5 rounded bg-gray-900 border border-gray-700">
                {{ (fact.tipo_comprobante || 'S/D').replace('FACTURA_', 'F-') }}
              </span>
              <span class="text-xs" :class="getStatusColor(fact.estado)">
                {{ fact.estado }}
              </span>
            </div>
            <div class="font-medium text-sm truncate">Total: ${{ formatNumber(fact.total) }}</div>
            <div class="text-xs text-gray-500 mt-1">{{ formatDate(fact.created_at) }}</div>
          </div>
        </div>
      </aside>

      <!-- MAIN CONTENT: Vista de Liquidación (AFIP Mirror) -->
      <main class="flex-1 overflow-y-auto p-8 relative">
        <div v-if="selectedFactura" class="max-w-4xl mx-auto">
          <!-- Banner Superior Info -->
          <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 mb-6 flex justify-between items-center shadow-lg">
            <div>
              <h2 class="text-lg font-bold">Liquidación #{{ shortId(selectedFactura.id) }}</h2>
              <p class="text-sm text-gray-400 font-mono mt-1">Ref Pedido: {{ selectedFactura.pedido_id || 'N/A' }}</p>
            </div>
            <div class="text-right">
              <div class="text-3xl font-black text-indigo-400">${{ formatNumber(selectedFactura.total) }}</div>
              <div class="text-xs text-gray-500 uppercase font-semibold tracking-wider">Total a Facturar</div>
            </div>
          </div>

          <!-- MODO ESPEJO AFIP -->
          <div class="border border-indigo-500/20 rounded-xl overflow-hidden shadow-2xl bg-gray-900 border-2">
            <div class="bg-indigo-900/30 px-6 py-3 border-b border-indigo-500/20 flex justify-between items-center">
              <h3 class="font-display font-medium text-indigo-200">
                <i class="fas fa-copy mr-2"></i> Plantilla Copia-Fácil (AFIP)
              </h3>
              <button @click="copyAllLines" class="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 rounded text-xs transition">
                Copiar Todo Txt
              </button>
            </div>
            
            <div class="p-6">
              <!-- CONCEPTOS A INCLUIR -->
              <table class="w-full text-sm text-left font-mono">
                <thead>
                  <tr class="text-gray-500 border-b border-gray-800">
                    <th class="pb-2 font-medium">Concepto</th>
                    <th class="pb-2 font-medium text-right">Cant</th>
                    <th class="pb-2 font-medium text-right">P. Unitario Neto</th>
                    <th class="pb-2 font-medium text-right">Alicuota IVA</th>
                    <th class="pb-2 font-medium text-right">Subtotal Neto</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in selectedFactura.items" :key="item.id" class="border-b border-gray-800/50 hover:bg-gray-800/20 transition-colors">
                    <td class="py-3 text-gray-200 group">
                      {{ item.descripcion }} 
                      <i @click="copy(item.descripcion)" class="fas fa-paste ml-2 text-gray-600 hover:text-indigo-400 cursor-pointer opacity-0 group-hover:opacity-100 transition"></i>
                    </td>
                    <td class="py-3 text-right text-gray-400">{{ item.cantidad }}</td>
                    <td class="py-3 text-right group">
                      $ {{ formatNumber(item.precio_unitario_neto) }}
                      <i @click="copy(formatNumberNoDot(item.precio_unitario_neto))" class="fas fa-paste ml-2 text-gray-600 hover:text-indigo-400 cursor-pointer opacity-0 group-hover:opacity-100 transition"></i>
                    </td>
                    <td class="py-3 text-right text-yellow-500/80">{{ item.alicuota_iva }}%</td>
                    <td class="py-3 text-right group">
                      $ {{ formatNumber(item.subtotal_neto) }}
                      <i @click="copy(formatNumberNoDot(item.subtotal_neto))" class="fas fa-paste ml-2 text-gray-600 hover:text-indigo-400 cursor-pointer opacity-0 group-hover:opacity-100 transition"></i>
                    </td>
                  </tr>
                </tbody>
              </table>

              <!-- RESUMEN IMPUESTOS -->
              <div class="mt-8 flex justify-end">
                <div class="w-72 bg-gray-800 p-4 rounded-lg border border-gray-700 shadow-inner">
                  <div class="flex justify-between mb-1 text-sm"><span class="text-gray-400">Neto Gravado:</span> <span class="font-mono text-gray-200">$ {{ formatNumber(selectedFactura.neto_gravado) }}</span></div>
                  <div class="flex justify-between mb-1 text-sm"><span class="text-gray-400">Exento:</span> <span class="font-mono text-gray-200">$ {{ formatNumber(selectedFactura.exento) }}</span></div>
                  <div class="flex justify-between mb-1 text-sm"><span class="text-gray-400">IVA 21%:</span> <span class="font-mono text-gray-200">$ {{ formatNumber(selectedFactura.iva_21) }}</span></div>
                  <div class="flex justify-between mb-1 text-sm"><span class="text-gray-400">IVA 10.5%:</span> <span class="font-mono text-gray-200">$ {{ formatNumber(selectedFactura.iva_105) }}</span></div>
                  <div class="border-t border-gray-700 my-2 pt-2 flex justify-between font-bold">
                    <span class="text-gray-300">Total:</span> <span class="font-mono text-indigo-400 text-lg">$ {{ formatNumber(selectedFactura.total) }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- PANEL DE SELLADO CAE -->
            <div v-if="selectedFactura.estado === 'BORRADOR' || selectedFactura.estado === 'LIQUIDADA_MANUAL'" class="bg-gray-800 border-t border-gray-700 p-6">
              <h4 class="font-medium text-gray-300 mb-4"><i class="fas fa-shield-alt mr-2 text-green-500"></i> Sellar Factura (Devolución AFIP)</h4>
              
              <div class="grid grid-cols-4 gap-4 mb-4">
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Punto Vta</label>
                  <input v-model.number="selloData.punto_venta" type="number" class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none">
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Nro Comprobante</label>
                  <input v-model.number="selloData.numero_comprobante" type="number" class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none">
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">CAE</label>
                  <input v-model="selloData.cae" type="text" class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none placeholder-gray-600" placeholder="Ej: 7123...">
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Vto CAE</label>
                  <input v-model="selloData.vto_cae" type="date" class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none text-gray-300">
                </div>
              </div>

              <div class="flex justify-end gap-3">
                 <button @click="sellarFactura" :disabled="isSealing" class="bg-green-600 hover:bg-green-500 px-6 py-2 rounded text-sm font-medium transition disabled:opacity-50">
                   <i class="fas fa-check mr-2"></i> Confirmar Emisión
                 </button>
              </div>
            </div>
            
            <!-- VISTA SELLADA -->
            <div v-if="selectedFactura.estado === 'AUTORIZADA_AFIP'" class="bg-gray-800 border-t border-gray-700 p-6 flex flex-col items-center justify-center text-center">
                <div class="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center text-green-500 mb-3 text-3xl">
                  <i class="fas fa-check-circle"></i>
                </div>
                <h4 class="font-bold text-green-400">Factura Registrada</h4>
                <div class="text-sm text-gray-400 font-mono mt-2">
                  COMPROBANTE: {{ String(selectedFactura.punto_venta || 0).padStart(4, '0') }}-{{ String(selectedFactura.numero_comprobante || 0).padStart(8, '0') }} <br>
                  CAE: {{ selectedFactura.cae }} | Vto: {{ selectedFactura.vto_cae }}
                </div>
            </div>

          </div>

        </div>

        <div v-else class="h-full flex flex-col items-center justify-center text-gray-500">
          <i class="fas fa-file-invoice mb-4 text-4xl opacity-20"></i>
          <p>Seleccione un comprobante para iniciar la liquidación manual.</p>
        </div>
      </main>
    </div>

    <!-- Modal Logística Asíncrona -->
    <div v-if="showLogisticsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div class="bg-[#0a0f1a] border border-indigo-500/50 rounded-xl p-8 w-[550px] shadow-[0_0_50px_rgba(99,102,241,0.2)]">
        <h3 class="text-xl font-bold text-white mb-2"><i class="fas fa-truck-loading text-indigo-400 mr-3"></i> Documento de Transporte</h3>
        <p class="text-gray-400 text-sm mb-6 leading-relaxed">La factura ha sido emitida y validada con CAE. ¿Cómo se despachará la mercadería asociada a esta operación?</p>

        <div class="space-y-4">
          <button @click="resolveLogistics('RAR')" class="w-full text-left p-5 rounded-xl border-2 border-emerald-500/30 hover:border-emerald-500 bg-emerald-500/5 hover:bg-emerald-500/10 transition-all group flex gap-4 items-center">
            <div class="h-10 w-10 shrink-0 bg-emerald-900/50 rounded-full flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
                <i class="fas fa-file-signature"></i>
            </div>
            <div>
                <h4 class="font-bold text-emerald-400 tracking-wide text-sm mb-1">Generar Remito Amparado (RAR-V1)</h4>
                <p class="text-xs text-gray-400 line-clamp-2">Crea un remito formal estampado con la leyenda AFIP y el CAE. Obligatorio para transporte por expreso terrestre o logística propia.</p>
            </div>
          </button>
          
          <button @click="resolveLogistics('NONE')" class="w-full text-left p-5 rounded-xl border-2 border-gray-700/50 hover:border-gray-500 bg-gray-800/20 hover:bg-gray-800/60 transition-all group flex gap-4 items-center">
            <div class="h-10 w-10 shrink-0 bg-gray-800 rounded-full flex items-center justify-center text-gray-500 group-hover:text-white transition-colors">
                <i class="fas fa-store"></i>
            </div>
            <div>
                <h4 class="font-bold text-gray-300 group-hover:text-white tracking-wide text-sm mb-1">Despacho sin Remito Interno</h4>
                <p class="text-xs text-gray-500 line-clamp-2">Para entregas en Mostrador (solo llevan Factura) o ventas de MercadoLibre (viaja con Etiqueta de Correo). No se generará hoja de ruta.</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from '@/stores/notification';

const notificationStore = useNotificationStore();

const facturas = ref([]);
const selectedFactura = ref(null);
const isSealing = ref(false);
const showLogisticsModal = ref(false);

const selloData = ref({
  punto_venta: null,
  numero_comprobante: null,
  cae: '',
  vto_cae: ''
});

onMounted(async () => {
  await fetchFetchuras();
  window.addEventListener('keydown', handleGlobalKeydown);
});

const handleGlobalKeydown = (e) => {
  if (e.key === 'F10') {
    e.preventDefault();
    sellarFactura();
  }
};

const fetchFetchuras = async () => {
  await fetchFacturas();
};

const fetchFacturas = async () => {
  try {
    const { data } = await api.get('/facturacion/');
    facturas.value = data;
  } catch(e) {
    notificationStore.add('Error cargando facturas', 'error');
  }
};

const selectFactura = async (f) => {
  try {
    const { data } = await api.get(`/facturacion/${f.id}`);
    selectedFactura.value = data;
    // Reset form
    selloData.value = {
      punto_venta: data.punto_venta || null,
      numero_comprobante: data.numero_comprobante || null,
      cae: data.cae || '',
      vto_cae: data.vto_cae || ''
    };
  } catch(e) {
    notificationStore.add('Error al cargar detalle de factura.', 'error');
  }
};

const sellarFactura = async () => {
  if (!selloData.value.cae || !selloData.value.numero_comprobante || !selloData.value.punto_venta) {
    return notificationStore.add('Debe completar Punto Venta, Nro Comprobante y CAE para sellar.', 'warning');
  }

  isSealing.value = true;
  try {
    const payload = {
      cae: selloData.value.cae,
      vto_cae: selloData.value.vto_cae || null,
      punto_venta: selloData.value.punto_venta,
      numero_comprobante: selloData.value.numero_comprobante,
      estado: 'AUTORIZADA_AFIP'
    };
    const { data } = await api.patch(`/facturacion/${selectedFactura.value.id}/sellar`, payload);
    
    selectedFactura.value = data;
    
    // Update local list manually
    const ix = facturas.value.findIndex(x => x.id === data.id);
    if(ix !== -1) facturas.value[ix] = data;
    
    notificationStore.add('Factura Sellada Correctamente.', 'success');
    
    // Preguntar por logística asíncrona
    showLogisticsModal.value = true;
    
  } catch(e) {
    notificationStore.add('Error al sellar factura: ' + (e.response?.data?.detail || e.message), 'error');
  } finally {
    isSealing.value = false;
  }
};

const resolveLogistics = async (decision) => {
    if (decision === 'RAR') {
        try {
            notificationStore.add('Generando Remito RAR-V1...', 'info');
            // Delegamos al backend la inteligencia de vincular.
            await api.post(`/remitos/puente/desde_factura/${selectedFactura.value.id}`);
            notificationStore.add('Remito originado. Ver en Tablero de Logística.', 'success');
        } catch(e) {
            notificationStore.add('Error generando puente logístico: ' + e.message, 'error');
        }
    } else {
        notificationStore.add('Operación liquidada por mostrador/externo.', 'info');
    }
    showLogisticsModal.value = false;
};

// Utilities
const copy = async (text) => {
  try {
    await navigator.clipboard.writeText(String(text));
    notificationStore.add(`Copiado: ${text}`, 'info');
  } catch (err) {
    console.error('Failed to copy: ', err);
  }
};

const copyAllLines = () => {
  if (!selectedFactura.value || !selectedFactura.value.items) return;
  const lines = selectedFactura.value.items.map(item => {
    return `${item.descripcion}\t${item.cantidad}\t${formatNumberNoDot(item.precio_unitario_neto)}\t${item.alicuota_iva}`;
  }).join('\n');
  copy(lines);
};

const formatNumber = (num) => Number(num).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const formatNumberNoDot = (num) => Number(num).toFixed(2).replace('.', ','); // AFIP format usually takes commas
const formatDate = (ds) => new Date(ds).toLocaleString();
const shortId = (id) => String(id).substr(0, 8);

const getStatusColor = (status) => {
  switch (status) {
    case 'BORRADOR': return 'text-yellow-500';
    case 'LIQUIDADA_MANUAL': return 'text-orange-400';
    case 'AUTORIZADA_AFIP': return 'text-green-500 font-bold';
    default: return 'text-gray-400';
  }
};
</script>
