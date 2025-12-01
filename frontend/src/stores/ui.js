import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
    const sidebarState = ref({
        operativo: true,
        logistica: false,
        agenda: false,
        maestros: false
    })

    const toggleSidebarCategory = (category) => {
        if (sidebarState.value[category] !== undefined) {
            sidebarState.value[category] = !sidebarState.value[category]
        }
    }

    return {
        sidebarState,
        toggleSidebarCategory
    }
}, {
    persist: true
})
