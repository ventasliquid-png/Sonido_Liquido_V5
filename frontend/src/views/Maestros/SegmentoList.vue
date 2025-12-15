<template>
    <div class="flex h-full w-full bg-[#081c26] text-gray-200 font-sans overflow-hidden">
        
        <!-- Main Content -->
        <main class="flex-1 flex flex-col min-w-0" :class="{ 'bg-[#0a1f2e]': isStacked }">
            
            <!-- Header -->
            <header class="h-16 flex items-center justify-between px-6 border-b border-cyan-900/20 bg-[#0a1f2e]/50 backdrop-blur-sm shrink-0">
                <div class="flex items-center gap-4">
                    <button v-if="isStacked" @click="$emit('close')" class="text-cyan-400 hover:text-cyan-300">
                        <i class="fas fa-arrow-left"></i>
                    </button>
                    <h1 class="font-outfit text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                        Administrar Segmentos
                    </h1>
                </div>

                <div class="flex gap-3">
                     <button 
                        @click="openNewSegmento"
                        class="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-sm shadow-lg shadow-cyan-900/20 transition-all transform active:scale-[0.98]"
                    >
                        <i class="fas fa-plus"></i>
                        <span>NUEVO (INS)</span>
                    </button>
                </div>
            </header>

            <!-- Search Bar -->
            <div class="p-6 pb-2">
                <div class="relative w-full max-w-2xl">
                    <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-cyan-500/50"></i>
                    <input 
                        v-model="searchQuery" 
                        type="text" 
                        placeholder="Buscar segmentos..." 
                        class="w-full bg-[#05151f] border border-cyan-900/30 rounded-xl py-3 pl-11 pr-12 text-white placeholder-gray-500 outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-all font-medium"
                    >
                    <div class="absolute right-4 top-1/2 -translate-y-1/2 flex gap-2">
                        <span class="text-[10px] font-bold bg-[#0a1f2e] text-gray-500 px-1.5 py-0.5 rounded border border-gray-800">Ctrl+K</span>
                    </div>
                </div>
            </div>
            
            <!-- List Header -->
            <div class="px-6 py-2 grid grid-cols-12 gap-4 text-[10px] uppercase font-bold text-cyan-500/70 tracking-wider">
                <div class="col-span-3">Nombre</div>
                <div class="col-span-6">Descripción</div>
                <div class="col-span-2 text-center">Estado</div>
                <div class="col-span-1 text-right">Acciones</div>
            </div>

            <!-- List Content -->
            <div class="flex-1 overflow-y-auto px-6 pb-6 scrollbar-thin scrollbar-thumb-cyan-900/20">
                <div v-if="filteredSegmentos.length === 0" class="flex flex-col items-center justify-center h-48 opacity-50">
                    <i class="fas fa-search text-3xl mb-2 text-cyan-900"></i>
                    <p class="text-sm">No se encontraron segmentos</p>
                </div>

                <div v-else class="space-y-1">
                    <div 
                        v-for="seg in filteredSegmentos" 
                        :key="seg.id"
                        @click="openInspector(seg)"
                        class="grid grid-cols-12 gap-4 items-center p-4 rounded-xl border border-transparent hover:border-cyan-500/20 hover:bg-cyan-900/10 cursor-pointer transition-all group"
                        :class="{ 'bg-cyan-900/20 border-cyan-500/30': selectedSegmento && selectedSegmento.id === seg.id }"
                    >
                        <div class="col-span-3 font-bold text-white group-hover:text-cyan-300 transition-colors">
                            {{ seg.nombre }}
                        </div>
                        <div class="col-span-6 text-sm text-gray-400 truncate">
                            {{ seg.descripcion || '-' }}
                        </div>
                        <div class="col-span-2 flex justify-center">
                            <span 
                                class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide border"
                                :class="seg.activo ? 'bg-emerald-900/30 text-emerald-400 border-emerald-500/30' : 'bg-red-900/30 text-red-400 border-red-500/30'"
                            >
                                {{ seg.activo ? 'Activo' : 'Inactivo' }}
                            </span>
                        </div>
                        <div class="col-span-1 flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                            <i class="fas fa-chevron-right text-cyan-500/50"></i>
                        </div>
                    </div>
                </div>

                <div class="mt-4 text-xs text-right text-gray-600 font-mono">
                    {{ filteredSegmentos.length }} Registros
                </div>
            </div>

            <CommandPalette 
                :show="showCommandPalette" 
                @close="showCommandPalette = false"
                @navigate="handleNavigation"
            />
        </main>

        <!-- Right Inspector Panel (Static) -->
        <aside class="w-96 shrink-0 z-30 shadow-xl overflow-hidden h-full"> 
            <SegmentoInspector 
                 :modelValue="selectedSegmento"
                 :is-new="isNewSegmento"
                 @close="closeInspector"
                 @save="handleSaveFromInspector"
                 @create="openNewSegmento"
            />
        </aside>

    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, reactive } from 'vue';
import { useMaestrosStore } from '../../stores/maestros';
import { useRouter } from 'vue-router';
// import AppSidebar from '../../components/layout/AppSidebar.vue'; // Removed: Handled by Layout
import SegmentoInspector from './SegmentoInspector.vue';
import CommandPalette from '../../components/common/CommandPalette.vue';

const props = defineProps({
    isStacked: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['close']);

const store = useMaestrosStore();
const router = useRouter();

const selectedSegmento = ref(null);
const isNewSegmento = ref(false);
const searchQuery = ref('');
const showCommandPalette = ref(false);

const normalizeText = (text) => {
    return text ? text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase() : ''
}

const filteredSegmentos = computed(() => {
    let items = store.segmentos || [];
    if (searchQuery.value) {
        const query = normalizeText(searchQuery.value);
        items = items.filter(s => 
            normalizeText(s.nombre).includes(query) || 
            normalizeText(s.id).includes(query)
        );
    }
    return items;
});

const openNewSegmento = () => {
    selectedSegmento.value = {
        id: '',
        nombre: '',
        descripcion: '',
        activo: true
    };
    isNewSegmento.value = true;
};

const openInspector = (segmento) => {
    // Clone to check changes? For now just assign/reference?
    // Better clone to avoid mutation of store directly before save
    selectedSegmento.value = { ...segmento };
    isNewSegmento.value = false;
};

const closeInspector = () => {
    selectedSegmento.value = null;
    isNewSegmento.value = false;
};

const handleSaveFromInspector = async (formData) => {
    try {
        if (isNewSegmento.value) {
            const { id, ...newSegmento } = formData;
            await store.createSegmento(newSegmento);
        } else {
            await store.updateSegmento(formData.id, formData);
        }
        closeInspector();
    } catch (error) {
        console.error('Error saving segmento', error);
        // Toast handled by store? If not, we should have one.
        // Assuming store or interceptor handles generic errors, but usually we need success feedback.
    }
};

const handleNavigation = (route) => {
    router.push(route);
};

const handleGlobalKeydown = (e) => {
    if (e.key === 'Insert') {
        e.preventDefault();
        openNewSegmento();
    }
    if (e.key === 'Escape') {
        if (showCommandPalette.value) {
            showCommandPalette.value = false;
            e.preventDefault();
        } else if (selectedSegmento.value) {
            closeInspector();
            e.preventDefault();
        } else if (props.isStacked) {
            emit('close');
            e.preventDefault();
        }
    }
    if (e.key === 'k' && e.ctrlKey) {
        e.preventDefault();
        showCommandPalette.value = true;
    }
};

onMounted(async () => {
    window.addEventListener('keydown', handleGlobalKeydown);
    await store.fetchSegmentos();
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeydown);
});
</script>
