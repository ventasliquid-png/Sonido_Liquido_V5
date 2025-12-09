<template>
  <aside class="flex w-64 flex-col border-r border-white/10 h-full transition-colors duration-300 bg-[#0a0a0a] z-50">
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

    <!-- Nav Links (No overflow hidden/auto to allow flyouts) -->
    <nav class="flex-1 px-4 py-2 space-y-4 relative">
      
      <!-- Most Used Section -->
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

      <!-- PEDIDOS -->
      <div class="relative group">
        <!-- Header Trigger -->
        <button class="w-full flex items-center justify-between px-4 py-3 rounded-lg bg-emerald-900/10 border border-emerald-900/20 hover:bg-emerald-900/20 hover:border-emerald-500/30 transition-all duration-200">
             <span class="flex items-center gap-3 text-emerald-400 font-bold tracking-wide">
                <i class="fas fa-shopping-cart w-5 text-center text-emerald-500"></i>
                PEDIDOS
            </span>
            <i class="fas fa-chevron-right text-xs text-emerald-500/30"></i>
        </button>

        <!-- Flyout Menu -->
        <div class="hidden group-hover:block absolute left-[95%] top-0 ml-2 w-64 bg-[#0e1f12] border border-emerald-500/30 rounded-xl shadow-2xl z-[100] backdrop-blur-xl p-3 transform transition-all duration-200 origin-top-left">
             <div class="text-[10px] uppercase font-bold text-emerald-500/50 mb-2 px-2 border-b border-emerald-500/20 pb-1">Acciones</div>
             <div class="space-y-1">
                <a href="#" @click.prevent="navigate('Pedidos')" class="nav-item-sub hover:bg-emerald-500/10">
                    <i class="fas fa-plus w-5 text-emerald-400"></i> 
                    <span class="text-white/80">Nuevo Pedido</span>
                </a>
                <a href="#" class="nav-item-sub text-white/30 cursor-not-allowed" title="Próximamente">
                    <i class="fas fa-list w-5"></i> Historial
                </a>
             </div>
        </div>
      </div>

      <!-- PRODUCTOS -->
      <div class="relative group">
         <button class="w-full flex items-center justify-between px-4 py-3 rounded-lg bg-rose-900/10 border border-rose-900/20 hover:bg-rose-900/20 hover:border-rose-500/30 transition-all duration-200">
             <span class="flex items-center gap-3 text-rose-400 font-bold tracking-wide">
                <i class="fas fa-box-open w-5 text-center text-rose-500"></i>
                PRODUCTOS
            </span>
             <i class="fas fa-chevron-right text-xs text-rose-500/30"></i>
        </button>

        <!-- Flyout Menu (Bordó) -->
        <div class="hidden group-hover:block absolute left-[95%] top-0 ml-2 w-64 bg-[#2e0a13] border border-rose-500/30 rounded-xl shadow-2xl z-[100] backdrop-blur-xl p-3">
             <div class="text-[10px] uppercase font-bold text-rose-500/50 mb-2 px-2 border-b border-rose-500/20 pb-1">Gestión de Catálogo</div>
             <div class="space-y-1">
                <a href="#" @click.prevent="navigate('Productos')" class="nav-item-sub hover:bg-rose-500/10" :class="{ 'active-link-rose': isActive('Productos') }">
                    <i class="fas fa-box w-5 text-rose-400"></i> 
                    <span class="text-white/80">Gestión de Productos</span>
                </a>
                
                <a href="#" @click.prevent="navigate('Rubros')" class="nav-item-sub hover:bg-rose-500/10" :class="{ 'active-link-rose': isActive('Rubros') }">
                     <i class="fas fa-folder-tree w-5 text-rose-400"></i> 
                     <span class="text-white/80">Rubros</span>
                </a>

                 <a href="#" @click.prevent="navigate('ListasPrecios')" class="nav-item-sub hover:bg-rose-500/10" :class="{ 'active-link-rose': isActive('ListasPrecios') }">
                    <i class="fas fa-tags w-5 text-rose-400"></i> 
                    <span class="text-white/80">Listas de Precios</span>
                </a>
             </div>
        </div>
      </div>

      <!-- CLIENTES -->
      <div class="relative group">
        <button class="w-full flex items-center justify-between px-4 py-3 rounded-lg bg-cyan-900/10 border border-cyan-900/20 hover:bg-cyan-900/20 hover:border-cyan-500/30 transition-all duration-200">
             <span class="flex items-center gap-3 text-cyan-400 font-bold tracking-wide">
                <i class="fas fa-users w-5 text-center text-cyan-500"></i>
                CLIENTES
            </span>
            <i class="fas fa-chevron-right text-xs text-cyan-500/30"></i>
        </button>

        <!-- Flyout Menu (Azul) -->
        <div class="hidden group-hover:block absolute left-[95%] top-0 ml-2 w-64 bg-[#0a1f2e] border border-cyan-500/30 rounded-xl shadow-2xl z-[100] backdrop-blur-xl p-3">
             <div class="text-[10px] uppercase font-bold text-cyan-500/50 mb-2 px-2 border-b border-cyan-500/20 pb-1">Cartera & Ventas</div>
             <div class="space-y-1">
                <a href="#" @click.prevent="navigate('HaweHome')" class="nav-item-sub hover:bg-cyan-500/10" :class="{ 'active-link-cyan': isActive('HaweHome') }">
                    <i class="fas fa-address-card w-5 text-cyan-400"></i> 
                    <span class="text-white/80">Gestión Clientes</span>
                </a>
                <a href="#" @click.prevent="navigate('Segmentos')" class="nav-item-sub hover:bg-cyan-500/10" :class="{ 'active-link-cyan': isActive('Segmentos') }">
                    <i class="fas fa-layer-group w-5 text-cyan-400"></i> 
                    <span class="text-white/80">Segmentos</span>
                </a>
                 <a href="#" @click.prevent="navigate('Vendedores')" class="nav-item-sub hover:bg-cyan-500/10" :class="{ 'active-link-cyan': isActive('Vendedores') }">
                    <i class="fas fa-user-tag w-5 text-cyan-400"></i> 
                    <span class="text-white/80">Vendedores</span>
                </a>
             </div>
        </div>
      </div>

      <!-- TABLAS COMPARTIDAS -->
       <div class="relative group">
        <button class="w-full flex items-center justify-between px-4 py-3 rounded-lg bg-amber-900/10 border border-amber-900/20 hover:bg-amber-900/20 hover:border-amber-500/30 transition-all duration-200">
             <span class="flex items-center gap-3 text-amber-500 font-bold tracking-wide">
                <i class="fas fa-table w-5 text-center text-amber-500"></i>
                MAESTROS
            </span>
            <i class="fas fa-chevron-right text-xs text-amber-500/30"></i>
        </button>

        <!-- Flyout Menu (Amber) -->
        <div class="hidden group-hover:block absolute left-[95%] top-0 ml-2 w-64 bg-[#1f1605] border border-amber-500/30 rounded-xl shadow-2xl z-[100] backdrop-blur-xl p-3">
             <div class="text-[10px] uppercase font-bold text-amber-500/50 mb-2 px-2 border-b border-amber-500/20 pb-1">Configuración Global</div>
             <div class="space-y-1">
                <a href="#" @click.prevent="navigate('Contactos')" class="nav-item-sub hover:bg-amber-500/10" :class="{ 'active-link-amber': isActive('Contactos') }">
                    <i class="fas fa-address-book w-5 text-amber-400"></i> 
                    <span class="text-white/80">Agenda Contactos</span>
                </a>
                <a href="#" @click.prevent="navigate('Transportes')" class="nav-item-sub hover:bg-amber-500/10" :class="{ 'active-link-amber': isActive('Transportes') }">
                    <i class="fas fa-truck w-5 text-amber-400"></i> 
                    <span class="text-white/80">Logística</span>
                </a>
                <a href="#" @click.prevent="handleDepositosClick" class="nav-item-sub hover:bg-amber-500/10">
                    <i class="fas fa-warehouse w-5 text-amber-400"></i> 
                    <span class="text-white/80">Depósitos</span>
                </a>
             </div>
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
import { useRouter, useRoute } from 'vue-router'
import { useNotificationStore } from '../../stores/notification'

// Clean props, no logical dependencies on theme or uiStore for sidebar State anymore
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
.nav-item-compact {
    @apply flex items-center gap-3 rounded-md px-2 py-1.5 text-xs font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white;
}
.nav-item-compact i {
    @apply w-4 text-center;
}
.nav-item-sub {
    @apply flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-all duration-200 border-l-2 border-transparent;
}

/* Specific Active Links within Flyouts */
.active-link-cyan {
    @apply text-white bg-cyan-900/30 border-cyan-400 text-cyan-50 font-bold;
}
.active-link-rose {
    @apply text-white bg-rose-900/30 border-rose-400 text-rose-50 font-bold;
}
.active-link-amber {
    @apply text-white bg-amber-900/30 border-amber-400 text-amber-50 font-bold;
}
</style>
