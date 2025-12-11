<template>
  <div class="h-full flex flex-col bg-[#0f172a] text-white">
    <!-- Header -->
    <header class="p-4 border-b border-gray-800 bg-[#1e293b] flex justify-between items-center shadow-md z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-cyan-400">
          <i class="fa-solid fa-broom mr-2"></i>Limpieza de Datos
        </h1>
        <div class="flex bg-gray-900 rounded-lg p-1 gap-1">
          <button 
            @click="loadData('clientes')"
            :class="['px-4 py-1 rounded-md text-sm transition-colors', currentType === 'clientes' ? 'bg-cyan-600 text-white shadow' : 'text-gray-400 hover:text-gray-200']"
          >
            Clientes
          </button>
          <button 
             @click="loadData('productos')"
             :class="['px-4 py-1 rounded-md text-sm transition-colors', currentType === 'productos' ? 'bg-rose-600 text-white shadow' : 'text-gray-400 hover:text-gray-200']"
          >
            Productos
          </button>
        </div>
      </div>
      
      <div class="flex items-center gap-3">
        <div v-if="hasUnsavedChanges" class="text-yellow-400 text-sm animate-pulse">
          <i class="fa-solid fa-circle-exclamation mr-1"></i>Cambios sin guardar
        </div>
        
        <button 
          @click="saveProgress" 
          class="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded shadow flex items-center gap-2 transition-transform active:scale-95 text-xs uppercase font-bold"
          :disabled="isSaving || loading"
        >
          <i v-if="isSaving" class="fa-solid fa-circle-notch fa-spin"></i>
          <i v-else class="fa-solid fa-floppy-disk"></i>
          Guardar
        </button>

        <button 
          @click="commitData" 
          class="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white px-4 py-2 rounded shadow flex items-center gap-2 transition-transform active:scale-95 font-bold shadow-cyan-500/20"
          :disabled="isSaving || loading || hasUnsavedChanges"
          title="Mueve los registros 'IMPORTAR' a la base de datos real"
        >
            <i class="fa-solid fa-file-import"></i>
            IMPORTAR A SISTEMA
        </button>
      </div>
    </header>

    <!-- Content (Grid) -->
    <main class="flex-1 overflow-auto p-4 relative">
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black/50 z-20">
         <div class="text-cyan-400 text-lg flex flex-col items-center gap-2">
            <i class="fa-solid fa-circle-notch fa-spin text-4xl"></i>
            Cargando datos...
         </div>
      </div>

      <table class="w-full text-left text-sm border-collapse">
        <thead class="sticky top-0 bg-[#1e293b] text-gray-400 uppercase text-xs z-10 shadow-sm">
          <tr>
            <th class="p-3 border-b border-gray-700 w-16">#</th>
            <th class="p-3 border-b border-gray-700 w-1/4 cursor-pointer hover:text-white" @click="sortMode = 'nombre'; toggleSort()">
                Nombre Original <i v-if="sortMode === 'nombre'" :class="['fa-solid', sortDesc ? 'fa-sort-alpha-up-alt' : 'fa-sort-alpha-down']"></i>
            </th>
            <th class="p-3 border-b border-gray-700 w-24 text-center cursor-pointer hover:text-white" @click="sortMode = 'frecuencia'; toggleSort()">
                Freq <i v-if="sortMode === 'frecuencia'" :class="['fa-solid', sortDesc ? 'fa-sort-down' : 'fa-sort-up']"></i>
            </th>
            <th class="p-3 border-b border-gray-700">Nombre Corregido</th>
            <th v-if="currentType === 'clientes'" class="p-3 border-b border-gray-700 w-32">CUIT</th>
            <th class="p-3 border-b border-gray-700 w-48">Alias (Código)</th>
            <th class="p-3 border-b border-gray-700 w-32 text-center">Acción</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800">
          <tr 
            v-for="(item, index) in sortedItems" 
            :key="item._id"
            :class="['hover:bg-[#1e293b] transition-colors group', getRowClass(item)]"
          >
            <td class="p-3 text-gray-500 font-mono">{{ index + 1 }}</td>
            <td class="p-3 font-medium text-gray-300 select-all">{{ item.nombre_original }}</td>
            <td class="p-3 text-center text-gray-400 font-mono">{{ item.frecuencia }}</td>
            
            <!-- Input Nombre -->
            <td class="p-2">
              <input 
                v-model="item.nombre_final"
                @input="markChanged"
                :class="['w-full bg-[#0a0a0a] border border-gray-700 rounded px-3 py-1.5 focus:border-cyan-500 focus:outline-none transition-colors text-white', item.estado === 'IGNORAR' ? 'opacity-50 line-through' : '']"
                :disabled="item.estado === 'IGNORAR'"
              />
            </td>

            <!-- Input CUIT -->
            <td v-if="currentType === 'clientes'" class="p-2 relative">
              <input 
                v-model="item.cuit"
                @input="handleCuitInput(item)"
                placeholder="Sin CUIT"
                :class="['w-full bg-[#0a0a0a] border rounded px-2 py-1.5 focus:outline-none text-xs font-mono transition-colors', 
                    !isCuitValid(item.cuit) ? 'border-red-500 text-red-500' : 'border-gray-700 text-blue-200 focus:border-cyan-500'
                ]"
                :disabled="item.estado === 'IGNORAR'"
                maxlength="11"
              />
              <div v-if="item.cuit && !isCuitValid(item.cuit)" class="absolute right-3 top-3 text-red-500 text-[10px]" title="CUIT Inválido">
                  <i class="fa-solid fa-triangle-exclamation"></i>
              </div>
            </td>
            
            <!-- Input Alias -->
            <td class="p-2">
              <input 
                v-model="item.alias"
                @input="markChanged"
                placeholder="Ej: LABME"
                class="w-full bg-[#0a0a0a] border border-gray-700 rounded px-2 py-1.5 focus:border-cyan-500 focus:outline-none text-xs text-yellow-200 uppercase"
                :disabled="item.estado === 'IGNORAR'"
              />
            </td>
            
            <!-- Acciones -->
            <td class="p-2 text-center">
                <div class="flex justify-center gap-1">
                    <button 
                        @click="setItemStatus(item, 'IMPORTAR')"
                        :class="['w-8 h-8 rounded flex items-center justify-center transition-colors', item.estado === 'PENDIENTE' ? 'bg-gray-700 hover:bg-gray-600 text-gray-400' : (item.estado === 'IMPORTAR' ? 'bg-green-600 text-white' : 'bg-transparent text-gray-600')]"
                        title="Importar"
                    >
                        <i class="fa-solid fa-check"></i>
                    </button>
                    <button 
                        @click="setItemStatus(item, 'IGNORAR')"
                        :class="['w-8 h-8 rounded flex items-center justify-center transition-colors', item.estado === 'IGNORAR' ? 'bg-red-900/50 text-red-500 border border-red-800' : 'bg-gray-700 hover:bg-gray-600 text-gray-400']"
                        title="Ignorar / Borrar"
                    >
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Empty State -->
      <div v-if="!loading && items.length === 0" class="flex flex-col items-center justify-center h-64 text-gray-500">
        <i class="fa-solid fa-inbox text-4xl mb-4"></i>
        <p>No hay datos cargados para {{ currentType }}.</p>
        <p class="text-sm mt-2">Corra el "Harvester" primero.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const currentType = ref('clientes'); // clientes | productos
const items = ref([]);
const loading = ref(false);
const isSaving = ref(false);
const hasUnsavedChanges = ref(false);
const sortDesc = ref(true);

const API_URL = 'http://localhost:8000'; // Ajustar dinamicamente si es necesario

const sortMode = ref('frecuencia'); // frecuencia | nombre



const sortedItems = computed(() => {
    // Return a new array reference to avoid mutating source
    return [...items.value].sort((a, b) => {
        if (sortMode.value === 'nombre') {
             // Sort by ORIGINAL name to prevent jumping while typing
             const nameA = (a.nombre_original || '').toLowerCase();
             const nameB = (b.nombre_original || '').toLowerCase();
             return sortDesc.value ? nameB.localeCompare(nameA) : nameA.localeCompare(nameB);
        } else {
             // Frecuencia
             if (sortDesc.value) return b.frecuencia - a.frecuencia;
             return a.frecuencia - b.frecuencia;
        }
    });
});

const loadData = async (type) => {
    if (hasUnsavedChanges.value) {
        if(!confirm("Tiene cambios sin guardar. ¿Desea descartarlos?")) return;
    }
    
    currentType.value = type;
    if (type === 'productos') sortMode.value = 'nombre';
    else sortMode.value = 'frecuencia';
    
    loading.value = true;
    try {
        const response = await axios.get(`${API_URL}/data_intel/candidates/${type}`);
        // Add random ID for stable v-for key
        items.value = response.data.items.map(i => ({
            ...i,
            _id: Math.random().toString(36).substr(2, 9),
            nombre_final: i.nombre_final || i.nombre_original,
            alias: i.alias || '',
            cuit: i.cuit || '',
            estado: i.estado || 'PENDIENTE'
        }));
        hasUnsavedChanges.value = false;
    } catch (error) {
        alert("Error cargando datos: " + error.message);
    } finally {
        loading.value = false;
    }
};

const saveProgress = async () => {
    isSaving.value = true;
    try {
        // Strip internal fields like _id before sending
        // AND enforce string types for optional fields to avoid validation errors
        const payloadItems = items.value.map(({ _id, ...rest }) => ({
            ...rest,
            alias: String(rest.alias || ''),
            cuit: String(rest.cuit || ''),
            nombre_final: String(rest.nombre_final || rest.nombre_original)
        }));
        console.log("Saving items:", payloadItems);
        
        await axios.post(`${API_URL}/data_intel/candidates/${currentType.value}`, {
            items: payloadItems
        });
        hasUnsavedChanges.value = false;
        // alert("Progreso guardado correctamente."); 
    } catch (error) {
        console.error("Save Error:", error);
        let errorDetail = error.response?.data?.detail || error.message;
        if (typeof errorDetail === 'object') {
            errorDetail = JSON.stringify(errorDetail, null, 2);
        }
        alert("Error guardando (" + currentType.value + "):\n" + errorDetail);
    } finally {
        isSaving.value = false;
    }
};

const commitData = async () => {
    if (hasUnsavedChanges.value) {
        // Auto-save before commit
        await saveProgress();
        if (hasUnsavedChanges.value) return; // If save failed
    }

    if (!confirm(`¿Está seguro de IMPORTAR los registros seleccionados a la base de datos de PRODUCCIÓN?\n\nEsta acción creará los clientes/productos reales en el sistema.`)) return;
    
    loading.value = true;
    try {
        const response = await axios.post(`${API_URL}/data_intel/commit/${currentType.value}`);
        // Mostrar resultado
        const { imported_count, errors } = response.data;
        let msg = `✅ Proceso Finalizado.\n\nSe importaron ${imported_count} registros exitosamente.`;
        if (errors && errors.length > 0) {
            msg += `\n\n⚠️ Hubo ${errors.length} errores/duplicados:\n` + errors.slice(0, 5).join('\n') + (errors.length > 5 ? '\n...' : '');
        }
        alert(msg);
        
        // Recargar para ver si cambió algo (opcional, por ahora mantenemos estado)
    } catch (error) {
        alert("❌ Error en importación masiva: " + (error.response?.data?.detail || error.message));
    } finally {
        loading.value = false;
    }
};

const setItemStatus = (item, status) => {
    item.estado = status;
    markChanged();
};

const markChanged = () => {
    hasUnsavedChanges.value = true;
};

const getRowClass = (item) => {
    if (item.estado === 'IGNORAR') return 'opacity-40 bg-red-900/10 grayscale line-through decoration-red-500/50 decoration-2';
    if (item.estado === 'IMPORTAR') return 'bg-gray-800/50 text-gray-500 grayscale'; // Grisado
    return '';
};

const cleanCuit = (value) => {
    return value.replace(/[^0-9]/g, '');
};

const validateCuit = (cuit) => {
    if (!cuit || cuit.length !== 11) return false;
    const multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
    let sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cuit[i]) * multipliers[i];
    }
    const mod = sum % 11;
    let digit = 11 - mod;
    if (digit === 11) digit = 0;
    if (digit === 10) digit = 9;
    return parseInt(cuit[10]) === digit;
};

const handleCuitInput = (item) => {
    item.cuit = cleanCuit(item.cuit);
    markChanged();
};

const isCuitValid = (cuit) => {
    if (!cuit) return true; // Empty is valid (pending)
    return validateCuit(cuit);
}

const toggleSort = () => {
    sortDesc.value = !sortDesc.value;
};

// Lifecycle
onMounted(() => {
    loadData('clientes');
});

</script>

<style scoped>
/* Scrollbar custom para que parezca app nativa */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #0f172a; 
}
::-webkit-scrollbar-thumb {
  background: #334155; 
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #475569; 
}
</style>
