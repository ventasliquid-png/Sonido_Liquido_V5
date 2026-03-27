<template>
    <div>
        <!-- DRAWER TOGGLE BUTTON (Floating right edge when closed) -->
        <button v-if="!modelValue"
                @click="toggle" 
                class="fixed right-0 top-1/2 transform -translate-y-1/2 bg-[#151515] border-l border-t border-b border-white/20 text-gray-400 hover:text-orange-400 hover:bg-white/10 p-2 rounded-l-lg shadow-lg z-[100] transition-all flex items-center gap-2 group"
                title="Ver Rentabilidad (F8)">
            <i class="fas fa-chevron-left group-hover:-translate-x-1 transition-transform"></i>
        </button>

        <!-- RIGHT DRAWER: COSTOS (Deslizable) -->
        <div class="fixed top-0 right-0 h-full w-96 bg-[#0f0f0f] border-l border-white/10 shadow-2xl transform transition-transform duration-200 ease-in-out z-50 flex flex-col"
             :class="modelValue ? 'translate-x-0' : 'translate-x-full'">
            
            <!-- Floating Close Button (Left Edge, Centered) -->
            <button @click="close" 
                    class="absolute left-0 top-1/2 transform -translate-x-full -translate-y-1/2 bg-[#151515] border-l border-t border-b border-white/20 text-gray-400 hover:text-red-400 hover:bg-white/10 p-2 rounded-l-lg shadow-lg z-50 transition-all flex items-center gap-2"
                    title="Cerrar Panel (ESC)">
                <i class="fas fa-chevron-right"></i>
            </button>

            <!-- Header -->
            <div class="p-5 border-b border-white/10 flex justify-between items-center bg-[#151515]">
                <h3 class="text-sm font-bold uppercase tracking-widest text-orange-400 flex items-center gap-2">
                    <i class="fas fa-chart-pie"></i> 
                    Análisis Rentabilidad
                </h3>
                <span class="text-[10px] text-gray-600 font-mono hidden md:inline">ESC para cerrar</span>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-auto p-4 space-y-6">
                
                <!-- Summary Card -->
                <div class="bg-orange-500/10 rounded-xl p-4 border border-orange-500/20 relative overflow-hidden">
                    <div class="absolute top-0 right-0 p-2 opacity-10">
                        <i class="fas fa-dollar-sign text-6xl text-orange-500"></i>
                    </div>

                      <div class="flex justify-between mb-2 relative z-10">
                        <span class="text-xs text-orange-300 font-medium">Costo Total</span>
                        <span class="font-mono text-white">$ {{ totalCosto.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</span>
                    </div>
                    <div class="flex justify-between mb-2 relative z-10">
                        <span class="text-xs text-green-400 font-medium">Venta Neta (Subtotal)</span>
                        <span class="font-mono text-white">$ {{ subtotal.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</span>
                    </div>
                    <div class="h-px bg-white/10 my-3 relative z-10"></div>
                    <div class="flex justify-between items-center relative z-10">
                        <span class="font-bold text-sm text-white uppercase tracking-wider">Utilidad Bruta</span>
                        <div class="text-right">
                             <div class="font-mono font-bold text-xl text-orange-400">$ {{ utilidad.toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</div>
                             <div class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-orange-500/20 border border-orange-500/30 mt-1">
                                <i class="fas fa-arrow-up text-[10px] text-orange-500"></i>
                                <span class="text-xs text-orange-400 font-bold">{{ rentabilidadGlobal.toFixed(1) }}%</span>
                             </div>
                        </div>
                    </div>
                </div>

                <!-- Row Breakdown Table -->
                <div class="space-y-3">
                    <h4 class="text-[10px] font-bold uppercase tracking-widest text-gray-500 ml-1">Detalle por Ítem</h4>
                    
                    <div class="border border-white/5 rounded-lg overflow-hidden">
                        <table class="w-full text-left">
                            <thead class="bg-white/5 text-[10px] uppercase font-bold text-gray-500">
                                <tr>
                                    <th class="px-3 py-2">Item</th>
                                    <th class="px-3 py-2 text-right">Costo</th>
                                    <th class="px-3 py-2 text-right">Margen</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-white/5 text-xs">
                                <tr v-for="item in (items || [])" :key="item.id" class="hover:bg-white/5 transition-colors">
                                    <td class="px-3 py-2 text-gray-300 max-w-[150px] truncate">{{ item.descripcion }}</td>
                                    <td class="px-3 py-2 text-right font-mono text-gray-400">
                                        $ {{ (Number(item.producto_obj?.costos?.costo_reposicion || 0) * item.cantidad).toLocaleString('es-AR') }}
                                    </td>
                                    <td class="px-3 py-2 text-right font-mono font-bold" 
                                        :class="(item.total - (item.producto_obj?.costos?.costo_reposicion || 0) * item.cantidad) > 0 ? 'text-emerald-400' : 'text-red-400'">
                                        {{ calculateItemMargin(item) }}%
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed } from 'vue';

const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false
    },
    items: {
        type: Array,
        default: () => []
    },
    subtotal: {
        type: Number,
        default: 0
    }
});

const emit = defineEmits(['update:modelValue']);

const toggle = () => {
    emit('update:modelValue', !props.modelValue);
};

const close = () => {
    emit('update:modelValue', false);
};



const totalCosto = computed(() => {
    if (!props.items) return 0;
    return props.items.reduce((sum, item) => {
        const costo = Number(item.producto_obj?.costos?.costo_reposicion || 0);
        return sum + (costo * item.cantidad);
    }, 0);
});

const utilidad = computed(() => props.subtotal - totalCosto.value);

const rentabilidadGlobal = computed(() => {
    if (props.subtotal === 0) return 0;
    return (utilidad.value / props.subtotal) * 100;
});

const calculateItemMargin = (item) => {
    if (!item) return 0;
    const vta = Number(item.total) || 0;
    const cto = Number(item.producto_obj?.costos?.costo_reposicion || 0) * (Number(item.cantidad) || 0);
    if (vta === 0) return 0;
    return (((vta - cto) / vta) * 100).toFixed(1);
};

// Keyboard Shortcuts Logic
const handleKeydown = (e) => {
    // F8 Toggle
    if (e.key === 'F8') {
        e.preventDefault();
        toggle();
    }
    // ESC Close (Critical for Privacy)
    if (e.key === 'Escape' && props.modelValue) {
        e.preventDefault();
        close();
    }
};

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});
</script>
