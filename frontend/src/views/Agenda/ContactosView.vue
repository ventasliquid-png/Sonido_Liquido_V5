<template>
  <div class="flex h-full w-full bg-[var(--hawe-bg-main)] text-gray-200 overflow-hidden font-sans relative">
    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col relative min-w-0">
      <!-- Top Bar (Indigo Theme) -->
      <header class="relative z-20 flex h-16 items-center justify-between border-b border-white/10 bg-black/10 px-6 backdrop-blur-sm shrink-0">
        <div class="flex items-center gap-4">
             <button v-if="isModal" @click="$emit('close')" class="text-white/50 hover:text-white transition-colors" title="Volver">
                <i class="fa-solid fa-arrow-left text-lg"></i>
            </button>
            <div class="flex items-center gap-3">
                 <div class="h-8 w-8 rounded-lg bg-indigo-600/20 text-indigo-400 flex items-center justify-center border border-indigo-500/30">
                    <i class="fa-solid fa-address-book"></i>
                </div>
                <h1 class="font-outfit text-xl font-semibold text-white truncate">
                    Agenda Global
                </h1>
            </div>
        </div>

        <!-- Search & Tools -->
        <div class="flex items-center gap-4 ml-4">
          <div class="relative hidden sm:block">
            <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar contactos..."
              class="h-9 w-48 lg:w-64 rounded-full border border-gray-700 bg-gray-800 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all"
            />
          </div>
          <div class="h-6 w-px bg-white/10 hidden sm:block"></div>
          
          <!-- View Toggle -->
          <div class="flex bg-white/5 rounded-lg p-1 border border-white/10">
            <button 
                @click="viewMode = 'grid'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'grid' ? 'bg-white/10 text-indigo-400' : 'text-white/30 hover:text-white'"
                title="Vista Cuadrícula"
            >
                <i class="fa-solid fa-border-all"></i>
            </button>
            <button 
                @click="viewMode = 'list'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'list' ? 'bg-white/10 text-indigo-400' : 'text-white/30 hover:text-white'"
                title="Vista Lista"
            >
                <i class="fa-solid fa-list"></i>
            </button>
          </div>

          <button 
            @click="openNewContacto"
            class="flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-bold text-white shadow-lg shadow-indigo-500/20 transition-all hover:bg-indigo-500 hover:shadow-indigo-500/40 whitespace-nowrap ml-2"
          >
            <i class="fa-solid fa-plus"></i>
            <span class="hidden sm:inline">Nuevo</span>
          </button>
        </div>
      </header>

      <!-- Content Grid -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-gray-900 scrollbar-thumb-gray-700">
        <div v-if="loading" class="flex items-center justify-center h-full">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="filteredContactos.length === 0" class="flex flex-col items-center justify-center h-full text-white/30">
            <i class="fa-regular fa-address-book text-4xl mb-4"></i>
            <p>No se encontraron contactos</p>
        </div>

        <!-- Grid View -->
        <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <div 
            v-for="contacto in filteredContactos" 
            :key="contacto.id"
            @click="selectContacto(contacto)"
            class="group relative flex flex-col justify-between rounded-xl border border-white/5 bg-white/5 p-4 transition-all hover:bg-white/10 hover:shadow-xl hover:shadow-indigo-900/20 cursor-pointer"
            :class="{ 'ring-2 ring-indigo-500 bg-white/10': selectedId === contacto.id }"
          >
            <div class="flex items-start gap-4">
                 <!-- Avatar Circular -->
                <div class="h-12 w-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-lg shrink-0 text-lg font-bold border-2 border-white/10">
                    {{ getInitials(contacto) }}
                </div>
                <div class="min-w-0 flex-1">
                    <h3 class="font-bold text-white leading-tight group-hover:text-indigo-300 transition-colors truncate">
                        {{ contacto.nombre }} {{ contacto.apellido }}
                    </h3>
                    <p class="text-xs text-white/50 truncate mt-0.5">{{ contacto.puesto || 'Sin Puesto' }}</p>
                    
                    <!-- Chips de Roles -->
                    <div class="flex flex-wrap gap-1 mt-2">
                        <span v-for="rol in (contacto.roles || []).slice(0, 2)" :key="rol" class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-white/10 text-white/70 border border-white/5">
                            {{ rol }}
                        </span>
                        <span v-if="(contacto.roles || []).length > 2" class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-white/10 text-white/50">
                            +{{ contacto.roles.length - 2 }}
                        </span>
                    </div>
                </div>
            </div>
            
            <!-- Footer: Empresa context -->
            <div class="mt-4 pt-3 border-t border-white/5 flex flex-col gap-1">
                 <div v-if="contacto.transporte" class="flex items-center gap-2 text-xs text-amber-500/80">
                    <i class="fa-solid fa-truck text-[10px]"></i>
                    <span class="truncate">{{ contacto.transporte.nombre }}</span>
                </div>
                <div v-else-if="contacto.cliente" class="flex items-center gap-2 text-xs text-blue-400/80">
                    <i class="fa-solid fa-building text-[10px]"></i>
                    <span class="truncate">{{ contacto.cliente.razon_social }}</span>
                </div>
                <!-- Si tuviera vinculo_id podríamos resolverlo, por ahora confiamos en el populate del backend si existe -->
                <div v-else class="flex items-center gap-2 text-xs text-gray-500">
                    <i class="fa-regular fa-user"></i>
                    <span class="italic">Particular</span>
                </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="flex flex-col gap-2">
             <div 
                v-for="contacto in filteredContactos" 
                :key="contacto.id"
                @click="selectContacto(contacto)"
                class="group flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-colors"
                :class="{ 'ring-1 ring-indigo-500 bg-white/10': selectedId === contacto.id }"
             >
                <div class="flex items-center gap-4 flex-1 min-w-0">
                    <div class="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shrink-0 text-xs font-bold">
                         {{ getInitials(contacto) }}
                    </div>
                    <div class="min-w-0 flex-1 grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div>
                             <h3 class="font-bold text-white truncate">{{ contacto.nombre }} {{ contacto.apellido }}</h3>
                             <p class="text-xs text-white/50 truncate sm:hidden">{{ contacto.puesto }}</p>
                        </div>
                        <p class="text-sm text-white/50 truncate hidden sm:block">{{ contacto.puesto || '---' }}</p>
                        <div class="hidden sm:block truncate text-xs">
                             <span v-if="contacto.transporte" class="text-amber-500">{{ contacto.transporte.nombre }}</span>
                             <span v-else-if="contacto.cliente" class="text-blue-400">{{ contacto.cliente.razon_social }}</span>
                             <span v-else class="text-gray-500">Particular</span>
                        </div>
                    </div>
                </div>
             </div>
        </div>
      </div>
    </main>
    
    <!-- Canvas Modal -->
     <transition name="slide-fade">
        <ContactCanvas 
            v-if="selectedId" 
            :contacto-id="selectedId"
            :initial-data="selectedContacto"
            @close="closeInspector"
            @save="handleSaveSuccess"
        />
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useContactosStore } from '../../stores/contactos' 
import ContactCanvas from './components/ContactCanvas.vue' // We will create this next

const props = defineProps({
    isModal: { type: Boolean, default: false }
})
const emit = defineEmits(['close'])

const contactosStore = useContactosStore()
const loading = computed(() => contactosStore.loading)
const allContactos = computed(() => contactosStore.contactos)

const searchQuery = ref('')
const viewMode = ref('grid')
const selectedId = ref(null)
const selectedContacto = ref(null)

onMounted(async () => {
    await contactosStore.fetchContactos()
})

const filteredContactos = computed(() => {
    let result = allContactos.value
    if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        result = result.filter(c => 
            c.nombre.toLowerCase().includes(q) || 
            c.apellido.toLowerCase().includes(q) ||
            (c.puesto && c.puesto.toLowerCase().includes(q))
        )
    }
    return result
})

const getInitials = (c) => {
    if (!c.nombre) return '?'
    return (c.nombre[0] + (c.apellido ? c.apellido[0] : '')).toUpperCase()
}

const selectContacto = (c) => {
    selectedId.value = c.id
    selectedContacto.value = c
}

const openNewContacto = () => {
    selectedId.value = 'new'
    selectedContacto.value = null // Canvas will handle defaults
}

const closeInspector = () => {
    selectedId.value = null
    selectedContacto.value = null
}

const handleSaveSuccess = async () => {
    await contactosStore.fetchContactos()
    closeInspector()
}
</script>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
