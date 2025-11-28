<template>
  <div class="flex h-full w-80 flex-col border-l border-gray-800 bg-gray-900/90 backdrop-blur-xl transition-all">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-gray-800 p-4">
      <h2 class="font-outfit text-sm font-bold uppercase tracking-wider text-gray-400">Inspector</h2>
      <button class="text-gray-500 hover:text-white">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- Content -->
    <div v-if="item" class="flex-1 overflow-y-auto p-6">
      <!-- Preview -->
      <div class="mb-6 flex justify-center">
        <div class="flex h-24 w-24 items-center justify-center rounded-full bg-gray-800 text-4xl text-cyan-500 shadow-[0_0_20px_rgba(6,182,212,0.2)]">
          <i class="fas fa-user"></i>
        </div>
      </div>

      <!-- Title -->
      <div class="mb-8 text-center">
        <h3 class="font-outfit text-xl font-bold text-white">{{ item.razon_social }}</h3>
        <p class="font-mono text-sm text-gray-500">{{ item.cuit }}</p>
      </div>

      <!-- Properties Grid -->
      <div class="space-y-6">
        <!-- Section -->
        <div>
          <h4 class="mb-2 text-xs font-semibold uppercase text-gray-600">Contacto Principal</h4>
          <div class="rounded-lg bg-gray-800/50 p-3">
            <div class="flex items-center gap-3">
              <div class="h-8 w-8 rounded-full bg-gray-700"></div>
              <div>
                <p class="text-sm font-medium text-gray-200">María González</p>
                <p class="text-xs text-gray-500">Compradora</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Section -->
        <div>
          <h4 class="mb-2 text-xs font-semibold uppercase text-gray-600">Estado Financiero</h4>
          <div class="grid grid-cols-2 gap-2">
            <div class="rounded-lg bg-gray-800/50 p-3 text-center">
              <p class="text-xs text-gray-500">Saldo</p>
              <p class="font-mono text-sm font-bold text-green-400">$0.00</p>
            </div>
            <div class="rounded-lg bg-gray-800/50 p-3 text-center">
              <p class="text-xs text-gray-500">Pedidos</p>
              <p class="font-mono text-sm font-bold text-white">12</p>
            </div>
          </div>
        </div>
        
         <!-- Section -->
        <div>
          <h4 class="mb-2 text-xs font-semibold uppercase text-gray-600">Logística</h4>
           <div class="rounded-lg bg-gray-800/50 p-3">
             <p class="text-sm text-gray-300"><i class="fas fa-truck mr-2 text-gray-500"></i>Via Cargo</p>
             <p class="text-xs text-gray-500 mt-1 ml-6">Domicilio Fiscal</p>
           </div>
        </div>

      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-1 flex-col items-center justify-center p-8 text-center text-gray-600">
      <i class="fas fa-mouse-pointer mb-4 text-3xl"></i>
      <p class="text-sm">Selecciona un elemento para ver sus propiedades</p>
    </div>
    
    <!-- Footer Actions -->
    <div v-if="item" class="border-t border-gray-800 p-4">
        <button class="w-full rounded-lg bg-cyan-600 py-2 text-sm font-bold text-white transition-colors hover:bg-cyan-500 shadow-[0_0_15px_rgba(8,145,178,0.4)]">
            <i class="fas fa-external-link-alt mr-2"></i> Abrir Ficha Completa
        </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    default: null
  }
})
</script>
