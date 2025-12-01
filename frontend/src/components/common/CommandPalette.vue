<template>
  <div v-if="show" class="fixed inset-0 z-[100] flex items-start justify-center pt-[20vh] px-4">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" @click="close"></div>

    <!-- Palette Window -->
    <div class="relative w-full max-w-lg bg-[#1a1f2e] border border-white/10 rounded-xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-200">
        <!-- Search Input -->
        <div class="flex items-center px-4 py-3 border-b border-white/10">
            <i class="fas fa-search text-gray-500 mr-3"></i>
            <input 
                ref="searchInput"
                v-model="query"
                type="text" 
                class="flex-1 bg-transparent border-none outline-none text-white placeholder-gray-500 text-lg"
                placeholder="Escribe un comando o destino..."
                @keydown.down.prevent="navigateResults(1)"
                @keydown.up.prevent="navigateResults(-1)"
                @keydown.enter.prevent="executeSelected"
                @keydown.esc.prevent="close"
            />
            <div class="text-xs text-gray-600 border border-gray-700 rounded px-1.5">ESC</div>
        </div>

        <!-- Results -->
        <div class="max-h-[60vh] overflow-y-auto py-2">
            <div v-if="filteredCommands.length === 0" class="px-4 py-8 text-center text-gray-500">
                <p>No se encontraron resultados para "{{ query }}"</p>
            </div>

            <div v-else>
                <div v-for="(group, groupName) in groupedCommands" :key="groupName">
                    <div class="px-4 py-2 text-xs font-bold text-gray-500 uppercase tracking-wider sticky top-0 bg-[#1a1f2e] z-10">
                        {{ groupName }}
                    </div>
                    <button
                        v-for="cmd in group"
                        :key="cmd.id"
                        class="w-full flex items-center px-4 py-3 text-left transition-colors group relative"
                        :class="{ 'bg-cyan-900/20': selectedIndex === cmd.index, 'hover:bg-white/5': selectedIndex !== cmd.index }"
                        @click="executeCommand(cmd)"
                        @mousemove="selectedIndex = cmd.index"
                    >
                        <!-- Selection Indicator -->
                        <div class="absolute left-0 top-0 bottom-0 w-1 bg-cyan-500 transition-opacity" :class="{ 'opacity-100': selectedIndex === cmd.index, 'opacity-0': selectedIndex !== cmd.index }"></div>
                        
                        <div class="flex items-center justify-center w-8 h-8 rounded bg-white/5 text-gray-400 mr-3 group-hover:text-white group-hover:bg-white/10 transition-colors">
                            <i :class="cmd.icon"></i>
                        </div>
                        <div class="flex-1">
                            <div class="text-sm font-medium text-gray-200 group-hover:text-white" :class="{ 'text-cyan-400': selectedIndex === cmd.index }">
                                {{ cmd.label }}
                            </div>
                            <div class="text-xs text-gray-500">{{ cmd.description }}</div>
                        </div>
                        <div v-if="cmd.shortcut" class="text-xs text-gray-600 bg-black/20 px-2 py-1 rounded">
                            {{ cmd.shortcut }}
                        </div>
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="px-4 py-2 bg-black/20 border-t border-white/5 text-[10px] text-gray-500 flex justify-between">
            <span><strong class="text-gray-400">↑↓</strong> para navegar</span>
            <span><strong class="text-gray-400">Enter</strong> para seleccionar</span>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
    show: Boolean
})

const emit = defineEmits(['close', 'navigate'])
const router = useRouter()
const searchInput = ref(null)
const query = ref('')
const selectedIndex = ref(0)

// Command Definitions
const commands = [
    { id: 'new-client', label: 'Nuevo Cliente', description: 'Crear una nueva ficha de cliente', icon: 'fas fa-user-plus', group: 'Acciones Rápidas', action: () => router.push({ name: 'HaweClientCanvas', params: { id: 'new' } }) },
    { id: 'clients', label: 'Ir a Clientes', description: 'Ver listado de clientes', icon: 'fas fa-users', group: 'Navegación', action: () => router.push({ name: 'Hawe' }) },
    { id: 'transportes', label: 'Transportes', description: 'Administrar empresas de transporte', icon: 'fas fa-truck', group: 'Logística', action: () => emit('navigate', { name: 'Transportes' }) },
    { id: 'segmentos', label: 'Segmentos', description: 'Administrar segmentos de clientes', icon: 'fas fa-layer-group', group: 'Maestros', action: () => emit('navigate', { name: 'Segmentos' }) },
    { id: 'pedidos', label: 'Pedidos', description: 'Gestión de pedidos (Próximamente)', icon: 'fas fa-shopping-cart', group: 'Operativo', action: () => alert('Próximamente') },
    { id: 'productos', label: 'Productos', description: 'Catálogo de productos (Próximamente)', icon: 'fas fa-box', group: 'Operativo', action: () => alert('Próximamente') },
    { id: 'depositos', label: 'Depósitos', description: 'Gestión de depósitos (Próximamente)', icon: 'fas fa-warehouse', group: 'Logística', action: () => alert('Próximamente') },
    { id: 'contactos', label: 'Contactos Globales', description: 'Agenda de contactos', icon: 'fas fa-address-book', group: 'Agenda', action: () => emit('navigate', { name: 'Contactos' }) },
    { id: 'logout', label: 'Cerrar Sesión', description: 'Salir del sistema', icon: 'fas fa-sign-out-alt', group: 'Sistema', action: () => emit('navigate', { name: 'Logout' }) },
]

const filteredCommands = computed(() => {
    const q = query.value.toLowerCase()
    let filtered = commands.filter(cmd => 
        cmd.label.toLowerCase().includes(q) || 
        cmd.description.toLowerCase().includes(q) ||
        cmd.group.toLowerCase().includes(q)
    )
    
    // Assign global index for navigation
    return filtered.map((cmd, index) => ({ ...cmd, index }))
})

const groupedCommands = computed(() => {
    const groups = {}
    filteredCommands.value.forEach(cmd => {
        if (!groups[cmd.group]) groups[cmd.group] = []
        groups[cmd.group].push(cmd)
    })
    return groups
})

watch(() => props.show, (newVal) => {
    if (newVal) {
        query.value = ''
        selectedIndex.value = 0
        nextTick(() => {
            searchInput.value?.focus()
        })
    }
})

watch(query, () => {
    selectedIndex.value = 0
})

const close = () => {
    emit('close')
}

const navigateResults = (direction) => {
    const max = filteredCommands.value.length - 1
    if (max < 0) return
    
    let newIndex = selectedIndex.value + direction
    if (newIndex < 0) newIndex = max
    if (newIndex > max) newIndex = 0
    
    selectedIndex.value = newIndex
}

const executeSelected = () => {
    const cmd = filteredCommands.value.find(c => c.index === selectedIndex.value)
    if (cmd) executeCommand(cmd)
}

const executeCommand = (cmd) => {
    cmd.action()
    close()
}
</script>
