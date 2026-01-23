<template>
  <div class="flex flex-col h-full w-full backdrop-blur-xl transition-all hud-border-cyan rounded-xl" 
       :class="isCompact ? 'bg-[#0f172a]/90 border-l border-cyan-500' : 'bg-[#0f172a]'">
    <!-- Persistent Header -->
    <div class="flex justify-between items-center border-b border-cyan-500/30 bg-black/20 shrink-0 transition-all"
         :class="isCompact ? 'p-3 py-2' : 'p-6'">
        <div>
            <h2 class="text-lg font-bold text-cyan-100 leading-tight">
                {{ modelValue?.razon_social || (isNew ? 'Nuevo Cliente' : 'Seleccione Cliente') }}
            </h2>
            <p class="text-xs text-cyan-400/50 font-mono mt-1">{{ headerSubtitle }}</p>
        </div>
        <button v-if="modelValue || isNew" @click="$emit('close')" class="text-cyan-900/50 hover:text-cyan-100 transition-colors">
            <i class="fas fa-times"></i>
        </button>
    </div>

    <!-- Inconsistency Banner -->
    <div v-if="hasInconsistency && !isNew" class="bg-red-500/10 border-b border-red-500/20 px-6 py-2 flex items-center justify-between group">
        <div class="flex items-center gap-2 overflow-hidden">
            <i class="fas fa-triangle-exclamation text-red-400 animate-pulse text-xs"></i>
            <span class="text-[10px] font-bold text-red-200/80 uppercase tracking-tighter truncate">
                Datos Inconsistentes: {{ formInconsistency.join(', ') }}
            </span>
        </div>
        <div class="text-[9px] text-red-400/50 font-medium italic opacity-0 group-hover:opacity-100 transition-opacity">
            Corregir para evitar errores fiscales
        </div>
    </div>

    <!-- Empty State -->
    <div v-if="!modelValue && !isNew" class="flex-1 flex flex-col items-center justify-center text-cyan-900/40 p-6 text-center">
        <i class="fas fa-user text-4xl mb-4"></i>
        <p>Seleccione un cliente para ver sus propiedades</p>
    </div>

    <!-- Form Content -->
    <div v-else class="flex-1 flex flex-col min-h-0">
        <!-- Tabs -->
        <div class="flex border-b border-cyan-900/20 shrink-0 bg-black/10">
            <button 
                @click="activeTab = 'general'"
                class="flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'general' ? 'border-cyan-400 text-cyan-400 bg-cyan-900/10' : 'border-transparent text-cyan-200/40 hover:text-cyan-200 hover:bg-cyan-900/5'"
            >
                General
            </button>
            <button 
                @click="activeTab = 'domicilios'"
                class="flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'domicilios' ? 'border-cyan-400 text-cyan-400 bg-cyan-900/10' : 'border-transparent text-cyan-200/40 hover:text-cyan-200 hover:bg-cyan-900/5'"
            >
                Domicilios
            </button>
            <button 
                @click="activeTab = 'contactos'"
                class="flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'contactos' ? 'border-cyan-400 text-cyan-400 bg-cyan-900/10' : 'border-transparent text-cyan-200/40 hover:text-cyan-200 hover:bg-cyan-900/5'"
            >
                Contactos
            </button>
        </div>

        <!-- Scrollable Body -->
        <div class="flex-1 overflow-y-auto space-y-6 scrollbar-thin scrollbar-thumb-cyan-900/50 scrollbar-track-transparent pb-20"
             :class="isCompact ? 'p-3' : 'p-6'">
            
            <!-- TAB: GENERAL -->
            <div v-if="activeTab === 'general'" class="space-y-4">
                
                <!-- SELECCIÓN POR PLANTILLA (F4 Flow) -->
                <div v-if="isNew" class="p-3 rounded-lg bg-cyan-500/5 border border-cyan-500/20 mb-4">
                    <label class="text-[0.65rem] font-bold text-cyan-400 uppercase tracking-widest mb-2 block">
                        Cargar desde Plantilla / Cantera
                    </label>
                    <SmartSelect
                        v-model="templateId"
                        :options="clienteStore.clientes"
                        canteraType="clientes"
                        placeholder="Buscar cliente para clonar..."
                        :allowCreate="true"
                        @update:modelValue="handleTemplateSelect"
                        @select-cantera="handleTemplateSelect"
                        @create-new="handleManualTemplate"
                        class="dark-smart-select"
                    />
                    <p class="text-[9px] text-cyan-400/30 mt-2 italic">
                        Tip: Útil para cargar sedes de un mismo grupo rápidamente.
                    </p>
                </div>

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
                  <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Razón Social <span class="text-red-400">*</span></label>
                  <input v-model="form.razon_social" autocomplete="off" spellcheck="false" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-colors placeholder-cyan-900/30" placeholder="Ej: Empresa S.A." />
                </div>

                <div>
                    <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">CUIT <span class="text-red-400">*</span></label>
                    <input v-model="form.cuit" autocomplete="off" spellcheck="false" @input="formatCuitInput" @blur="checkCuitBackend" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-colors font-mono placeholder-cyan-900/30" placeholder="00-00000000-0" maxlength="13" />
                    
                    <!-- Alert: Duplicated CUIT -->
                    <div v-if="cuitWarningClients.length > 0 && !cuitWarningDismissed" class="mt-2 bg-yellow-900/20 border border-yellow-500/30 rounded p-3 text-xs animate-pulse-once">
                        <div class="flex justify-between items-start mb-2">
                            <p class="text-yellow-400 font-bold flex items-center gap-2">
                                <i class="fas fa-exclamation-triangle"></i> CUIT compartido:
                            </p>
                            <button @click="dismissCuitWarning" class="text-[10px] bg-yellow-500/20 hover:bg-yellow-500/40 text-yellow-200 px-2 py-0.5 rounded border border-yellow-500/30 transition-colors uppercase font-bold" title="Ignorar advertencia y continuar creación">
                                Ok, Nueva Sede
                            </button>
                        </div>
                        
                        <p class="text-[10px] text-yellow-500/70 mb-2 italic">
                            Este CUIT ya existe. Doble click para editar el existente, o "Ok" para crear nueva sede.
                        </p>

                        <ul class="space-y-1 max-h-60 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-yellow-700/50">
                            <li 
                                v-for="dup in cuitWarningClients" 
                                :key="dup.id" 
                                @dblclick="selectExistingClient(dup)"
                                class="text-yellow-200/70 hover:text-yellow-100 hover:bg-yellow-500/10 cursor-pointer bg-black/20 p-2 rounded border border-transparent hover:border-yellow-500/30 transition-all select-none"
                                title="Doble click para cargar este cliente"
                            >
                                <div class="flex justify-between items-center">
                                    <span class="font-bold">{{ dup.razon_social }}</span>
                                    <i class="fas fa-external-link-alt text-[10px] opacity-50"></i>
                                </div>
                                <div class="text-[10px] opacity-70 mt-0.5">{{ dup.domicilio_principal || 'Sin domicilio registrado' }}</div>
                            </li>
                        </ul>
                    </div>

                    <p v-if="cuitError" class="text-[10px] text-red-400 mt-1">{{ cuitError }}</p>
                </div>

                <div @contextmenu.prevent="openIvaContextMenu" class="cursor-context-menu">
                    <div class="flex justify-between mb-1">
                        <label class="block text-xs font-bold uppercase text-cyan-900/50">Condición IVA <span class="text-red-400">*</span></label>
                        <button @click="openAbm('IVA')" class="text-[10px] uppercase font-bold text-cyan-500 hover:text-cyan-400 focus:outline-none" title="Administrar Condiciones">
                            <i class="fas fa-cog"></i> ABM
                        </button>
                    </div>
                    <select v-model="form.condicion_iva_id" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors appearance-none">
                        <option :value="null">Seleccionar...</option>
                        <option v-for="cond in condicionesIva" :key="cond.id" :value="cond.id">{{ cond.nombre }}</option>
                    </select>
                </div>

                <div>
                    <div class="flex justify-between mb-1">
                        <label class="block text-xs font-bold uppercase text-cyan-900/50">Segmento <span class="text-red-400">*</span></label>
                        <button @click="openAbm('SEGMENTO')" class="text-[10px] uppercase font-bold text-cyan-500 hover:text-cyan-400 focus:outline-none" title="Administrar Segmentos">
                            <i class="fas fa-cog"></i> ABM
                        </button>
                    </div>
                    <select v-model="form.segmento_id" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors appearance-none">
                        <option :value="null">Sin Segmento</option>
                        <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
                    </select>

                </div>

                <div>
                    <div class="flex justify-between mb-1">
                        <label class="block text-xs font-bold uppercase text-cyan-900/50">Lista de Precios <span class="text-red-400">*</span></label>
                         <button @click="router.push({name: 'ListasPrecios'})" class="text-[10px] uppercase font-bold text-cyan-500 hover:text-cyan-400 focus:outline-none" title="Ir a Gestión de Listas">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                    </div>
                    <select v-model="form.lista_precios_id" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors appearance-none">
                        <option :value="null" disabled>Seleccione Lista...</option>
                        <option v-for="lista in listasPrecios" :key="lista.id" :value="lista.id">{{ lista.nombre }}</option>
                    </select>
                </div>


                <!-- DOMICILIO FISCAL (Solo Alta) -->
                <div v-if="isNew" class="pt-4 border-t border-cyan-900/20">
                    <h3 class="text-xs font-bold text-cyan-400 mb-3 flex items-center gap-2">
                        <i class="fas fa-map-marker-alt"></i> DOMICILIO FISCAL (Obligatorio)
                    </h3>
                    <div class="space-y-3">
                        <div>
                            <label class="block text-[10px] font-bold uppercase text-cyan-900/50 mb-1">Calle <span class="text-red-400">*</span></label>
                            <input v-model="fiscalForm.calle" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-colors placeholder-cyan-900/30" placeholder="Ej: San Martin" />
                        </div>
                        <div class="flex gap-2">
                             <div class="w-1/3">
                                <label class="block text-[10px] font-bold uppercase text-cyan-900/50 mb-1">Altura <span class="text-red-400">*</span></label>
                                <input v-model="fiscalForm.numero" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors placeholder-cyan-900/30" />
                             </div>
                             <div class="w-2/3">
                                <label class="block text-[10px] font-bold uppercase text-cyan-900/50 mb-1">Localidad <span class="text-red-400">*</span></label>
                                <input v-model="fiscalForm.localidad" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors placeholder-cyan-900/30" />
                             </div>
                        </div>
                        <div>
                            <label class="block text-[10px] font-bold uppercase text-cyan-900/50 mb-1">Provincia <span class="text-red-400">*</span></label>
                            <select v-model="fiscalForm.provincia_id" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors appearance-none text-xs">
                                <option :value="null">Seleccionar...</option>
                                <option v-for="prov in provincias" :key="prov.id" :value="prov.id">{{ prov.nombre }}</option>
                            </select>
                        </div>
                         <div>
                            <select v-model="fiscalForm.transporte_id" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors appearance-none text-xs">
                                <option :value="null">Transporte Sugerido</option>
                                <option v-for="trans in transportes" :key="trans.id" :value="trans.id">{{ trans.nombre }}</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div v-if="isNew" class="pt-2 text-[10px] text-red-400/80 italic text-right">
                    * Campos Obligatorios
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
                        v-for="dom in sortedDomicilios" 
                        :key="dom.id"
                        @dblclick="openDomicilioForm(dom)"
                        class="bg-cyan-900/5 border border-cyan-900/20 rounded-lg p-3 relative group hover:bg-cyan-900/10 transition-colors cursor-pointer select-none"
                    >
                        <div class="flex justify-between items-start pr-24">
                            <div class="flex items-center gap-2">
                            <span v-if="dom.es_fiscal" class="text-[10px] bg-purple-500/30 text-purple-200 font-bold px-2 py-0.5 rounded border border-purple-500/50 shadow-sm shadow-purple-900/20">FISCAL</span>
                            <span v-else class="text-[10px] bg-slate-700 text-white font-bold px-2 py-0.5 rounded border border-slate-600 shadow-sm shadow-black/20">SUCURSAL</span>
                            
                            <!-- Logistics Icon -->
                            <div v-if="dom.es_entrega" class="ml-2" :title="dom.origen_logistico === 'RETIRO_EN_PLANTA' ? 'Nos Retiran' : 'Despachamos'">
                                <i v-if="dom.origen_logistico === 'RETIRO_EN_PLANTA'" class="fa-solid fa-truck-pickup text-cyan-400 text-xs"></i>
                                <i v-else class="fa-solid fa-dolly text-emerald-400 text-xs"></i>
                            </div>
                        </div>
                        </div>
                        <p class="text-sm font-medium text-cyan-100 mt-1">{{ dom.calle }} {{ dom.numero }}</p>
                        <p class="text-xs text-cyan-200/50">{{ dom.localidad }}</p>
                        
                        <!-- Actions: Edit, Delete, Toggle -->
                        <div class="absolute top-2 right-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            
                            <!-- Toggle Active (Slider) - Except Fiscal -->
                            <button 
                                v-if="!dom.es_fiscal"
                                @click.stop="toggleDomicilioActive(dom)"
                                :title="dom.activo ? 'Desactivar Domicilio' : 'Activar Domicilio'"
                                class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0"
                                :class="dom.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                            >
                                <span 
                                    class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                    :class="dom.activo ? 'translate-x-3.5' : 'translate-x-1'"
                                />
                            </button>

                            <!-- Edit -->
                            <button @click.stop="openDomicilioForm(dom)" class="text-cyan-200 hover:text-white bg-white/10 hover:bg-white/20 p-1.5 rounded transition-colors" title="Editar">
                                <i class="fas fa-pencil-alt"></i>
                            </button>
                            
                            <!-- Delete (Tachito) - Except Fiscal -->
                            <button 
                                v-if="!dom.es_fiscal" 
                                @click.stop="deleteDomicilio(dom)" 
                                class="text-red-400 hover:text-red-300 bg-white/10 hover:bg-white/20 p-1.5 rounded transition-colors"
                                title="Eliminar Domicilio"
                            >
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    
                    <button @click="openDomicilioForm()" class="w-full py-2 border border-dashed border-cyan-500/30 rounded-lg text-cyan-400/50 hover:text-cyan-300 hover:border-cyan-400/50 hover:bg-cyan-500/5 transition-all text-xs font-bold uppercase">
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

        <!-- Domicilio Form Overlay - Outside Tabs -->
        <!-- Domicilio Form Overlay - Outside Tabs -->
        <Teleport to="body">
            <div v-if="showDomicilioForm" class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" @click.self="showDomicilioForm = false">
                <DomicilioForm 
                    :show="showDomicilioForm" 
                    :domicilio="selectedDomicilio" 
                    @close="showDomicilioForm = false"
                    @saved="handleDomicilioSaved"
                />
            </div>
        </Teleport>

        <!-- Footer Actions (Sticky Bottom) -->
        <div class="sticky bottom-0 left-0 right-0 p-6 border-t border-cyan-900/20 flex gap-3 shrink-0 bg-black/40 z-50 shadow-[0_-5px_20px_rgba(0,0,0,0.5)]">
            <button @click="save" class="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white py-2 rounded font-bold transition-colors shadow-lg shadow-cyan-900/20">
                <span v-if="saving"><i class="fas fa-spinner fa-spin mr-2"></i>Guardando...</span>
                <span v-else>Guardar (F10)</span>
            </button>
            <button v-if="!isNew" @click="remove" class="px-3 bg-red-900/20 hover:bg-red-900/40 text-red-400 rounded border border-red-500/30 transition-colors" title="Dar de baja lógica">
                <i class="fas fa-toggle-off"></i> <span class="ml-2 text-[10px] font-bold uppercase">Baja Lógica</span>
            </button>
            <button v-if="!isNew && !form.activo" @click="hardDelete" class="px-3 bg-red-600 hover:bg-red-500 text-white rounded shadow-lg shadow-red-900/40 transition-all active:scale-95" title="Eliminación Definitiva">
                <i class="fas fa-trash-alt"></i> <span class="ml-2 text-[10px] font-bold uppercase">Baja Física</span>
            </button>
        </div>
    </div>
    
    <!-- Condicion IVA Form Overlay (Old logic preserved but hidden/not used mostly) -->
    <CondicionIvaForm 
        :show="showCondicionIvaForm"
        :initial-view="condicionIvaStartView" 
        @close="showCondicionIvaForm = false"
        @saved="handleCondicionIvaSaved"
    />

    <!-- NEW SIMPLE ABM MODAL -->
    <Teleport to="body">
        <SimpleAbmModal
            v-if="showAbm"
            :title="abmTitle"
            :items="abmItems"
            :isLoading="abmLoading"
            @close="showAbm = false"
            @create="handleAbmCreate"
            @delete="handleAbmDelete"
        />
    </Teleport>

    <!-- Global Context Menu -->
    <Teleport to="body">
        <ContextMenu 
            v-if="contextMenu.show"
            v-model="contextMenu.show" 
            :x="contextMenu.x" 
            :y="contextMenu.y" 
            :actions="contextMenu.actions" 
            @close="contextMenu.show = false"
        />
    </Teleport>
</div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { useMaestrosStore } from '../../../stores/maestros'
import { useClientesStore } from '../../../stores/clientes'
import { useNotificationStore } from '../../../stores/notification'
import clientesService from '../../../services/clientes'
import DomicilioForm from './DomicilioForm.vue'
import CondicionIvaForm from '../../Maestros/CondicionIvaForm.vue'
import ContextMenu from '../../../components/common/ContextMenu.vue'
import SimpleAbmModal from '../../../components/common/SimpleAbmModal.vue'
import SmartSelect from '../../../components/ui/SmartSelect.vue'

const props = defineProps({
    modelValue: {
        type: Object,
        default: null
    },
    isNew: {
        type: Boolean,
        default: false
    },
    mode: {
        type: String,
        default: 'full' // 'full' | 'compact'
    }
})

const emit = defineEmits(['update:modelValue', 'close', 'save', 'delete', 'hard-delete', 'manage-segmentos', 'switch-client'])

const isCompact = computed(() => props.mode === 'compact')


const maestrosStore = useMaestrosStore()
const clienteStore = useClientesStore()
const notificationStore = useNotificationStore()

const segmentos = computed(() => maestrosStore.segmentos)
const condicionesIva = computed(() => maestrosStore.condicionesIva)
const provincias = computed(() => maestrosStore.provincias)
const transportes = computed(() => maestrosStore.transportes)

const listasPrecios = computed(() => maestrosStore.listasPrecios)
const sortedDomicilios = computed(() => {
    if (!form.value.domicilios) return []
    // [GY-FIX] Filter only active domicilios (Soft Delete View)
    return [...form.value.domicilios]
        .filter(d => d.activo !== false)
        .sort((a, b) => {
            if (a.es_fiscal && !b.es_fiscal) return -1
            if (!a.es_fiscal && b.es_fiscal) return 1
            return (a.alias || a.calle || '').localeCompare(b.alias || b.calle || '')
        })
})

const activeTab = ref('general')
const saving = ref(false)
const form = ref({})
const cuitError = ref(null)
const pristineName = ref('')
const templateId = ref(null)

const formInconsistency = computed(() => {
    const issues = []
    
    // Check CUIT (except for INT or Consumidor Final)
    const isSpecial = form.value.razon_social?.toUpperCase().includes('CONSUMIDOR FINAL') || 
                      form.value.condicion_iva_id === 'INT' // This assumes 'INT' is an ID or label, will verify
    
    if (!form.value.cuit && !isSpecial) {
        issues.push('CUIT faltante')
    }
    
    if (!form.value.condicion_iva_id) {
        issues.push('Condición IVA faltante')
    }
    
    if (!form.value.segmento_id && !isSpecial) {
        issues.push('Segmento no definido')
    }

    // Check Fiscal Domicile
    const hasFiscal = form.value.domicilios?.some(d => d.es_fiscal && d.activo)
    if (!hasFiscal && !props.isNew) {
        issues.push('Sin domicilio fiscal activo')
    }

    return issues
})

const hasInconsistency = computed(() => formInconsistency.value.length > 0)

const headerTitle = computed(() => {
    if (!props.modelValue && !props.isNew) return 'Inspector'
    return props.isNew ? 'Nuevo Cliente' : 'Editar Cliente'
})

const headerSubtitle = computed(() => {
    // Fix reactivity: check form.value.cuit if editing, or modelValue if valid. 
    // Actually form.value is the source of truth for the inputs.
    return form.value.cuit || (props.isNew ? 'Nuevo' : 'Sin CUIT')
})

const formatCuitInput = () => {
    let val = form.value.cuit || ''
    // Allow digits and up to 2 separators (-, _, /)
    // First remove anything that is not digit or separator
    val = val.replace(/[^0-9\-_/]/g, '')
    
    // Check separator count
    const separators = val.match(/[\-_/]/g)
    if (separators && separators.length > 2) {
        // Keep only first 2
       // This is complex to do via regex replace on the fly, easier to warn or truncate.
       // Let's iterate chars
       let count = 0
       let newVal = ''
       for (let char of val) {
           if (['-', '_', '/'].includes(char)) {
               count++
               if (count <= 2) newVal += char
           } else {
               newVal += char
           }
       }
       val = newVal
    }
    
    form.value.cuit = val.slice(0, 13) // Max 13 chars
    cuitError.value = null
    // Reset warning on typing
    cuitWarningDismissed.value = false
    if (val.length < 13) cuitWarningClients.value = []
}

// CUIT Multi-Sede Warning System
const cuitWarningClients = ref([])
const cuitWarningDismissed = ref(false)

const dismissCuitWarning = () => {
    cuitWarningDismissed.value = true
}

const checkCuitBackend = async () => {
    // Check if we have a potentially valid CUIT (at least 11 digits, valid structure)
    if (!form.value.cuit) return
    if (!validateCuit(form.value.cuit)) return 
    
    try {
        const res = await clienteStore.checkCuit(form.value.cuit, props.isNew ? null : form.value.id)
        if (res.status === 'EXISTS' || res.status === 'INACTIVE') {
            cuitWarningClients.value = res.existing_clients
            // Do not reset dismissed flag here if it was already dismissed for THIS cuit?
            // Actually users might tab out multiple times. If they dismissed it, keep it dismissed unless they changed input.
            // But 'cuitWarningDismissed' is reset in 'formatCuitInput' (on input). 
            // So here we don't need to force reset it to false, allowing persistance if user just tabs out again.
            // However, if we found new results (different list?), maybe we should?
            // For simplicity, if input didn't change (handled by formatCuitInput), we respect current dismissed state.
        } else {
            cuitWarningClients.value = []
            cuitWarningDismissed.value = false
        }
    } catch (e) {
        console.error("Error checking CUIT:", e)
    }
}

const selectExistingClient = (clientSummary) => {
    if(confirm(`¿Desea descartar el alta y cargar el cliente "${clientSummary.razon_social}"?`)) {
         emit('switch-client', clientSummary.id)
    }
}

const validateCuit = (cuit) => {
    if (!cuit) return false
    const clean = cuit.replace(/[^0-9]/g, '')
    if (clean.length !== 11) return false
    
    // [GY-FIX] Excepción de CUITs Genéricos (Consumidor Final / Mostrador)
    if (['00000000000', '99999999999', '11111111111'].includes(clean)) return true;
    
    const multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    let total = 0
    for (let i = 0; i < 10; i++) {
        total += parseInt(clean[i]) * multipliers[i]
    }
    
    let mod = total % 11
    let digit = mod === 0 ? 0 : 11 - mod
    if (digit === 10) digit = 9 // Rare case, typically handled by different algorithm variant but acceptable for standard simplified check
    
    // Official algorithm handles 10 slightly differently (Type Z), but standard personal/business CUITs follow this.
    // If we want to be strict: 
    // Verification digit is clean[10]
    const valid = digit === parseInt(clean[10])
    if (!valid) {
        cuitError.value = 'CUIT inválido (Dígito verificador incorrecto)'
    } else {
        cuitError.value = null
    }
    return valid
}

// Fiscal Form for New Client
const fiscalForm = ref({
    calle: '',
    numero: '',
    localidad: '',
    provincia_id: null,
    transporte_id: null
})

// Domicilio Management (Editing)
const showDomicilioForm = ref(false)
const selectedDomicilio = ref(null)

const openDomicilioForm = (dom = null) => {
    selectedDomicilio.value = dom
    showDomicilioForm.value = true
}

const handleDomicilioSaved = async (domData) => {
    try {
        if (domData.id) {
            await clienteStore.updateDomicilio(form.value.id, domData.id, domData)
            notificationStore.add('Domicilio actualizado', 'success')
        } else {
            await clienteStore.createDomicilio(form.value.id, domData)
            notificationStore.add('Domicilio creado', 'success')
        }
        
        // [GY-FIX] Force Refresh from Backend to ensure Full Consistency
        // Bypass return value optimization to guarantee relationships (active/fiscal) are 100% synced
        const freshClient = await clienteStore.fetchClienteById(form.value.id)
        form.value = JSON.parse(JSON.stringify(freshClient)) // Deep copy to reset form state
        
        showDomicilioForm.value = false
    } catch (error) {
        console.error(error)
        notificationStore.add('Error al guardar domicilio', 'error')
    }
}

// Condicion IVA Management
const showCondicionIvaForm = ref(false)
const condicionIvaStartView = ref('list')

const openCondicionIva = (view = 'list') => {
    condicionIvaStartView.value = view
    showCondicionIvaForm.value = true
}

const handleCondicionIvaSaved = async () => {
    await maestrosStore.fetchCondicionesIva()
    // Don't close automatically if in list mode? Or close?
    // User requested "Alta rápida". If fast add, usually close.
    if (condicionIvaStartView.value === 'form') {
         showCondicionIvaForm.value = false
    } else {
        // In manager mode, stay open?
        // But CondicionIvaForm emits 'saved', let's just refresh.
        // It handles internal view switch if needed.
    }
    notificationStore.add('Condición de IVA actualizada', 'success')
}

// Context Menu Logic
const contextMenu = ref({
    show: false,
    x: 0,
    y: 0,
    actions: []
})

const openIvaContextMenu = (e) => {
    contextMenu.value = {
        show: true,
        x: e.clientX,
        y: e.clientY,
        actions: [
            { 
                label: 'Administrar (ABM)', 
                iconClass: 'fas fa-tasks', 
                handler: () => { openCondicionIva('list') } 
            },
            { 
                label: 'Nueva Condición (+)', 
                iconClass: 'fas fa-plus', 
                handler: () => { openCondicionIva('form') } 
            }
        ]
    }
}


// Initialize form when modelValue changes
watch(() => props.modelValue, (newVal) => {
    if (newVal) {
        form.value = JSON.parse(JSON.stringify(newVal)) // Deep copy
        // Ensure arrays exist
        if (!form.value.domicilios) form.value.domicilios = []
        if (newVal.activo === undefined) form.value.activo = true // Default to true if undefined
        // Ensure arrays exist
    } else {
        form.value = {}
    }
    
    // Reset fiscal form
    if (props.isNew) {
        activeTab.value = 'general'
        fiscalForm.value = {
            calle: '',
            numero: '',
            localidad: '',
            provincia_id: null,
            transporte_id: null
        }
        templateId.value = null
        pristineName.value = form.value.razon_social || ''
    }
}, { immediate: true })

const handleTemplateSelect = (itemOrId) => {
    let template = null;
    if (typeof itemOrId === 'object') {
        template = itemOrId;
    } else {
        template = clienteStore.clientes.find(c => c.id === itemOrId);
    }

    if (template) {
        // Inherit everything except ID, CUIT (usually differs for clones unless multi-sede)
        form.value = {
            ...JSON.parse(JSON.stringify(template)),
            id: null,
            // Keep current CUIT if user already typed it? or clear it?
            // Usually if they search template, they want to KEEP their typed CUIT but get the REST.
            cuit: form.value.cuit || '',
             _isClone: true
        };
        pristineName.value = template.razon_social;
        // If template has fiscal address, maybe load it too?
        // Let's assume they want to change the address.
    }
}

const handleManualTemplate = (name) => {
    // [GY-MOD] Manual creation bypass if not found in Cantera
    if (name) {
        form.value.razon_social = name
        // Set focus to CUIT field maybe? Or just leave it.
    }
    templateId.value = null
    notificationStore.add('Alta Manual: Complete los datos', 'info')
}

// --- ABM LOGIC ---
const showAbm = ref(false)
const abmLoading = ref(false)
const abmType = ref(null) // 'IVA' | 'SEGMENTO'
const abmTitle = computed(() => abmType.value === 'IVA' ? 'Condiciones de IVA' : 'Segmentos')
const abmItems = computed(() => abmType.value === 'IVA' ? condicionesIva.value : segmentos.value)

const openAbm = (type) => {
    abmType.value = type
    showAbm.value = true
}

const handleAbmCreate = async (name) => {
    // [GY-UX] Duplicate Validation (Frontend)
    const exists = abmItems.value.some(item => item.nombre.toLowerCase() === name.toLowerCase())
    if (exists) {
        notificationStore.add(`"${name}" ya existe en la lista`, 'warning')
        return
    }

    abmLoading.value = true
    try {
        let res;
        if (abmType.value === 'IVA') {
            res = await maestrosStore.createCondicionIva({ nombre: name })
            if (res && res.id) form.value.condicion_iva_id = res.id
        } else {
            res = await maestrosStore.createSegmento({ nombre: name })
            if (res && res.id) form.value.segmento_id = res.id
        }
        notificationStore.add('Elemento creado y seleccionado', 'success')
        showAbm.value = false
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al crear elemento', 'error')
    } finally {
        abmLoading.value = false
    }
}

const handleAbmDelete = async (id) => {
    try {
        if (abmType.value === 'IVA') {
            await maestrosStore.deleteCondicionIva(id)
        } else {
             // Implement Segmento deletion
             if (maestrosStore.deleteSegmento) {
                 await maestrosStore.deleteSegmento(id)
             } else {
                 console.warn("deleteSegmento implementation missing in store")
                 alert("Funcionalidad no implementada en backend aún.")
                 return
             }
        }
        notificationStore.add('Elemento eliminado', 'success')
    } catch (e) {
        console.error(e)
        notificationStore.add('Error: Elemento en uso o fallo técnico', 'error')
    }
}


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
        // [DEOU Flow] If no changes in name for a new template-based item, cancel save
        if (props.isNew && form.value.razon_social === pristineName.value && form.value._isClone) {
            alert('No se detectaron cambios en el nombre. No se generará un nuevo registro.');
            emit('close');
            return;
        }

        // Validation for New Client
        // Shared Validations (Create & Edit)
        if (!form.value.razon_social) {
             alert('La Razón Social es obligatoria.')
             saving.value = false
             return
        }
        if (!form.value.cuit) {
             alert('El CUIT es obligatorio.')
             saving.value = false
             return
        }
        
        // CUIT Validation
        if (!validateCuit(form.value.cuit)) {
            cuitError.value = 'CUIT inválido (Dígito verificador incorrecto)'
            saving.value = false
            return
        }

        // Check if Generic CUIT
        const cleanCuit = form.value.cuit ? form.value.cuit.replace(/[^0-9]/g, '') : ''
        const isGenericCuit = ['00000000000', '99999999999', '11111111111'].includes(cleanCuit)

        if (!form.value.segmento_id && !isGenericCuit) {
            alert('El Segmento es obligatorio.')
            saving.value = false
            return
        }
        if (!form.value.lista_precios_id) {
            alert('La Lista de Precios es obligatoria.')
            saving.value = false
            return
        }
        if (!form.value.condicion_iva_id && !isGenericCuit) {
             // For Generic, we can auto-set Consumidor Final if not set
             if (isGenericCuit) {
                 const consFinal = condicionesIva.value.find(c => c.nombre.toLowerCase().includes('consumidor final'))
                 if (consFinal) form.value.condicion_iva_id = consFinal.id
                 else {
                     // If we can't find it, don't block? Or blocking is safer? 
                     // Let's soft warn or default to the first one?
                     // Better: Auto-set to "Consumidor Final" ID if known, or skip.
                     // The backend might require it though. 
                     // Let's assume Consumidor Final exists.
                     // If user didn't select, we try to find it.
                 }
             } else {
                alert('La Condición IVA es obligatoria.')
                saving.value = false
                return
             }
        }

        // Specific Validations for New Client
        if (props.isNew) {
            // [GY-FIX] Skip Address Check for Generic CUITs
            if (!isGenericCuit) {
                if (!fiscalForm.value.calle || !fiscalForm.value.numero || !fiscalForm.value.localidad || !fiscalForm.value.provincia_id) {
                    alert('Por favor complete todos los datos obligatorios del Domicilio Fiscal.')
                    saving.value = false
                    return
                }
            } else {
                // Auto-fill dummy fiscal for generic if empty
                if (!fiscalForm.value.calle) {
                     fiscalForm.value = {
                         calle: 'Mostrador',
                         numero: 'S/N',
                         localidad: 'Local',
                         provincia_id: provincias.value.length > 0 ? provincias.value[0].id : null, 
                         transporte_id: null
                     }
                }
            }

            // FORCE CHECK before saving to ensure state is up to date
            await checkCuitBackend()
            
            // Check duplicates (Skip for Generic)
            if (cuitWarningClients.value.length > 0 && !isGenericCuit) {
                if (cuitWarningDismissed.value) {
                    form.value.requiere_auditoria = true
                } else {
                    if(!confirm(`Este CUIT ya existe en ${cuitWarningClients.value.length} clientes. ¿Confirma que es una nueva sede/facultad?`)) {
                        saving.value = false
                        return
                    }
                    form.value.requiere_auditoria = true
                }
            }

            // Add Fiscal Address to payload
            form.value.domicilios = [{
                ...fiscalForm.value,
                es_fiscal: true,
                es_entrega: true,
                activo: true,
                tipo: 'FISCAL'
            }]
        }

        // [GY-FIX] Sanitize CUIT: Remove all separators before saving
        // User Requirement: Allow delimiters in UI but SAVE only digits.
        if (form.value.cuit) {
            form.value.cuit = form.value.cuit.replace(/[^0-9]/g, '')
        }
        
        // [GY-FIX] ACTUALLY SAVE TO STORE/BACKEND
        let result;
        if (props.isNew) {
            result = await clienteStore.createCliente(form.value)
        } else {
            result = await clienteStore.updateCliente(form.value.id, form.value)
        }

        emit('save', result)
        notificationStore.add(`Cliente ${props.isNew ? 'creado' : 'actualizado'} con éxito`, 'success')
        
        // [GY-UX] Auto-close on new client success or reset?
        // User requested: "que el formulario se limpie o cierre"
        if (props.isNew) {
             emit('close')
        }
    } catch(e) {
        console.error(e)
        // Show clearer error
        alert('Error al guardar: ' + (e.response?.data?.detail || e.message))
    } finally {
        saving.value = false
    }
}

const deleteDomicilio = async (dom) => {
    if (!confirm(`¿Está seguro que desea eliminar el domicilio de ${dom.calle}? Esta acción no se puede deshacer.`)) return
    
    try {
        await clientesService.deleteDomicilio(form.value.id, dom.id)
        
        // Refresh client
        const updatedClient = await clienteStore.fetchClienteById(form.value.id)
        form.value = JSON.parse(JSON.stringify(updatedClient))
        emit('switch-client', updatedClient.id) // Force refresh
        
        notificationStore.add('Domicilio eliminado', 'success')
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al eliminar domicilio', 'error')
    }
}

const toggleDomicilioActive = async (dom) => {
    try {
        const newState = !dom.activo
        // Optimistic update
        dom.activo = newState
        
        await clientesService.updateDomicilio(form.value.id, dom.id, { activo: newState })
        
        // Background refresh to ensure consistency
        await clienteStore.fetchClienteById(form.value.id)
        
        // Force list refresh to ensure indicators update in Grid/List
        clienteStore.fetchClientes()
    } catch (e) {
        console.error(e)
        dom.activo = !dom.activo // Revert on error
        notificationStore.add('Error al actualizar estado', 'error')
    }
}

const remove = () => {
    if (confirm('¿Seguro que desea dar de baja LOGICA a este cliente? (Pasará a Inactivo)')) {
        emit('delete', form.value)
    }
}

const hardDelete = () => {
    if (confirm('⚠ ATENCION: ¿Está seguro de realizar la BAJA FISICA? Esta acción eliminará permanentemente al cliente de la base de datos y no se puede deshacer.')) {
        emit('hard-delete', form.value)
    }
}

const handleKeydown = (e) => {
    if (e.code === 'F10') {
        if (showDomicilioForm.value) return // Let modal handle it
        e.preventDefault()
        save()
    }
    if (e.key === 'Escape' && !showDomicilioForm.value) { // Don't close inspector if domicile modal is open
        e.preventDefault()
        emit('close')
    }
}

onMounted(() => {
    maestrosStore.fetchAll() // Ensure we have masters
    window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})
</script>
