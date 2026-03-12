<template>
  <div v-if="show" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
    <div class="bg-[#0f172a] w-full max-w-2xl rounded-xl shadow-2xl border border-rose-500/30 overflow-hidden flex flex-col max-h-[90vh]">
        
        <!-- Header -->
        <div class="p-6 bg-gradient-to-r from-rose-900/30 to-[#0f172a] border-b border-rose-900/40 flex items-center justify-between">
            <div>
                <h2 class="text-xl font-bold text-white flex items-center gap-3">
                    <i class="fas fa-exclamation-triangle text-amber-500 animate-pulse"></i>
                    Baja de Rubro: {{ sourceRubro?.nombre }}
                </h2>
                <p class="text-rose-200/50 text-sm mt-1">Este rubro contiene elementos asociados.</p>
            </div>
            <button @click="cancel" class="text-rose-900/50 hover:text-white transition-colors">
                <i class="fas fa-times text-xl"></i>
            </button>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6">
            
            <!-- Dependency Warning -->
            <div class="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4 flex gap-4">
                <div class="text-amber-500 text-2xl"><i class="fas fa-network-wired"></i></div>
                <div>
                     <p class="text-amber-100 font-bold mb-1">Imposible eliminar directamente</p>
                     <p class="text-amber-200/70 text-sm">
                        Para desactivar este rubro, primero debes reasignar sus dependencias a otro rubro existente.
                    </p>
                </div>
            </div>

            <!-- Stats -->
            <div class="grid grid-cols-2 gap-4">
                <div class="bg-black/40 rounded-lg p-4 border border-rose-500/10 flex items-center justify-between">
                    <div>
                        <div class="text-2xl font-bold text-white">{{ dependencies.cantidad_hijos }}</div>
                        <div class="text-xs text-white/50 uppercase tracking-wider">Sub-rubros</div>
                    </div>
                    <i class="fas fa-sitemap text-rose-500/20 text-3xl"></i>
                </div>
                <div class="bg-black/40 rounded-lg p-4 border border-rose-500/10 flex items-center justify-between">
                    <div>
                        <div class="text-2xl font-bold text-white">{{ dependencies.cantidad_productos }}</div>
                        <div class="text-xs text-white/50 uppercase tracking-wider">Productos</div>
                    </div>
                    <i class="fas fa-box text-rose-500/20 text-3xl"></i>
                </div>
            </div>

            <!-- List Preview (Collapsible?) -->
            <div class="space-y-2">
                <div v-if="dependencies.cantidad_hijos > 0">
                    <h3 class="text-xs font-bold text-white/40 uppercase mb-2">Sub-rubros afectados ({{ dependencies.cantidad_hijos }})</h3>
                    <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-2 bg-black/20 rounded border border-white/5">
                        <button 
                            v-for="h in dependencies.rubros_hijos" 
                            :key="h.id" 
                            @click="$emit('edit-subrubro', h)"
                            class="px-2 py-1 bg-rose-900/20 border border-rose-500/20 rounded text-xs text-rose-200 truncate max-w-[150px] hover:bg-rose-600 hover:text-white cursor-pointer transition-colors flex items-center gap-2 group"
                            title="Click para editar y reasignar"
                        >
                            {{ h.nombre }} <i class="fas fa-pencil-alt opacity-0 group-hover:opacity-100 text-[10px]"></i>
                        </button>
                    </div>
                </div>

                <div v-if="dependencies.cantidad_productos > 0">
                     <h3 class="text-xs font-bold text-white/40 uppercase mb-2">Productos afectados ({{ dependencies.cantidad_productos }})</h3>
                     <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-2 bg-black/20 rounded border border-white/5">
                        <span v-for="p in dependencies.productos" :key="p.id" class="px-2 py-1 bg-cyan-900/20 border border-cyan-500/20 rounded text-xs text-cyan-200 truncate max-w-[150px]">
                            {{ p.nombre }}
                        </span>
                    </div>
                </div>
            </div>

            <!-- Action: Select Target -->
            <div class="pt-6 border-t border-rose-900/20">
                <h3 class="text-sm font-bold text-white mb-4">Seleccionar Destino de Migración</h3>
                
                <div class="flex gap-2">
                    <div class="flex-1">
                        <label class="block text-xs font-bold text-white/50 uppercase mb-1">Mover todo a:</label>
                        <select v-model="targetRubroId" class="w-full bg-[#050b14] border border-rose-500/30 rounded p-3 text-white focus:border-rose-500 outline-none">
                            <option :value="null">-- Seleccionar Rubro --</option>
                            <option v-for="r in availableTargets" :key="r.id" :value="r.id">
                                {{ r.nombre }} ({{ r.codigo }})
                            </option>
                        </select>
                    </div>
                    <button @click="$emit('create-new')" class="self-end px-4 py-3 bg-rose-600/20 hover:bg-rose-600 text-rose-200 hover:text-white border border-rose-500/50 rounded transition-all font-bold whitespace-nowrap" title="Crear Nuevo Rubro (F4)">
                        <i class="fas fa-plus"></i> Nuevo
                    </button>
                </div>
            </div>

        </div>

        <!-- Footer -->
        <div class="p-6 border-t border-rose-900/20 bg-[#0a101b] flex justify-end gap-3">
            <button @click="cancel" class="px-4 py-2 text-white/50 hover:text-white transition-colors font-medium">
                Cancelar
            </button>
            <button 
                @click="confirmMigration" 
                :disabled="!targetRubroId || processing"
                class="px-6 py-2 bg-gradient-to-r from-amber-600 to-rose-600 text-white rounded font-bold shadow-lg shadow-rose-900/50 disabled:opacity-50 disabled:cursor-not-allowed hover:from-amber-500 hover:to-rose-500 transition-all"
            >
                <span v-if="processing"><i class="fas fa-spinner fa-spin mr-2"></i>Migrando...</span>
                <span v-else>Migrar y Dar de Baja</span>
            </button>
        </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import rubrosApi from '../../../services/rubrosApi.js' // Check path context
import { useNotificationStore } from '../../../stores/notification'

const props = defineProps({
    show: Boolean,
    sourceRubro: Object,
    allRubros: Array // Passed from parent to avoid refetching
})

const emit = defineEmits(['close', 'success', 'create-new'])
const notificationStore = useNotificationStore()

const dependencies = ref({
    rubros_hijos: [],
    productos: [],
    cantidad_hijos: 0,
    cantidad_productos: 0
})
const loadingDeps = ref(false)
const processing = ref(false)
const targetRubroId = ref(null)

const availableTargets = computed(() => {
    if (!props.allRubros || !props.sourceRubro) return []
    // Exclude self and self-descendants (simple check: id != source.id)
    // Full recursion check handled by backend, but we can filter obvious self.
    return props.allRubros.filter(r => r.id !== props.sourceRubro.id && r.activo)
})

const fetchDeps = async () => {
    if (!props.sourceRubro) return
    loadingDeps.value = true
    try {
        // Need to ensure rubrosApi has this new method or call generic axios
        // assuming rubrosApi is just the object from services/rubrosApi.js which uses 'api' instance
        // We might need to extend services/rubrosApi.js first or use raw api call.
        // Let's assume we extended it or will mock it here? 
        // Better: Expect parent to pass deps? No, wizard should fetch.
        // I'll assume I update rubrosApi.js next.
        const { data } = await rubrosApi.getDependencies(props.sourceRubro.id)
        dependencies.value = data
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al analizar dependencias', 'error')
    } finally {
        loadingDeps.value = false
    }
}

watch(() => props.show, (val) => {
    if (val && props.sourceRubro) {
        targetRubroId.value = null
        fetchDeps()
    }
})

const confirmMigration = async () => {
    if (!targetRubroId.value) return
    if (!confirm(`¿Confirma mover todo a "${availableTargets.value.find(r => r.id === targetRubroId.value)?.nombre}" y desactivar "${props.sourceRubro.nombre}"?`)) return

    processing.value = true
    try {
        await rubrosApi.migrateAndDelete(props.sourceRubro.id, {
            target_rubro_id: targetRubroId.value,
            new_status: false
        })
        notificationStore.add('Migración completada y rubro desactivado', 'success')
        emit('success')
        emit('close')
    } catch (e) {
        console.error(e)
        const msg = e.response?.data?.detail || 'Error en la migración'
        notificationStore.add(msg, 'error')
    } finally {
        processing.value = false
    }
}

const cancel = () => {
    emit('close')
}
</script>
