// [IDENTIDAD] - frontend\src\composables\useFormHistory.js
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

import { ref, watch } from 'vue'
import debounce from 'lodash/debounce'

// [GY-UX] Pasamos un Ref directamente para que el Undo sobrescriba el estado origen
export function useFormHistory(stateRef, maxHistory = 20) {
    const history = ref([])
    const future = ref([])
    const isUndoing = ref(false)

    // Deep clone helper
    const clone = (obj) => JSON.parse(JSON.stringify(obj))

    // Initialize history
    history.value.push(clone(stateRef.value))

    // Capture explicit snapshot
    const snapshot = () => {
        const lastState = history.value[history.value.length - 1]
        const currentState = clone(stateRef.value)
        if (JSON.stringify(lastState) !== JSON.stringify(currentState)) {
            history.value.push(currentState)
            if (history.value.length > maxHistory) history.value.shift()
            future.value = [] // Clear redo stack on new change
        }
    }

    // Debounced automatic capture
    const debouncedSave = debounce((newVal) => {
        const lastState = history.value[history.value.length - 1]
        if (JSON.stringify(lastState) !== JSON.stringify(newVal)) {
            history.value.push(clone(newVal))
            if (history.value.length > maxHistory) history.value.shift()
            future.value = [] // Clear redo stack on new change
        }
    }, 800)

    // Watch for automatic changes
    watch(stateRef, (newVal) => {
        if (isUndoing.value) {
            isUndoing.value = false
            return
        }
        debouncedSave(newVal)
    }, { deep: true })

    const undo = () => {
        if (history.value.length <= 1) return

        const current = history.value.pop()
        future.value.push(current)

        const previous = history.value[history.value.length - 1]
        isUndoing.value = true
        stateRef.value = clone(previous)
    }

    const redo = () => {
        if (future.value.length === 0) return

        const next = future.value.pop()
        history.value.push(next)

        isUndoing.value = true
        stateRef.value = clone(next)
    }

    const reset = () => {
        history.value = [clone(stateRef.value)]
        future.value = []
    }

    return {
        stateRef,
        undo,
        redo,
        reset,
        snapshot,
        canUndo: () => history.value.length > 1,
        canRedo: () => future.value.length > 0
    }
}
