<template>
    <div class="fixed inset-y-0 right-0 w-[700px] bg-[#1a1a1a] border-l border-white/10 shadow-2xl z-50 flex flex-col font-sans">
        
        <!-- HEADER ACTIONS -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[#1a1a1a] shrink-0 z-20">
            <div class="flex items-center gap-4">
                <button @click="$emit('close')" class="text-white/40 hover:text-white transition-colors">
                    <i class="fa-solid fa-times text-lg"></i>
                </button>
                <div>
                    <h2 class="text-lg font-bold text-white leading-tight">
                        {{ isNew ? 'Nueva Persona' : form.nombre + ' ' + form.apellido }}
                    </h2>
                    <p class="text-xs text-white/30 uppercase tracking-wider font-medium">
                        {{ isNew ? 'Creación de Identidad' : 'Gestión de Vínculos' }}
                    </p>
                </div>
            </div>
            <div class="flex items-center gap-3">
                 <button 
                    v-if="!isNew"
                    @click="deleteContacto"
                    class="h-9 w-9 rounded-full flex items-center justify-center text-red-400 hover:bg-red-500/10 transition-colors"
                    title="Eliminar Persona"
                >
                    <i class="fa-regular fa-trash-can"></i>
                </button>
                <button 
                    @click="savePersona"
                    :disabled="saving"
                    class="h-9 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2"
                >
                    <span v-if="saving" class="animate-spin h-4 w-4 border-2 border-white/30 border-t-white rounded-full"></span>
                    <span>{{ saving ? 'Guardando...' : 'Guardar Cambios' }}</span>
                </button>
            </div>
        </div>

        <!-- SCROLLABLE BODY -->
        <div class="flex-1 overflow-y-auto custom-scrollbar p-8 pb-32 space-y-10">

            <!-- SECCIÓN 1: IDENTIDAD (Panel Superior) -->
            <section class="bg-[#252525] rounded-2xl p-6 border border-white/5 relative overflow-hidden group">
                <!-- Decorative Background -->
                <div class="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

                <div class="flex gap-6 relative z-10">
                    <!-- Avatar -->
                    <div class="shrink-0">
                         <div class="h-24 w-24 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-3xl font-bold text-white shadow-xl border-4 border-[#252525] cursor-pointer hover:scale-105 transition-transform">
                            {{ initials }}
                        </div>
                    </div>

                    <!-- Datos Principales -->
                    <div class="flex-1 space-y-4">
                        <div class="grid grid-cols-2 gap-4 relative">
                            <!-- NOMBRE (Con Typeahead) -->
                            <div class="relative">
                                <label class="text-xs font-bold text-indigo-400 uppercase mb-1 block flex justify-between">
                                    Nombre
                                    <span v-if="isSearching" class="text-xs text-indigo-300 animate-pulse">Buscando...</span>
                                </label>
                                <div class="relative">
                                    <input 
                                        v-model="form.nombre" 
                                        type="text" 
                                        :readonly="personaExistenteSeleccionada"
                                        class="w-full bg-black/20 border rounded-lg px-3 py-2 text-white placeholder-white/20 focus:outline-none transition-colors"
                                        :class="personaExistenteSeleccionada ? 'border-green-500/50 bg-green-500/10 text-green-100 cursor-not-allowed' : 'border-white/10 focus:border-indigo-500'"
                                        placeholder="Nombre de pila"
                                        autocomplete="off"
                                    >
                                    <!-- Botón Limpiar (Solo si seleccionado) -->
                                    <button 
                                        v-if="personaExistenteSeleccionada"
                                        @click="limpiarPersonaSeleccionada"
                                        class="absolute right-2 top-1/2 -translate-y-1/2 text-white/40 hover:text-white p-1 rounded-full hover:bg-white/10 transition-colors"
                                        title="Limpiar y crear nueva persona"
                                    >
                                        <i class="fa-solid fa-xmark"></i>
                                    </button>
                                </div>

                                <!-- DROPDOWN ESPEJISMO -->
                                <div v-if="sugerencias?.length > 0 && !personaExistenteSeleccionada" 
                                     class="absolute top-full left-0 right-0 mt-2 bg-[#1a1a1a] border border-indigo-500/30 rounded-lg shadow-2xl z-50 overflow-hidden ring-1 ring-black/5"
                                >
                                    <div class="px-3 py-2 bg-indigo-500/10 border-b border-indigo-500/20 text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-2">
                                        <i class="fa-solid fa-bolt text-yellow-400"></i> Coincidencias Detectadas
                                    </div>
                                    <ul class="max-h-60 overflow-y-auto custom-scrollbar">
                                        <li v-for="s in sugerencias" :key="s.id" 
                                            @click="seleccionarPersonaExistente(s)"
                                            class="px-4 py-3 hover:bg-indigo-600/20 cursor-pointer border-b border-white/5 last:border-0 group transition-colors"
                                        >
                                            <div class="flex items-center justify-between">
                                                <div>
                                                    <div class="font-bold text-white group-hover:text-indigo-200 transition-colors">
                                                        {{ s.nombre }} {{ s.apellido }}
                                                    </div>
                                                    <div class="text-xs text-white/40 flex flex-col gap-0.5 mt-1">
                                                        <span v-if="s.canales_personales?.length">
                                                            <i class="fa-brands fa-whatsapp w-4 text-center"></i> {{ s.canales_personales[0].valor }}
                                                        </span>
                                                        <span v-else class="italic">Sin contacto personal</span>
                                                    </div>
                                                </div>
                                                <span class="px-2 py-1 rounded text-[10px] font-bold bg-white/5 text-white/50 border border-white/10 group-hover:bg-indigo-500 group-hover:text-white group-hover:border-indigo-400 transition-all">
                                                    YA EXISTE
                                                </span>
                                            </div>
                                        </li>
                                    </ul>
                                </div>
                            </div>

                            <!-- APELLIDO -->
                            <div>
                                <label class="text-xs font-bold text-indigo-400 uppercase mb-1 block">Apellido</label>
                                <input 
                                    v-model="form.apellido" 
                                    type="text" 
                                    :readonly="personaExistenteSeleccionada"
                                    class="w-full bg-black/20 border rounded-lg px-3 py-2 text-white placeholder-white/20 focus:outline-none transition-colors"
                                    :class="personaExistenteSeleccionada ? 'border-green-500/50 bg-green-500/10 text-green-100 cursor-not-allowed' : 'border-white/10 focus:border-indigo-500'"
                                    placeholder="Apellido (Opcional)"
                                >
                            </div>
                        </div>

                        <!-- Contacto Personal -->
                        <div class="grid grid-cols-2 gap-4">
                             <div class="relative">
                                <i class="fa-brands fa-whatsapp absolute left-3 top-1/2 -translate-y-1/2 text-white/30"></i>
                                <input v-model="personalPhone" type="text" class="w-full bg-transparent border-b border-white/10 py-1 pl-8 text-sm text-white focus:border-green-500 focus:outline-none transition-colors" placeholder="+54 9 ...">
                            </div>
                            <div class="relative">
                                <i class="fa-regular fa-envelope absolute left-3 top-1/2 -translate-y-1/2 text-white/30"></i>
                                <input v-model="personalEmail" type="email" class="w-full bg-transparent border-b border-white/10 py-1 pl-8 text-sm text-white focus:border-blue-500 focus:outline-none transition-colors" placeholder="email@personal.com">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Contexto Social (Expandable or visible) -->
                <div class="mt-6 pt-6 border-t border-white/5 grid grid-cols-2 gap-6">
                    <div>
                        <label class="text-xs text-white/40 mb-1 block">Fecha de Nacimiento</label>
                         <input v-model="form.fecha_nacimiento" type="date" class="bg-black/20 border border-white/10 rounded px-2 py-1 text-sm text-white/80 focus:outline-none w-full">
                    </div>
                     <div>
                        <label class="text-xs text-white/40 mb-1 block">Notas Personales (Gustos, Familia)</label>
                        <textarea v-model="form.notas" rows="2" class="w-full bg-black/20 border border-white/10 rounded px-2 py-1 text-sm text-white/80 focus:outline-none resize-none" placeholder="Le gusta el café amargo..."></textarea>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN 2: BILLETERA DE VÍNCULOS -->
            <section>
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                        <i class="fa-solid fa-link text-indigo-400"></i> Vinculaciones Comerciales
                    </h3>
                    <button @click="showAddLink = !showAddLink" class="text-xs bg-white/5 hover:bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded transition-colors border border-white/5 hover:border-indigo-500/30">
                        + Nueva Vinculación
                    </button>
                </div>

                <!-- Modulo de Agregar Vínculo (Collapse) -->
                <div v-if="showAddLink" class="mb-6 bg-[#252525] rounded-xl p-4 border border-indigo-500/30 shadow-lg animate-in fade-in slide-in-from-top-2">
                    <h4 class="text-xs font-bold text-white mb-3">Vincular a nueva Organización</h4>
                    
                    <div class="flex gap-2 mb-3">
                         <div class="w-1/3 flex gap-2">
                             <select v-model="newLinkType" class="bg-black/20 border border-white/10 rounded px-2 text-xs text-white h-9 focus:outline-none w-1/2">
                                <option value="CLIENTE">CLIENTE</option>
                                <option value="TRANSPORTE">TRANSPORTE</option>
                            </select>
                            <!-- Role Selector -->
                             <select v-model="newLinkRole" class="bg-black/20 border border-white/10 rounded px-2 text-xs text-white h-9 focus:outline-none w-1/2 relative z-50" title="Seleccione Rol">
                                <option value="" disabled selected>Rol...</option>
                                <option v-for="t in tiposContacto" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                            </select>
                         </div>

                        <div class="relative flex-1">
                            <input 
                                v-model="newLinkSearch" 
                                type="text" 
                                class="w-full bg-black/20 border border-white/10 rounded h-9 px-3 text-sm text-white focus:outline-none focus:border-indigo-500"
                                :placeholder="newLinkType === 'CLIENTE' ? 'Buscar Cliente...' : 'Buscar Transporte...'"
                                @focus="newLinkDropdown = true"
                            >
                            <!-- Dropdown -->
                            <div v-if="newLinkDropdown && filteredEntities.length > 0" class="absolute top-full left-0 w-full mt-1 bg-[#303030] border border-white/10 rounded shadow-xl max-h-48 overflow-y-auto z-50">
                                <div 
                                    v-for="entity in filteredEntities" 
                                    :key="entity.id"
                                    @click="selectEntity(entity)"
                                    class="px-3 py-2 text-sm text-white hover:bg-indigo-600 cursor-pointer"
                                >
                                    {{ entity.razon_social || entity.nombre }}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="flex justify-end gap-2">
                        <button @click="showAddLink = false" class="text-xs text-white/50 hover:text-white px-3 py-1">Cancelar</button>
                        <button 
                            @click="confirmAddLink" 
                            :disabled="!selectedEntity || !newLinkRole"
                            class="text-xs bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-1.5 rounded disabled:opacity-50 font-medium"
                        >
                            Vincular
                        </button>
                    </div>
                </div>

                <!-- Lista de Cards -->
                <div class="space-y-4">
                    <div v-if="form.vinculos.length === 0" class="text-center py-8 border-2 border-dashed border-white/5 rounded-xl text-white/20 text-sm">
                        Esta persona no tiene vínculos comerciales activos.
                    </div>

                    <div 
                        v-for="link in form.vinculos" 
                        :key="link.id" 
                        class="bg-[#202020] rounded-xl border border-white/5 flex transition-all hover:border-white/10 group relative"
                    >
                        <!-- Color Bar -->
                        <div class="w-1.5 shrink-0 rounded-l-xl" :class="{
                            'bg-blue-500': link.entidad_tipo === 'CLIENTE',
                            'bg-amber-500': link.entidad_tipo === 'TRANSPORTE',
                            'bg-gray-500': !link.activo
                        }"></div>

                        <div class="flex-1 p-4">
                             <!-- Header Card -->
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <div class="text-xs font-bold opacity-60 mb-0.5" :class="link.entidad_tipo === 'CLIENTE' ? 'text-blue-400' : 'text-amber-400'">
                                        {{ link.entidad_tipo }}
                                    </div>
                                    <h4 class="text-white font-semibold text-lg leading-none">
                                        {{ getEntityName(link) }}
                                    </h4>
                                </div>
                                <div class="flex items-center gap-2">
                                    <!-- Status Switch -->
                                    <button 
                                        @click.stop="toggleLinkStatus(link)"
                                        class="w-8 h-4 rounded-full p-0.5 transition-colors duration-200 focus:outline-none"
                                        :class="link.activo ? 'bg-green-500/20' : 'bg-red-500/20'"
                                        title="Alternar estado Activo/Inactivo"
                                    >
                                        <div 
                                            class="w-3 h-3 rounded-full shadow-sm transform transition-transform duration-200"
                                            :class="[
                                                link.activo ? 'translate-x-4 bg-green-400' : 'translate-x-0 bg-red-400'
                                            ]"
                                        ></div>
                                    </button>
                                    
                                    <!-- Delete Action -->
                                    <button @click="removeLink(link)" class="text-white/10 hover:text-red-400 ml-2 transition-colors">
                                        <i class="fa-solid fa-unlink"></i>
                                    </button>
                                </div>
                            </div>

                            <!-- Inputs: Rol y Contacto -->
                            <div class="grid grid-cols-2 gap-4 mt-3">
                                <div>
                                    <label class="text-[10px] text-white/30 uppercase block mb-1">Rol / Puesto</label>
                                    <!-- EDITABLE ROLE SELECTOR -->
                                    <select 
                                        :value="link.tipo_contacto_id" 
                                        @change="updateLinkRole(link, $event.target.value)"
                                        class="bg-black/40 border border-white/10 rounded px-2 py-1 text-xs text-white/90 w-full focus:outline-none focus:border-indigo-500 appearance-none relative z-10"
                                    >
                                        <option value="" disabled>Seleccione...</option>
                                        <option v-for="t in tiposContacto" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                                    </select>
                                    <!-- Only show if EMPTY -->
                                    <div v-if="tiposContacto.length === 0" class="text-xs text-red-500">Sin roles cargados</div>
                                </div>
                                <div>
                                    <label class="text-[10px] text-white/30 uppercase block">Contacto Corp.</label>
                                     <div class="text-sm text-white/80 truncate">
                                        {{ getLaboralContact(link) }}
                                     </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useContactosStore } from '../../../stores/contactos'
import { useClientesStore } from '../../../stores/clientes'
import { useLogisticaStore } from '../../../stores/logistica'
import { useNotificationStore } from '../../../stores/notification'
import { useMaestrosStore } from '../../../stores/maestros' 
import debounce from 'lodash/debounce'  

const props = defineProps({
    contactoId: { type: [String, Number], default: null },
    initialData: { type: Object, default: null }
})

const emit = defineEmits(['close', 'save'])

const contactosStore = useContactosStore()
const clientesStore = useClientesStore()
const logisticaStore = useLogisticaStore()
const maestrosStore = useMaestrosStore() 
const notificationStore = useNotificationStore()

// Stores Data
const { clientes } = storeToRefs(clientesStore)
const { empresas: transportes } = storeToRefs(logisticaStore)
const { tiposContacto } = storeToRefs(maestrosStore) 

// State
const saving = ref(false)
const isNew = computed(() => props.contactoId === 'new')

// Form Identity
const form = ref({
    nombre: '',
    apellido: '',
    fecha_nacimiento: null,
    domicilio_personal: '',
    notas: '', // Mapped to notas_globales
    canales_personales: [], 
    vinculos: [] // Read-only list mostly
})

// Helpers for Personal Channels
const personalPhone = computed({
    get: () => form.value.canales_personales?.find(c => c.tipo === 'WHATSAPP')?.valor || '',
    set: (val) => updatePersonalChannel('WHATSAPP', val)
})

const personalEmail = computed({
    get: () => form.value.canales_personales?.find(c => c.tipo === 'EMAIL')?.valor || '',
    set: (val) => updatePersonalChannel('EMAIL', val)
})

const updatePersonalChannel = (type, value) => {
    const idx = form.value.canales_personales.findIndex(c => c.tipo === type)
    if (idx >= 0) {
        form.value.canales_personales[idx].valor = value
    } else {
        form.value.canales_personales.push({ tipo: type, valor: value, etiqueta: 'Personal' })
    }
}

// Add Link Logic
const showAddLink = ref(false)
const newLinkType = ref('CLIENTE')
const newLinkSearch = ref('')
const newLinkRole = ref('') // New: Stores ID of selected role
const newLinkDropdown = ref(false)
const selectedEntity = ref(null)

const filteredEntities = computed(() => {
    const query = newLinkSearch.value.toLowerCase()
    const list = newLinkType.value === 'CLIENTE' ? clientes.value : transportes.value
    if (!list) return []
    if (!query) return list.slice(0, 10)
    return list.filter(item => {
        const name = (item.razon_social || item.nombre || '').toLowerCase()
        return name.includes(query)
    }).slice(0, 10)
})

const selectEntity = (entity) => {
    selectedEntity.value = entity
    newLinkSearch.value = entity.razon_social || entity.nombre
    newLinkDropdown.value = false
}

// Shortcuts
const handleKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault()
        savePersona()
    }
    if (e.key === 'Escape') {
        emit('close')
    }
}

onMounted(async () => {
    window.addEventListener('keydown', handleKeydown)
    // Reload Stores
    if (clientes.value.length === 0) await clientesStore.fetchClientes()
    if (transportes.value.length === 0) await logisticaStore.fetchEmpresas()
    // Always fetch latest roles
    await maestrosStore.fetchTiposContacto() 

    if (!isNew.value && props.initialData) {
        // Map Props to Form
        const d = props.initialData
        form.value = {
            id: d.id || props.contactoId, 
            nombre: d.nombre || d.nombre_completo?.split(' ')[0],
            apellido: d.apellido || d.nombre_completo?.split(' ').slice(1).join(' '), 
            fecha_nacimiento: d.fecha_nacimiento ? d.fecha_nacimiento.split('T')[0] : null,
            domicilio_personal: d.domicilio_personal,
            notas: d.observaciones || d.notas_globales || d.notas,
            canales_personales: d.canales_personales || [],
            vinculos: d.vinculos || []
        }
        
        // Channels reconstruction (Legacy to Visual)
        if (d.celular_personal && !form.value.canales_personales.find(c => c.tipo === 'WHATSAPP')) {
            form.value.canales_personales.push({ tipo: 'WHATSAPP', valor: d.celular_personal })
        }
        if (d.email_personal && !form.value.canales_personales.find(c => c.tipo === 'EMAIL')) {
            form.value.canales_personales.push({ tipo: 'EMAIL', valor: d.email_personal })
        }
    } else {
        // Default Role on New
        if (tiposContacto.value.length > 0) newLinkRole.value = tiposContacto.value[0].id
    }
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

const confirmAddLink = async () => {
    if (!selectedEntity.value) return
    if (!newLinkRole.value) { // Validation
        notificationStore.add("Debe seleccionar un Rol.", "warning")
        return
    }
    if (isNew.value) {
        notificationStore.add("Guarda la persona antes de añadir vínculos.", "warning")
        return
    }

    try {
        // Try getting role name too for better defaults
        const selectedRoleObj = tiposContacto.value.find(t => t.id === newLinkRole.value)
        const roleLabel = selectedRoleObj ? selectedRoleObj.nombre : 'Vinculado'

        const payload = {
            // Vinculo Fields using Agenda API conventions
            cliente_id: newLinkType.value === 'CLIENTE' ? selectedEntity.value.id : null,
            transporte_id: newLinkType.value === 'TRANSPORTE' ? selectedEntity.value.id : null,
            tipo_contacto_id: newLinkRole.value, // Ensure ID
            puesto: roleLabel, // [FIX] Send Label as 'puesto' alias for 'rol'
            estado: true,
            persona_id: props.contactoId
        }

        const newVinculo = await contactosStore.addVinculo(props.contactoId, payload)
        
        // Robust duplicate check/update
        const exists = form.value.vinculos.some(v => v.id === newVinculo.id)
        if (!exists) {
            form.value.vinculos.push(newVinculo)
        } else {
             const idx = form.value.vinculos.findIndex(v => v.id === newVinculo.id)
             if (idx !== -1) form.value.vinculos[idx] = newVinculo
        }
        
        // Reset
        showAddLink.value = false
        selectedEntity.value = null
        newLinkSearch.value = ''
    } catch (e) {
        console.error(e)
        notificationStore.add("Error al vincular", "error")
    }
}

const updateLinkRole = async (link, newRoleId) => {
    try {
        // [FIX] Find the label for the selected ID
        const selectedRole = tiposContacto.value.find(t => t.id === newRoleId)
        const roleLabel = selectedRole ? selectedRole.nombre : 'Vinculado'

        // Optimistic
        link.tipo_contacto_id = newRoleId
        link.rol = roleLabel // Update local for immediate feedback
        
        // Call backend to update both ID and Label
        // The backend 'update_vinculo' might only map fields in schema.
        // Schema 'VinculoUpdate' has 'rol' and 'tipo_contacto_id'.
        // So sending both is correct.
        await contactosStore.updateVinculo(props.contactoId, link.id, { 
            tipo_contacto_id: newRoleId,
            rol: roleLabel 
        })
        notificationStore.add("Rol actualizado", "success")
    } catch (e) {
        console.error(e)
        notificationStore.add("Error actualizando rol", "error")
    }
}

const toggleLinkStatus = async (link) => {
    // Optimistic UI Update
    const originalState = link.activo
    link.activo = !originalState
    
    try {
        await contactosStore.updateVinculo(props.contactoId, link.id, { activo: link.activo })
    } catch (error) {
        // Revert on error
        link.activo = originalState
        console.error("Failed to toggle status", error)
    }
}

// --- BÚSQUEDA PERSONAS (NIKE P SEARCH & LINK) ---
const busquedaQuery = ref('')
const sugerencias = ref([])
const isSearching = ref(false)
const personaExistenteSeleccionada = ref(false)

// Función debounced para no saturar backend
const debouncedSearch = debounce(async (val) => {
    if (!val || val.length < 3 || personaExistenteSeleccionada.value) {
        sugerencias.value = []
        return
    }
    
    isSearching.value = true
    try {
        // Buscamos contra toda la base
        const resultados = await contactosStore.searchPersonas(val)
        // Filtramos para no sugerir la misma persona que ya estamos editando (si aplica)
        sugerencias.value = resultados.filter(p => p.id !== form.value.id)
    } finally {
        isSearching.value = false
    }
}, 300)

// Watcher unificado para Nombre/Apellido
watch(() => form.value.nombre, (val) => {
    // Solo buscar si estamos en modo CREACIÓN (id null) o si explícitamente el usuario quiere buscar
    if (!form.value.id) debouncedSearch(val)
})

// Selección de "Espejismo"
const seleccionarPersonaExistente = (persona) => {
    // 1. Cargar datos de la persona
    form.value.id = persona.id
    form.value.nombre = persona.nombre
    form.value.apellido = persona.apellido
    form.value.domicilio_personal = persona.domicilio_personal
    form.value.notas = persona.notas_globales
    
    // Mapear canales personales
    if (persona.canales_personales && Array.isArray(persona.canales_personales)) {
       // Convertir al formato interno si es necesario, o usarlos directo
    }

    // 2. Bloquear edición de identidad (Solo lectura)
    personaExistenteSeleccionada.value = true
    sugerencias.value = [] // Limpiar dropdown
    
    // 3. Abrir modo "Nuevo Vínculo" automáticamente
    showAddLink.value = true
}

const limpiarPersonaSeleccionada = () => {
    // Resetear a modo "Nueva Persona"
    form.value.id = null
    form.value.nombre = ''
    form.value.apellido = ''
    form.value.domicilio_personal = ''
    form.value.notas = ''
    personaExistenteSeleccionada.value = false
    sugerencias.value = []
    showAddLink.value = false
}


const removeLink = async (link) => {
    if (!confirm(`¿Desvincular de ${getEntityName(link)}?`)) return
    try {
        await contactosStore.deleteVinculo(props.contactoId, link.id)
        form.value.vinculos = form.value.vinculos.filter(v => v.id !== link.id)
    } catch (e) {}
}

const savePersona = async () => {
    if (!form.value.nombre) return notificationStore.add("El nombre es obligatorio", "error")
    
    saving.value = true
    try {
        // MAP UI TO BACKEND SCHEMA (MULTIPLEX V6)
        // Store targets '/contactos' which expects 'ContactoUpdate' schema:
        // - nombre, apellido
        // - canales: List[{ tipo, valor, etiqueta }]
        // - notas (maps to notas_globales)
        // - domicilio_personal
        
        // Ensure channels format
        const cleanChannels = form.value.canales_personales.map(c => ({
            tipo: c.tipo,
            valor: c.valor,
            etiqueta: c.etiqueta || 'Personal'
        })).filter(c => c.valor && c.valor.length > 0)

        const payload = {
            nombre: form.value.nombre,
            apellido: form.value.apellido || '',
            notas: form.value.notas, // Backend maps 'notas' -> notas_globales
            domicilio_personal: form.value.domicilio_personal,
            canales: cleanChannels,
            // Explicitly set null entities to target Personal Data update in Service
            cliente_id: null,
            transporte_id: null
        }
        
        if (isNew.value) {
            await contactosStore.createContacto(payload)
        } else {
            const cleanId = String(props.contactoId)
            await contactosStore.updateContacto(cleanId, payload)
        }
        emit('save')
        emit('close') // Keep the close behavior
        notificationStore.add("Datos guardados correctamente", "success")
    } catch(e) {
        console.error(e)
        const msg = e.response?.data?.detail || "Error al guardar (Verifique datos)"
        notificationStore.add(msg, "error")
    } finally {
        saving.value = false
    }
}

// Helpers Display
const getEntityName = (link) => {
    if (link.entidad_tipo === 'CLIENTE') {
        const c = clientes.value.find(x => x.id === link.entidad_id)
        return c ? c.razon_social : 'Cliente Desconocido'
    } else {
        const t = transportes.value.find(x => x.id === link.entidad_id)
        return t ? t.nombre : 'Transporte Desconocido'
    }
}

const getLaboralContact = (link) => {
    if (!link.canales_laborales || link.canales_laborales.length === 0) return '-'
    // Try to find email or phone
    const email = link.canales_laborales.find(c => c.tipo === 'EMAIL')
    if (email) return email.valor
    const phone = link.canales_laborales.find(c => c.tipo === 'WHATSAPP' || c.tipo === 'TELEFONO')
    return phone ? phone.valor : (link.canales_laborales[0]?.valor || '-')
}

const initials = computed(() => {
    const n = form.value.nombre || '?'
    const a = form.value.apellido || ''
    return (n[0] + (a[0] || '')).toUpperCase()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #111; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }

/* FIX: Ensure options are dark in forced dark mode on Windows */
select option {
    background-color: #1a1a1a;
    color: white;
}
</style>
