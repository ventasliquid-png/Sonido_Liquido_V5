<template>
  <aside class="flex w-64 flex-col border-r border-white/10 bg-black/20 h-full">
    <!-- Logo Area -->
    <div class="flex h-16 items-center px-6 border-b border-white/10 shrink-0">
      <div class="h-8 w-8 rounded bg-gradient-to-br from-gray-700 to-gray-900 mr-3 shadow-lg flex items-center justify-center">
        <i class="fas fa-bolt" :class="logoColor"></i>
      </div>
      <span class="font-outfit text-lg font-bold tracking-tight text-white">HAWE <span :class="logoColor">V5</span></span>
    </div>

    <!-- Search / Command Palette Trigger -->
    <div class="p-4 pb-2">
        <button 
            @click="$emit('open-command-palette')"
            class="w-full flex items-center gap-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-400 transition-all group"
        >
            <i class="fas fa-search text-gray-500 group-hover:text-cyan-400 transition-colors"></i>
            <span>Buscar...</span>
            <span class="ml-auto text-xs bg-white/10 px-1.5 py-0.5 rounded text-gray-500 group-hover:text-gray-300">Ctrl+K</span>
        </button>
    </div>

    <!-- Nav Links -->
    <nav class="flex-1 overflow-y-auto px-4 py-2 space-y-6 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-white/10">
      
      <!-- Most Used Section -->
      <div class="space-y-1">
        <h3 class="px-2 text-xs font-semibold uppercase text-cyan-400/80 tracking-wider mb-2">Más Usados</h3>
        <a href="#" @click.prevent="navigate('HaweClientCanvas', { id: 'new' })" class="nav-item">
            <i class="fas fa-plus-circle text-green-400"></i>
            Nuevo Cliente
        </a>
        <a href="#" @click.prevent="navigate('HaweHome')" class="nav-item">
            <i class="fas fa-users text-blue-400"></i>
            Clientes
        </a>
         <a href="#" @click.prevent="navigate('Transportes')" class="nav-item">
            <i class="fas fa-truck text-orange-400"></i>
            Transportes
        </a>
      </div>

      <!-- Categories -->
      
      <!-- OPERATIVO -->
      <div class="space-y-1">
        <button @click="toggleCategory('operativo')" class="category-header">
            <span class="flex items-center gap-2">
                <i class="fas fa-briefcase w-5 text-center text-gray-400"></i>
                OPERATIVO
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200" :class="{ 'rotate-90': uiStore.sidebarState.operativo }"></i>
        </button>
        <div v-show="uiStore.sidebarState.operativo" class="pl-4 space-y-1 pt-1">
            <a href="#" class="nav-item-sub">
                <i class="fas fa-shopping-cart w-5"></i> Pedidos
            </a>
            <a href="#" @click.prevent="navigate('HaweHome')" class="nav-item-sub active-link">
                <i class="fas fa-users w-5"></i> Clientes
            </a>
            <a href="#" @click.prevent="navigate('Productos')" class="nav-item-sub">
                <i class="fas fa-box w-5"></i> Productos
            </a>
        </div>
      </div>

      <!-- LOGISTICA -->
      <div class="space-y-1">
        <button @click="toggleCategory('logistica')" class="category-header">
             <span class="flex items-center gap-2">
                <i class="fas fa-truck-loading w-5 text-center text-gray-400"></i>
                LOGÍSTICA
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200" :class="{ 'rotate-90': uiStore.sidebarState.logistica }"></i>
        </button>
        <div v-show="uiStore.sidebarState.logistica" class="pl-4 space-y-1 pt-1">
            <a href="#" @click.prevent="navigate('Transportes')" class="nav-item-sub">
                <i class="fas fa-truck w-5"></i> Transportes
            </a>
            <a href="#" @click.prevent="handleDepositosClick" class="nav-item-sub">
                <i class="fas fa-warehouse w-5"></i> Depósitos Internos
            </a>
             <a href="#" class="nav-item-sub text-white/30 cursor-not-allowed" title="Próximamente">
                <i class="fas fa-map-marked-alt w-5"></i> Hoja de Ruta
            </a>
        </div>
      </div>

      <!-- AGENDA -->
      <div class="space-y-1">
        <button @click="toggleCategory('agenda')" class="category-header">
             <span class="flex items-center gap-2">
                <i class="fas fa-address-book w-5 text-center text-gray-400"></i>
                AGENDA
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200" :class="{ 'rotate-90': uiStore.sidebarState.agenda }"></i>
        </button>
        <div v-show="uiStore.sidebarState.agenda" class="pl-4 space-y-1 pt-1">
            <a href="#" @click.prevent="navigate('Contactos')" class="nav-item-sub">
                <i class="fas fa-user-tie w-5"></i> Contactos Globales
            </a>
        </div>
      </div>

       <!-- MAESTROS -->
      <div class="space-y-1">
        <button @click="toggleCategory('maestros')" class="category-header">
             <span class="flex items-center gap-2">
                <i class="fas fa-cogs w-5 text-center text-gray-400"></i>
                MAESTROS
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200" :class="{ 'rotate-90': uiStore.sidebarState.maestros }"></i>
        </button>
        <div v-show="uiStore.sidebarState.maestros" class="pl-4 space-y-1 pt-1">
            <a href="#" @click.prevent="navigate('Segmentos')" class="nav-item-sub">
                <i class="fas fa-layer-group w-5"></i> Segmentos
            </a>
             <a href="#" @click.prevent="navigate('ListasPrecios')" class="nav-item-sub">
                <i class="fas fa-tags w-5"></i> Listas de Precios
            </a>
             <a href="#" @click.prevent="navigate('Vendedores')" class="nav-item-sub">
                <i class="fas fa-user-tag w-5"></i> Vendedores
            </a>
        </div>
      </div>

    </nav>

    <!-- User Profile -->
    <div 
      class="border-t border-white/10 p-4 cursor-pointer hover:bg-white/5 transition-colors group mt-auto"
      @click="$emit('logout')"
      title="Cerrar Sesión"
    >
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-full bg-white/10 flex items-center justify-center text-white/50 group-hover:text-white transition-colors">
          <i class="fas fa-user"></i>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-white group-hover:text-cyan-400 transition-colors truncate">Usuario</p>
          <p class="text-xs text-white/50">Cerrar Sesión</p>
        </div>
        <i class="fas fa-sign-out-alt text-white/30 group-hover:text-red-400 transition-colors"></i>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'

import { useUIStore } from '../../stores/ui'
import { useNotificationStore } from '../../stores/notification'

const props = defineProps({
    theme: {
        type: String,
        default: 'cyan' // cyan, orange, pink, green
    }
})

const router = useRouter()
const emit = defineEmits(['logout', 'open-command-palette', 'navigate'])
const uiStore = useUIStore()
const notificationStore = useNotificationStore()

const themeColors = {
    cyan: 'text-cyan-400',
    orange: 'text-orange-400',
    pink: 'text-pink-400',
    green: 'text-emerald-400'
}

const activeThemeClass = computed(() => {
    switch (props.theme) {
        case 'orange': return 'border-orange-400 bg-orange-400/10 text-white'
        case 'pink': return 'border-pink-400 bg-pink-400/10 text-white'
        case 'green': return 'border-emerald-400 bg-emerald-400/10 text-white'
        default: return 'border-cyan-400 bg-cyan-400/10 text-white'
    }
})

const logoColor = computed(() => themeColors[props.theme] || themeColors.cyan)

const toggleCategory = (cat) => {
    uiStore.toggleSidebarCategory(cat)
}

const navigate = (routeName, params = {}) => {
    router.push({ name: routeName, params })
}

const handleDepositosClick = () => {
    notificationStore.add('Módulo de Depósitos próximamente', 'info')
}
</script>

<style scoped>
.nav-item {
    @apply flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-white/70 transition-colors hover:bg-white/10 hover:text-white;
}
.nav-item i {
    @apply w-5 text-center;
}
.category-header {
    @apply w-full flex items-center justify-between px-2 py-1.5 text-xs font-bold text-white/40 hover:text-white/80 uppercase tracking-wider transition-colors;
}
.nav-item-sub {
    @apply flex items-center gap-3 rounded-md px-3 py-2 text-sm text-white/60 transition-colors hover:bg-white/10 hover:text-white border-l-2 border-transparent;
}
.active-link {
    @apply text-white bg-white/5 border-cyan-400;
}
</style>
