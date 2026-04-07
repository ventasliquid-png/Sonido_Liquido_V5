// [IDENTIDAD] - frontend\src\views\Maestros\AddressHubView.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

<template>
  <div class="flex h-full w-full bg-[#081c26] text-gray-200 font-sans overflow-hidden">
    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-w-0">
      <!-- Header -->
      <header class="h-16 flex items-center justify-between px-6 border-b border-cyan-900/20 bg-[#0a1f2e]/50 backdrop-blur-sm shrink-0">
        <div class="flex items-center gap-6">
          <h1 class="font-outfit text-xl font-bold bg-gradient-to-r from-white to-cyan-400 bg-clip-text text-transparent">
            Address Hub Soberano (V5.2.3.1 GOLD)
          </h1>
          <!-- Filter Segments -->
          <div class="flex bg-black/40 rounded-xl p-1 border border-white/5">
            <button 
              v-for="f in ['TODOS', 'ACTIVOS', 'INACTIVOS']" 
              :key="f"
              @click="activeFilter = f"
              :class="activeFilter === f ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-900/40' : 'text-white/40 hover:text-white/60'"
              class="px-4 py-1.5 rounded-lg text-[10px] font-black tracking-widest transition-all uppercase"
            >
              {{ f }}
            </button>
          </div>
        </div>
        <div class="flex gap-3">
          <button 
            @click="openNewAddress"
            class="flex items-center gap-2 px-6 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-black text-xs uppercase tracking-wider shadow-lg shadow-cyan-900/40 transition-all transform active:scale-95"
          >
            <i class="fas fa-plus"></i>
            <span>Nuevo Domicilio</span>
          </button>
        </div>
      </header>

      <!-- Search Bar -->
      <div class="p-6 pb-2">
        <div class="relative w-full max-w-2xl group">
          <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-cyan-500/30 group-focus-within:text-cyan-400 transition-colors"></i>
          <input 
            v-model="searchQuery" 
            @input="handleSearch"
            type="text" 
            placeholder="Buscar por calle, alias o localidad..." 
            class="w-full bg-black/20 border border-white/5 rounded-2xl py-3 pl-11 pr-12 text-white placeholder-cyan-500/20 outline-none focus:border-cyan-500/50 focus:bg-black/40 transition-all font-medium shadow-inner"
          >
        </div>
      </div>

      <!-- List Header -->
      <div class="px-8 py-3 grid grid-cols-12 gap-4 text-[10px] uppercase font-black text-cyan-500/50 tracking-[0.2em] border-b border-white/5">
        <div @click="toggleSort('calle')" class="col-span-3 cursor-pointer hover:text-cyan-400 transition-colors flex items-center gap-2">
          Calle / Domicilio
          <i v-if="sortBy === 'calle'" class="fas" :class="sortOrder === 'asc' ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
        </div>
        <div @click="toggleSort('localidad')" class="col-span-2 cursor-pointer hover:text-cyan-400 transition-colors flex items-center gap-2 text-center justify-center">
          Localidad
          <i v-if="sortBy === 'localidad'" class="fas" :class="sortOrder === 'asc' ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
        </div>
        <div @click="toggleSort('provincia_nombre')" class="col-span-2 cursor-pointer hover:text-cyan-400 transition-colors flex items-center gap-2 text-center justify-center">
          Provincia
          <i v-if="sortBy === 'provincia_nombre'" class="fas" :class="sortOrder === 'asc' ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
        </div>
        <div class="col-span-1 text-center">Maps</div>
        <div @click="toggleSort('usage_count')" class="col-span-2 cursor-pointer hover:text-cyan-400 transition-colors flex items-center gap-2 justify-center">
          Vínculos (N:M)
          <i v-if="sortBy === 'usage_count'" class="fas" :class="sortOrder === 'asc' ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
        </div>
        <div class="col-span-2 text-right">Acciones</div>
      </div>

      <!-- List Content -->
      <div class="flex-1 overflow-y-auto px-6 pb-6 scrollbar-thin scrollbar-thumb-cyan-900/20">
        <div v-if="loading" class="flex flex-col items-center justify-center h-48 opacity-50">
           <i class="fas fa-circle-notch fa-spin text-3xl mb-2 text-cyan-600"></i>
           <p class="text-sm font-bold uppercase tracking-widest text-cyan-500/50">Sincronizando Hub...</p>
        </div>

        <div v-else-if="sortedAddresses.length === 0" class="flex flex-col items-center justify-center h-48 opacity-50">
          <i class="fas fa-search text-3xl mb-2 text-cyan-900"></i>
          <p class="text-sm">No se encontraron domicilios</p>
        </div>

        <div v-else class="space-y-2 mt-2">
          <div 
            v-for="(addr, index) in sortedAddresses" 
            :key="addr.id"
            @click="editAddress(addr)"
            class="grid grid-cols-12 gap-4 items-center px-6 py-4 rounded-2xl border border-white/5 bg-[#0a1f2e]/40 hover:bg-cyan-500/5 hover:border-cyan-500/30 cursor-pointer transition-all group relative"
          >
            <!-- Background Glow on Hover -->
            <div class="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/0 to-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>

            <!-- Calle & Alias -->
            <div class="col-span-3 min-w-0">
              <div class="font-outfit font-bold text-white group-hover:text-cyan-300 transition-colors truncate">
                {{ addr.calle }} {{ addr.numero }}
              </div>
              <div class="text-[10px] uppercase font-bold tracking-wider" :class="addr.alias ? 'text-cyan-500/70' : 'text-white/20'">
                {{ addr.alias || 'Sín Alias' }}
                <span v-if="addr.piso || addr.depto" class="ml-2 text-white/40">
                  | P:{{ addr.piso || '-' }} D:{{ addr.depto || '-' }}
                </span>
              </div>
            </div>

            <!-- Localidad -->
            <div class="col-span-2 text-center text-sm font-medium text-gray-400 truncate">
              {{ addr.localidad || '-' }}
            </div>

            <!-- Provincia -->
            <div class="col-span-2 text-center text-sm font-medium text-gray-400 truncate uppercase tracking-tighter">
              {{ addr.provincia_nombre || '-' }}
            </div>

            <!-- Maps -->
            <div class="col-span-1 flex justify-center">
              <button 
                @click.stop="openMaps(addr)"
                class="h-10 w-10 rounded-xl flex items-center justify-center transition-all border border-transparent active:scale-90"
                :class="addr.is_maps_manual ? 'bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 border-cyan-500/30' : 'bg-emerald-500/10 text-emerald-500/60 hover:bg-emerald-500/20 border-emerald-500/20'"
                :title="addr.is_maps_manual ? 'Link Verificado (Manual)' : 'Link Autogenerado (Estimado)'"
              >
                <i class="fas fa-map-marker-alt"></i>
              </button>
            </div>

            <!-- Vínculos (N:M) with Popover -->
            <div class="col-span-2 flex items-center justify-center relative">
               <button 
                 @mouseenter="showPopover(addr, $event)"
                 @mouseleave="hidePopover"
                 @click.stop="openVinculosManager(addr)" 
                 class="px-4 py-1.5 rounded-full bg-cyan-600/10 border border-cyan-500/20 text-cyan-400 text-[10px] font-black uppercase tracking-widest hover:bg-cyan-600 hover:text-white transition-all transform active:scale-95 flex items-center gap-2"
               >
                 <span>{{ addr.usage_count }}</span>
                 <span>Vínculos</span>
               </button>

               <!-- Intelligence Popover (Dynamic Positioning) -->
               <div 
                 v-if="hoveredAddrId === addr.id"
                 class="absolute left-1/2 -translate-x-1/2 w-64 bg-slate-900 border border-white/10 rounded-2xl shadow-2xl z-[100] p-4 backdrop-blur-xl animate-in fade-in duration-200"
                 :class="index === 0 ? 'top-full mt-2 slide-in-from-top-2' : 'bottom-full mb-2 slide-in-from-bottom-2'"
               >
                 <label class="text-[9px] font-black uppercase text-cyan-500/50 block mb-2 tracking-widest">Entidades Vinculadas</label>
                 <div class="space-y-2">
                    <div v-for="v in addr.vinculos_detalles" :key="v.id" class="flex items-center justify-between text-[10px]">
                       <span class="text-white font-bold truncate pr-2">{{ v.nombre }}</span>
                       <div class="flex items-center gap-1 shrink-0">
                          <span class="px-1 py-0.5 rounded bg-white/5 text-white/40 border border-white/5">{{ v.rol_display || 'V' }}</span>
                          <i v-if="v.mirror_active" class="fas fa-link text-amber-500 text-[8px]" title="Sincronizado (Mirror)"></i>
                       </div>
                    </div>
                    <div v-if="!addr.vinculos_detalles?.length" class="text-white/20 text-[10px] italic">Sin vínculos activos</div>
                 </div>
               </div>
            </div>

            <!-- Acciones (Switch de Vida) -->
            <div class="col-span-2 flex justify-end items-center gap-4">
               <div class="flex items-center gap-3 pr-2">
                 <span class="text-[9px] font-black uppercase tracking-tighter" :class="(addr.bit_identidad & 1) ? 'text-emerald-500' : 'text-red-500'">
                   {{ (addr.bit_identidad & 1) ? 'Activo' : 'Inactivo' }}
                 </span>
                 <button 
                   @click.stop="toggleActivation(addr)"
                   class="w-10 h-5 rounded-full relative transition-all duration-300 overflow-hidden border border-white/10"
                   :class="(addr.bit_identidad & 1) ? 'bg-emerald-600/40' : 'bg-red-900/40'"
                 >
                   <div 
                     class="absolute top-0.5 w-4 h-4 bg-white rounded-full transition-all duration-300 shadow-lg"
                     :class="(addr.bit_identidad & 1) ? 'left-[22px]' : 'left-0.5'"
                   ></div>
                 </button>
               </div>
               
               <button @click.stop="editAddress(addr)" class="h-9 w-9 flex items-center justify-center hover:bg-cyan-500/20 rounded-xl text-cyan-500 transition-colors opacity-40 group-hover:opacity-100">
                  <i class="fas fa-pencil-alt text-xs"></i>
               </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Address Dialog -->
    <AddressDialog 
      :show="showDialog"
      :isEdit="!!selectedAddress"
      :initialData="selectedAddress"
      :usageCount="selectedAddress?.usage_count || 0"
      @close="closeDialog"
      @save="handleSave"
    />

    <!-- Vinculos Manager Dialog -->
    <VinculosManagerDialog
      :show="showVinculosManager"
      :address="selectedAddress"
      @close="showVinculosManager = false"
      @refresh="fetchAddresses"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../services/api';
import AddressDialog from '../../components/dialogs/AddressDialog.vue';

import VinculosManagerDialog from '../../components/dialogs/VinculosManagerDialog.vue';

const addresses = ref([]);
const searchQuery = ref('');
const loading = ref(true);
const showDialog = ref(false);
const showVinculosManager = ref(false);
const isEdit = ref(false);
const selectedAddress = ref(null);

// Sorting
const sortBy = ref('calle');
const sortOrder = ref('asc');
const activeFilter = ref('ACTIVOS');
const hoveredAddrId = ref(null);

const fetchAddresses = async () => {
  loading.value = true;
  try {
    const res = await api.get('/clientes/hub/list');
    addresses.value = res.data;
  } catch (err) {
    console.error("Error fetching Address Hub:", err);
  } finally {
    loading.value = false;
  }
};

const handleSearch = async () => {
    if (!searchQuery.value) {
        return fetchAddresses();
    }
    try {
        const res = await api.get(`/clientes/hub/search?q=${searchQuery.value}`);
        addresses.value = res.data;
    } catch (err) {
        console.error("Search error:", err);
    }
};

const sortedAddresses = computed(() => {
  let filtered = [...addresses.value];
  
  if (activeFilter.value === 'ACTIVOS') {
    filtered = filtered.filter(a => (a.bit_identidad & 1));
  } else if (activeFilter.value === 'INACTIVOS') {
    filtered = filtered.filter(a => !(a.bit_identidad & 1));
  }

  return filtered.sort((a, b) => {
    let valA = a[sortBy.value];
    let valB = b[sortBy.value];
    
    // Handle falsy
    if (valA === null || valA === undefined) valA = '';
    if (valB === null || valB === undefined) valB = '';
    
    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();
    
    if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1;
    if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1;
    return 0;
  });
});

const toggleSort = (col) => {
  if (sortBy.value === col) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortBy.value = col;
    sortOrder.value = 'asc';
  }
};

const openNewAddress = () => {
    selectedAddress.value = null;
    showDialog.value = true;
};

const editAddress = (addr) => {
    selectedAddress.value = { ...addr };
    showDialog.value = true;
};

const closeDialog = () => {
    showDialog.value = false;
    selectedAddress.value = null;
};

const handleSave = async (formData) => {
    try {
        if (selectedAddress.value) {
            await api.put(`/clientes/hub/${selectedAddress.value.id}`, formData);
        } else {
            await api.post('/clientes/hub', formData);
        }
        showDialog.value = false;
        fetchAddresses();
    } catch (err) {
        console.error("Save error:", err);
        alert(err.response?.data?.detail || "Error al guardar el domicilio");
    }
};

const toggleActivation = async (addr) => {
    const isCurrentlyActive = (addr.bit_identidad & 1);
    const hasHistory = (addr.bit_identidad & 2);
    
    let msg = isCurrentlyActive 
        ? `¿Desea desactivar el domicilio en ${addr.calle}?`
        : `¿Desea reactivar el domicilio en ${addr.calle}?`;
        
    if (isCurrentlyActive && hasHistory) {
      msg = `ATENCIÓN: Este domicilio tiene historial logístico. Se ocultará pero no se eliminará físicamente. ¿Continuar?`;
    }
        
    if (confirm(msg)) {
        try {
            const newBits = isCurrentlyActive ? (addr.bit_identidad & ~1) : (addr.bit_identidad | 1);
            await api.put(`/clientes/hub/${addr.id}`, { bit_identidad: newBits });
            fetchAddresses();
        } catch (err) {
            console.error("Toggle error:", err);
            alert("Error al cambiar estado del domicilio");
        }
    }
};

const openMaps = (addr) => {
  if (addr.maps_link) {
    window.open(addr.maps_link, '_blank');
  }
};

const openVinculosManager = (addr) => {
    selectedAddress.value = addr;
    showVinculosManager.value = true;
};

const showPopover = (addr) => {
    hoveredAddrId.value = addr.id;
};

const hidePopover = () => {
    hoveredAddrId.value = null;
};

onMounted(fetchAddresses);
</script>

<style scoped>
.font-outfit {
  font-family: 'Outfit', sans-serif;
}

/* Animations */
.list-enter-active, .list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from, .list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.animate-popover-in {
  animation: popover-in 0.2s cubic-bezier(0, 0, 0.2, 1);
}

@keyframes popover-in {
  from { opacity: 0; transform: translate(-50%, 10px) scale(0.95); }
  to { opacity: 1; transform: translate(-50%, 0) scale(1); }
}
</style>
