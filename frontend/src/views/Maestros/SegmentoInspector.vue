<template>
    <div class="h-full flex flex-col bg-[#05151f]/95 border-l border-cyan-900/30">
        <!-- Empty State -->
        <div v-if="!modelValue" class="flex flex-col items-center justify-center h-full text-white/30 p-6 text-center">
             <i class="fas fa-layer-group text-4xl mb-4 text-cyan-900/50"></i>
             <p class="text-sm">Seleccione un segmento<br>para ver sus detalles</p>
             <button 
                @click="$emit('create')"
                class="mt-4 px-4 py-2 bg-cyan-900/20 hover:bg-cyan-900/40 text-cyan-400 text-xs font-bold uppercase tracking-wider rounded border border-cyan-500/30 transition-all"
            >
                + Nuevo Segmento
             </button>
        </div>

        <!-- Form State -->
        <div v-else class="flex flex-col h-full">
            <!-- Header -->
            <div class="h-16 flex items-center justify-between px-6 border-b border-cyan-900/30 bg-[#0a253a]/50 backdrop-blur-sm shrink-0">
                <h2 class="font-outfit text-lg font-bold text-white tracking-wide">
                    <span class="text-cyan-400 mr-2">{{ isNew ? 'Nuevo' : 'Editar' }}</span> Segmento
                </h2>
                <button 
                    @click="$emit('close')" 
                    class="h-8 w-8 rounded-full flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all"
                    title="Cerrar (ESC)"
                >
                    <i class="fas fa-times"></i>
                </button>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-cyan-900/30 hover:scrollbar-thumb-cyan-900/50">
                
                <!-- ID/Code - Disabled if editing -->
                <div class="group">
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-cyan-500/70 mb-1.5 ml-1">Código Identificador</label>
                    <div class="relative">
                        <input 
                            :value="isNew ? 'Autogenerado' : localForm.id" 
                            type="text" 
                            disabled
                            class="w-full bg-[#0a1f2e] text-white/50 border border-cyan-900/10 rounded-lg px-4 py-2.5 focus:outline-none transition-all cursor-not-allowed font-mono text-sm"
                        />
                        <i class="fas fa-lock absolute right-3 top-3 text-white/20 text-xs"></i>
                    </div>
                </div>

                <!-- Nombre -->
                <div class="group">
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-cyan-500/70 mb-1.5 ml-1">Nombre Descriptivo</label>
                    <input 
                        v-model="localForm.nombre" 
                        ref="nombreInput"
                        type="text" 
                        class="w-full bg-[#0a1f2e] text-white border border-cyan-900/30 rounded-lg px-4 py-2.5 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 transition-all placeholder-white/20"
                        placeholder="Ej: Mayoristas"
                    />
                </div>

                <!-- Descripcion -->
                 <div class="group">
                    <label class="block text-[10px] uppercase tracking-wider font-bold text-cyan-500/70 mb-1.5 ml-1">Descripción (Opcional)</label>
                    <textarea 
                        v-model="localForm.descripcion" 
                        rows="3"
                        class="w-full bg-[#0a1f2e] text-white border border-cyan-900/30 rounded-lg px-4 py-2.5 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/50 transition-all resize-none placeholder-white/20"
                        placeholder="Detalles adicionales del segmento..."
                    ></textarea>
                </div>

                <!-- Toggle Estado -->
                <div class="flex items-center justify-between bg-[#0a1f2e]/50 p-4 rounded-lg border border-cyan-900/20">
                    <div>
                        <span class="block text-sm font-bold text-white">Estado Activo</span>
                        <span class="text-xs text-white/40">Habilitar este segmento para uso</span>
                    </div>
                    <button 
                        @click="localForm.activo = !localForm.activo"
                        class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-[#05151f]"
                        :class="localForm.activo ? 'bg-cyan-600' : 'bg-gray-700'"
                    >
                        <span 
                            class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-lg"
                            :class="localForm.activo ? 'translate-x-6' : 'translate-x-1'"
                        />
                    </button>
                </div>

            </div>

            <!-- Footer Actions -->
            <div class="p-6 border-t border-cyan-900/30 bg-[#081c26] space-y-3 shrink-0">
                <button 
                    @click="handleSave"
                    class="w-full py-3 bg-gradient-to-r from-cyan-700 to-cyan-600 hover:from-cyan-600 hover:to-cyan-500 text-white rounded-lg font-bold shadow-lg shadow-cyan-900/30 hover:shadow-cyan-500/20 transition-all transform active:scale-[0.98] flex items-center justify-center gap-2"
                >
                    <i class="fas fa-save"></i>
                    <span>Guardar (F10)</span>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
    modelValue: {
        type: Object,
        default: null
    },
    isNew: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['close', 'save', 'create'])

const localForm = ref({
    id: '',
    nombre: '',
    descripcion: '',
    activo: true
})

const nombreInput = ref(null)

watch(() => props.modelValue, (newVal) => {
    if (newVal) {
        localForm.value = { ...newVal }
        // Focus name on open if new or just opened
        setTimeout(() => {
            if (nombreInput.value) nombreInput.value.focus()
        }, 100)
    }
}, { immediate: true })

const handleSave = () => {
    emit('save', localForm.value)
}

// Global Shortcuts handled by parent or here if focused?
// Parent handles global F10/ESC usually, but button click here works too.
</script>
