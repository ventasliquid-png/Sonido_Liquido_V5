<template>
    <div 
        v-if="show" 
        class="fixed z-50 bg-white rounded-lg shadow-lg border border-gray-200 py-1 min-w-[160px]"
        :style="{ top: `${y}px`, left: `${x}px` }"
        @click.stop
    >
        <div 
            v-for="(action, index) in actions" 
            :key="index"
            class="px-4 py-2 hover:bg-gray-100 cursor-pointer flex items-center gap-2 text-sm text-gray-700"
            @click="handleAction(action)"
        >
            <span v-if="action.icon">{{ action.icon }}</span>
            <span>{{ action.label }}</span>
        </div>
    </div>
    <div 
        v-if="show" 
        class="fixed inset-0 z-40" 
        @click="close"
        @contextmenu.prevent="close"
    ></div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
    modelValue: Boolean,
    x: Number,
    y: Number,
    actions: {
        type: Array,
        default: () => []
    }
});

const emit = defineEmits(['update:modelValue', 'close']);

const show = ref(props.modelValue);

watch(() => props.modelValue, (val) => {
    show.value = val;
});

const close = () => {
    emit('update:modelValue', false);
    emit('close');
};

const handleAction = (action) => {
    action.handler();
    close();
};
</script>
