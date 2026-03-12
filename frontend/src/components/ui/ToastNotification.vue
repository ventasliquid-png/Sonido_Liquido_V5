<script setup>
import { useNotificationStore } from '../../stores/notification';

const store = useNotificationStore();
</script>

<template>
    <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
        <TransitionGroup name="toast">
            <div 
                v-for="notification in store.notifications" 
                :key="notification.id"
                class="pointer-events-auto min-w-[300px] max-w-md p-4 rounded shadow-lg border-l-4 flex items-start gap-3 transform transition-all duration-300"
                :class="{
                    'bg-white border-green-500 text-gray-800': notification.type === 'success',
                    'bg-white border-red-500 text-gray-800': notification.type === 'error',
                    'bg-white border-blue-500 text-gray-800': notification.type === 'info',
                    'bg-white border-yellow-500 text-gray-800': notification.type === 'warning'
                }"
            >
                <!-- Icons -->
                <span v-if="notification.type === 'success'" class="text-green-500 text-xl">✅</span>
                <span v-else-if="notification.type === 'error'" class="text-red-500 text-xl">❌</span>
                <span v-else-if="notification.type === 'warning'" class="text-yellow-500 text-xl">⚠️</span>
                <span v-else class="text-blue-500 text-xl">ℹ️</span>

                <div class="flex-1">
                    <p class="text-sm font-medium">{{ notification.message }}</p>
                </div>

                <button @click="store.remove(notification.id)" class="text-gray-400 hover:text-gray-600">
                    ✕
                </button>
            </div>
        </TransitionGroup>
    </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
