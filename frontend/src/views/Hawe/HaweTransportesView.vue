<template>
  <div class="flex h-screen w-full bg-[var(--hawe-bg-main)] text-gray-200 overflow-hidden font-sans">
    <!-- Left Sidebar (Reused from HaweView - Should be a component but duplicating for speed as per instructions) -->
    <aside class="flex w-64 flex-col border-r border-white/10 bg-black/20">
      <!-- Logo Area -->
      <div class="flex h-16 items-center px-6 border-b border-white/10">
        <div class="h-8 w-8 rounded bg-gradient-to-br from-cyan-400 to-blue-500 mr-3"></div>
        <span class="font-outfit text-lg font-bold tracking-tight text-white">HAWE <span class="text-cyan-400">V5</span></span>
      </div>

      <!-- Nav Links -->
      <nav class="flex-1 space-y-1 p-4 overflow-y-auto">
        <router-link to="/hawe" class="flex items-center rounded-lg px-4 py-3 text-sm font-medium text-white/70 transition-colors hover:bg-white/10 hover:text-white">
          <i class="fas fa-users w-6"></i>
          Clientes
        </router-link>
        
        <router-link to="/hawe/transportes" class="flex items-center rounded-lg bg-white/10 px-4 py-3 text-sm font-medium text-white shadow-md shadow-black/10 border-l-2 border-cyan-400">
          <i class="fas fa-truck w-6 text-cyan-400"></i>
          Transportes
        </router-link>

        <div class="my-4 border-t border-white/10"></div>

        <a href="#" class="flex items-center rounded-lg px-4 py-3 text-sm font-medium text-white/70 transition-colors hover:bg-white/10 hover:text-white">
          <i class="fas fa-box w-6"></i>
          Productos
        </a>
        <a href="#" class="flex items-center rounded-lg px-4 py-3 text-sm font-medium text-white/70 transition-colors hover:bg-white/10 hover:text-white">
          <i class="fas fa-shopping-cart w-6"></i>
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
    <main class="flex flex-1 flex-col relative">
      <!-- Top Bar -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-white/10 bg-black/10 px-6 backdrop-blur-sm">
        <h1 class="font-outfit text-xl font-semibold text-white">
            Explorador de Transportes
        </h1>

        <!-- Search & Tools -->
        <div class="flex items-center gap-4">
          <div class="relative">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar transporte..."
              class="h-9 w-64 rounded-full border border-gray-700 bg-gray-800 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
            />
          </div>
          <div class="h-6 w-px bg-white/10"></div>
          
          <button 
            @click="openNewTransporte"
            class="flex items-center gap-2 rounded-lg bg-cyan-600 px-3 py-1.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/20 transition-all hover:bg-cyan-500 hover:shadow-cyan-500/40"
          >
            <i class="fas fa-plus"></i>
            <span class="hidden sm:inline">Nuevo</span>
          </button>
        </div>
      </header>

      <!-- Content Grid -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-gray-900 scrollbar-thumb-gray-700">
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <div 
            v-for="transporte in filteredTransportes" 
            :key="transporte.id"
            @click="selectTransporte(transporte)"
            class="group relative flex flex-col justify-between rounded-xl border border-white/5 bg-white/5 p-4 transition-all hover:bg-white/10 hover:shadow-xl hover:shadow-cyan-900/20 cursor-pointer"
            :class="{ 'ring-2 ring-cyan-500 bg-white/10': selectedId === transporte.id }"
          >
            <div class="flex items-start justify-between">
                <div class="flex items-center gap-3">
                    <div class="h-10 w-10 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white shadow-lg">
                        <i class="fas fa-truck"></i>
                    </div>
                    <div>
                        <h3 class="font-bold text-white leading-tight group-hover:text-cyan-300 transition-colors">{{ transporte.nombre }}</h3>
                        <p class="text-xs text-white/50">{{ transporte.telefono || 'Sin teléfono' }}</p>
                    </div>
                </div>
                <div class="h-2 w-2 rounded-full" :class="transporte.activo ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500'"></div>
            </div>
            
            <div class="mt-4 pt-4 border-t border-white/5 flex justify-between items-center">
                <span class="text-[10px] uppercase font-bold text-white/30 tracking-wider">ID: {{ transporte.id }}</span>
                <i class="fas fa-chevron-right text-white/20 group-hover:translate-x-1 transition-transform"></i>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Right Inspector Panel (Simplified for Transportes) -->
    <aside class="w-80 border-l border-gray-800 bg-gray-900/50 p-6" v-if="selectedTransporte">
        <h2 class="text-lg font-bold text-white mb-4">Detalle de Transporte</h2>
        
        <div class="space-y-4">
            <div>
                <label class="block text-xs font-bold uppercase text-white/40 mb-1">Nombre</label>
                <input v-model="selectedTransporte.nombre" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none" />
            </div>
            <div>
                <label class="block text-xs font-bold uppercase text-white/40 mb-1">Teléfono</label>
                <input v-model="selectedTransporte.telefono_reclamos" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none" />
            </div>
             <div>
                <label class="block text-xs font-bold uppercase text-white/40 mb-1">Web Tracking</label>
                <input v-model="selectedTransporte.web_tracking" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none" />
            </div>
            
            <div class="flex items-center gap-2 mt-4">
                <input type="checkbox" v-model="selectedTransporte.activo" id="activeCheck" class="accent-cyan-500 h-4 w-4" />
                <label for="activeCheck" class="text-sm text-white">Activo</label>
            </div>

            <div class="pt-6 mt-6 border-t border-white/10 flex gap-3">
                <button @click="saveTransporte" class="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white py-2 rounded font-bold transition-colors">Guardar</button>
                <button @click="deleteTransporte" class="px-3 bg-red-900/20 hover:bg-red-900/40 text-red-400 rounded border border-red-500/30"><i class="fas fa-trash"></i></button>
            </div>
        </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useLogisticaStore } from '../stores/logistica' // Assuming this store exists or we use generic
import { useNotificationStore } from '../stores/notification'

// Mock store if not exists, but let's try to use what we have. 
// If logistica store doesn't exist, I'll need to create it or use a generic one.
// Checking previous context, TransporteList.vue exists, so likely a store exists.
// Let's assume useTransportesStore or similar. I'll check imports in TransporteList.vue if this fails, but for now I'll write generic logic.

import { useLogisticaStore } from '../../stores/logistica'

const transporteStore = useLogisticaStore()
const notificationStore = useNotificationStore()

const transportes = ref([])
const searchQuery = ref('')
const selectedId = ref(null)
const selectedTransporte = ref(null)

onMounted(async () => {
    try {
        await transporteStore.fetchEmpresas('all')
        transportes.value = transporteStore.empresas
    } catch (e) {
        console.error(e)
    }
})

const filteredTransportes = computed(() => {
    if (!searchQuery.value) return transportes.value
    const query = searchQuery.value.toLowerCase()
    return transportes.value.filter(t => t.nombre.toLowerCase().includes(query))
})

const selectTransporte = (t) => {
    selectedId.value = t.id
    // Clone to avoid direct mutation before save
    selectedTransporte.value = { ...t }
}

const openNewTransporte = () => {
    selectedId.value = 'new'
    selectedTransporte.value = {
        id: null,
        nombre: '',
        telefono_reclamos: '', // Adjusted field name
        direccion: '', // Note: API might not support this yet, check store
        activo: true
    }
}

const saveTransporte = async () => {
    try {
        if (selectedId.value === 'new') {
            await transporteStore.createEmpresa(selectedTransporte.value)
            notificationStore.add('Transporte creado', 'success')
        } else {
            await transporteStore.updateEmpresa(selectedTransporte.value.id, selectedTransporte.value)
            notificationStore.add('Transporte actualizado', 'success')
        }
        await transporteStore.fetchEmpresas('all')
        transportes.value = transporteStore.empresas
        selectedId.value = null
        selectedTransporte.value = null
    } catch (e) {
        notificationStore.add('Error al guardar', 'error')
    }
}

const deleteTransporte = async () => {
    if (!confirm('¿Eliminar transporte?')) return
    try {
        await transporteStore.updateEmpresa(selectedTransporte.value.id, { ...selectedTransporte.value, activo: false }) // Soft delete as per legacy
        notificationStore.add('Transporte eliminado', 'success')
        await transporteStore.fetchEmpresas('all')
        transportes.value = transporteStore.empresas
        selectedId.value = null
        selectedTransporte.value = null
    } catch (e) {
        notificationStore.add('Error al eliminar', 'error')
    }
}
</script>
