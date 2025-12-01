<template>
  <div class="flex h-screen w-full bg-[var(--hawe-bg-main)] text-gray-200 overflow-hidden font-sans">
    <!-- Left Sidebar (Reused from HaweView) -->
    <aside class="flex w-64 flex-col border-r border-white/10 bg-black/20">
      <!-- Logo Area -->
      <div class="flex h-16 items-center px-6 border-b border-white/10">
        <div class="h-8 w-8 rounded bg-gradient-to-br from-cyan-400 to-blue-500 mr-3"></div>
        <span class="font-outfit text-lg font-bold tracking-tight text-white">HAWE <span class="text-cyan-400">V5</span></span>
      </div>

      <!-- Nav Links -->
      <nav class="flex-1 space-y-1 p-4 overflow-y-auto">
        <router-link to="/hawe" class="flex items-center rounded-lg px-4 py-3 text-sm font-medium text-white/70 transition-colors hover:bg-white/10 hover:text-white">
          <i class="fa-solid fa-users w-6"></i>
          Clientes
        </router-link>
        
        <router-link to="/hawe/transportes" class="flex items-center rounded-lg bg-white/10 px-4 py-3 text-sm font-medium text-white shadow-md shadow-black/10 border-l-2 border-cyan-400">
          <i class="fa-solid fa-truck w-6 text-cyan-400"></i>
          Transportes
        </router-link>

        <div class="my-4 border-t border-white/10"></div>

        <a href="#" class="flex items-center rounded-lg px-4 py-3 text-sm font-medium text-white/70 transition-colors hover:bg-white/10 hover:text-white">
          <i class="fa-solid fa-box w-6"></i>
          Productos
        </a>
        <a href="#" class="flex items-center rounded-lg px-4 py-3 text-sm font-medium text-white/70 transition-colors hover:bg-white/10 hover:text-white">
          <i class="fa-solid fa-shopping-cart w-6"></i>
          Pedidos
        </a>
      </nav>

      <!-- User Profile -->
      <div class="border-t border-white/10 p-4">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-full bg-white/10"></div>
          <div>
            <p class="text-sm font-medium text-white">Usuario</p>
            <p class="text-xs text-white/50">Admin</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <TransporteManager />
  </div>
</template>

<script setup>
import TransporteManager from './components/TransporteManager.vue'
</script>
