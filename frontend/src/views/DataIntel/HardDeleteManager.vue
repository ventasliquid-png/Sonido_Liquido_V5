<template>
  <div class="h-full flex flex-col bg-[#0f172a] text-white">
    <!-- Header -->
    <header class="p-4 border-b border-gray-800 bg-[#1e293b] flex justify-between items-center shadow-md z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-red-500">
          <i class="fa-solid fa-dumpster-fire mr-2"></i>Gestión de Bajas Físicas
        </h1>
        <div class="flex bg-gray-900 rounded-lg p-1 gap-1">
          <button 
            @click="loadData('clientes')"
            :class="['px-4 py-1 rounded-md text-sm transition-colors', currentType === 'clientes' ? 'bg-cyan-900/50 text-cyan-200 border border-cyan-500/30' : 'text-gray-400 hover:text-gray-200']"
            :disabled="loading"
          >
            Clientes Inactivos
          </button>
          <button 
             @click="loadData('productos')"
             :class="['px-4 py-1 rounded-md text-sm transition-colors', currentType === 'productos' ? 'bg-rose-900/50 text-rose-200 border border-rose-500/30' : 'text-gray-400 hover:text-gray-200']"
             :disabled="loading"
          >
            Productos Inactivos
          </button>
        </div>
      </div>
      
      <div class="flex items-center gap-3">
         <button @click="reloadData" class="text-gray-400 hover:text-white" title="Recargar">
             <i class="fas fa-sync" :class="{'fa-spin': loading}"></i>
         </button>
      </div>
    </header>

    <!-- Content -->
    <main class="flex-1 overflow-auto p-6 relative">
      
      <!-- LOADING OVERLAY -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black/50 z-20">
         <div class="text-cyan-400 text-lg flex flex-col items-center gap-2">
            <i class="fa-solid fa-circle-notch fa-spin text-4xl"></i>
            Analizando integridad referencial...
         </div>
      </div>

      <!-- MAIN TABLE -->
      <div>
          <div v-if="items.length === 0 && !loading" class="flex flex-col items-center justify-center h-64 text-gray-500">
             <i class="fas fa-check-circle text-4xl mb-4 text-emerald-500/50"></i>
             <p>No hay {{ currentType }} inactivos.</p>
          </div>

          <div v-else class="grid gap-2">
             <div v-for="item in items" :key="item.id" 
                  class="bg-[#1e293b]/50 border border-white/5 rounded-lg p-4 flex items-center justify-between hover:bg-[#1e293b] transition-colors group">
                 
                 <!-- INFO -->
                 <div class="flex items-center gap-4">
                     <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-xs"
                          :class="item.integrity?.safe ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'">
                         <i :class="item.integrity?.safe ? 'fas fa-check' : 'fas fa-link'"></i>
                     </div>
                     <div>
                         <h3 class="font-bold text-white text-sm">
                             {{ currentType === 'clientes' ? item.razon_social : item.nombre }}
                         </h3>
                         <p class="text-xs text-gray-500 font-mono">
                             ID: {{ currentType === 'clientes' ? (item.cuit || 'Sin CUIT') : (item.sku || 'Sin SKU') }}
                         </p>
                     </div>
                 </div>

                 <!-- INTEGRITY STATUS -->
                 <div class="flex items-center gap-6">
                     <div class="text-right">
                         <span class="block text-[10px] uppercase font-bold tracking-wider" 
                               :class="item.integrity?.safe ? 'text-emerald-500' : 'text-red-400'">
                             {{ item.integrity?.safe ? 'SEGURO PARA ELIMINAR' : 'BLOQUEADO' }}
                         </span>
                         <span class="text-xs text-gray-400">
                             {{ item.integrity?.message || 'Verificando...' }}
                         </span>
                     </div>

                     <!-- ACTION BUTTON -->
                     <button 
                        @click="confirmHardDelete(item)"
                        :disabled="!item.integrity?.safe"
                        class="w-10 h-10 rounded-lg flex items-center justify-center transition-all border"
                        :class="[
                            item.integrity?.safe 
                                ? 'bg-red-500/10 border-red-500/30 text-red-500 hover:bg-red-500 hover:text-white cursor-pointer' 
                                : 'bg-gray-800 border-gray-700 text-gray-600 cursor-not-allowed opacity-50'
                        ]"
                        :title="item.integrity?.safe ? 'ELIMINAR DEFINITIVAMENTE' : 'Bloqueado por dependencias'"
                     >
                         <i class="fas fa-trash-alt"></i>
                     </button>
                 </div>
             </div>
          </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';
import { useClientesStore } from '../../stores/clientes';
import { useProductosStore } from '../../stores/productos';

const clientesStore = useClientesStore();
const productosStore = useProductosStore();

// --- DATA STATE ---
const currentType = ref('clientes');
const items = ref([]);
const loading = ref(false);

const reloadData = () => loadData(currentType.value);

const loadData = async (type) => {
    currentType.value = type;
    loading.value = true;
    items.value = [];
    
    try {
        let endpoint = type === 'clientes' ? '/clientes/' : '/productos/';
        
        // Fetch Inactive Items
        const res = await api.get(endpoint, { params: { include_inactive: true, limit: 1000 } });
        
        // Filter ONLY inactive items (Baja Lógica)
        const inactives = res.data.filter(i => i.activo === false);
        
        // Check Integrity for each
        const checkedItems = await Promise.all(inactives.map(async (item) => {
             try {
                const id = item.id; 
                const checkRes = await api.get(`${endpoint}${id}/integrity_check`);
                return { ...item, integrity: checkRes.data };
             } catch (e) {
                 return { ...item, integrity: { safe: false, message: 'Error verificando integridad' } };
             }
        }));
        
        items.value = checkedItems;

    } catch (e) {
        console.error("Error loading data:", e);
    } finally {
        loading.value = false;
    }
};

const confirmHardDelete = async (item) => {
    if (!confirm(`⚠️ PELIGRO ⚠️\n\n¿Confirma la ELIMINACIÓN FÍSICA de:\n${currentType.value === 'clientes' ? item.razon_social : item.nombre}?\n\nEsta acción NO se puede deshacer.`)) return;
    
    try {
        loading.value = true;
        
        if (currentType.value === 'clientes') {
            // Use Store Action to ensure Global State Update
            await clientesStore.hardDeleteCliente(item.id);
        } else {
            // Manual API call for products if store action missing, or add to store.
            // Let's assume store might not have it yet, so use mixed approach if needed.
            // But productsStore usually has delete. Let's check or safe-fail to API.
            // For now, let's use API for products if we are not sure, but for clients we use Store.
            // Actually, let's use API + Store Refresh for products to be safe if `hardDelete` isn't in store.
             await api.delete(`/productos/${item.id}/hard`);
             // Force refresh products store to remove from list
             productosStore.fetchProductos();
        }
        
        // Remove from local list
        items.value = items.value.filter(i => i.id !== item.id);
        
    } catch (e) {
        console.error(e);
        alert("Error al eliminar: " + (e.response?.data?.detail || e.message));
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    loadData('clientes');
});
</script>
