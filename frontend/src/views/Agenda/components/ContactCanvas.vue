<template>
    <div class="fixed inset-y-0 right-0 w-[600px] bg-[#1e1e1e] border-l border-white/10 shadow-2xl z-50 flex flex-col font-sans">
        <!-- Header Actions -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[#1e1e1e] shrink-0">
             <div class="flex items-center gap-4">
                <button @click="$emit('close')" class="text-white/50 hover:text-white transition-colors">
                    <i class="fa-solid fa-times text-lg"></i>
                </button>
                <h2 class="text-lg font-semibold text-white">
                    {{ isNew ? 'Nuevo Contacto' : 'Editar Contacto' }}
                </h2>
            </div>
            <div class="flex items-center gap-3">
                 <button 
                    v-if="!isNew"
                    @click="deleteContacto"
                    class="h-9 w-9 rounded-full flex items-center justify-center text-red-400 hover:bg-red-500/10 transition-colors"
                    title="Eliminar contacto"
                >
                    <i class="fa-regular fa-trash-can"></i>
                </button>
                <button 
                    @click="save"
                    :disabled="saving"
                    class="h-9 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2"
                >
                    <span v-if="saving" class="animate-spin h-4 w-4 border-2 border-white/30 border-t-white rounded-full"></span>
                    <span>{{ saving ? 'Guardando...' : 'Guardar' }}</span>
                </button>
            </div>
        </div>

        <!-- Scrollable Content -->
        <div class="flex-1 overflow-y-auto p-8 custom-scrollbar">
            
            <!-- Identity Header (Avatar + Name) -->
            <div class="flex flex-col items-center mb-8">
                 <div class="relative group">
                    <div class="h-24 w-24 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-3xl font-bold text-white shadow-2xl border-4 border-[#1e1e1e] cursor-pointer">
                        {{ initials }}
                    </div>
                     <!-- Camera Icon Overlay -->
                    <div class="absolute inset-0 flex items-center justify-center bg-black/50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                        <i class="fa-solid fa-camera text-white"></i>
                    </div>
                </div>
                
                <div class="mt-6 w-full max-w-sm flex flex-col gap-3">
                    <div class="grid grid-cols-2 gap-3">
                        <div class="relative">
                            <i class="fa-regular fa-user absolute left-3 top-1/2 -translate-y-1/2 text-white/30"></i>
                            <input 
                                v-model="form.nombre"
                                type="text" 
                                placeholder="Nombre" 
                                class="w-full bg-white/5 border border-white/10 rounded-lg py-2 pl-10 pr-3 text-white focus:outline-none focus:border-indigo-500 transition-colors placeholder-white/20"
                            >
                        </div>
                        <div class="relative">
                             <input 
                                v-model="form.apellido"
                                type="text" 
                                placeholder="Apellido" 
                                class="w-full bg-white/5 border border-white/10 rounded-lg py-2 px-3 text-white focus:outline-none focus:border-indigo-500 transition-colors placeholder-white/20"
                            >
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sections -->
            <div class="space-y-8">
                
                <!-- 1. Datos Laborales -->
                <section>
                    <h3 class="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-4 border-b border-indigo-500/20 pb-2">
                        Contexto Laboral
                    </h3>
                    <div class="grid grid-cols-1 gap-4">
                        <!-- Puesto -->
                        <div class="relative">
                             <label class="block text-xs text-white/40 mb-1 ml-1">Puesto / Cargo</label>
                             <div class="relative">
                                <i class="fa-solid fa-briefcase absolute left-3 top-1/2 -translate-y-1/2 text-white/30"></i>
                                <input 
                                    v-model="form.puesto"
                                    type="text" 
                                    placeholder="Ej: Gerente de Compras" 
                                    class="w-full bg-white/5 border border-white/10 rounded-lg py-2 pl-10 pr-3 text-white focus:outline-none focus:border-indigo-500 transition-colors"
                                >
                            </div>
                        </div>

                         <!-- Empresa Selector (Cliente o Transporte) -->
                         <div>
                            <label class="block text-xs text-white/40 mb-1 ml-1">Organización</label>
                             <div class="grid grid-cols-2 gap-2 mb-2">
                                <button 
                                    @click="empresaType = 'CLIENTE'"
                                    class="py-1.5 rounded border text-xs font-medium transition-colors"
                                    :class="empresaType === 'CLIENTE' ? 'bg-blue-600/20 border-blue-500 text-blue-400' : 'bg-white/5 border-white/5 text-white/30 hover:bg-white/10'"
                                >
                                    <i class="fa-solid fa-building mr-1"></i> Cliente
                                </button>
                                <button 
                                    @click="empresaType = 'TRANSPORTE'"
                                    class="py-1.5 rounded border text-xs font-medium transition-colors"
                                    :class="empresaType === 'TRANSPORTE' ? 'bg-amber-600/20 border-amber-500 text-amber-400' : 'bg-white/5 border-white/5 text-white/30 hover:bg-white/10'"
                                >
                                    <i class="fa-solid fa-truck mr-1"></i> Transporte
                                </button>
                            </div>

                            <select 
                                v-if="empresaType === 'CLIENTE'"
                                v-model="form.cliente_id"
                                class="w-full bg-white/5 border border-white/10 text-white rounded-lg p-2.5 focus:border-blue-500 focus:outline-none"
                            >
                                <option :value="null">-- Seleccionar Cliente --</option>
                                <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.razon_social }}</option>
                            </select>

                            <select 
                                v-if="empresaType === 'TRANSPORTE'"
                                v-model="form.transporte_id"
                                class="w-full bg-white/5 border border-white/10 text-white rounded-lg p-2.5 focus:border-amber-500 focus:outline-none"
                            >
                                <option :value="null">-- Seleccionar Transporte --</option>
                                <option v-for="t in transportes" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                            </select>
                         </div>

                         <!-- Roles (Tags) -->
                         <div>
                            <label class="block text-xs text-white/40 mb-2 ml-1">Roles / Etiquetas</label>
                            <div class="flex flex-wrap gap-2 mb-2">
                                <span v-for="rol in form.roles" :key="rol" class="px-2 py-1 rounded bg-indigo-500/20 text-indigo-300 text-xs border border-indigo-500/30 flex items-center gap-1">
                                    {{ rol }}
                                    <button @click="removeRole(rol)" class="hover:text-white"><i class="fa-solid fa-times"></i></button>
                                </span>
                            </div>
                            <div class="flex gap-2">
                                <input 
                                    v-model="newRole"
                                    @keydown.enter.prevent="addRole"
                                    type="text" 
                                    placeholder="Agregar rol (Enter)..." 
                                    class="flex-1 bg-white/5 border border-white/10 rounded-lg py-1.5 px-3 text-sm text-white focus:outline-none focus:border-indigo-500"
                                >
                                <button @click="addRole" class="text-white/50 hover:text-indigo-400"><i class="fa-solid fa-plus-circle text-lg"></i></button>
                            </div>
                         </div>
                    </div>
                </section>

                <!-- 2. Omnicanal -->
                <section>
                    <h3 class="text-xs font-bold text-green-400 uppercase tracking-wider mb-4 border-b border-green-500/20 pb-2">
                        Canales de Contacto
                    </h3>
                    <div class="space-y-3">
                         <div v-for="(canal, index) in form.canales" :key="index" class="flex items-center gap-2 group">
                            <!-- Tipo Selector Icon -->
                             <div class="relative">
                                <select 
                                    v-model="canal.tipo"
                                    class="w-8 h-8 opacity-0 absolute inset-0 cursor-pointer z-10"
                                >
                                    <option value="WHATSAPP">WHATSAPP</option>
                                    <option value="EMAIL">EMAIL</option>
                                    <option value="TELEFONO">TELEFONO</option>
                                </select>
                                <div class="w-8 h-8 rounded bg-white/5 border border-white/10 flex items-center justify-center text-white/70 group-hover:border-white/30">
                                    <i v-if="canal.tipo === 'WHATSAPP'" class="fa-brands fa-whatsapp text-green-400"></i>
                                    <i v-else-if="canal.tipo === 'EMAIL'" class="fa-regular fa-envelope text-blue-400"></i>
                                    <i v-else-if="canal.tipo === 'TELEFONO'" class="fa-solid fa-phone text-gray-400"></i>
                                </div>
                             </div>
                            
                            <!-- Valor -->
                             <input 
                                v-model="canal.valor"
                                type="text" 
                                class="flex-1 bg-transparent border-b border-white/10 py-1 text-white focus:outline-none focus:border-green-500 transition-colors"
                                :placeholder="canal.tipo === 'EMAIL' ? 'correo@ejemplo.com' : '+54 9 ...'"
                            >
                            
                            <!-- Etiqueta -->
                             <input 
                                v-model="canal.etiqueta"
                                type="text" 
                                placeholder="Etiqueta (opcional)"
                                class="w-24 bg-transparent border-b border-white/10 py-1 text-xs text-white/50 focus:outline-none focus:text-white transition-colors text-right"
                            >

                             <button @click="removeCanal(index)" class="text-white/20 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                <i class="fa-solid fa-times"></i>
                            </button>
                         </div>

                         <button @click="addCanal" class="text-xs text-green-400 hover:text-green-300 font-medium flex items-center gap-1 mt-2">
                            <i class="fa-solid fa-plus"></i> Agregar Canal
                         </button>
                    </div>
                </section>

                <!-- 3. Inteligencia -->
                <section>
                    <h3 class="text-xs font-bold text-amber-400 uppercase tracking-wider mb-4 border-b border-amber-500/20 pb-2">
                        Inteligencia & Notas
                    </h3>
                    <div class="space-y-4">
                         <div>
                            <label class="block text-xs text-white/40 mb-1 ml-1">Referencia de Origen</label>
                            <input 
                                v-model="form.referencia_origen"
                                type="text" 
                                placeholder="¿Cómo llegó a nosotros?" 
                                class="w-full bg-white/5 border border-white/10 rounded-lg py-2 px-3 text-white focus:outline-none focus:border-amber-500 transition-colors text-sm"
                            >
                        </div>
                        <div>
                            <label class="block text-xs text-white/40 mb-1 ml-1">Notas Privadas</label>
                            <textarea 
                                v-model="form.notas"
                                rows="4"
                                placeholder="Escribe aquí cualquier detalle relevante..."
                                class="w-full bg-white/5 border border-white/10 rounded-lg py-2 px-3 text-white focus:outline-none focus:border-amber-500 transition-colors text-sm resize-none"
                            ></textarea>
                        </div>
                    </div>
                </section>

            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useContactosStore } from '../../../stores/contactos'
import { useClientesStore } from '../../../stores/clientes'
import { useLogisticaStore } from '../../../stores/logistica'
import { useNotificationStore } from '../../../stores/notification'

const props = defineProps({
    contactoId: { type: [String, Number], default: null },
    initialData: { type: Object, default: null }
})

const emit = defineEmits(['close', 'save'])

const contactosStore = useContactosStore()
const clientesStore = useClientesStore()
const logisticaStore = useLogisticaStore()
const notificationStore = useNotificationStore()

const saving = ref(false)
const isNew = computed(() => props.contactoId === 'new')

const empresaType = ref('CLIENTE') // 'CLIENTE' or 'TRANSPORTE'
const newRole = ref('')

// Form State
const form = ref({
    nombre: '',
    apellido: '',
    puesto: '',
    cliente_id: null,
    transporte_id: null,
    referencia_origen: '',
    domicilio_personal: '',
    roles: [],
    canales: [], // [{ tipo: 'WHATSAPP', valor: '', etiqueta: '' }]
    notas: '',
    estado: true
})

// Options
const clientes = computed(() => clientesStore.clientes)
const transportes = computed(() => logisticaStore.empresas)

const initials = computed(() => {
    if (!form.value.nombre) return '?'
    return (form.value.nombre[0] + (form.value.apellido ? form.value.apellido[0] : '')).toUpperCase()
})

onMounted(async () => {
    // Load Dependencies
    if (clientesStore.clientes.length === 0) await clientesStore.fetchClientes()
    if (logisticaStore.empresas.length === 0) await logisticaStore.fetchEmpresas()

    // Init Form
    if (!isNew.value && props.initialData) {
        form.value = JSON.parse(JSON.stringify(props.initialData))
        // Determine Context
        if (form.value.transporte_id) empresaType.value = 'TRANSPORTE'
        else empresaType.value = 'CLIENTE'
        
        // Ensure arrays
        if (!form.value.roles) form.value.roles = []
        if (!form.value.canales) form.value.canales = []
    } else {
        // Defaults
        form.value.canales.push({ tipo: 'WHATSAPP', valor: '', etiqueta: 'Personal' })
    }
})

// Actions
const addRole = () => {
    if (newRole.value && !form.value.roles.includes(newRole.value.toUpperCase())) {
        form.value.roles.push(newRole.value.toUpperCase())
        newRole.value = ''
    }
}
const removeRole = (rol) => {
    form.value.roles = form.value.roles.filter(r => r !== rol)
}

const addCanal = () => {
    form.value.canales.push({ tipo: 'WHATSAPP', valor: '', etiqueta: '' })
}
const removeCanal = (index) => {
    form.value.canales.splice(index, 1)
}

const save = async () => {
    // Validation
    if (!form.value.nombre || !form.value.apellido) {
        notificationStore.add('Nombre y Apellido son obligatorios', 'warning')
        return
    }

    saving.value = true
    try {
        // Cleanup IDs based on type
        if (empresaType.value === 'CLIENTE') form.value.transporte_id = null
        else form.value.cliente_id = null

        if (isNew.value) {
            await contactosStore.createContacto(form.value)
        } else {
            await contactosStore.updateContacto(props.contactoId, form.value)
        }
        emit('save')
    } catch (e) {
        // Error handled in store
    } finally {
        saving.value = false
    }
}

const deleteContacto = async () => {
    if (!confirm('¿Eliminar este contacto?')) return
    try {
        await contactosStore.deleteContacto(props.contactoId)
        emit('save')
    } catch (e) {}
}
</script>

<style scoped>
/* Custom Scrollbar for Dark Mode */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #111;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
