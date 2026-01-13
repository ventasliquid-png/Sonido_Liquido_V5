<template>
    <div class="p-6 flex flex-col h-full min-w-[20rem] text-gray-200">
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-bold text-white">
                {{ isNew ? 'Nuevo Contacto' : 'Editar Contacto' }}
            </h2>
            <button @click="$emit('close')" class="text-white/40 hover:text-white transition-colors">
                <i class="fas fa-times"></i>
            </button>
        </div>

        <div class="space-y-4 flex-1 overflow-y-auto">
            <!-- Active Toggle -->
            <div class="flex items-center justify-between bg-white/5 p-3 rounded-lg border border-white/10">
                <span class="text-sm font-bold text-white">Estado</span>
                <div class="flex items-center gap-2">
                    <span class="text-[10px] font-bold uppercase" :class="localPersona.activo ? 'text-green-400' : 'text-red-400'">
                        {{ localPersona.activo ? 'ACTIVO' : 'INACTIVO' }}
                    </span>
                    <button 
                        @click="toggleActive"
                        class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none"
                        :class="localPersona.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                    >
                        <span 
                            class="inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform shadow-sm"
                            :class="localPersona.activo ? 'translate-x-4.5' : 'translate-x-1'"
                        />
                    </button>
                </div>
            </div>

            <div>
                <label class="block text-xs font-bold uppercase text-white/40 mb-1">Nombre Completo *</label>
                <input v-model="localPersona.nombre_completo" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-pink-400 outline-none transition-colors" placeholder="Ej: Juan Perez" />
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold uppercase text-white/40 mb-1">Email Personal</label>
                    <input v-model="localPersona.email_personal" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-pink-400 outline-none transition-colors" placeholder="juan@example.com" />
                </div>
                <div>
                    <label class="block text-xs font-bold uppercase text-white/40 mb-1">Celular Personal</label>
                    <input v-model="localPersona.celular_personal" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-pink-400 outline-none transition-colors" placeholder="+54 9 11..." />
                </div>
            </div>

            <div>
                <label class="block text-xs font-bold uppercase text-white/40 mb-1">Observaciones</label>
                <textarea v-model="localPersona.observaciones" rows="3" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-pink-400 outline-none transition-colors resize-none" placeholder="Gustos, cumpleaños, etc..."></textarea>
            </div>
        </div>

        <div class="pt-6 mt-6 border-t border-white/10 flex gap-3">
            <button @click="save" class="flex-1 bg-pink-600 hover:bg-pink-500 text-white py-2 rounded font-bold transition-colors shadow-lg shadow-pink-900/20">
                <span v-if="saving"><i class="fas fa-spinner fa-spin mr-2"></i>Guardando...</span>
                <span v-else>Guardar (F10)</span>
            </button>
            <button v-if="!isNew" @click="remove" class="px-3 bg-red-900/20 hover:bg-red-900/40 text-red-400 rounded border border-red-500/30 transition-colors" title="Dar de baja">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { useAgendaStore } from '../../../stores/agenda'
import { useNotificationStore } from '../../../stores/notification'

const props = defineProps({
    persona: {
        type: Object,
        default: null
    }
})

const emit = defineEmits(['close', 'saved'])

const agendaStore = useAgendaStore()
const notificationStore = useNotificationStore()
const saving = ref(false)

const localPersona = ref({
    id: null,
    nombre_completo: '',
    email_personal: '',
    celular_personal: '',
    observaciones: '',
    activo: true,
    vinculos: []
})

const isNew = computed(() => !props.persona || !props.persona.id)

watch(() => props.persona, (newVal) => {
    if (newVal) {
        localPersona.value = JSON.parse(JSON.stringify(newVal))
    } else {
        // Reset for new
        localPersona.value = {
            id: null,
            nombre_completo: '',
            email_personal: '',
            celular_personal: '',
            observaciones: '',
            activo: true,
            vinculos: []
        }
    }
}, { immediate: true })

const toggleActive = () => {
    if (localPersona.value.activo) {
        // If active, use the remove routine (Tachito) which confirms, saves, and closes
        remove()
    } else {
        // If inactive, just toggle local state (user must save)
        localPersona.value.activo = true
    }
}

const save = async () => {
    if (!localPersona.value.nombre_completo) {
        notificationStore.add('El nombre es obligatorio', 'error')
        return
    }

    saving.value = true
    try {
        if (isNew.value) {
            await agendaStore.createPersona(localPersona.value)
        } else {
            await agendaStore.updatePersona(localPersona.value.id, localPersona.value)
        }
        emit('saved')
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al guardar contacto', 'error')
    } finally {
        saving.value = false
    }
}

const remove = async () => {
    if (!confirm('¿Seguro que desea dar de baja este contacto?')) return
    try {
        await agendaStore.updatePersona(localPersona.value.id, { activo: false })
        emit('saved')
        emit('close')
    } catch (e) {
        notificationStore.add('Error al dar de baja', 'error')
    }
}

const handleKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault()
        save()
    }
}

onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})
</script>
