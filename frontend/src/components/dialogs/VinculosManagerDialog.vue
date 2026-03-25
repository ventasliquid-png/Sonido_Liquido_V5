<template>
  <div v-if="show" class="fixed inset-0 z-[150] flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl">
    <div class="bg-slate-900 border border-white/10 rounded-3xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[85vh]">
      <!-- Header -->
      <header class="h-20 flex items-center justify-between px-8 border-b border-white/5 bg-white/5 shrink-0">
        <div class="flex items-center gap-4">
          <div class="h-12 w-12 rounded-2xl bg-cyan-600/20 flex items-center justify-center text-cyan-400">
            <i class="fas fa-link text-xl"></i>
          </div>
          <div>
            <h3 class="font-outfit font-bold text-xl text-white">Gestor de Relaciones (N:M)</h3>
            <p class="text-[10px] text-white/40 uppercase font-black tracking-widest">{{ address?.calle }} {{ address?.numero }}</p>
          </div>
        </div>
        <button @click="$emit('close')" class="h-10 w-10 rounded-full hover:bg-white/10 text-white/40 hover:text-white transition-all">
          <i class="fas fa-times"></i>
        </button>
      </header>

      <div class="flex-1 overflow-hidden flex flex-col md:flex-row">
        <!-- Current Links -->
        <div class="flex-1 p-6 border-r border-white/5 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">
           <label class="text-[10px] uppercase font-black text-cyan-500/70 tracking-widest mb-4 block">Entidades Vinculadas</label>
           
           <div v-if="address?.vinculos_detalles?.length === 0" class="flex flex-col items-center justify-center py-12 text-white/20">
              <i class="fas fa-unlink text-4xl mb-3 opacity-20"></i>
              <p class="text-xs font-bold uppercase">Sin vínculos activos</p>
           </div>

           <div v-else class="space-y-3">
             <div v-for="v in address.vinculos_detalles" :key="v.id" class="group flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-white/10 transition-all">
                <div class="flex items-center gap-4 flex-1">
                  <div class="h-8 w-8 rounded-lg bg-white/5 flex items-center justify-center text-white/40 shrink-0">
                     <i class="fas fa-user-tie text-[10px]"></i>
                  </div>
                  <div class="flex flex-col gap-1 min-w-0">
                    <span class="text-xs font-bold text-white/80 group-hover:text-white transition-colors truncate">{{ v.nombre }}</span>
                    <div class="flex items-center gap-2">
                      <span class="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                        {{ v.rol_display || 'Vínculo' }}
                      </span>
                      <span v-if="v.mirror_active" class="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-500 border border-amber-500/20 flex items-center gap-1">
                        <i class="fas fa-link text-[8px]"></i> ESPEJO
                      </span>
                    </div>
                  </div>
                </div>
                <button 
                 @click="handleUnlink(v.id)"
                 class="h-10 w-10 rounded-xl bg-red-500/10 text-red-400 opacity-0 group-hover:opacity-100 hover:bg-red-500 hover:text-white transition-all flex items-center justify-center shrink-0 ml-4 shadow-lg shadow-red-500/10"
                 title="Desvincular"
                >
                  <i class="fas fa-trash-alt text-xs"></i>
                </button>
              </div>
           </div>
        </div>

        <!-- Link New Client -->
        <div class="w-full md:w-80 bg-white/[0.02] p-6 flex flex-col gap-4">
           <label class="text-[10px] uppercase font-black text-emerald-500/70 tracking-widest block">Vincular Nueva Entidad</label>
           
           <div class="relative">
             <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-white/20"></i>
             <input 
               v-model="searchQuery"
               placeholder="Buscar cliente..."
               class="w-full bg-slate-950 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white text-xs outline-none focus:border-emerald-500/50 transition-all"
               @input="handleSearch"
             />
           </div>

           <!-- Search Results -->
           <div class="flex-1 overflow-y-auto space-y-2 scrollbar-none">
             <button 
               v-for="c in searchResults" 
               :key="c.id" 
               @click="handleLink(c.id)"
               class="w-full text-left p-3 rounded-xl hover:bg-emerald-600/20 border border-transparent hover:border-emerald-500/30 transition-all group flex items-center justify-between"
             >
               <span class="text-[11px] text-white/50 group-hover:text-white font-medium truncate">{{ c.razon_social }}</span>
               <i class="fas fa-plus text-emerald-500 opacity-0 group-hover:opacity-100"></i>
             </button>
           </div>

           <div class="p-4 rounded-xl bg-cyan-600/5 border border-cyan-500/10 mt-auto">
             <p class="text-[9px] text-cyan-400 leading-relaxed font-medium">
               <i class="fas fa-info-circle mr-1"></i>
               Vincular una entidad no duplica registros; solo crea una referencia compartida.
             </p>
           </div>
        </div>
      </div>

      <!-- Footer -->
      <footer class="h-20 border-t border-white/5 flex items-center justify-center bg-white/5">
         <button 
           @click="$emit('close')"
           class="px-8 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-white font-bold text-xs transition-all uppercase tracking-widest"
         >
           Cerrar Gestor
         </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import api from '../../services/api';

const props = defineProps({
  show: Boolean,
  address: Object
});

const emit = defineEmits(['close', 'refresh']);

const searchQuery = ref('');
const searchResults = ref([]);

const handleSearch = async () => {
    if (searchQuery.value.length < 3) {
        searchResults.value = [];
        return;
    }
    try {
        const res = await api.get(`/clientes/?q=${searchQuery.value}`);
        // Filter out already linked ones
        const alreadyLinked = props.address?.vinculos_detalles?.map(v => v.id) || [];
        searchResults.value = res.data.filter(c => !alreadyLinked.includes(c.id)).slice(0, 10);
    } catch (err) {
        console.error("Search error:", err);
    }
}

const handleLink = async (clientId) => {
    try {
        await api.post(`/clientes/hub/${props.address.id}/links/${clientId}`);
        searchQuery.value = '';
        searchResults.value = [];
        emit('refresh');
    } catch (err) {
        console.error("Link error:", err);
        alert("Error al vincular entidad.");
    }
}

const handleUnlink = async (clientId) => {
    if (!confirm("¿Seguro que desea desvincular esta entidad de esta dirección?")) return;
    try {
        await api.delete(`/clientes/hub/${props.address.id}/links/${clientId}`);
        emit('refresh');
    } catch (err) {
        console.error("Unlink error:", err);
        alert("Error al desvincular entidad.");
    }
}

watch(() => props.show, (newVal) => {
    if (newVal) {
        searchQuery.value = '';
        searchResults.value = [];
    }
});
</script>

<style scoped>
.font-outfit {
  font-family: 'Outfit', sans-serif;
}
</style>
