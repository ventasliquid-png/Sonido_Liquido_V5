// [IDENTIDAD] - frontend\src\composables\useKeyboardShortcuts.js
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

import { onMounted, onUnmounted } from 'vue';

export function useKeyboardShortcuts(shortcuts) {
    const handleKeydown = (event) => {
        const key = event.key;
        if (shortcuts[key]) {
            event.preventDefault();
            shortcuts[key]();
        }
    };

    onMounted(() => {
        window.addEventListener('keydown', handleKeydown);
    });

    onUnmounted(() => {
        window.removeEventListener('keydown', handleKeydown);
    });
}
