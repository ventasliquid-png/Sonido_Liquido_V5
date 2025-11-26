<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
    modelValue: {
        type: [String, Number],
        default: null
    },
    options: {
        type: Array,
        default: () => []
    },
    label: {
        type: String,
        default: 'Seleccionar'
    },
    allowCreate: {
        type: Boolean,
        default: true
    },
    placeholder: {
        type: String,
        default: 'Seleccionar...'
    }
});

const emit = defineEmits(['update:modelValue', 'create-new']);
const selectRef = ref(null);

const triggerCreate = () => {
    if (props.allowCreate) {
        emit('create-new');
    }
};

const handleWindowKeydown = (e) => {
    if (e.key === 'F4') {
        // Check if the select element is focused
        if (selectRef.value && selectRef.value === document.activeElement) {
            e.preventDefault();
            e.stopPropagation();
            triggerCreate();
        }
    }
};

onMounted(() => {
    window.addEventListener('keydown', handleWindowKeydown, { capture: true });
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleWindowKeydown, { capture: true });
});

const handleChange = (e) => {
    const val = e.target.value;
    if (val === '__NEW__') {
        // Reset select to previous value or null to avoid showing "Nuevo" as selected
        e.target.value = props.modelValue || ''; 
        triggerCreate();
    } else {
        emit('update:modelValue', val);
    }
};

const focusSelect = () => {
    if (selectRef.value) {
        selectRef.value.focus();
    }
};
</script>

<template>
    <div class="w-full">
        <label v-if="label" class="block text-xs font-bold text-gray-600 mb-1" @click="focusSelect">{{ label }}</label>
        <div class="flex gap-2">
            <div class="relative flex-1">
                <select 
                    ref="selectRef"
                    :value="modelValue"
                    @change="handleChange"
                    class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none bg-white appearance-none cursor-pointer"
                >
                    <option :value="null">{{ placeholder }}</option>
                    <option v-if="allowCreate" value="__NEW__" class="font-bold text-[#54cb9b] bg-green-50">
                        ➕ Nuevo (F4)
                    </option>
                    <option v-for="opt in options" :key="opt.id" :value="opt.id">
                        {{ opt.nombre || opt.descripcion }}
                    </option>
                </select>
                <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                    <svg class="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                </div>
            </div>
            
            <button 
                v-if="allowCreate"
                @click="triggerCreate"
                class="px-3 py-2 bg-gray-100 border border-gray-300 rounded text-gray-600 hover:bg-gray-200 hover:text-gray-800 transition-colors font-bold text-sm flex items-center justify-center"
                title="Crear Nuevo (F4)"
                type="button"
                tabindex="-1"
            >
                [+]
            </button>
        </div>
    </div>
</template>
