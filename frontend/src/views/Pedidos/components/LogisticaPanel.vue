<template>
    <div class="bg-[#051f15] border border-emerald-900/30 rounded-lg p-4 space-y-4 no-zen">
        <!-- Header -->
        <div class="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest text-emerald-500/70 border-b border-emerald-900/10 pb-2">
            <span class="flex items-center gap-2">
                <i class="fas fa-truck-fast"></i> Logística y Entrega
            </span>
            <div class="flex items-center gap-3">
                 <span v-if="suggestedProvincia" class="text-[8px] bg-emerald-500/10 text-emerald-400/50 px-2 py-0.5 rounded border border-emerald-500/20">
                    <i class="fas fa-location-dot mr-1"></i> Sugerir para: {{ suggestedProvincia }}
                </span>
                <span class="px-2 py-0.5 rounded bg-emerald-900/20 text-emerald-400" :class="statusColorClass">
                    {{ modelValue.estado_logistico || 'PENDIENTE' }}
                </span>
            </div>
        </div>

        <!-- Row 1: Address & Transport -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            <!-- Address Selector -->
            <div class="space-y-1">
                <label class="text-[9px] font-bold text-white/40 uppercase">Domicilio de Entrega</label>
                <div v-if="clientAddresses.length > 0" class="space-y-1 max-h-[120px] overflow-y-auto scrollbar-thin">
                    <div 
                        v-for="dom in clientAddresses" 
                        :key="dom.id"
                        @click="updateAddress(dom.id)"
                        class="p-2 rounded border cursor-pointer transition-all relative group"
                        :class="modelValue.domicilio_entrega_id === dom.id ? 'bg-emerald-600/20 border-emerald-500' : 'bg-black/20 border-white/5 hover:border-emerald-500/30'"
                    >
                        <div class="flex justify-between items-start">
                            <span class="text-[10px] font-bold text-white truncate w-full">{{ dom.calle }} {{ dom.numero }}</span>
                            <span v-if="dom.es_entrega" class="text-[8px] bg-emerald-500/20 text-emerald-300 px-1 rounded ml-1 shrink-0">ENTREGA</span>
                            <span v-else-if="dom.es_fiscal" class="text-[8px] bg-purple-500/20 text-purple-300 px-1 rounded ml-1 shrink-0">FISCAL</span>
                        </div>
                        <p class="text-[9px] text-white/50 truncate">{{ dom.localidad }} <span v-if="dom.provincia_id" class="text-white/30">({{ dom.provincia_id }})</span></p>
                    </div>
                </div>
                <!-- Fallback if no addresses -->
                <div v-else class="text-[10px] text-white/30 italic p-2 border border-white/5 border-dashed rounded text-center">
                    El cliente no tiene domicilios cargados.
                </div>
            </div>

            <!-- Transport Selector -->
            <div class="space-y-1">
                <label class="text-[9px] font-bold text-white/40 uppercase">Transporte (Empresa o Sucursal)</label>
                <SmartSelect
                    :modelValue="modelValue.transporte_id"
                    @update:modelValue="updateTransport"
                    :options="transportOptions"
                    placeholder="Seleccionar Transporte..."
                    :allowCreate="false"
                />
                
                <!-- Transport Info / Warnings -->
                <div v-if="selectedTransport" class="mt-2 p-2 rounded bg-black/20 border border-white/5 text-[9px]">
                    <div class="flex justify-between items-center mb-1">
                        <div class="flex items-center gap-2">
                            <i class="fas fa-info-circle text-emerald-500"></i>
                            <span class="font-bold text-emerald-300">{{ selectedTransportInfo.label }}</span>
                        </div>
                        <span v-if="isLastUsed" class="text-[8px] text-emerald-500/50 italic">Último utilizado</span>
                    </div>
                    <div class="flex gap-2">
                        <span class="flex items-center gap-1" :class="selectedTransportInfo.retiro ? 'text-green-400' : 'text-amber-400'">
                            <i class="fas" :class="selectedTransportInfo.retiro ? 'fa-check' : 'fa-exclamation-triangle'"></i>
                            {{ selectedTransportInfo.retiro ? 'Acepta retiro en local' : 'Requiere despacho' }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Row 2: Costs & Alerts -->
        <div class="bg-black/20 rounded p-3 space-y-3">
             <!-- [MVP ALERT] $400k Rule -->
             <div v-if="showAlert400k" class="flex items-start gap-2 bg-amber-500/10 border border-amber-500/30 p-2 rounded animate-pulse">
                <i class="fas fa-exclamation-circle text-amber-500 mt-0.5"></i>
                <div>
                    <p class="text-[10px] font-bold text-amber-500 uppercase">Alerta de Flete Interno</p>
                    <p class="text-[10px] text-amber-200/70 leading-tight">Pedido bajo $400k. Verifique si corresponde cobrar despacho o envío bonificado.</p>
                </div>
             </div>

             <div class="grid grid-cols-2 gap-4">
                <!-- Cost to Client -->
                <div>
                    <label class="text-[9px] font-bold text-emerald-500/40 uppercase block mb-1">Flete a Destino ($)</label>
                    <div class="relative group">
                         <span class="absolute left-2 top-1/2 -translate-y-1/2 text-emerald-500/50 text-xs">$</span>
                         <input 
                            type="number" 
                            :value="modelValue.costo_envio_cliente" 
                            @change="updateCost('costo_envio_cliente', $event.target.value)"
                            class="w-full bg-[#02110c] border border-emerald-900/30 rounded pl-5 pr-2 py-1.5 text-xs font-bold text-white focus:outline-none focus:border-emerald-500"
                            placeholder="0.00"
                        />
                    </div>
                    <p class="text-[8px] text-white/30 mt-1">* Se suma al total si se factura</p>
                </div>

                <!-- Internal Cost (Alberto) -->
                <div :class="{ 'opacity-50 grayscale': !requiresInternalFreight }">
                    <label class="text-[9px] font-bold uppercase block mb-1" :class="requiresInternalFreight ? 'text-amber-500/40' : 'text-white/20'">
                        {{ requiresInternalFreight ? 'Flete de Despacho (Alberto)' : 'Despacho No Requerido' }}
                    </label>
                     <div class="relative group">
                          <span class="absolute left-2 top-1/2 -translate-y-1/2 text-xs" :class="requiresInternalFreight ? 'text-amber-500/50' : 'text-white/10'">$</span>
                          <input 
                             type="number" 
                             :value="modelValue.costo_flete_interno"
                             @change="updateCost('costo_flete_interno', $event.target.value)"
                             :disabled="!requiresInternalFreight"
                             class="w-full bg-black/20 border rounded pl-5 pr-2 py-1.5 text-xs font-bold focus:outline-none transition-colors"
                             :class="requiresInternalFreight ? 'bg-[#1a1405] border-amber-900/30 text-amber-100 focus:border-amber-500' : 'border-white/5 text-white/20 cursor-not-allowed'"
                             placeholder="0.00"
                         />
                    </div>
                    <p class="text-[8px] mt-1" :class="requiresInternalFreight ? 'text-amber-500/30' : 'text-white/10'">
                        {{ requiresInternalFreight ? '* Costo de flete interno/remis' : 'Transporte retira por local' }}
                    </p>
                </div>
             </div>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import SmartSelect from '@/components/ui/SmartSelect.vue';
import { useLogisticaStore } from '@/stores/logistica';
import { usePedidosStore } from '@/stores/pedidos';
import { useNotificationStore } from '@/stores/notification';

const props = defineProps({
    modelValue: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['update']);

const logisticaStore = useLogisticaStore();
const pedidosStore = usePedidosStore();
const notification = useNotificationStore();

const lastUsedId = ref(null);

onMounted(async () => {
    // Parallel fetching for speed
    await Promise.all([
        logisticaStore.empresas.length === 0 ? logisticaStore.fetchEmpresas() : Promise.resolve(),
        logisticaStore.fetchAllNodos()
    ]);

    // Pre-selection logic for new orders
    if (!props.modelValue.transporte_id && props.modelValue.cliente_id) {
        lastUsedId.value = await pedidosStore.fetchLastUsedTransport(props.modelValue.cliente_id);
        if (lastUsedId.value) {
            updateTransport(lastUsedId.value);
            notification.add('Se pre-seleccionó el último transporte utilizado', 'info');
        }
    }
});

// Computed Data
const clientAddresses = computed(() => {
    return props.modelValue.cliente?.domicilios || [];
});

const currentProvinciaId = computed(() => {
    const selectedDom = clientAddresses.value.find(d => d.id === props.modelValue.domicilio_entrega_id);
    return selectedDom?.provincia_id || null;
});

const suggestedProvincia = computed(() => currentProvinciaId.value);

const transportOptions = computed(() => {
    let options = logisticaStore.transportOptions;
    const prov = currentProvinciaId.value;

    if (prov) {
        // Simple sorting for suggestions: provincial nodes first
        return [...options].sort((a, b) => {
            const aMatch = a.provincia_id === prov ? 1 : 0;
            const bMatch = b.provincia_id === prov ? 1 : 0;
            return bMatch - aMatch;
        });
    }

    return options;
});

const selectedOption = computed(() => {
    return transportOptions.value.find(o => o.id === props.modelValue.transporte_id);
});

const selectedTransportInfo = computed(() => {
    const opt = selectedOption.value;
    if (!opt) return null;

    return {
        label: opt.nombre,
        retiro: opt.type === 'nodo' ? opt.data.es_punto_retiro : (opt.data.servicio_retiro_domicilio || false)
    };
});

const selectedTransport = computed(() => {
    const opt = selectedOption.value;
    if (!opt) return null;
    // For backward compatibility with alert logic
    return {
        ...opt.data,
        servicio_retiro_domicilio: selectedTransportInfo.value.retiro
    };
});

const isLastUsed = computed(() => props.modelValue.transporte_id === lastUsedId.value);

const requiresInternalFreight = computed(() => {
    if (!selectedTransportInfo.value) return true;
    return !selectedTransportInfo.value.retiro;
});

// Alerts Logic
const showAlert400k = computed(() => {
    if (!selectedTransport.value) return false;
    
    // Condition 1: Requires Dispatch (No Pick-up)
    const requiresDispatch = !selectedTransportInfo.value.retiro;
    if (!requiresDispatch) return false;

    // Condition 2: Low Amount (< 400k)
    const isLowAmount = props.modelValue.total < 400000;
    
    return isLowAmount;
});

const statusColorClass = computed(() => {
    const s = props.modelValue.estado_logistico;
    if (s === 'ENTREGADO') return 'bg-green-500/20 text-green-300';
    if (s === 'DESPACHADO') return 'bg-blue-500/20 text-blue-300';
    return 'bg-emerald-900/20 text-emerald-400';
});

// Updates
const updateAddress = async (domicilioId) => {
    try {
        await pedidosStore.updatePedido(props.modelValue.id, { domicilio_entrega_id: domicilioId });
        props.modelValue.domicilio_entrega_id = domicilioId; // Optimistic
        notification.add('Domicilio de entrega actualizado', 'success');
    } catch (e) {
        notification.add('Error actualizando domicilio', 'error');
    }
};

const updateTransport = async (transporteId) => {
    try {
        await pedidosStore.updatePedido(props.modelValue.id, { transporte_id: transporteId });
        props.modelValue.transporte_id = transporteId; // Optimistic
        notification.add('Transporte actualizado', 'success');
    } catch (e) {
        notification.add('Error actualizando transporte', 'error');
    }
};

const updateCost = async (field, value) => {
    try {
        const payload = {};
        payload[field] = parseFloat(value) || 0;
        await pedidosStore.updatePedido(props.modelValue.id, payload);
        props.modelValue[field] = payload[field];
        notification.add('Costo actualizado', 'success');
    } catch (e) {
        notification.add('Error actualizando costo', 'error');
    }
};

</script>

<style scoped>
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(16, 185, 129, 0.2);
  border-radius: 10px;
}
</style>
