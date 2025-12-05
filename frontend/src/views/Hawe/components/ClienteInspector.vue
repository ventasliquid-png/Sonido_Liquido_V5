<template>
  <aside class="w-96 border-l border-cyan-900/30 bg-[#05151f]/95 flex flex-col z-30 shadow-2xl overflow-hidden h-full backdrop-blur-xl">
    <!-- Empty State -->
    <div v-if="!modelValue && !isNew" class="flex flex-col items-center justify-center h-full text-cyan-900/40 p-6 text-center">
        <i class="fas fa-user text-4xl mb-4"></i>
        <p>Seleccione un cliente para ver sus propiedades</p>
    </div>

    <!-- Form Content -->
    <div v-else class="flex flex-col h-full">
        <!-- Header -->
        <div class="flex justify-between items-center p-6 border-b border-cyan-900/20 bg-[#0a253a]/30 shrink-0">
            <div>
                <h2 class="text-lg font-bold text-cyan-100 leading-tight">
                    {{ isNew ? 'Nuevo Cliente' : 'Editar Cliente' }}
                </h2>
                <p v-if="!isNew" class="text-xs text-cyan-400/50 font-mono mt-1">{{ form.cuit || 'Sin CUIT' }}</p>
            </div>
            <button @click="$emit('close')" class="text-cyan-900/50 hover:text-cyan-100 transition-colors">
                <i class="fas fa-times"></i>
            </button>
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-cyan-900/20 shrink-0 bg-[#0a253a]/10">
            <button 
                @click="activeTab = 'general'"
                class="flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'general' ? 'border-cyan-400 text-cyan-400 bg-cyan-900/10' : 'border-transparent text-cyan-900/50 hover:text-cyan-200 hover:bg-cyan-900/5'"
            >
                General
            </button>
            <button 
                @click="activeTab = 'domicilios'"
                class="flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'domicilios' ? 'border-cyan-400 text-cyan-400 bg-cyan-900/10' : 'border-transparent text-cyan-900/50 hover:text-cyan-200 hover:bg-cyan-900/5'"
                :disabled="isNew"
            >
                Domicilios
            </button>
            <button 
                @click="activeTab = 'contactos'"
                class="flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'contactos' ? 'border-cyan-400 text-cyan-400 bg-cyan-900/10' : 'border-transparent text-cyan-900/50 hover:text-cyan-200 hover:bg-cyan-900/5'"
                :disabled="isNew"
            >
                Contactos
            </button>
        </div>

        <!-- Scrollable Body -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-cyan-900/50 scrollbar-track-transparent">
            
            <!-- TAB: GENERAL -->
            <div v-if="activeTab === 'general'" class="space-y-4">
                <!-- Active Toggle -->
                <div class="flex items-center justify-between bg-cyan-900/10 p-3 rounded-lg border border-cyan-900/20">
                    <span class="text-sm font-bold text-cyan-100">Estado</span>
                    <div class="flex items-center gap-2">
                        <span class="text-[10px] font-bold uppercase" :class="form.activo ? 'text-green-400' : 'text-red-400'">
                            {{ form.activo ? 'ACTIVO' : 'INACTIVO' }}
                        </span>
                        <button 
                            @click="toggleActive"
                            class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none"
                            :class="form.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                        >
                            <span 
                                class="inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform shadow-sm"
                                :class="form.activo ? 'translate-x-4.5' : 'translate-x-1'"
                            />
                        </button>
                    </div>
                </div>

                <!-- Fields -->
                <div>
                    <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Razón Social *</label>
                    <input v-model="form.razon_social" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors placeholder-cyan-900/30" placeholder="Ej: Empresa S.A." />
                </div>

                <div>
                    <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">CUIT</label>
                    <input v-model="form.cuit" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors font-mono placeholder-cyan-900/30" placeholder="00-00000000-0" maxlength="13" />
                </div>

                <div>
                    <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Segmento</label>
                    <select v-model="form.segmento_id" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors appearance-none">
                        <option :value="null">Sin Segmento</option>
                        <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Condición IVA</label>
                    <select v-model="form.condicion_iva" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors appearance-none">
                        <option value="Responsable Inscripto">Responsable Inscripto</option>
                        <option value="Monotributista">Monotributista</option>
                        <option value="Exento">Exento</option>
                        <option value="Consumidor Final">Consumidor Final</option>
                    </select>
                </div>

                <div class="pt-4 border-t border-cyan-900/20">
                    <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Observaciones</label>
                    <textarea v-model="form.observaciones" rows="3" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors resize-none text-sm placeholder-cyan-900/30"></textarea>
                </div>
            </div>

            <!-- TAB: DOMICILIOS -->
            <div v-else-if="activeTab === 'domicilios'" class="space-y-4">
                <div v-if="isNew" class="text-center p-4 text-cyan-900/50 text-sm">
                    Guarde el cliente para agregar domicilios.
                </div>
                <div v-else class="space-y-3">
                    <div 
                        v-for="dom in form.domicilios" 
                        :key="dom.id"
                        class="bg-cyan-900/5 border border-cyan-900/20 rounded-lg p-3 relative group hover:bg-cyan-900/10 transition-colors"
                    >
                        <div class="flex justify-between items-start">
                            <span v-if="dom.es_fiscal" class="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 rounded border border-purple-500/30">FISCAL</span>
                            <span v-else class="text-[10px] bg-gray-700 text-gray-300 px-1.5 rounded">SUCURSAL</span>
                        </div>
                        <p class="text-sm font-medium text-cyan-100 mt-1">{{ dom.calle }} {{ dom.numero }}</p>
                        <p class="text-xs text-cyan-200/50">{{ dom.localidad }}</p>
                        
                        <!-- Edit Button (Placeholder) -->
                        <button class="absolute top-2 right-2 text-cyan-900/30 hover:text-cyan-100 opacity-0 group-hover:opacity-100 transition-opacity">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                    </div>
                    
                    <button class="w-full py-2 border border-dashed border-cyan-900/30 rounded-lg text-cyan-900/50 hover:text-cyan-400 hover:border-cyan-500/30 hover:bg-cyan-500/5 transition-all text-xs font-bold uppercase">
                        <i class="fas fa-plus mr-1"></i> Agregar Domicilio
                    </button>
                </div>
            </div>

            <!-- TAB: CONTACTOS -->
            <div v-else-if="activeTab === 'contactos'" class="space-y-4">
                <div v-if="isNew" class="text-center p-4 text-cyan-900/50 text-sm">
                    Guarde el cliente para agregar contactos.
                </div>
                <div v-else class="space-y-3">
                    <div 
                        v-for="contact in form.vinculos" 
                        :key="contact.id"
                        class="bg-cyan-900/5 border border-cyan-900/20 rounded-lg p-3 flex items-center gap-3 relative group hover:bg-cyan-900/10 transition-colors"
                    >
                        <div class="h-8 w-8 rounded-full bg-gradient-to-br from-cyan-600 to-blue-500 flex items-center justify-center text-xs font-bold text-white shrink-0">
                            {{ contact.nombre ? contact.nombre.substring(0,2).toUpperCase() : 'NN' }}
                        </div>
                        <div>
                            <p class="text-sm font-bold text-cyan-100">{{ contact.nombre }}</p>
                            <p class="text-[10px] text-cyan-200/50 uppercase">{{ contact.rol || 'Sin Rol' }}</p>
                        </div>
                         <!-- Edit Button (Placeholder) -->
                        <button class="absolute top-2 right-2 text-cyan-900/30 hover:text-cyan-100 opacity-0 group-hover:opacity-100 transition-opacity">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                    </div>

                     <button class="w-full py-2 border border-dashed border-cyan-900/30 rounded-lg text-cyan-900/50 hover:text-cyan-400 hover:border-cyan-500/30 hover:bg-cyan-500/5 transition-all text-xs font-bold uppercase">
                        <i class="fas fa-plus mr-1"></i> Agregar Contacto
                    </button>
                </div>
            </div>

        </div>

        <!-- Footer Actions -->
        <div class="p-6 border-t border-cyan-900/20 flex gap-3 shrink-0 bg-[#020a0f]">
            <button @click="save" class="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white py-2 rounded font-bold transition-colors shadow-lg shadow-cyan-900/20">
                <span v-if="saving"><i class="fas fa-spinner fa-spin mr-2"></i>Guardando...</span>
                <span v-else>Guardar (F10)</span>
            </button>
            <button v-if="!isNew" @click="remove" class="px-3 bg-red-900/20 hover:bg-red-900/40 text-red-400 rounded border border-red-500/30 transition-colors" title="Dar de baja">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { useMaestrosStore } from '../../../stores/maestros'

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

const emit = defineEmits(['update:modelValue', 'close', 'save', 'delete'])

const maestrosStore = useMaestrosStore()
const segmentos = computed(() => maestrosStore.segmentos)

const activeTab = ref('general')
const saving = ref(false)
const form = ref({})

// Initialize form when modelValue changes
watch(() => props.modelValue, (newVal) => {
    if (newVal) {
        form.value = JSON.parse(JSON.stringify(newVal)) // Deep copy
        // Ensure arrays exist
        if (!form.value.domicilios) form.value.domicilios = []
        if (!form.value.vinculos) form.value.vinculos = []
    } else {
        form.value = {}
    }
    // Reset tab on new selection
    if (props.isNew) activeTab.value = 'general'
}, { immediate: true })

const toggleActive = () => {
    if (form.value.activo) {
        // If turning off, we might want to trigger the delete flow or just toggle
        // For now, just toggle, but parent might intercept save
        if (!confirm('¿Está seguro que desea desactivar este cliente?')) return
    }
    form.value.activo = !form.value.activo
}

const save = async () => {
    saving.value = true
    try {
        emit('save', form.value)
    } finally {
        saving.value = false
    }
}

const remove = () => {
    if (confirm('¿Seguro que desea dar de baja este cliente?')) {
        emit('delete', form.value)
    }
}

const handleKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault()
        save()
    }
    if (e.key === 'Escape') {
        e.preventDefault()
        emit('close')
    }
}

onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})
</script>
