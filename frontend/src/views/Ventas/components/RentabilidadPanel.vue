<template>
    <div>
        <!-- DRAWER TOGGLE BUTTON (Floating right edge when closed) -->
        <button v-if="!modelValue"
                @click="toggle" 
                class="fixed right-0 top-1/2 transform -translate-y-1/2 bg-[#151515] border-l border-t border-b border-white/20 text-gray-400 hover:text-orange-400 hover:bg-white/10 p-2 rounded-l-lg shadow-lg z-40 transition-all flex items-center gap-2 group"
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
                        <span class="font-mono text-white">$ 356,760.00</span>
                    </div>
                    <div class="flex justify-between mb-2 relative z-10">
                        <span class="text-xs text-green-400 font-medium">Venta Neta</span>
                        <span class="font-mono text-white">$ 492,480.00</span>
                    </div>
                    <div class="h-px bg-white/10 my-3 relative z-10"></div>
                    <div class="flex justify-between items-center relative z-10">
                        <span class="font-bold text-sm text-white uppercase tracking-wider">Utilidad</span>
                        <div class="text-right">
                             <div class="font-mono font-bold text-xl text-orange-400">$ 135,720.00</div>
                             <div class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-orange-500/20 border border-orange-500/30 mt-1">
                                <i class="fas fa-arrow-up text-[10px] text-orange-500"></i>
                                <span class="text-xs text-orange-400 font-bold">27.5%</span>
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
                                <tr class="hover:bg-white/5 transition-colors">
                                    <td class="px-3 py-2 text-gray-300">Surgizime E2 1Lt</td>
                                    <td class="px-3 py-2 text-right font-mono text-gray-400">$ 7,620</td>
                                    <td class="px-3 py-2 text-right font-mono text-emerald-400 font-bold">31%</td>
                                </tr>
                                <tr class="hover:bg-white/5 transition-colors">
                                    <td class="px-3 py-2 text-gray-300">Surgizime E2 5Lts</td>
                                    <td class="px-3 py-2 text-right font-mono text-gray-400">$ 28,980</td>
                                    <td class="px-3 py-2 text-right font-mono text-emerald-400 font-bold">31%</td>
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
import { onMounted, onUnmounted } from 'vue';

const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:modelValue']);

const toggle = () => {
    emit('update:modelValue', !props.modelValue);
};

const close = () => {
    emit('update:modelValue', false);
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
