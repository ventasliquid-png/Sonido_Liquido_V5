<template>
  <div class="flex h-full w-full bg-[#081c26] text-gray-200 font-sans overflow-hidden">
    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-w-0">
      <!-- Header -->
      <header class="h-16 flex items-center justify-between px-6 border-b border-cyan-900/20 bg-[#0a1f2e]/50 backdrop-blur-sm shrink-0">
        <div class="flex items-center gap-4">
          <h1 class="font-outfit text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            Address Hub Soberano (V5.2 GOLD)
          </h1>
        </div>
        <div class="flex gap-3">
          <button 
            @click="openNewAddress"
            class="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-sm shadow-lg shadow-cyan-900/20 transition-all transform active:scale-[0.98]"
          >
            <i class="fas fa-plus text-xs"></i>
            <span>NUEVO DOMICILIO</span>
          </button>
        </div>
      </header>

      <!-- Search Bar -->
      <div class="p-6 pb-2">
        <div class="relative w-full max-w-2xl">
          <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-cyan-500/50"></i>
          <input 
            v-model="searchQuery" 
            @input="handleSearch"
            type="text" 
            placeholder="Buscar por calle, alias o localidad..." 
            class="w-full bg-[#05151f] border border-cyan-900/30 rounded-xl py-3 pl-11 pr-12 text-white placeholder-gray-500 outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-all font-medium"
          >
        </div>
      </div>

      <!-- List Header -->
      <div class="px-6 py-2 grid grid-cols-12 gap-4 text-[10px] uppercase font-bold text-cyan-500/70 tracking-wider">
        <div class="col-span-3">Calle / Domicilio</div>
        <div class="col-span-3">Alias / Referencia</div>
        <div class="col-span-2">Localidad</div>
        <div class="col-span-2 text-center">Uso (N:M)</div>
        <div class="col-span-2 text-right">Acciones</div>
      </div>

      <!-- List Content -->
      <div class="flex-1 overflow-y-auto px-6 pb-6 scrollbar-thin scrollbar-thumb-cyan-900/20">
        <div v-if="loading" class="flex flex-col items-center justify-center h-48 opacity-50">
           <i class="fas fa-circle-notch fa-spin text-3xl mb-2 text-cyan-600"></i>
           <p class="text-sm">Cargando Address Hub...</p>
        </div>

        <div v-else-if="addresses.length === 0" class="flex flex-col items-center justify-center h-48 opacity-50">
          <i class="fas fa-search text-3xl mb-2 text-cyan-900"></i>
          <p class="text-sm">No se encontraron domicilios</p>
        </div>

        <div v-else class="space-y-1">
          <div 
            v-for="addr in addresses" 
            :key="addr.id"
            @click="editAddress(addr)"
            class="grid grid-cols-12 gap-4 items-center p-4 rounded-xl border border-transparent hover:border-cyan-500/20 hover:bg-cyan-900/10 cursor-pointer transition-all group"
          >
            <div class="col-span-3 font-bold text-white group-hover:text-cyan-300 transition-colors">
              {{ addr.calle }} {{ addr.numero }}
              <div v-if="addr.piso || addr.depto" class="text-[10px] text-cyan-500">
                Piso {{ addr.piso }} Depto {{ addr.depto }}
              </div>
            </div>
            <div class="col-span-3 text-sm text-gray-400 truncate">
              {{ addr.alias || '-' }}
            </div>
            <div class="col-span-2 text-sm text-gray-400">
              {{ addr.localidad || '-' }}
            </div>
            <div class="col-span-2 flex justify-center">
              <span 
                class="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide bg-cyan-900/30 text-cyan-400 border border-cyan-500/30"
                :title="`Usado por ${addr.usage_count || 0} entidades`"
              >
                {{ addr.usage_count || 0 }} VÍNCULOS
              </span>
            </div>
            <div class="col-span-2 flex justify-end gap-2 pr-2">
               <button @click.stop="editAddress(addr)" class="p-2 hover:bg-cyan-500/20 rounded-lg text-cyan-500 transition-colors">
                  <i class="fas fa-pencil-alt"></i>
               </button>
               <button @click.stop="confirmDelete(addr)" class="p-2 hover:bg-red-500/20 rounded-lg text-red-500 transition-colors">
                  <i class="fas fa-trash-alt"></i>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';
import AddressDialog from '../../components/dialogs/AddressDialog.vue';

const addresses = ref([]);
const searchQuery = ref('');
const loading = ref(true);
const showDialog = ref(false);
const selectedAddress = ref(null);

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
            // Update
            await api.put(`/clientes/hub/${selectedAddress.value.id}`, formData);
        } else {
            // Create
            await api.post('/clientes/hub', formData);
        }
        showDialog.value = false;
        fetchAddresses();
    } catch (err) {
        console.error("Save error:", err);
        alert(err.response?.data?.detail || "Error al guardar el domicilio");
    }
};

const confirmDelete = async (addr) => {
    const msg = addr.usage_count > 0 
        ? `ATENCIÓN: Este domicilio tiene ${addr.usage_count} vínculos activos. NO se recomienda borrarlo si está en uso. ¿Desea intentar la eliminación física?`
        : `¿Realmente desea eliminar permanentemente el domicilio en ${addr.calle}?`;
        
    if (confirm(msg)) {
        try {
            await api.delete(`/clientes/hub/${addr.id}`);
            fetchAddresses();
        } catch (err) {
            console.error("Delete error:", err);
            alert(err.response?.data?.detail || "Error al eliminar el domicilio");
        }
    }
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
</style>
