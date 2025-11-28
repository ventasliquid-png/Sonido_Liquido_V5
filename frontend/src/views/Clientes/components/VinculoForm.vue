<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import agendaService from '../../../services/agenda';
import maestrosService from '../../../services/maestros';
import clientesService from '../../../services/clientes';
import { useNotificationStore } from '../../../stores/notification';
import SmartSelect from '../../../components/ui/SmartSelect.vue';

const props = defineProps({
    show: Boolean,
    clienteId: String,
    vinculoId: {
        type: String,
        default: null
    }
});

const emit = defineEmits(['close', 'saved']);

const notificationStore = useNotificationStore();
const loading = ref(false);
const searching = ref(false);

// Data
const tiposContacto = ref([]);
const searchResults = ref([]);
const showResults = ref(false);

// Form State
const mode = ref('search'); // search, create_persona, edit_vinculo
const searchQuery = ref('');
const selectedPersona = ref(null);

const formData = ref({
    tipo_contacto_id: '',
    email_laboral: '',
    telefono_escritorio: '',
    es_principal: false
});

const newPersonaData = ref({
    nombre_completo: '',
    celular_personal: '',
    email_personal: ''
});

// Load Maestros
const loadMaestros = async () => {
    try {
        const res = await maestrosService.getTiposContacto();
        tiposContacto.value = res.data;
    } catch (error) {
        console.error("Error loading maestros", error);
    }
};

const loadVinculo = async (id) => {
    try {
        const res = await clientesService.getById(props.clienteId);
        const vinculo = res.data.vinculos.find(v => v.id === id);
        
        if (vinculo) {
            selectedPersona.value = vinculo.persona;
            searchQuery.value = vinculo.persona?.nombre_completo || '';
            mode.value = 'edit_vinculo';
            
            formData.value = {
                tipo_contacto_id: vinculo.tipo_contacto_id,
                email_laboral: vinculo.email_laboral || '',
                telefono_escritorio: vinculo.telefono_escritorio || '',
                es_principal: vinculo.es_principal
            };
        }
    } catch (error) {
        console.error("Error loading vinculo", error);
        notificationStore.add('Error al cargar datos del contacto.', 'error');
    }
};

watch(() => props.show, async (val) => {
    if (val) {
        resetForm();
        await loadMaestros();
        if (props.vinculoId) {
            await loadVinculo(props.vinculoId);
        }
    }
});

const resetForm = () => {
    mode.value = 'search';
    searchQuery.value = '';
    selectedPersona.value = null;
    searchResults.value = [];
    formData.value = {
        tipo_contacto_id: '',
        email_laboral: '',
        telefono_escritorio: '',
        es_principal: false
    };
    newPersonaData.value = {
        nombre_completo: '',
        celular_personal: '',
        email_personal: ''
    };
};

// Search Logic
let searchTimeout;
const handleSearchInput = () => {
    if (searchTimeout) clearTimeout(searchTimeout);
    if (searchQuery.value.length < 3) {
        searchResults.value = [];
        showResults.value = false;
        return;
    }
    
    searching.value = true;
    searchTimeout = setTimeout(async () => {
        try {
            const res = await agendaService.searchPersonas(searchQuery.value);
            searchResults.value = res.data;
            showResults.value = true;
        } catch (error) {
            console.error(error);
        } finally {
            searching.value = false;
        }
    }, 300);
};

const selectPersona = (persona) => {
    selectedPersona.value = persona;
    showResults.value = false;
    searchQuery.value = persona.nombre_completo;
    mode.value = 'edit_vinculo';
    
    // Pre-fill fields if available
    formData.value.email_laboral = persona.email_personal || ''; 
    formData.value.telefono_escritorio = persona.celular_personal || '';
};

const startCreatePersona = () => {
    newPersonaData.value.nombre_completo = searchQuery.value; // Use what they typed
    mode.value = 'create_persona';
    showResults.value = false;
};

const handleSave = async () => {
    loading.value = true;
    try {
        let personaId = selectedPersona.value?.id;

        // 1. Create Persona if needed
        if (mode.value === 'create_persona') {
            const newPersona = await agendaService.createPersona(newPersonaData.value);
            personaId = newPersona.data.id;
        }

        // 2. Create or Update Vinculo
        const payload = {
            cliente_id: props.clienteId,
            persona_id: personaId,
            tipo_contacto_id: formData.value.tipo_contacto_id,
            email_laboral: formData.value.email_laboral || null,
            telefono_escritorio: formData.value.telefono_escritorio || null,
            es_principal: formData.value.es_principal
        };

        if (props.vinculoId) {
            // Update logic (we need an update endpoint in backend/frontend)
            // Currently clientesService only has createVinculo.
            // We need to implement updateVinculo in service and backend.
            // For now, let's assume we need to add it.
            // Wait, the user asked for "lápiz".
            // Let's check if we have update endpoint.
            // backend/agenda/router.py has NO update endpoint for vinculo, only delete.
            // backend/clientes/router.py has delete.
            // We need to add PUT /agenda/vinculos/{id} or similar.
            // For this step, I will just log it and notify user or implement it?
            // "Debe tener un lápiz y un tachito".
            // I should implement the update.
            await clientesService.updateVinculo(props.clienteId, props.vinculoId, payload);
            notificationStore.add('Contacto actualizado exitosamente.', 'success');
        } else {
            await clientesService.createVinculo(props.clienteId, payload);
            notificationStore.add('Contacto agregado exitosamente.', 'success');
        }
        emit('saved');
        emit('close');

    } catch (error) {
        console.error("Error saving vinculo", error);
        notificationStore.add('Error al guardar el contacto.', 'error');
    } finally {
        loading.value = false;
    }
};



const handleCreateTipoContacto = async (nombre) => {
    try {
        const id = nombre.toUpperCase().replace(/\s+/g, '_');
        const res = await maestrosService.createTipoContacto({ id, nombre });
        tiposContacto.value.push(res.data);
        formData.value.tipo_contacto_id = res.data.id;
        notificationStore.add(`Rol "${nombre}" creado.`, 'success');
    } catch (error) {
        console.error("Error creating tipo contacto", error);
        notificationStore.add('Error al crear el rol.', 'error');
    }
};

const handleWhatsappFocus = () => {
    if (!newPersonaData.value.celular_personal) {
        newPersonaData.value.celular_personal = '+54 9 ';
    }
};

const handleWhatsappBlur = () => {
    if (newPersonaData.value.celular_personal === '+54 9 ') {
        newPersonaData.value.celular_personal = '';
    }
};

const close = () => {
    emit('close');
};
</script>

<template>
    <div v-if="show" @keydown.f4.stop.prevent @keydown.f10.stop.prevent="handleSave" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
        <div class="bg-white w-full max-w-lg rounded-lg shadow-xl overflow-hidden animate-scale-in">
            
            <!-- Header -->
            <div class="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h3 class="text-lg font-bold text-gray-800">Nuevo Contacto</h3>
                <button @click="close" class="text-gray-400 hover:text-gray-600">✕</button>
            </div>

            <!-- Body -->
            <div class="p-6 space-y-6">
                
                <!-- STEP 1: SEARCH / IDENTIFY -->
                <div v-if="mode === 'search'" class="relative">
                    <label class="block text-xs font-bold text-gray-600 mb-1">Buscar Persona</label>
                    <input 
                        v-model="searchQuery" 
                        @input="handleSearchInput"
                        type="text" 
                        class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none" 
                        placeholder="Escriba nombre o apellido..." 
                        autofocus
                    />
                    <div v-if="searching" class="absolute right-3 top-8">
                        <div class="animate-spin h-4 w-4 border-2 border-[#54cb9b] border-t-transparent rounded-full"></div>
                    </div>

                    <!-- Results Dropdown -->
                    <div v-if="showResults" class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
                        <ul class="py-1">
                            <li 
                                v-for="p in searchResults" 
                                :key="p.id" 
                                @click="selectPersona(p)"
                                class="px-4 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-50 last:border-0"
                            >
                                <p class="text-sm font-bold text-gray-800">{{ p.nombre_completo }}</p>
                                <p class="text-xs text-gray-500">{{ p.email_personal }}</p>
                            </li>
                            <li 
                                @click="startCreatePersona"
                                class="px-4 py-3 bg-green-50 text-[#54cb9b] font-bold text-sm cursor-pointer hover:bg-green-100 flex items-center gap-2"
                            >
                                <span>+</span> Crear nueva persona: "{{ searchQuery }}"
                            </li>
                        </ul>
                    </div>
                </div>

                <!-- STEP 2: CREATE PERSONA (If new) -->
                <div v-if="mode === 'create_persona'" class="bg-green-50 p-4 rounded border border-green-100 space-y-3">
                    <div class="flex justify-between items-center">
                        <h4 class="text-sm font-bold text-green-800 uppercase">Nueva Persona</h4>
                        <button @click="mode = 'search'" class="text-xs text-green-600 hover:underline">Cambiar</button>
                    </div>
                    
                    <div>
                        <label class="block text-xs font-bold text-gray-600 mb-1">Nombre Completo *</label>
                        <input v-model="newPersonaData.nombre_completo" type="text" class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-bold text-gray-600 mb-1">Celular Personal</label>
                            <input 
                                v-model="newPersonaData.celular_personal" 
                                @focus="handleWhatsappFocus"
                                @blur="handleWhatsappBlur"
                                type="text" 
                                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" 
                                placeholder="+54 9..." 
                            />
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-600 mb-1">Email Personal</label>
                            <input v-model="newPersonaData.email_personal" type="text" class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                        </div>
                    </div>
                </div>

                <!-- STEP 3: VINCULO DETAILS (Always shown if persona selected or creating) -->
                <div v-if="mode !== 'search'" class="space-y-4 animate-fade-in">
                    <div v-if="mode === 'edit_vinculo'" class="flex justify-between items-center bg-blue-50 p-3 rounded border border-blue-100">
                        <div>
                            <p class="text-xs text-blue-600 font-bold uppercase">Persona Seleccionada</p>
                            <p class="text-sm font-bold text-gray-800">{{ selectedPersona.nombre_completo }}</p>
                        </div>
                        <button @click="resetForm" class="text-xs text-blue-500 hover:underline">Cambiar</button>
                    </div>

                    <div class="border-t border-gray-100 pt-4">
                        <h4 class="text-sm font-bold text-gray-500 uppercase mb-3">Datos del Vínculo Laboral</h4>
                        
                        <div class="grid grid-cols-1 gap-4">
                            <div>
                                <SmartSelect
                                    v-model="formData.tipo_contacto_id"
                                    :options="tiposContacto"
                                    label="Rol / Tipo de Contacto *"
                                    placeholder="Seleccionar o crear rol..."
                                    :allow-create="true"
                                    @create="handleCreateTipoContacto"
                                />
                            </div>
                            
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-xs font-bold text-gray-600 mb-1">Email Laboral</label>
                                    <input v-model="formData.email_laboral" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
                                </div>
                                <div>
                                    <label class="block text-xs font-bold text-gray-600 mb-1">Tel. Escritorio / Interno</label>
                                    <input v-model="formData.telefono_escritorio" type="text" class="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
                                </div>
                            </div>

                            <div class="flex items-center gap-2">
                                <input v-model="formData.es_principal" type="checkbox" id="es_principal" class="rounded text-[#54cb9b] focus:ring-[#54cb9b]" />
                                <label for="es_principal" class="text-sm text-gray-700">Es el contacto principal</label>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

            <!-- Footer -->
            <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
                <button @click="close" class="px-4 py-2 text-gray-600 font-bold text-xs hover:bg-gray-200 rounded transition-colors">CANCELAR</button>
                <button 
                    @click="handleSave" 
                    :disabled="loading || mode === 'search' || !formData.tipo_contacto_id"
                    class="px-6 py-2 bg-[#54cb9b] text-white font-bold text-xs rounded shadow-sm hover:bg-[#45b085] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                    <span v-if="loading" class="animate-spin h-3 w-3 border-2 border-white border-t-transparent rounded-full"></span>
                    GUARDAR CONTACTO
                </button>
            </div>
        </div>
    </div>
</template>
