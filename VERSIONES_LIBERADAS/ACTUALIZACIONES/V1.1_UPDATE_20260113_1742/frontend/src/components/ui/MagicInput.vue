<template>
    <div class="relative w-full h-full">
        <input 
            ref="inputRef"
            type="text" 
            v-model="displayValue"
            class="w-full h-full bg-transparent outline-none transition-colors"
            :class="[
                inputClass,
                isError ? 'text-red-400 border-red-500 ring-1 ring-red-500' : ''
            ]"
            :placeholder="placeholder"
            @focus="handleFocus"
            @blur="handleBlur"
            @keydown.enter.prevent="handleEnter"
            @keydown.tab="handleBlur"
        >
        <!-- Indicator of 'Formula Mode' -->
        <div v-if="isFormula" class="absolute right-1 top-1/2 -translate-y-1/2 text-[8px] text-blue-400 font-bold pointer-events-none">
            fx
        </div>
    </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
    modelValue: {
        type: [Number, String],
        default: 0
    },
    inputClass: {
        type: String,
        default: ''
    },
    placeholder: {
        type: String,
        default: ''
    },
    decimals: {
        type: Number,
        default: 2
    }
});

const emit = defineEmits(['update:modelValue', 'change', 'tab']);

const inputRef = ref(null);
const displayValue = ref('');
const isFocused = ref(false);
const isError = ref(false);

// If user types operators, it's a formula
const isFormula = computed(() => {
    return typeof displayValue.value === 'string' && /[\+\-\*\/]/.test(displayValue.value);
});

// Watch external changes
watch(() => props.modelValue, (val) => {
    if (!isFocused.value) {
        displayValue.value = val === 0 || val === null ? '' : val.toString();
    }
}, { immediate: true });

const handleFocus = (e) => {
    isFocused.value = true;
    // On focus, select all for quick override
    e.target.select();
};

const evaluateMath = (expression) => {
    try {
        // Sanitize: only numbers, operators, dots, parens
        const sanitized = expression.replace(/,/g, '.').replace(/[^0-9\.\+\-\*\/\(\)]/g, '');
        if (!sanitized) return null;

        // DANGER: eval is evil, but for a local calculator with strict sanitization it's acceptable in this context.
        // Alternative: use a math parser lib, but 'Function' is lighter.
        // We use Function constructor which is safer than direct eval locally
        const result = new Function(`return ${sanitized}`)();
        
        if (!isFinite(result) || isNaN(result)) throw new Error('Invalid Result');
        
        // Rounding
        const factor = Math.pow(10, props.decimals);
        return Math.round(result * factor) / factor;

    } catch (e) {
        console.warn("Math Eval Error", e);
        return null; // Return null on error so we don't update
    }
};

const commitValue = () => {
    isError.value = false;
    let raw = displayValue.value;
    
    if (!raw) {
        emit('update:modelValue', 0);
        emit('change', 0);
        return;
    }

    // Try calc
    const result = evaluateMath(raw.toString());

    if (result !== null) {
        displayValue.value = result.toString();
        emit('update:modelValue', result);
        emit('change', result);
    } else {
        // Validation error or keep original text?
        // Let's revert to old value if calc fails to prevent data loss or show error
        isError.value = true;
        // Optionally revert: displayValue.value = props.modelValue;
    }
};

const handleBlur = () => {
    isFocused.value = false;
    commitValue();
};

const handleEnter = (e) => {
    commitValue();
    e.target.blur(); // Remove focus to confirm visually
    // Optionally focus next field if parent handles it, but 'blur' is enough usually
};

</script>

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
