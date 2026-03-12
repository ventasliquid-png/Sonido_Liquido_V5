<script setup>
import { ref } from 'vue';
import { useNotificationStore } from '../../stores/notification';

const props = defineProps({
    text: {
        type: String,
        required: true
    },
    label: {
        type: String,
        default: ''
    },
    icon: {
        type: String,
        default: '' // 'email', 'whatsapp', etc.
    }
});

const notificationStore = useNotificationStore();
const showTooltip = ref(false);
const timeout = ref(null);

const handleMouseEnter = () => {
    if (timeout.value) clearTimeout(timeout.value);
    showTooltip.value = true;
};

const handleMouseLeave = () => {
    timeout.value = setTimeout(() => {
        showTooltip.value = false;
    }, 300); // Small delay to allow moving to the tooltip
};

const copyToClipboard = async () => {
    try {
        await navigator.clipboard.writeText(props.text);
        notificationStore.add('Copiado al portapapeles', 'success');
        showTooltip.value = false;
    } catch (err) {
        console.error('Failed to copy', err);
        notificationStore.add('Error al copiar', 'error');
    }
};
</script>

<template>
    <div class="relative inline-block" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
        <!-- Trigger -->
        <div class="cursor-pointer group flex items-center gap-1.5 text-gray-500 hover:text-[#54cb9b] transition-colors">
            <slot name="icon">
                <!-- Default Icons based on prop -->
                <svg v-if="icon === 'email'" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                <svg v-else-if="icon === 'whatsapp'" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
            </slot>
            <span class="text-xs font-medium truncate max-w-[180px]">{{ text }}</span>
        </div>

        <!-- Tooltip Card -->
        <div 
            v-if="showTooltip" 
            class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 w-64 bg-white rounded-lg shadow-xl border border-gray-100 p-3 animate-scale-in"
            @mouseenter="handleMouseEnter"
            @mouseleave="handleMouseLeave"
        >
            <div class="flex items-center gap-3 mb-2">
                <div class="bg-gray-100 p-2 rounded-full text-gray-500">
                    <slot name="icon">
                        <svg v-if="icon === 'email'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                        <svg v-else-if="icon === 'whatsapp'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                    </slot>
                </div>
                <div>
                    <p class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">{{ label }}</p>
                    <p class="text-sm font-bold text-gray-800 break-all">{{ text }}</p>
                </div>
            </div>
            <button 
                @click="copyToClipboard"
                class="w-full flex items-center justify-center gap-2 bg-gray-50 hover:bg-gray-100 text-gray-600 py-1.5 rounded text-xs font-bold transition-colors border border-gray-200"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
                Copiar
            </button>
            
            <!-- Arrow -->
            <div class="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-white filter drop-shadow-sm"></div>
        </div>
    </div>
</template>

<style scoped>
.animate-scale-in {
    animation: scaleIn 0.15s cubic-bezier(0.16, 1, 0.3, 1);
    transform-origin: bottom center;
}

@keyframes scaleIn {
    from { opacity: 0; transform: translate(-50%, 10px) scale(0.95); }
    to { opacity: 1; transform: translate(-50%, 0) scale(1); }
}
</style>
