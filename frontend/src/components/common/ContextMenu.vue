<template>
    <div 
        v-if="show" 
        class="fixed z-[99999] bg-[#0a253a] rounded-lg shadow-xl border border-cyan-500/30 py-1 min-w-[160px]"
        :style="{ top: `${y}px`, left: `${x}px` }"
        @click.stop
    >
        <div 
            v-for="(action, index) in actions" 
            :key="index"
            class="px-4 py-2 hover:bg-cyan-900/40 cursor-pointer flex items-center gap-2 text-sm text-cyan-100 transition-colors"
            @click="handleAction(action)"
        >
            <i v-if="action.iconClass" :class="action.iconClass" class="w-4 text-center text-cyan-400"></i>
            <span v-else-if="action.icon">{{ action.icon }}</span>
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
