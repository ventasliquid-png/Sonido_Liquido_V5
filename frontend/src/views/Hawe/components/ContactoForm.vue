<template>
    <div v-if="show" class="fixed inset-0 z-[70] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
        <div class="bg-[#0a253a] border border-white/10 rounded-xl w-full max-w-md shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <!-- Header -->
            <div class="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-black/20">
                <h3 class="text-lg font-bold text-white">
                    {{ isEditing ? 'Editar Contacto' : 'Nuevo Contacto' }}
                </h3>
                <button @click="$emit('close')" class="text-white/50 hover:text-white transition-colors">
                    <i class="fa-solid fa-times text-xl"></i>
                </button>
            </div>

            <!-- Body -->
            <div class="p-6 overflow-y-auto space-y-6 scrollbar-thin scrollbar-thumb-white/10">
                
                <!-- Persona Section -->
                <div class="space-y-4">
                    <h4 class="text-xs font-bold uppercase text-cyan-400 border-b border-cyan-500/30 pb-1 mb-2">Datos Personales</h4>
                    
                    <div>
                        <label class="block text-xs font-bold uppercase text-white/40 mb-1">Nombre Completo *</label>
                        <input 
                            v-model="form.persona.nombre_completo" 
                            type="text" 
                            class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none transition-colors"
                            placeholder="Juan Pérez"
                            :disabled="isEditing" 
                        />
                        <p v-if="isEditing" class="text-[10px] text-white/30 mt-1">El nombre de la persona no se edita desde aquí.</p>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold uppercase text-white/40 mb-1">Celular Personal</label>
                            <input v-model="form.persona.celular_personal" type="text" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none transition-colors" placeholder="+54 9..." />
                        </div>
                        <div>
                            <label class="block text-xs font-bold uppercase text-white/40 mb-1">Email Personal</label>
                            <input v-model="form.persona.email_personal" type="email" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none transition-colors" placeholder="personal@gmail.com" />
                        </div>
                    </div>
                </div>

                <!-- Vinculo Section -->
                <div class="space-y-4">
                    <h4 class="text-xs font-bold uppercase text-cyan-400 border-b border-cyan-500/30 pb-1 mb-2">Datos Laborales</h4>
                    
                    <div>
                        <label class="block text-xs font-bold uppercase text-white/40 mb-1">Rol / Tipo *</label>
                        <select v-model="form.vinculo.tipo_contacto_id" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none appearance-none [&>option]:bg-slate-900">
                            <option :value="null">Seleccionar Rol...</option>
                            <option v-for="tipo in tiposContacto" :key="tipo.id" :value="tipo.id">{{ tipo.nombre }}</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold uppercase text-white/40 mb-1">Email Laboral</label>
                        <input v-model="form.vinculo.email_laboral" type="email" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none transition-colors" placeholder="trabajo@empresa.com" />
                    </div>

                    <div>
                        <label class="block text-xs font-bold uppercase text-white/40 mb-1">Teléfono Escritorio</label>
                        <input v-model="form.vinculo.telefono_escritorio" type="text" class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none transition-colors" placeholder="Interno 123..." />
                    </div>

                    <div class="flex items-center gap-2 pt-2">
                        <input type="checkbox" v-model="form.vinculo.es_principal" id="principalCheck" class="accent-cyan-500 h-4 w-4" />
                        <label for="principalCheck" class="text-sm text-white cursor-pointer select-none">Contacto Principal</label>
                    </div>
                </div>

            </div>

            <!-- Footer -->
            <div class="p-4 border-t border-white/10 bg-black/20 flex justify-end gap-3">
                <button @click="$emit('close')" class="px-4 py-2 text-white/50 hover:text-white transition-colors text-sm font-bold">Cancelar</button>
                <button 
                    @click="save" 
                    class="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg font-bold shadow-lg shadow-cyan-900/20 transition-all flex items-center gap-2"
                    :disabled="saving"
                >
                    <i v-if="saving" class="fa-solid fa-spinner fa-spin"></i>
                    <span>{{ saving ? 'Guardando...' : 'Guardar' }}</span>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMaestrosStore } from '../../../stores/maestros'
import { useAgendaStore } from '../../../stores/agenda'
import { useClientesStore } from '../../../stores/clientes'
import { useNotificationStore } from '../../../stores/notification'

const props = defineProps({
    show: Boolean,
    clienteId: {
        type: String,
        required: true
    },
    contacto: {
        type: Object,
        default: null
    }
})

const emit = defineEmits(['close', 'saved'])

const maestrosStore = useMaestrosStore()
const agendaStore = useAgendaStore()
const clientesStore = useClientesStore()
const notificationStore = useNotificationStore()

const tiposContacto = computed(() => maestrosStore.tiposContacto)
const saving = ref(false)

const form = ref({
    persona: {
        id: null,
        nombre_completo: '',
        celular_personal: '',
        email_personal: ''
    },
    vinculo: {
        id: null,
        tipo_contacto_id: null,
        email_laboral: '',
        telefono_escritorio: '',
        es_principal: false
    }
})

const isEditing = computed(() => !!props.contacto)

onMounted(() => {
    maestrosStore.fetchTiposContacto()
})

watch(() => props.show, (val) => {
    if (val) {
        resetForm()
        if (props.contacto) {
            loadContacto(props.contacto)
        }
    }
})

const resetForm = () => {
    form.value = {
        persona: {
            id: null,
            nombre_completo: '',
            celular_personal: '',
            email_personal: ''
        },
        vinculo: {
            id: null,
            tipo_contacto_id: null,
            email_laboral: '',
            telefono_escritorio: '',
            es_principal: false
        }
    }
}

const loadContacto = (c) => {
    // Map existing contact data
    // c is a VinculoComercial object with nested persona
    form.value.vinculo = {
        id: c.id,
        tipo_contacto_id: c.tipo_contacto_id,
        email_laboral: c.email_laboral,
        telefono_escritorio: c.telefono_escritorio,
        es_principal: c.es_principal
    }
    
    if (c.persona) {
        form.value.persona = {
            id: c.persona.id,
            nombre_completo: c.persona.nombre_completo,
            celular_personal: c.persona.celular_personal,
            email_personal: c.persona.email_personal
        }
    }
}

const save = async () => {
    if (!form.value.persona.nombre_completo && !isEditing.value) {
        notificationStore.add('El nombre es obligatorio', 'error')
        return
    }
    if (!form.value.vinculo.tipo_contacto_id) {
        notificationStore.add('El rol es obligatorio', 'error')
        return
    }

    saving.value = true
    try {
        let personaId = form.value.persona.id

        // 1. Create/Update Persona
        if (!isEditing.value) {
            // Create new persona
            const newPersona = await agendaStore.createPersona(form.value.persona)
            personaId = newPersona.id
        } else {
            // Update persona details (optional, maybe we only update vinculo?)
            // For now, let's update persona too if fields changed
            await agendaStore.updatePersona(personaId, form.value.persona)
        }

        // 2. Create/Update Vinculo
        const vinculoData = {
            ...form.value.vinculo,
            cliente_id: props.clienteId,
            persona_id: personaId
        }

        if (!isEditing.value) {
            await clientesStore.createVinculo(props.clienteId, vinculoData)
            notificationStore.add('Contacto creado', 'success')
        } else {
            await clientesStore.updateVinculo(props.clienteId, form.value.vinculo.id, vinculoData)
            notificationStore.add('Contacto actualizado', 'success')
        }

        emit('saved')
        emit('close')
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al guardar contacto', 'error')
    } finally {
        saving.value = false
    }
}
</script>
