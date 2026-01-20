<template>
  <div class="flex h-screen w-full bg-[#050c12] text-gray-200 overflow-hidden font-sans">
    
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative min-w-0">
      <!-- Top Bar -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-amber-900/20 bg-[#0d121a]/80 px-6 backdrop-blur-md shrink-0">
        <div class="flex items-center gap-4">
            <div class="h-10 w-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-500 border border-amber-500/20 shadow-lg shadow-amber-900/20">
                <i class="fas fa-gem text-xl"></i>
            </div>
            <h1 class="font-outfit text-xl font-bold tracking-tight text-white">
                Cantera de Maestros
                <span class="ml-2 text-xs font-normal text-amber-500/70 border border-amber-500/30 px-2 py-0.5 rounded-full uppercase tracking-widest">
                    {{ activeTab === 'clientes' ? 'Clientes' : 'Productos' }}
                </span>
            </h1>
        </div>

        <!-- Search & Tools -->
        <div class="flex items-center gap-6">
          <!-- Tab Switcher -->
          <div class="flex bg-white/5 rounded-xl p-1 border border-white/10">
            <button 
                @click="activeTab = 'clientes'"
                class="flex items-center gap-2 px-4 py-1.5 text-xs font-bold rounded-lg transition-all"
                :class="activeTab === 'clientes' ? 'bg-amber-600 text-white shadow-lg shadow-amber-900/40' : 'text-gray-400 hover:text-white hover:bg-white/5'"
            >
                <i class="fas fa-users"></i>
                CLIENTES
            </button>
            <button 
                @click="activeTab = 'productos'"
                class="flex items-center gap-2 px-4 py-1.5 text-xs font-bold rounded-lg transition-all"
                :class="activeTab === 'productos' ? 'bg-amber-600 text-white shadow-lg shadow-amber-900/40' : 'text-gray-400 hover:text-white hover:bg-white/5'"
            >
                <i class="fas fa-box-open"></i>
                PRODUCTOS
            </button>
          </div>

          <div class="h-6 w-px bg-white/10"></div>

          <div class="relative">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-amber-500/50"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Filtrar en cantera..."
              class="h-10 w-72 rounded-xl border border-white/10 bg-black/40 pl-10 pr-4 text-sm text-amber-100 placeholder-white/20 focus:border-amber-500/50 focus:outline-none focus:ring-2 focus:ring-amber-500/20 transition-all"
            />
          </div>

          <div class="h-6 w-px bg-white/10"></div>

          <!-- Quick Actions -->
          <div class="flex gap-2">
              <button 
                @click="fetchData"
                class="h-10 w-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-amber-400 hover:bg-amber-500/10 transition-all"
                title="Refrescar"
              >
                <i class="fas fa-sync-alt" :class="{'animate-spin': loading}"></i>
              </button>
          </div>
        </div>
      </header>

      <!-- Scrollable Content -->
      <div class="flex-1 overflow-y-auto p-8 custom-scrollbar bg-[#050c12]">
        
        <!-- Loading Overlay -->
        <div v-if="loading" class="flex flex-col items-center justify-center h-64 opacity-50">
            <i class="fas fa-circle-notch fa-spin text-4xl text-amber-500 mb-4"></i>
            <p class="text-sm font-medium tracking-widest text-amber-500/70 border-t border-amber-900/20 pt-2 uppercase">Consultando Espejos...</p>
        </div>

        <!-- LISTADO DE CLIENTES -->
        <div v-else-if="activeTab === 'clientes'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
            <div 
                v-for="item in filteredItems" :key="item.id"
                class="group relative bg-[#0d121a] border border-white/5 rounded-2xl p-4 hover:border-amber-500/30 transition-all hover:translate-y-[-2px] shadow-lg hover:shadow-amber-900/10"
                :class="{'opacity-40 grayscale': !item.activo}"
            >
                <div class="flex justify-between items-start mb-3">
                    <div class="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="flex gap-2">
                        <span v-if="!item.activo" class="text-[9px] bg-red-900/30 text-red-500 px-2 py-0.5 rounded-full border border-red-500/20 font-bold uppercase tracking-tighter">Inactivo</span>
                        <button 
                            @click="inactivate(item)" 
                            class="h-7 w-7 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-gray-500 hover:text-red-500 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all"
                            title="Baja Definitiva"
                        >
                            <i class="fas fa-eye-slash"></i>
                        </button>
                    </div>
                </div>
                <h3 class="font-bold text-gray-100 truncate mb-1" :title="item.razon_social">{{ item.razon_social }}</h3>
                <p class="text-[10px] font-mono text-gray-500 mb-4">{{ item.cuit }}</p>
                
                <div class="flex items-center justify-between pt-4 border-t border-white/5">
                    <div class="flex -space-x-2">
                         <div class="h-6 w-6 rounded-full border-2 border-[#0d121a] bg-amber-500/20 flex items-center justify-center text-[10px] text-amber-400 font-bold" title="Cantera Original">C</div>
                    </div>
                    <button 
                        @click="handleImport(item)"
                        class="text-[10px] font-bold text-amber-500 hover:text-amber-400 uppercase tracking-widest flex items-center gap-2"
                    >
                        <span>Importar</span>
                        <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- LISTADO DE PRODUCTOS -->
        <div v-else-if="activeTab === 'productos'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
             <div 
                v-for="item in filteredItems" :key="item.id"
                class="group relative bg-[#0d121a] border border-white/5 rounded-2xl p-4 hover:border-amber-500/30 transition-all hover:translate-y-[-2px] shadow-lg hover:shadow-amber-900/10"
                :class="{'opacity-40 grayscale': !item.activo}"
            >
                <div class="flex justify-between items-start mb-3">
                    <div class="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-500">
                        <i class="fas fa-box"></i>
                    </div>
                    <div class="flex gap-2">
                         <span v-if="!item.activo" class="text-[9px] bg-red-900/30 text-red-500 px-2 py-0.5 rounded-full border border-red-500/20 font-bold uppercase tracking-tighter">Inactivo</span>
                        <button 
                            @click="inactivate(item)" 
                            class="h-7 w-7 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-gray-500 hover:text-red-500 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all"
                            title="Baja Definitiva"
                        >
                            <i class="fas fa-eye-slash"></i>
                        </button>
                    </div>
                </div>
                <h3 class="font-bold text-gray-100 truncate mb-1" :title="item.nombre">{{ item.nombre }}</h3>
                <p class="text-[10px] font-mono text-gray-500 mb-4">{{ item.sku }}</p>
                
                <div class="flex items-center justify-between pt-4 border-t border-white/5">
                    <span class="text-xs font-bold text-blue-400">{{ formatCurrency(item.precio_especial || 0) }}</span>
                    <button 
                        @click="handleImport(item)"
                        class="text-[10px] font-bold text-amber-500 hover:text-amber-400 uppercase tracking-widest flex items-center gap-2"
                    >
                        <span>Importar</span>
                        <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- Empty State -->
        <div v-if="!loading && filteredItems.length === 0" class="flex flex-col items-center justify-center h-64 opacity-20">
            <i class="fas fa-ghost text-6xl mb-4"></i>
            <p class="text-xl font-bold">No se encontraron registros</p>
        </div>

      </div>

      <!-- Pagination / Footer Info -->
      <footer class="h-10 bg-black/40 border-t border-white/5 px-6 flex items-center justify-between text-[10px] text-gray-500 uppercase tracking-widest font-bold">
          <div>
              Mostrando {{ filteredItems.length }} de {{ allItems.length }} registros en Cantera
          </div>
          <div class="flex gap-4">
              <span class="flex items-center gap-1"><i class="fas fa-circle text-amber-500 animate-pulse"></i> Sincronizado</span>
              <span class="text-amber-500/50">IPL V6 2026</span>
          </div>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import canteraService from '@/services/canteraService';
import { useNotificationStore } from '@/stores/notification';

const notificationStore = useNotificationStore();
const activeTab = ref('clientes');
const searchQuery = ref('');
const loading = ref(false);
const allItems = ref([]);

const fetchData = async () => {
    loading.value = true;
    try {
        const res = activeTab.value === 'clientes' 
            ? await canteraService.getClientes(300) 
            : await canteraService.getProductos(300);
        allItems.value = res.data;
    } catch (e) {
        notificationStore.add('Error al consultar cantera', 'error');
    } finally {
        loading.value = false;
    }
};

const filteredItems = computed(() => {
    if (!searchQuery.value) return allItems.value;
    const q = searchQuery.value.toLowerCase();
    if (activeTab.value === 'clientes') {
        return allItems.value.filter(i => 
            i.razon_social?.toLowerCase().includes(q) || 
            i.cuit?.includes(q)
        );
    } else {
        return allItems.value.filter(i => 
            i.nombre?.toLowerCase().includes(q) || 
            i.sku?.toLowerCase().includes(q)
        );
    }
});

const handleImport = async (item) => {
    try {
        notificationStore.add('Importando...', 'info');
        if (activeTab.value === 'clientes') {
            await canteraService.importCliente(item.id);
        } else {
            // Reutilizamos el endpoint de importación de productos si existiera en el router general
            // o lo implementamos en canteraService si no está.
            await canteraService.importProducto(item.id); 
        }
        notificationStore.add('Importado con éxito', 'success');
    } catch (e) {
        notificationStore.add('Error al importar', 'error');
    }
};

const inactivate = async (item) => {
    const type = activeTab.value === 'clientes' ? 'cliente' : 'producto';
    if (!confirm(`¿Eliminar definitivamente este ${type} de la Cantera? No podrá recuperarse fácilmente.`)) return;
    
    try {
        if (activeTab.value === 'clientes') {
            await canteraService.inactivateCliente(item.id);
        } else {
            await canteraService.inactivateProducto(item.id);
        }
        item.activo = false; // Optimistic update
        notificationStore.add('Registro inactivado en maestros', 'success');
        fetchData(); // Refresh list
    } catch (e) {
        notificationStore.add('Error al dar de baja', 'error');
    }
};

const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(val);
};

onMounted(fetchData);
watch(activeTab, fetchData);

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(251, 191, 36, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(251, 191, 36, 0.2);
}
</style>
