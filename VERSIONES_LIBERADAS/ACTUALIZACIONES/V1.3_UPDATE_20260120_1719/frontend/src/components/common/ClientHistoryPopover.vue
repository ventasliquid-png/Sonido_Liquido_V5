<template>
    <div 
        v-if="visible"
        class="absolute z-[70] bg-[#1a1a1a] text-slate-200 rounded-lg shadow-2xl border border-slate-700 w-80 overflow-hidden font-sans"
        :style="{ top: y + 'px', left: x + 'px' }"
    >
        <!-- Header -->
        <div class="bg-black/40 px-3 py-2 border-b border-slate-700 flex justify-between items-center">
            <span class="text-[10px] uppercase font-bold tracking-widest text-[#54cb9b]">Historial Reciente</span>
            <button @click="$emit('close')" class="text-slate-500 hover:text-white transition-colors">
                <i class="fa-solid fa-times text-xs"></i>
            </button>
        </div>

        <!-- Content -->
        <div class="max-h-64 overflow-y-auto custom-scrollbar bg-[#111]">
            <div v-if="orders.length === 0" class="p-4 text-center text-xs opacity-50 italic">
                Sin pedidos recientes.
            </div>

            <div 
                v-for="order in orders" 
                :key="order.id"
                class="border-b border-slate-800/50 p-3 hover:bg-white/5 transition-colors group"
            >
                <div class="flex justify-between items-baseline mb-1">
                    <span class="font-mono text-xs font-bold text-amber-500">{{ formatDate(order.fecha) }}</span>
                    <span class="font-mono text-xs font-medium opacity-70">{{ formatCurrency(order.total) }}</span>
                </div>
                
                <!-- Items Preview (Compact) -->
                <div class="space-y-0.5 mt-2">
                    <div 
                        v-for="item in order.items.slice(0, 3)" 
                        :key="item.id"
                        class="flex justify-between text-[10px] text-slate-400"
                    >
                        <span class="truncate pr-2">{{ item.producto_nombre || item.producto_id }}</span>
                        <span class="font-mono opacity-60">{{ formatCurrency(item.precio_unitario) }}</span>
                    </div>
                     <div v-if="order.items.length > 3" class="text-[9px] text-slate-600 italic">
                        + {{ order.items.length - 3 }} productos más...
                    </div>
                </div>

                <div class="mt-2 text-right">
                    <span 
                        class="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded border border-slate-700 opacity-60 group-hover:opacity-100 transition-opacity"
                        :class="statusClass(order.estado)"
                    >
                        {{ order.estado }}
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
    visible: Boolean,
    x: Number,
    y: Number,
    orders: {
        type: Array,
        default: () => []
    }
});

defineEmits(['close']);

const formatDate = (str) => {
    if(!str) return '';
    return new Date(str).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit' });
}

const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(val);
};

const statusClass = (st) => {
    if(st === 'CUMPLIDO') return 'text-emerald-400 border-emerald-900';
    if(st === 'PENDIENTE') return 'text-amber-400 border-amber-900';
    return 'text-slate-400';
}
</script>
