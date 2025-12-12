<template>
  <aside class="flex w-64 flex-col border-r border-white/10 h-full transition-colors duration-300 bg-[#0a0a0a] z-50 shrink-0">
    <!-- Logo Area -->
    <div class="flex h-16 items-center px-6 border-b border-white/10 shrink-0">
      <div class="h-8 w-8 rounded bg-gradient-to-br from-gray-700 to-gray-900 mr-3 shadow-lg flex items-center justify-center">
        <i class="fas fa-bolt text-cyan-400"></i>
      </div>
      <span class="font-outfit text-lg font-bold tracking-tight text-white">HAWE <span class="text-cyan-400">V5</span></span>
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
    <nav class="flex-1 px-4 py-2 space-y-2 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">
      
      <!-- Most Used Section -->
      <div class="mx-2 mb-4 rounded-lg bg-white/5 border border-white/10 p-2 space-y-1">
        <h3 class="px-2 text-[10px] font-bold uppercase text-cyan-400/80 tracking-wider mb-2 flex items-center gap-2">
            <i class="fas fa-star text-yellow-500/50"></i> Más Usados
        </h3>
        <a href="#" @click.prevent="navigate('HaweClientCanvas', { id: 'new' })" class="nav-item-compact">
            <i class="fas fa-plus-circle text-green-400"></i>
            <span class="truncate">Nuevo Cliente</span>
        </a>
        <a href="#" @click.prevent="navigate('TacticalLoader')" class="nav-item-compact">
            <i class="fas fa-cart-plus text-yellow-400"></i>
            <span class="truncate">Nuevo Pedido (Táctico)</span>
        </a>
      </div>

      <!-- PEDIDOS Group -->
      <div class="space-y-1">
        <button 
            @click="toggleGroup('PEDIDOS')"
            class="w-full flex items-center justify-between px-4 py-3 rounded-lg border transition-all duration-200"
            :class="isGroupActive('PEDIDOS') || expandedGroups.includes('PEDIDOS') ? 'bg-emerald-900/20 border-emerald-500/30' : 'bg-transparent border-transparent hover:bg-white/5'"
        >
             <span class="flex items-center gap-3 text-emerald-400 font-bold tracking-wide text-sm">
                <i class="fas fa-shopping-cart w-5 text-center" :class="isGroupActive('PEDIDOS') ? 'text-emerald-400' : 'text-emerald-500/50'"></i>
                PEDIDOS
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200" :class="expandedGroups.includes('PEDIDOS') ? 'rotate-90 text-emerald-400' : 'text-white/20'"></i>
        </button>
        
        <div v-show="expandedGroups.includes('PEDIDOS')" class="pl-4 space-y-1">
            <a href="#" @click.prevent="navigate('TacticalLoader')" class="nav-item-sub" :class="{ 'active-link-emerald': isActive('TacticalLoader') }">
                <i class="fas fa-plus w-4"></i> 
                <span>Nuevo Pedido (Táctico)</span>
            </a>
            <a href="#" class="nav-item-sub text-white/30 cursor-not-allowed">
                <i class="fas fa-list w-4"></i> 
                <span>Historial</span>
            </a>
        </div>
      </div>

      <!-- PRODUCTOS Group -->
      <div class="space-y-1">
        <button 
            @click="toggleGroup('PRODUCTOS')"
            class="w-full flex items-center justify-between px-4 py-3 rounded-lg border transition-all duration-200"
            :class="isGroupActive('PRODUCTOS') || expandedGroups.includes('PRODUCTOS') ? 'bg-rose-900/20 border-rose-500/30' : 'bg-transparent border-transparent hover:bg-white/5'"
        >
             <span class="flex items-center gap-3 text-rose-400 font-bold tracking-wide text-sm">
                <i class="fas fa-box-open w-5 text-center" :class="isGroupActive('PRODUCTOS') ? 'text-rose-400' : 'text-rose-500/50'"></i>
                PRODUCTOS
            </span>
             <i class="fas fa-chevron-right text-xs transition-transform duration-200" :class="expandedGroups.includes('PRODUCTOS') ? 'rotate-90 text-rose-400' : 'text-white/20'"></i>
        </button>

        <div v-show="expandedGroups.includes('PRODUCTOS')" class="pl-4 space-y-1">
             <a href="#" @click.prevent="navigate('Productos')" class="nav-item-sub" :class="{ 'active-link-rose': isActive('Productos') }">
                <i class="fas fa-box w-4"></i> 
                <span>Gestión de Productos</span>
            </a>
            <a href="#" @click.prevent="navigate('Rubros')" class="nav-item-sub" :class="{ 'active-link-rose': isActive('Rubros') }">
                 <i class="fas fa-folder-tree w-4"></i> 
                 <span>Rubros</span>
            </a>
             <a href="#" @click.prevent="navigate('ListasPrecios')" class="nav-item-sub" :class="{ 'active-link-rose': isActive('ListasPrecios') }">
                <i class="fas fa-tags w-4"></i> 
                <span>Listas de Precios</span>
            </a>
        </div>
      </div>

      <!-- CLIENTES Group -->
      <div class="space-y-1">
        <button 
            @click="toggleGroup('CLIENTES')"
            class="w-full flex items-center justify-between px-4 py-3 rounded-lg border transition-all duration-200"
            :class="isGroupActive('CLIENTES') || expandedGroups.includes('CLIENTES') ? 'bg-cyan-900/20 border-cyan-500/30' : 'bg-transparent border-transparent hover:bg-white/5'"
        >
             <span class="flex items-center gap-3 text-cyan-400 font-bold tracking-wide text-sm">
                <i class="fas fa-users w-5 text-center" :class="isGroupActive('CLIENTES') ? 'text-cyan-400' : 'text-cyan-500/50'"></i>
                CLIENTES
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200" :class="expandedGroups.includes('CLIENTES') ? 'rotate-90 text-cyan-400' : 'text-white/20'"></i>
        </button>

        <div v-show="expandedGroups.includes('CLIENTES')" class="pl-4 space-y-1">
            <a href="#" @click.prevent="navigate('HaweHome')" class="nav-item-sub" :class="{ 'active-link-cyan': isActive('HaweHome') }">
                <i class="fas fa-address-card w-4"></i> 
                <span>Gestión Clientes</span>
            </a>
            <a href="#" @click.prevent="navigate('Segmentos')" class="nav-item-sub" :class="{ 'active-link-cyan': isActive('Segmentos') }">
                <i class="fas fa-layer-group w-4"></i> 
                <span>Segmentos</span>
            </a>
             <a href="#" @click.prevent="navigate('Vendedores')" class="nav-item-sub" :class="{ 'active-link-cyan': isActive('Vendedores') }">
                <i class="fas fa-user-tag w-4"></i> 
                <span>Vendedores</span>
            </a>
        </div>
      </div>

      <!-- MAESTROS Group -->
       <div class="space-y-1">
        <button 
            @click="toggleGroup('MAESTROS')"
            class="w-full flex items-center justify-between px-4 py-3 rounded-lg border transition-all duration-200"
            :class="isGroupActive('MAESTROS') || expandedGroups.includes('MAESTROS') ? 'bg-amber-900/20 border-amber-500/30' : 'bg-transparent border-transparent hover:bg-white/5'"
        >
             <span class="flex items-center gap-3 text-amber-500 font-bold tracking-wide text-sm">
                <i class="fas fa-table w-5 text-center" :class="isGroupActive('MAESTROS') ? 'text-amber-500' : 'text-amber-500/50'"></i>
                MAESTROS
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200" :class="expandedGroups.includes('MAESTROS') ? 'rotate-90 text-amber-500' : 'text-white/20'"></i>
        </button>

        <div v-show="expandedGroups.includes('MAESTROS')" class="pl-4 space-y-1">
            <a href="#" @click.prevent="navigate('Contactos')" class="nav-item-sub" :class="{ 'active-link-amber': isActive('Contactos') }">
                <i class="fas fa-address-book w-4"></i> 
                <span>Agenda Contactos</span>
            </a>
            <a href="#" @click.prevent="navigate('Transportes')" class="nav-item-sub" :class="{ 'active-link-amber': isActive('Transportes') }">
                <i class="fas fa-truck w-4"></i> 
                <span>Logística</span>
            </a>
            <a href="#" @click.prevent="handleDepositosClick" class="nav-item-sub hover:text-amber-200 text-white/50">
                <i class="fas fa-warehouse w-4"></i> 
                <span>Depósitos</span>
            </a>
        </div>
      </div>

      <!-- DATA INTEL Group (Pilot) -->
      <div class="space-y-1">
        <button 
            @click="toggleGroup('INTEL')"
            class="w-full flex items-center justify-between px-4 py-3 rounded-lg border transition-all duration-200"
            :class="isGroupActive('INTEL') || expandedGroups.includes('INTEL') ? 'bg-indigo-900/20 border-indigo-500/30' : 'bg-transparent border-transparent hover:bg-white/5'"
        >
             <span class="flex items-center gap-3 text-indigo-400 font-bold tracking-wide text-sm">
                <i class="fas fa-brain w-5 text-center" :class="isGroupActive('INTEL') ? 'text-indigo-400' : 'text-indigo-500/50'"></i>
                INTELIGENCIA
            </span>
            <i class="fas fa-chevron-right text-xs transition-transform duration-200" :class="expandedGroups.includes('INTEL') ? 'rotate-90 text-indigo-400' : 'text-white/20'"></i>
        </button>

        <div v-show="expandedGroups.includes('INTEL')" class="pl-4 space-y-1">
            <a href="#" @click.prevent="navigate('data-cleaner')" class="nav-item-sub" :class="{ 'active-link-indigo': isActive('data-cleaner') }">
                <i class="fas fa-broom w-4"></i> 
                <span>Depurador de Datos</span>
            </a>
        </div>
      </div>

    </nav>

    <!-- User Profile -->
    <div 
      class="border-t border-white/10 p-4 cursor-pointer hover:bg-white/5 transition-colors group mt-auto shrink-0"
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
import { useRouter, useRoute } from 'vue-router'
import { ref, watch, onMounted } from 'vue'
import { useNotificationStore } from '../../stores/notification'

const props = defineProps({
    theme: {
        type: String,
        default: 'cyan'
    }
})

const router = useRouter()
const route = useRoute()
const emit = defineEmits(['logout', 'open-command-palette', 'navigate'])
const notificationStore = useNotificationStore()
const expandedGroups = ref([])

const navigate = (routeName, params = {}) => {
    router.push({ name: routeName, params })
}

const isActive = (routeName) => {
    return route.name === routeName
}

const isGroupActive = (group) => {
    if (group === 'CLIENTES') return ['HaweHome', 'Segmentos', 'Vendedores', 'HaweClientCanvas'].includes(route.name)
    if (group === 'PRODUCTOS') return ['Productos', 'Rubros', 'ListasPrecios'].includes(route.name)
    if (group === 'MAESTROS') return ['Contactos', 'Transportes'].includes(route.name)
    if (group === 'PEDIDOS') return ['Pedidos', 'PedidoTactico'].includes(route.name)
    if (group === 'INTEL') return ['data-cleaner'].includes(route.name)
    return false
}

const toggleGroup = (group) => {
    const index = expandedGroups.value.indexOf(group)
    if (index === -1) {
        expandedGroups.value.push(group)
    } else {
        expandedGroups.value.splice(index, 1)
    }
}

const autoExpand = () => {
    ['CLIENTES', 'PRODUCTOS', 'MAESTROS', 'PEDIDOS'].forEach(group => {
        if (isGroupActive(group) && !expandedGroups.value.includes(group)) {
            expandedGroups.value.push(group)
        }
    })
}

watch(() => route.name, () => {
    autoExpand()
})

onMounted(() => {
    autoExpand()
})

const handleDepositosClick = () => {
    notificationStore.add('Módulo de Depósitos próximamente', 'info')
}
</script>

<style scoped>
.nav-item-compact {
    @apply flex items-center gap-3 rounded-md px-2 py-1.5 text-xs font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white;
}
.nav-item-compact i {
    @apply w-4 text-center;
}
.nav-item-sub {
    @apply flex items-center gap-3 rounded-r-md px-3 py-2 text-sm transition-all duration-200 border-l-2 border-white/5 hover:bg-white/5 hover:text-white text-white/60;
}

/* Specific Active Links */
.active-link-cyan {
    @apply text-cyan-200 bg-cyan-900/10 border-cyan-400 font-bold;
}
.active-link-rose {
    @apply text-rose-200 bg-rose-900/10 border-rose-400 font-bold;
}
.active-link-amber {
    @apply text-amber-200 bg-amber-900/10 border-amber-400 font-bold;
}
.active-link-emerald {
    @apply text-emerald-200 bg-emerald-900/10 border-emerald-400 font-bold;
}
.active-link-indigo {
    @apply text-indigo-200 bg-indigo-900/10 border-indigo-400 font-bold;
}
</style>
