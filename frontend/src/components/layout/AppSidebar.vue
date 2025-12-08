<template>
  <aside class="flex w-64 flex-col border-r h-full transition-colors duration-300" :class="themeBgClass">
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
      
      <!-- Most Used Section (Containerized) -->
      <div class="mx-2 mb-4 rounded-lg bg-white/5 border border-white/10 p-2 space-y-1">
        <h3 class="px-2 text-[10px] font-bold uppercase text-cyan-400/80 tracking-wider mb-2 flex items-center gap-2">
            <i class="fas fa-star text-yellow-500/50"></i> Más Usados
        </h3>
        <a href="#" @click.prevent="navigate('HaweClientCanvas', { id: 'new' })" class="nav-item-compact">
            <i class="fas fa-plus-circle text-green-400"></i>
            <span class="truncate">Nuevo Cliente</span>
        </a>
        <a href="#" @click.prevent="navigate('Pedidos')" class="nav-item-compact">
            <i class="fas fa-cart-plus text-yellow-400"></i>
            <span class="truncate">Nuevo Pedido</span>
        </a>
      </div>

      <!-- PEDIDOS (Placeholder) -->
      <div class="space-y-1">
        <button @click="toggleCategory('pedidos')" class="category-header group bg-emerald-900/20 border-l-2 border-emerald-500/50">
            <span class="flex items-center gap-2 text-emerald-400 font-bold">
                <i class="fas fa-shopping-cart w-5 text-center text-emerald-500"></i>
                PEDIDOS
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200 text-emerald-500/50" :class="{ 'rotate-90': uiStore.sidebarState.pedidos }"></i>
        </button>
        <div v-show="uiStore.sidebarState.pedidos" class="pl-4 space-y-1 pt-1">
            <a href="#" @click.prevent="navigate('Pedidos')" class="nav-item-sub text-white/60 hover:text-white transition-colors">
                <i class="fas fa-plus w-5"></i> Nuevo Pedido
            </a>
            <a href="#" class="nav-item-sub text-white/30 cursor-not-allowed" title="Próximamente">
                <i class="fas fa-list w-5"></i> Historial
            </a>
        </div>
      </div>

      <!-- PRODUCTOS -->
      <div class="space-y-1">
        <button @click="toggleCategory('productos')" class="category-header group bg-rose-900/20 border-l-2 border-rose-500/50">
            <span class="flex items-center gap-2 text-rose-400 font-bold">
                <i class="fas fa-box-open w-5 text-center text-rose-500"></i>
                PRODUCTOS
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200 text-rose-500/50" :class="{ 'rotate-90': uiStore.sidebarState.productos }"></i>
        </button>
        <div v-show="uiStore.sidebarState.productos" class="pl-4 space-y-1 pt-1">
            <a href="#" @click.prevent="navigate('Productos')" class="nav-item-sub" :class="{ 'active-link border-rose-400': isActive('Productos') }">
                <i class="fas fa-box w-5"></i> Gestión Productos
            </a>
            
            <!-- Rubros with Hover Menu -->
            <div class="relative group/rubros">
                <a href="#" @click.prevent="navigate('Rubros')" class="nav-item-sub flex justify-between items-center" :class="{ 'active-link border-rose-400': isActive('Rubros') }">
                    <div class="flex items-center gap-3">
                        <i class="fas fa-folder-tree w-5"></i> Rubros
                    </div>
                    <i class="fas fa-chevron-right text-[10px] opacity-0 group-hover/rubros:opacity-50"></i>
                </a>
                <!-- Hover Dropdown -->
                <div class="hidden group-hover/rubros:block absolute left-full top-0 ml-2 w-48 bg-[#1a050b] border border-rose-900/50 rounded-lg shadow-xl z-50 overflow-hidden transform transition-all">
                    <div class="px-3 py-2 text-xs font-bold text-rose-400 border-b border-rose-900/30 bg-rose-900/10">Jeraquía Rubros</div>
                    <a href="#" class="block px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-rose-900/20 transition-colors">
                        <i class="fas fa-folder-open mr-2 text-rose-500/50"></i> Sub-Rubros
                    </a>
                    <a href="#" class="block px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-rose-900/20 transition-colors">
                        <i class="fas fa-tags mr-2 text-rose-500/50"></i> Familias
                    </a>
                </div>
            </div>

             <a href="#" @click.prevent="navigate('ListasPrecios')" class="nav-item-sub" :class="{ 'active-link border-rose-400': isActive('ListasPrecios') }">
                <i class="fas fa-tags w-5"></i> Listas de Precios
            </a>
        </div>
      </div>

      <!-- CLIENTES -->
      <div class="space-y-1">
        <button @click="toggleCategory('clientes')" class="category-header group bg-cyan-900/20 border-l-2 border-cyan-500/50">
             <span class="flex items-center gap-2 text-cyan-400 font-bold">
                <i class="fas fa-users w-5 text-center text-cyan-500"></i>
                CLIENTES
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200 text-cyan-500/50" :class="{ 'rotate-90': uiStore.sidebarState.clientes }"></i>
        </button>
        <div v-show="uiStore.sidebarState.clientes" class="pl-4 space-y-1 pt-1">
            <a href="#" @click.prevent="navigate('HaweHome')" class="nav-item-sub" :class="{ 'active-link border-cyan-400': isActive('HaweHome') }">
                <i class="fas fa-address-card w-5"></i> Gestión Clientes
            </a>
            <a href="#" @click.prevent="navigate('Segmentos')" class="nav-item-sub" :class="{ 'active-link border-cyan-400': isActive('Segmentos') }">
                <i class="fas fa-layer-group w-5"></i> Segmentos de Mercado
            </a>
             <a href="#" @click.prevent="navigate('Vendedores')" class="nav-item-sub" :class="{ 'active-link border-cyan-400': isActive('Vendedores') }">
                <i class="fas fa-user-tag w-5"></i> Vendedores
            </a>
        </div>
      </div>

      <!-- TABLAS COMPARTIDAS -->
      <div class="space-y-1">
        <button @click="toggleCategory('compartidas')" class="category-header group bg-amber-900/20 border-l-2 border-amber-500/50">
             <span class="flex items-center gap-2 text-amber-500 font-bold">
                <i class="fas fa-table w-5 text-center text-amber-500"></i>
                TABLAS COMPARTIDAS
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200 text-amber-500/50" :class="{ 'rotate-90': uiStore.sidebarState.compartidas }"></i>
        </button>
        <div v-show="uiStore.sidebarState.compartidas" class="pl-4 space-y-1 pt-1">
            <a href="#" @click.prevent="navigate('Contactos')" class="nav-item-sub" :class="{ 'active-link': isActive('Contactos') }">
                <i class="fas fa-address-book w-5"></i> Agenda Global
            </a>
            <a href="#" @click.prevent="navigate('Transportes')" class="nav-item-sub" :class="{ 'active-link': isActive('Transportes') }">
                <i class="fas fa-truck w-5"></i> Logística / Transportes
            </a>
            <a href="#" @click.prevent="handleDepositosClick" class="nav-item-sub">
                <i class="fas fa-warehouse w-5"></i> Depósitos Internos
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
import { useRouter, useRoute } from 'vue-router'

import { useUIStore } from '../../stores/ui'
import { useNotificationStore } from '../../stores/notification'

const props = defineProps({
    theme: {
        type: String,
        default: 'cyan' // cyan, orange, rose, green
    }
})

const router = useRouter()
const route = useRoute()
const emit = defineEmits(['logout', 'open-command-palette', 'navigate'])
const uiStore = useUIStore()
const notificationStore = useNotificationStore()

const themeColors = {
    cyan: 'text-cyan-400',
    orange: 'text-orange-400',
    rose: 'text-rose-400',
    green: 'text-emerald-400',
    amber: 'text-amber-500'
}

const themeBgClass = computed(() => {
    switch (props.theme) {
        case 'orange': return 'bg-[#1a0a05] border-orange-900/30'
        case 'rose': return 'bg-[#1f050a] border-rose-900/30'
        case 'green': return 'bg-[#0e1f12] border-emerald-900/30'
        case 'amber': return 'bg-[#1f1605] border-amber-900/30'
        default: return 'bg-[#05151f] border-cyan-900/30'
    }
})

const logoColor = computed(() => themeColors[props.theme] || themeColors.cyan)

const toggleCategory = (cat) => {
    uiStore.toggleSidebarCategory(cat)
}

const navigate = (routeName, params = {}) => {
    router.push({ name: routeName, params })
}

const isActive = (routeName) => {
    return route.name === routeName
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
.nav-item-compact {
    @apply flex items-center gap-3 rounded-md px-2 py-1.5 text-xs font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white;
}
.nav-item-compact i {
    @apply w-4 text-center;
}
.category-header {
    @apply w-full flex items-center justify-between px-2 py-2 text-[10px] uppercase tracking-wider transition-all mb-1 rounded-r-md;
}
.nav-item-sub {
    @apply flex items-center gap-3 rounded-md px-3 py-2 text-sm text-white/60 transition-colors hover:bg-white/10 hover:text-white border-l-2 border-transparent;
}
.active-link {
    @apply text-white bg-white/5;
}
/* Dynamic Active Border Colors */
.active-link[href*="Productos"], .active-link[href*="Rubros"] {
     /* This logic is hard to do with pure CSS if we want it dynamic based on prop. 
        We'll rely on the parent passing the theme and maybe inline style or class binding in template.
        Actually, let's just use a generic active class and bind the border color in template.
     */
}
</style>
