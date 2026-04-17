// [IDENTIDAD] - frontend\src\composables\useKeyboardShortcuts.js
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

import { onMounted, onUnmounted } from 'vue';

export function useKeyboardShortcuts(shortcuts) {
    const handleKeydown = (event) => {
        // Ignorar si el foco está en un input o textarea para no bloquear el comportamiento nativo del navegador
        const activeElement = document.activeElement;
        const isInput = activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA' || activeElement.isContentEditable);
        
        let keyCombo = event.key.toLowerCase();
        
        // Determinar combinación exacta
        if (event.ctrlKey && event.shiftKey && keyCombo === 'z') {
            keyCombo = 'ctrl+shift+z';
        } else if (event.ctrlKey && keyCombo === 'z') {
            keyCombo = 'ctrl+z';
        } else if (event.ctrlKey && keyCombo === 's') {
            keyCombo = 'ctrl+s';
        } else {
            keyCombo = event.key; // Fallback a la tecla original ('F10', 'Escape', etc.)
        }

        if (shortcuts[keyCombo]) {
            // Solo prevenir default si no es un atajo dentro de un input que queremos permitir
            // (Ej: F10 para guardar se bloquea en inputs también, pero ctrl+z dentro de input se debe permitir y NO llegar aquí)
            if (isInput && (keyCombo === 'ctrl+z' || keyCombo === 'ctrl+shift+z')) {
                return; // Dejamos que el navegador haga Undo/Redo del texto
            }

            event.preventDefault();
            shortcuts[keyCombo]();
        }
    };

    onMounted(() => {
        window.addEventListener('keydown', handleKeydown);
    });

    onUnmounted(() => {
        window.removeEventListener('keydown', handleKeydown);
    });
}
