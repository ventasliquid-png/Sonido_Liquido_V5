import { ref, watch, toRaw } from 'vue'

export function useFormHistory(initialState) {
    const history = ref([])
    const future = ref([])
    const state = ref({ ...initialState })
    const isUndoing = ref(false)

    // Deep clone helper
    const clone = (obj) => JSON.parse(JSON.stringify(obj))

    // Initialize history
    history.value.push(clone(initialState))

    // Watch for changes
    watch(state, (newVal) => {
        if (isUndoing.value) {
            isUndoing.value = false
            return
        }

        // Debounce or check for meaningful changes could go here
        // For now, simple push
        const lastState = history.value[history.value.length - 1]
        if (JSON.stringify(lastState) !== JSON.stringify(newVal)) {
            history.value.push(clone(newVal))
            future.value = [] // Clear redo stack on new change
        }
    }, { deep: true })

    const undo = () => {
        if (history.value.length <= 1) return

        const current = history.value.pop()
        future.value.push(current)

        const previous = history.value[history.value.length - 1]
        isUndoing.value = true
        state.value = clone(previous)
    }

    const redo = () => {
        if (future.value.length === 0) return

        const next = future.value.pop()
        history.value.push(next)

        isUndoing.value = true
        state.value = clone(next)
    }

    const reset = (newState) => {
        state.value = clone(newState)
        history.value = [clone(newState)]
        future.value = []
    }

    return {
        state,
        undo,
        redo,
        reset,
        canUndo: () => history.value.length > 1,
        canRedo: () => future.value.length > 0
    }
}
