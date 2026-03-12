<template>
    <div class="absolute top-full left-0 mt-2 w-72 bg-[#0f172a] border border-cyan-500/30 rounded-xl shadow-[0_0_30px_rgba(0,0,0,0.5)] overflow-hidden z-[60] backdrop-blur-xl animate-in fade-in slide-in-from-top-2 duration-200">
        <!-- Header -->
        <div class="px-4 py-2 border-b border-cyan-500/20 bg-cyan-950/30 flex justify-between items-center">
            <div class="flex items-center gap-2">
                <span class="text-[10px] font-bold text-cyan-400 uppercase tracking-widest"><i class="fas fa-address-book mr-1"></i> Agenda Rápida</span>
                <button 
                    @click="handleSync" 
                    class="text-[9px] text-cyan-500/50 hover:text-white transition-colors" 
                    title="Sincronizar con Google (Simulación)"
                    :disabled="isSyncing"
                >
                    <i class="fab fa-google" :class="isSyncing ? 'fa-spin' : ''"></i>
                </button>
            </div>
            <div class="text-[9px] text-cyan-500/50">{{ contactos.length }} Vínculos</div>
        </div>

        <!-- List -->
        <div class="max-h-[300px] overflow-y-auto scrollbar-thin scrollbar-thumb-cyan-500/20">
            <div v-if="contactos.length === 0" class="p-6 text-center">
                <p class="text-[10px] text-white/30 italic">Sin contactos vinculados</p>
            </div>
            
            <div v-else class="divide-y divide-white/5">
                <div v-for="contact in contactos" :key="contact.id" class="p-3 hover:bg-white/5 transition-colors group">
                    <div class="flex items-center gap-3 mb-2">
                         <div class="h-6 w-6 rounded-full bg-gradient-to-br from-cyan-600 to-blue-600 flex items-center justify-center text-[9px] font-bold text-white shadow-sm shrink-0">
                            {{ getInitials(contact.nombre) }}
                        </div>
                        <div class="min-w-0 flex-1">
                            <p class="text-xs font-bold text-white truncate">{{ contact.nombre }}</p>
                            <p class="text-[9px] text-cyan-500/70 truncate">{{ contact.rol || 'Sin Rol' }}</p>
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="grid grid-cols-2 gap-2 mt-1">
                        <!-- Phone -->
                        <div v-if="contact.telefono || contact.celular" 
                             @click="copyToClipboard(contact.telefono || contact.celular, 'Teléfono')"
                             class="flex items-center gap-2 px-2 py-1 bg-black/20 rounded cursor-pointer hover:bg-green-900/20 hover:text-green-400 transition-colors text-white/40 group/action"
                        >
                            <i class="fas fa-phone text-[9px]"></i>
                            <span class="text-[10px] font-mono truncate select-all">{{ contact.telefono || contact.celular }}</span>
                            <i class="fas fa-copy text-[8px] ml-auto opacity-0 group-hover/action:opacity-100"></i>
                        </div>
                        
                        <!-- Email -->
                        <div v-if="contact.email" 
                             @click="copyToClipboard(contact.email, 'Email')"
                             class="flex items-center gap-2 px-2 py-1 bg-black/20 rounded cursor-pointer hover:bg-blue-900/20 hover:text-blue-400 transition-colors text-white/40 group/action"
                        >
                            <i class="fas fa-envelope text-[9px]"></i>
                            <span class="text-[10px] font-mono truncate select-all">{{ contact.email }}</span>
                            <i class="fas fa-copy text-[8px] ml-auto opacity-0 group-hover/action:opacity-100"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="bg-black/40 border-t border-white/5 p-2 flex justify-center">
            <button @click="$emit('manager')" class="text-[9px] font-bold text-cyan-500/50 hover:text-cyan-400 uppercase tracking-wider transition-colors">
                Gestionar Vínculos <i class="fas fa-arrow-right ml-1"></i>
            </button>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue' // Import ref
import { useNotificationStore } from '../../../stores/notification'
import axios from 'axios' // Direct axios or use service

const props = defineProps({
    contactos: {
        type: Array,
        default: () => []
    }
})

const emit = defineEmits(['manager'])
const notificationStore = useNotificationStore()
const isSyncing = ref(false)

const handleSync = async () => {
    isSyncing.value = true
    try {
        const res = await axios.post('/agenda/google/sync')
        notificationStore.add(res.data.message, 'info')
    } catch (e) {
        console.error(e)
        notificationStore.add('Error en sincronización simulada', 'error')
    } finally {
        isSyncing.value = false
    }
}

const getInitials = (name) => {
    if (!name) return 'NN'
    return name.substring(0, 2).toUpperCase()
}

const copyToClipboard = (text, label) => {
    if (!text) return
    navigator.clipboard.writeText(text)
    notificationStore.add(`${label} copiado al portapapeles`, 'info') // Simple feedback
}
</script>
