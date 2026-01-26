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

      <!-- ACTION TOOLBAR -->
      <div v-if="items.length > 0" class="flex items-center gap-4 mb-4 bg-gray-800/50 p-2 rounded-lg border border-gray-700">
          <div class="flex items-center gap-2 px-2 cursor-pointer" @click="toggleSelectAll">
                <input 
                    type="checkbox" 
                    :checked="isAllSelected"
                    class="rounded bg-[#020a0f] border-cyan-500/50 text-cyan-500 focus:ring-0 focus:ring-offset-0 cursor-pointer h-5 w-5"
                />
                <span class="text-xs font-bold text-gray-400 select-none">Seleccionar Todos</span>
          </div>

          <div class="h-4 w-px bg-gray-700"></div>

          <!-- BULK ACTIONS -->
           <button 
            v-if="selectedIds.length > 0"
            @click="handleBulkRescue"
            class="flex items-center gap-2 rounded-lg bg-emerald-600/20 px-4 py-1.5 text-sm font-bold text-emerald-400 shadow-lg border border-emerald-500/30 hover:bg-emerald-600/40 transition-all"
          >
            <i class="fas fa-life-ring"></i>
            <span>RESCATAR ({{ selectedIds.length }})</span>
          </button>

          <button 
            v-if="selectedIds.length > 0"
            @click="handleBulkHardDelete"
            class="flex items-center gap-2 rounded-lg bg-red-600/20 px-4 py-1.5 text-sm font-bold text-red-500 shadow-lg border border-red-500/30 hover:bg-red-600/40 transition-all ml-auto"
          >
            <i class="fas fa-dumpster-fire"></i>
            <span>ELIMINAR SELECCIONADOS ({{ selectedIds.length }})</span>
          </button>
      </div>

      <!-- MAIN TABLE -->
      <div>
          <div v-if="items.length === 0 && !loading" class="flex flex-col items-center justify-center h-64 text-gray-500">
             <i class="fas fa-check-circle text-4xl mb-4 text-emerald-500/50"></i>
             <p>No hay {{ currentType }} inactivos.</p>
          </div>

          <div v-else class="grid gap-2">
             <div v-for="item in items" :key="item.id" 
                  class="bg-[#1e293b]/50 border border-white/5 rounded-lg p-4 flex items-center justify-between hover:bg-[#1e293b] transition-colors group cursor-pointer"
                  @click="toggleSelection(item.id)">
                 
                 <!-- CHECKBOX + INFO -->
                 <div class="flex items-center gap-4">
                     <div class="p-2" @click.stop="">
                        <input 
                            type="checkbox" 
                            :checked="selectedIds.includes(item.id)" 
                            @change="toggleSelection(item.id)"
                            class="rounded bg-[#020a0f] border-cyan-500/50 text-cyan-500 focus:ring-0 focus:ring-offset-0 cursor-pointer h-5 w-5"
                        />
                     </div>
                     <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-xs shrink-0"
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

                     <!-- ACTION BUTTONS -->
                     <button 
                        @click.stop="rescueItem(item)"
                        class="w-10 h-10 rounded-lg flex items-center justify-center transition-all border bg-emerald-500/10 border-emerald-500/30 text-emerald-500 hover:bg-emerald-500 hover:text-white"
                        title="Rescatar (Volver a Padrón)"
                     >
                         <i class="fas fa-undo"></i>
                     </button>

                     <button 
                        @click.stop="confirmHardDelete(item)"
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
import { ref, onMounted, computed } from 'vue';
import api from '../../services/api';
import { useClientesStore } from '../../stores/clientes';
import { useProductosStore } from '../../stores/productos';
import { useNotificationStore } from '../../stores/notification';

const clientesStore = useClientesStore();
const productosStore = useProductosStore();
const notificationStore = useNotificationStore();

// --- DATA STATE ---
const currentType = ref('clientes');
const items = ref([]);
const loading = ref(false);
const selectedIds = ref([]); // SELECTION STATE

const reloadData = () => loadData(currentType.value);

// --- SELECTION LOGIC ---
const isAllSelected = computed(() => {
    return items.value.length > 0 && selectedIds.value.length === items.value.length;
});

const toggleSelectAll = () => {
    if (isAllSelected.value) {
        selectedIds.value = [];
    } else {
        selectedIds.value = items.value.map(i => i.id);
    }
};

const toggleSelection = (id) => {
    if (selectedIds.value.includes(id)) {
        selectedIds.value = selectedIds.value.filter(i => i !== id);
    } else {
        selectedIds.value.push(id);
    }
};

// --- DATA LOADING ---
const loadData = async (type) => {
    currentType.value = type;
    loading.value = true;
    items.value = [];
    selectedIds.value = []; // Reset selection on type change
    
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

// --- ACTION LOGIC ---

// --- ACTION LOGIC ---

const isClientComplete = (item) => {
    // Logic matches HaweView.vue toggleClienteStatus
    if (currentType.value !== 'clientes') return true; // No strict checks for products yet or handled differently
    
    // Check mandatory fields
    const missing = [];
    if (!item.segmento_id) missing.push("Segmento");
    if (!item.lista_precios_id) missing.push("Lista de Precios");
    if (!item.condicion_iva_id) missing.push("Condición IVA");
    
    return {
        valid: missing.length === 0,
        missing: missing
    };
};

// 1. RESCUE (Reactivar)
const rescueItem = async (item) => {
    try {
        const integrity = isClientComplete(item);
        const targetActiveStatus = integrity.valid;
        
        let confirmMsg = `¿Restaurar "${currentType.value === 'clientes' ? item.razon_social : item.nombre}" al padrón`;
        if (targetActiveStatus) {
            confirmMsg += ' activo?';
        } else {
            confirmMsg += ' como INACTIVO?\n\n(El registro tiene datos incompletos: ' + integrity.missing.join(', ') + '. Se restaurará para que pueda corregirlo, pero permanecerá inactivo).';
        }

        if (!confirm(confirmMsg)) return;
        
        loading.value = true;
        
        // Force status based on integrity
        const payload = { ...item, activo: targetActiveStatus };

        if (currentType.value === 'clientes') {
            await clientesStore.updateCliente(item.id, payload);
        } else {
            // Products
            await productosStore.updateProducto(item.id, payload);
        }
        
        // Remove from list
        items.value = items.value.filter(i => i.id !== item.id);
        selectedIds.value = selectedIds.value.filter(id => id !== item.id);
        
        if (targetActiveStatus) {
            notificationStore.add('Registro rescatado y activado exitosamente', 'success');
        } else {
            notificationStore.add('Registro rescatado como INACTIVO (Faltan datos)', 'warning');
        }
        
    } catch (e) {
        console.error(e);
        alert('Error al rescatar: ' + e.message);
    } finally {
        loading.value = false;
    }
};

const handleBulkRescue = async () => {
    if (!confirm(`¿Restaurar ${selectedIds.value.length} registros seleccionados?`)) return;
    
    loading.value = true;
    let successActive = 0;
    let successInactive = 0;
    
    for (const id of selectedIds.value) {
        try {
            const item = items.value.find(i => i.id === id);
            if (!item) continue;
            
            const integrity = isClientComplete(item);
            const targetActiveStatus = integrity.valid; // If valid -> Active, Else -> Inactive

            if (currentType.value === 'clientes') {
                await clientesStore.updateCliente(id, { ...item, activo: targetActiveStatus });
            } else {
                await productosStore.updateProducto(id, { ...item, activo: targetActiveStatus });
            }
            
            if (targetActiveStatus) successActive++;
            else successInactive++;

        } catch (e) {
            console.error(`Failed to rescue ${id}`, e);
        }
    }
    
    // Refresh list
    await loadData(currentType.value);
    
    if (successInactive > 0) {
        notificationStore.add(`${successActive} activados. ${successInactive} restaurados como INACTIVOS.`, 'warning');
        alert(`Operación completada:\n\n- ${successActive} registros activados correctamente.\n- ${successInactive} registros restaurados como INACTIVOS por falta de datos.\n\nPuede completarlos desde el padrón principal.`);
    } else {
        notificationStore.add(`${successActive} registros rescatados exitosamente`, 'success');
    }
};


// 2. HARD DELETE (Eliminar Definitivamente)
const confirmHardDelete = async (item) => {
    if (!confirm(`⚠️ PELIGRO ⚠️\n\n¿Confirma la ELIMINACIÓN FÍSICA de:\n${currentType.value === 'clientes' ? item.razon_social : item.nombre}?\n\nEsta acción NO se puede deshacer.`)) return;
    
    try {
        loading.value = true;
        await executeHardDelete(item.id);
        
        // Remove from local list
        items.value = items.value.filter(i => i.id !== item.id);
        selectedIds.value = selectedIds.value.filter(id => id !== item.id);
        
    } catch (e) {
        console.error(e);
        alert("Error al eliminar: " + (e.response?.data?.detail || e.message));
    } finally {
        loading.value = false;
    }
};

const handleBulkHardDelete = async () => {
    const safeToDeleteIds = items.value.filter(i => selectedIds.value.includes(i.id) && i.integrity?.safe).map(i => i.id);
    const blockedCount = selectedIds.value.length - safeToDeleteIds.length;
    
    if (safeToDeleteIds.length === 0) {
        alert("Ninguno de los elementos seleccionados es seguro para eliminar (tienen dependencias).");
        return;
    }
    
    let msg = `⚠️ PELIGRO MASIVO ⚠️\n\nSe eliminarán DEFINITIVAMENTE ${safeToDeleteIds.length} registros.\n`;
    if (blockedCount > 0) msg += `(Se omitirán ${blockedCount} registros bloqueados por dependencias)\n`;
    msg += `\n¿ESTÁ COMPLETAMENTE SEGURO?`;
    
    if (!confirm(msg)) return;
    
    loading.value = true;
    let successCount = 0;
    
    for (const id of safeToDeleteIds) {
        try {
            await executeHardDelete(id);
            successCount++;
        } catch (e) {
            console.error(`Failed to delete ${id}`, e);
        }
    }
    
    await loadData(currentType.value);
    notificationStore.add(`${successCount} registros eliminados definitivamente`, 'success');
};

const executeHardDelete = async (id) => {
    if (currentType.value === 'clientes') {
        await clientesStore.hardDeleteCliente(id);
    } else {
        await api.delete(`/productos/${id}/hard`);
        productosStore.fetchProductos();
    }
};

onMounted(() => {
    loadData('clientes');
});
</script>
