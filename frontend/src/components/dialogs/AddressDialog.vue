
<template>
  <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
    <div class="bg-slate-900 border border-cyan-500/30 rounded-3xl w-full max-w-lg overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
      <!-- Header -->
      <header class="h-16 flex items-center justify-between px-6 border-b border-white/5 bg-white/5 shrink-0">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-xl bg-cyan-600/20 flex items-center justify-center text-cyan-400">
            <i class="fas fa-map-marker-alt"></i>
          </div>
          <h3 class="font-outfit font-bold text-lg text-white">
            {{ isEdit ? 'Editar Domicilio' : 'Nuevo Domicilio' }}
          </h3>
        </div>
        <button @click="$emit('close')" class="h-8 w-8 rounded-full hover:bg-white/10 text-white/40 hover:text-white transition-all">
          <i class="fas fa-times"></i>
        </button>
      </header>

      <!-- Form Content (Scrollable) -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-cyan-900/20">
        <!-- Alias / Name -->
        <div class="space-y-2">
          <label class="text-[10px] uppercase font-bold text-cyan-500/70 tracking-widest pl-1">Nombre o Alias</label>
          <input 
            v-model="form.alias" 
            placeholder="Ej: Sede Norte, Deposito Central"
            class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-cyan-500/50 transition-all font-medium"
          />
        </div>

        <div class="grid grid-cols-12 gap-4">
          <!-- Calle -->
          <div class="col-span-12 sm:col-span-8 space-y-2">
            <label class="text-[10px] uppercase font-bold text-cyan-500/70 tracking-widest pl-1">Calle / Avenida</label>
            <input 
              v-model="form.calle" 
              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-cyan-500/50 transition-all font-medium"
            />
          </div>
          <!-- Numero -->
          <div class="col-span-12 sm:col-span-4 space-y-2">
            <label class="text-[10px] uppercase font-bold text-cyan-500/70 tracking-widest pl-1">Número</label>
            <input 
              v-model="form.numero" 
              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-cyan-500/50 transition-all font-medium"
            />
          </div>
        </div>

        <div class="grid grid-cols-12 gap-4">
          <div class="col-span-6 space-y-2">
            <label class="text-[10px] uppercase font-bold text-cyan-500/70 tracking-widest pl-1">Piso</label>
            <input v-model="form.piso" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-cyan-500/50 transition-all font-medium" />
          </div>
          <div class="col-span-6 space-y-2">
            <label class="text-[10px] uppercase font-bold text-cyan-500/70 tracking-widest pl-1">Depto</label>
            <input v-model="form.depto" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-cyan-500/50 transition-all font-medium" />
          </div>
        </div>

        <div class="grid grid-cols-12 gap-4">
          <div class="col-span-6 space-y-2">
            <label class="text-[10px] uppercase font-bold text-cyan-500/70 tracking-widest pl-1">CP</label>
            <input v-model="form.cp" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-cyan-500/50 transition-all font-medium" />
          </div>
          <div class="col-span-6 space-y-2">
            <label class="text-[10px] uppercase font-bold text-cyan-500/70 tracking-widest pl-1">Localidad</label>
            <input v-model="form.localidad" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-cyan-500/50 transition-all font-medium" />
          </div>
        </div>

        <!-- Province -->
        <div class="space-y-2">
           <label class="text-[10px] uppercase font-bold text-cyan-500/70 tracking-widest pl-1">Provincia</label>
           <select 
             v-model="form.provincia_id" 
             class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white outline-none focus:border-cyan-500/50 transition-all font-medium appearance-none"
           >
             <option value="CABA">Capital Federal (CABA)</option>
             <option value="BUENOS_AIRES">Buenos Aires</option>
             <option value="CORDOBA">Córdoba</option>
             <option value="SANTA_FE">Santa Fe</option>
             <option value="MENDOZA">Mendoza</option>
           </select>
        </div>

        <!-- Warning Area -->
        <div v-if="usageCount > 0" class="p-4 rounded-2xl bg-amber-500/5 border border-amber-500/20 text-amber-500 text-[10px] flex gap-3 animate-pulse">
            <i class="fas fa-exclamation-triangle mt-0.5"></i>
            <div>
              <p class="font-bold uppercase tracking-widest mb-1">Afectación Sistémica</p>
              <p class="leading-relaxed opacity-80">
                Esta dirección está vinculada a **{{ usageCount }}** clientes. <br>
                Los cambios se propagarán a todas las entidades de forma inmediata.
              </p>
            </div>
        </div>
      </div>

      <!-- Footer -->
      <footer class="p-6 pt-0 flex justify-end gap-3 shrink-0">
        <button 
          @click="$emit('close')" 
          class="px-5 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-white/50 hover:text-white font-bold text-xs transition-all"
        >
          CANCELAR
        </button>
        <button 
          @click="handleSubmit" 
          class="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow-xl shadow-cyan-900/20 transition-all transform active:scale-[0.98]"
        >
          {{ isEdit ? 'GUARDAR MAESTRO' : 'CREAR DOMICILIO' }}
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  show: Boolean,
  initialData: Object,
  isEdit: Boolean,
  usageCount: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['close', 'save']);

const form = ref({
  alias: '',
  calle: '',
  numero: '',
  piso: '',
  depto: '',
  cp: '',
  localidad: '',
  provincia_id: 'CABA'
});

watch(() => props.initialData, (newVal) => {
    if (newVal) {
        form.value = { ...newVal };
    } else {
        form.value = {
            alias: '',
            calle: '',
            numero: '',
            piso: '',
            depto: '',
            cp: '',
            localidad: '',
            provincia_id: 'CABA'
        };
    }
}, { immediate: true });

const handleSubmit = () => {
  emit('save', { ...form.value });
};
</script>

<style scoped>
.font-outfit {
  font-family: 'Outfit', sans-serif;
}
</style>
