<template>
  <teleport to="body">
    <transition name="fade">
        <div 
            v-if="store.isOpen"
            class="fixed z-[9999] bg-[#020617]/95 border-2 border-emerald-500/50 rounded-xl shadow-[0_0_40px_rgba(16,185,129,0.3)] flex flex-col backdrop-blur-3xl overflow-hidden animate-in fade-in zoom-in-95 duration-100"
            :style="positionStyles"
        >
            <!-- Input Area -->
            <div class="relative p-2">
                <span class="absolute left-3 top-1/2 -translate-y-1/2 text-emerald-500/50 font-mono font-bold">∑</span>
                <input 
                    ref="formulaInput"
                    v-model="formula"
                    type="text"
                    @keydown="handleKeydown"
                    @blur="handleBlur"
                    class="w-full bg-transparent py-2 pl-6 pr-2 text-xl font-mono font-bold text-emerald-400 focus:outline-none placeholder-emerald-900/50"
                    placeholder="=..."
                    autocomplete="off"
                />
            </div>

            <!-- Dashboard / Status Bar -->
            <div class="flex items-center justify-between px-3 py-1.5 bg-emerald-950/40 border-t border-emerald-500/20 text-[10px] uppercase font-bold tracking-widest text-emerald-500/70">
                <!-- Shifters -->
                <div class="flex items-center gap-1.5 bg-black/40 rounded px-1.5 py-0.5 border border-emerald-500/10" title="Usa Flechas Arriba/Abajo">
                    <button @click="decreaseMagnitude" class="hover:text-emerald-300 hover:bg-white/5 rounded px-1 transition-colors" tabindex="-1"><i class="fas fa-chevron-down"></i></button>
                    <span class="w-14 text-center">{{ magnitudeLabel }}</span>
                    <button @click="increaseMagnitude" class="hover:text-emerald-300 hover:bg-white/5 rounded px-1 transition-colors" tabindex="-1"><i class="fas fa-chevron-up"></i></button>
                </div>
                
                <!-- Preview -->
                <div class="text-emerald-300 text-lg tabular-nums">
                    {{ previewResult }}
                </div>
            </div>
        </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useCalculatorStore } from '@/stores/calculatorStore';

const store = useCalculatorStore();
const formulaInput = ref(null);
const formula = ref('');
const isSubmitting = ref(false);

const magnitude = ref(-2);

watch(() => store.isOpen, async (newVal) => {
    if (newVal) {
        formula.value = store.initialValue || '=';
        magnitude.value = -2; // Default to 2 decimals
        isSubmitting.value = false;
        await nextTick();
        if (formulaInput.value) {
            formulaInput.value.focus();
            formulaInput.value.setSelectionRange(formula.value.length, formula.value.length);
        }
    }
});

const positionStyles = computed(() => {
    // Dropdown slightly below the input
    const width = Math.max(store.width, 240);
    return {
        top: `${store.y + 40}px`,
        left: `${store.x}px`,
        width: `${width}px`
    };
});

const increaseMagnitude = () => { if (magnitude.value < 3) magnitude.value++; };
const decreaseMagnitude = () => { if (magnitude.value > -4) magnitude.value--; };

const magnitudeLabel = computed(() => {
    switch(magnitude.value) {
        case -4: return '.0000';
        case -3: return '.000';
        case -2: return '.00';
        case -1: return '.0';
        case 0: return 'ENT';
        case 1: return 'DEC';
        case 2: return 'CEN';
        case 3: return 'MIL';
        default: return '???';
    }
});

const previewResult = computed(() => {
    if (!formula.value) return '0.00';
    
    let expr = formula.value;
    if (expr.startsWith('=') || expr.startsWith('+')) {
        expr = expr.substring(1);
    }
    expr = expr.replace(/,/g, '.');
    
    if (/^[-()\d/*+.]+$/.test(expr) && expr.trim().length > 0) {
        try {
            // eslint-disable-next-line no-eval
            const result = new Function('return ' + expr)();
            if (isNaN(result) || !isFinite(result)) return '...';
            
            const mag = magnitude.value;
            const factor = 10 ** mag;
            
            // JS floating point math quirks (e.g. 1.005 * 100). Safe Rounding:
            // We use Number(Math.round(result / factor + "e-1")) but an easier way is algebraic:
            const finalValue = Math.round(result / factor) * factor;
            
            if (mag <= 0) {
                return finalValue.toFixed(Math.abs(mag));
            } else {
                return finalValue.toFixed(2); 
            }
        } catch (e) {
            return '...';
        }
    }
    return '...';
});

const executeSubmit = () => {
    if (isSubmitting.value) return;
    const p = previewResult.value;
    if (p !== '...' && p !== '') {
        isSubmitting.value = true;
        store.submit(parseFloat(p), magnitude.value);
    } else if (formula.value === '=' || formula.value === '+' || formula.value === '') {
        // Just cancel if empty
        isSubmitting.value = true;
        store.close();
    }
};

const handleKeydown = (e) => {
    if (e.key === 'Escape') {
        store.close();
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        increaseMagnitude();
    } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        decreaseMagnitude();
    } else if (e.key === 'Enter') {
        e.preventDefault();
        executeSubmit();
    }
};

const handleBlur = (e) => {
    // Tabbed out or clicked away
    setTimeout(() => {
        if (!store.isOpen) return;
        if (!formulaInput.value || document.activeElement !== formulaInput.value) {
            if (document.activeElement?.className?.includes('hover:text-emerald-300')) {
                // Button was clicked, return focus to input
                formulaInput.value.focus();
                return;
            }
            executeSubmit();
        }
    }, 150);
};

</script>

<style scoped>
/* Scoped specific keyframes can be omitted if tailwind is fully operative */
</style>
