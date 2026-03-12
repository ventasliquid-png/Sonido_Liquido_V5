<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
    <div class="bg-[#0f172a] w-full max-w-[95vw] h-[90vh] rounded-xl border border-amber-500/30 shadow-[0_0_50px_rgba(245,158,11,0.1)] flex flex-col overflow-hidden relative">
        

        <!-- EXPLICIT TITLE BAR -->
        <div class="bg-amber-500/10 border-b border-amber-500/20 py-2 px-6 flex justify-between items-center shrink-0">
            <div class="flex items-center gap-3">
                 <i class="fas fa-truck-front text-amber-500 text-lg"></i>
                 <h1 class="text-xs font-black uppercase tracking-[0.2em] text-amber-500">
                    FICHA ALTA DE TRANSPORTE
                 </h1>
            </div>
            <div class="flex items-center gap-4">
                 <span class="text-[10px] text-white/30 font-mono" v-if="!isNew">ID: {{ modelValue.id }}</span>
                 <button @click="$emit('close')" class="text-white/30 hover:text-white transition-colors">
                    <i class="fas fa-times text-lg"></i>
                 </button>
            </div>
        </div>

        <!-- MAIN BODY: Scrollable -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-amber-900/50 scrollbar-track-black/20">
            
            <!-- RECTANGLE 1: IDENTITY & DATA -->
            <section class="bg-black/20 border border-white/5 rounded-lg p-5 space-y-5 shadow-inner">
                 <!-- Row 1: Name | Address | Location | Province -->
                 <div class="grid grid-cols-12 gap-4 items-end">
                      <!-- Name -->
                      <div class="col-span-4 group">
                          <label class="block text-[10px] font-bold text-amber-500/60 uppercase mb-1 tracking-wider">
                              Razón Social <span class="text-red-500">*</span>
                          </label>
                          <div class="relative">
                              <input 
                                 ref="nameInput"
                                 v-model="localModel.nombre" 
                                 class="input-hawe-gold w-full text-lg font-bold" 
                                 placeholder="Nombre del Transporte" 
                              />
                              <i class="fas fa-pen absolute right-3 top-3 text-white/10 text-xs"></i>
                          </div>
                      </div>
                      
                      <!-- Tax Address -->
                      <div class="col-span-4">
                          <label class="block text-[10px] font-bold text-white/30 uppercase mb-1">Dirección Fiscal</label>
                          <input v-model="localModel.direccion" class="input-hawe-gold w-full text-sm" placeholder="Calle, Número, Piso..." />
                      </div>

                      <!-- Location -->
                      <div class="col-span-2">
                          <label class="block text-[10px] font-bold text-white/30 uppercase mb-1">Localidad</label>
                          <input v-model="localModel.localidad" class="input-hawe-gold w-full text-xs" placeholder="Localidad" />
                      </div>

                      <!-- Province -->
                      <div class="col-span-2">
                          <label class="block text-[10px] font-bold text-white/30 uppercase mb-1">Provincia</label>
                          <select v-model="localModel.provincia_id" class="input-hawe-gold w-full text-xs">
                               <option :value="null">Seleccionar</option>
                               <option v-for="prov in provincias" :key="prov.id" :value="prov.id">{{ prov.nombre }}</option>
                          </select>
                      </div>
                 </div>

                 <!-- Row 2: Fiscal Data | Separator | Contact Data -->
                 <!-- No titles "Datos Fiscales" or "Datos de Contacto" as requested -->
                 <div class="flex items-center gap-6 pt-3 border-t border-white/5">
                      
                      <!-- Fiscal Data Group -->
                      <div class="flex items-end gap-3 w-1/3">
                           <div class="flex-1">
                               <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">CUIT <span class="text-red-500">*</span></label>
                               <input v-model="localModel.cuit" class="input-hawe-gold w-full font-mono text-xs" placeholder="XX-XXXXXXXX-X" :class="{'border-red-500 text-red-400': cuitError}" />
                               <p v-if="cuitError" class="text-[9px] text-red-400 mt-1 font-bold">{{ cuitError }}</p>
                           </div>
                           <div class="flex-1">
                               <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Condición IVA <span class="text-red-500">*</span></label>
                               <select v-model="localModel.condicion_iva_id" class="input-hawe-gold w-full text-xs">
                                   <option :value="null">Sel. IVA</option>
                                   <option v-for="ci in condicionesIva" :key="ci.id" :value="ci.id">{{ ci.nombre }}</option>
                               </select>
                           </div>
                      </div>

                      <!-- Vertical Separator -->
                      <div class="w-px h-10 bg-white/10"></div>

                      <!-- Contact Data Group -->
                      <div class="flex items-end gap-3 flex-1">
                           <div class="flex-1 min-w-[120px]">
                               <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Teléfono</label>
                               <input v-model="localModel.telefono_reclamos" class="input-hawe-gold w-full text-xs" placeholder="Fijo/Móvil" />
                           </div>
                           <div class="flex-1 min-w-[120px]">
                               <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">WhatsApp</label>
                               <input v-model="localModel.whatsapp" class="input-hawe-gold w-full text-xs" placeholder="+54 9..." />
                           </div>
                           <div class="flex-1 min-w-[150px]">
                               <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Email</label>
                               <input v-model="localModel.email" class="input-hawe-gold w-full text-xs" placeholder="contacto@..." />
                           </div>
                           <div class="flex-1 min-w-[150px]">
                               <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Web / Tracking</label>
                               <input v-model="localModel.web_tracking" class="input-hawe-gold w-full text-xs" placeholder="https://..." />
                           </div>
                      </div>
                 </div>
            </section>

            <!-- RECTANGLE 2: DISPATCH (CABA/AMBA) -->
            <section class="bg-black/20 border border-white/5 rounded-lg p-5 shadow-inner">
                 <!-- Header Row with Inline Controls -->
                 <div class="flex items-center gap-6 mb-2 h-8">
                     <h3 class="text-sm font-bold text-amber-500 uppercase tracking-wider shrink-0">
                        Despacho y Recepción (CABA/AMBA)
                     </h3>
                     
                     <div class="flex items-center ml-4">
                           <input type="checkbox" v-model="dispatchSameAsCentral" id="sameAddress" class="h-4 w-4 rounded accent-amber-500 cursor-pointer">
                           <label for="sameAddress" class="ml-2 text-[11px] font-bold text-white/70 cursor-pointer select-none uppercase tracking-wide">Misma que Central</label>
                     </div>

                     <!-- Operational Flags Checked -->
                     <div class="ml-auto flex items-center gap-6">
                           <div class="checkbox-wrapper flex items-center gap-2">
                                <input id="chkPickup" type="checkbox" v-model="localModel.servicio_retiro_domicilio" class="h-3.5 w-3.5 rounded accent-green-500 cursor-pointer" />
                                <label for="chkPickup" class="text-[10px] font-bold text-white/50 cursor-pointer uppercase">Acepta Retiro</label>
                           </div>
                           <div class="checkbox-wrapper flex items-center gap-2">
                                <input id="chkWeb" type="checkbox" v-model="localModel.requiere_carga_web" class="h-3.5 w-3.5 rounded accent-purple-500 cursor-pointer" />
                                <label for="chkWeb" class="text-[10px] font-bold text-white/50 cursor-pointer uppercase">Requiere Carga Web Obligatoria</label>
                           </div>
                     </div>
                 </div>

                 <!-- Body Row (Conditional) - ALL IN ONE LINE -->
                 <div v-if="!dispatchSameAsCentral" class="grid grid-cols-12 gap-4 items-end mt-4 animate-fade-in-down border-t border-white/5 pt-4">
                      <!-- Dispatch Address -->
                      <div class="col-span-4">
                          <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Dirección Despacho</label>
                          <input v-model="localModel.direccion_despacho" class="input-hawe-gold w-full text-xs" placeholder="Dirección CABA..." />
                      </div>
                      
                      <!-- Hours -->
                      <div class="col-span-3">
                          <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Horario Recepción</label>
                          <input v-model="localModel.horario_despacho" class="input-hawe-gold w-full text-xs" placeholder="Ej: 8:00 a 16:00" />
                      </div>

                      <!-- Phone Dispatch -->
                      <div class="col-span-2">
                          <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Tel. Despacho</label>
                          <input v-model="localModel.telefono_despacho" class="input-hawe-gold w-full text-xs" placeholder="Tel. Puerta" />
                      </div>

                      <!-- Contact Note (Using internal observation or extra field? Let's assume generic extra field or override contact) -->
                      <!-- User asked for "Contacto". -->
                       <div class="col-span-3">
                          <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Contacto / Ref.</label>
                          <input v-model="localModel.contacto_despacho" class="input-hawe-gold w-full text-xs" placeholder="Persona de contacto" />
                      </div>
                 </div>
            </section>

            <!-- RECTANGLE 3: BRANCHES (SUCURSAL 1) -->
            <section class="bg-black/20 border border-white/5 rounded-lg p-5 shadow-inner">
                 <!-- If NOT New, Normal List -->
                 <div v-if="!isNew">
                     <div class="flex justify-between items-center mb-4">
                         <h3 class="text-sm font-bold text-emerald-500 uppercase tracking-wider">Sucursales (Destinos)</h3>
                         <button @click="openBranchModal" class="text-[10px] bg-emerald-900/40 text-emerald-400 hover:text-white px-3 py-1 rounded border border-emerald-500/30 uppercase font-bold transition-all">
                             + Nueva Sucursal
                         </button>
                     </div>
                     <TransporteBranches :transport-id="modelValue.id" />
                 </div>

                 <!-- If IS New, Show "Carga Sucursal 1" Form -->
                 <div v-else>
                     <div class="flex items-center gap-2 mb-3">
                         <i class="fas fa-map-marked-alt text-emerald-500/70"></i>
                         <h3 class="text-sm font-bold text-emerald-500/80 uppercase tracking-wider">Datos de Carga de Sucursal 1 (Opcional)</h3>
                     </div>
                     
                     <div class="bg-emerald-900/5 border border-emerald-500/10 rounded-lg p-3 grid grid-cols-12 gap-3 items-end">
                          <div class="col-span-3">
                              <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Nombre Sucursal</label>
                              <input v-model="firstBranch.nombre_nodo" class="input-hawe-gold w-full text-xs border-emerald-500/20 focus:border-emerald-500" placeholder="Ej: Sucursal Córdoba" />
                          </div>
                          <div class="col-span-3">
                              <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Dirección</label>
                              <input v-model="firstBranch.direccion_completa" class="input-hawe-gold w-full text-xs border-emerald-500/20 focus:border-emerald-500" placeholder="Dirección local" />
                          </div>
                          <div class="col-span-2">
                              <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Localidad</label>
                              <input v-model="firstBranch.localidad" class="input-hawe-gold w-full text-xs border-emerald-500/20 focus:border-emerald-500" placeholder="Localidad" />
                          </div>
                          <div class="col-span-2">
                              <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Provincia</label>
                              <select v-model="firstBranch.provincia_id" class="input-hawe-gold w-full text-xs border-emerald-500/20 focus:border-emerald-500">
                                   <option :value="null">Seleccionar</option>
                                   <option v-for="prov in provincias" :key="prov.id" :value="prov.id">{{ prov.nombre }}</option>
                              </select>
                          </div>
                          <div class="col-span-2">
                              <label class="block text-[9px] font-bold text-white/20 uppercase mb-1">Teléfono</label>
                              <input v-model="firstBranch.telefono" class="input-hawe-gold w-full text-xs border-emerald-500/20 focus:border-emerald-500" placeholder="Tel. Sucursal" />
                          </div>
                     </div>
                 </div>
            </section>
            
            <!-- RECTANGLE 4: NOTES (Bottom) -->
            <section class="bg-black/20 border border-white/5 rounded-lg p-5">
                <div v-if="!showNotes && !localModel.observaciones" class="flex justify-start">
                     <button @click="showNotes = true" class="text-xs font-bold text-white/30 uppercase tracking-widest hover:text-white bg-white/5 hover:bg-white/10 px-4 py-2 rounded border border-white/5 hover:border-white/20 transition-all flex items-center gap-2">
                        <i class="fas fa-comment-alt"></i> Agregar Observaciones
                     </button>
                </div>
                <div v-else class="animate-fade-in-up">
                    <div class="flex justify-between items-center mb-2">
                        <label class="text-xs font-bold text-amber-500/70 uppercase tracking-wider"><i class="fas fa-comment-alt mr-1"></i> Observaciones</label>
                        <button v-if="!localModel.observaciones" @click="showNotes = false" class="text-[10px] text-white/30 hover:text-red-400 uppercase">Ocultar</button>
                    </div>
                    <textarea 
                        v-model="localModel.observaciones" 
                        rows="3" 
                        class="w-full bg-black/40 border border-white/10 rounded p-3 text-white focus:border-amber-500 outline-none transition-all resize-none text-sm placeholder-white/10 shadow-inner"
                        placeholder="Notas internas..."
                    ></textarea>
                </div>
            </section>

        </div>

        <!-- FOOTER: Actions -->
        <div class="h-16 border-t border-white/10 bg-black/40 flex items-center justify-between px-6 shrink-0 z-20 backdrop-blur-md">
             <div class="text-[10px] text-white/20 font-mono">
                 <span v-if="localModel.updated_at">Actualizado: {{ formatDate(localModel.updated_at) }}</span>
             </div>
             <div class="flex gap-4">
                  <button @click="$emit('close')" class="px-6 py-2 rounded border border-white/10 text-white/40 hover:text-white hover:bg-white/5 transition-colors font-bold text-xs uppercase tracking-wider">
                      Cancelar
                  </button>
                  <button @click="save" class="px-8 py-2 rounded bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-500 hover:to-yellow-500 text-white font-bold shadow-lg shadow-amber-900/40 transition-all flex items-center gap-2 text-xs uppercase tracking-wide">
                      <span v-if="saving"><i class="fas fa-spinner fa-spin"></i> Procesando...</span>
                      <span v-else><i class="fas fa-save"></i> Guardar Ficha</span>
                  </button>
             </div>
        </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed, nextTick } from 'vue';
import { useLogisticaStore } from '../../../stores/logistica';
import { useMaestrosStore } from '../../../stores/maestros';
import { useNotificationStore } from '../../../stores/notification';
import TransporteBranches from './TransporteBranches.vue'; 

const props = defineProps({
    modelValue: {
        type: Object,
        default: () => ({})
    }
});

const emit = defineEmits(['update:modelValue', 'close', 'save']);

// Stores
const logisticaStore = useLogisticaStore();
const maestrosStore = useMaestrosStore();
const notification = useNotificationStore();

// Local State
const localModel = ref({ ...props.modelValue });
const dispatchSameAsCentral = ref(false);
const saving = ref(false);
const showNotes = ref(false);
const nameInput = ref(null);

// Pending Branch State (Sucursal 1)
const firstBranch = ref({
    nombre_nodo: '',
    direccion_completa: '',
    localidad: '',
    provincia_id: null,
    telefono: '',
    es_punto_despacho: false,
    es_punto_retiro: true
});

const isNew = computed(() => !localModel.value.id);
const provincias = computed(() => maestrosStore.provincias);
const condicionesIva = computed(() => maestrosStore.condicionesIva);

// Watchers
watch(() => props.modelValue, (val) => {
    localModel.value = { ...val };
    checkDispatchSimilarity();
    if (val.observaciones) showNotes.value = true;
}, { deep: true });

watch(dispatchSameAsCentral, (val) => {
    if (val) {
        localModel.value.direccion_despacho = localModel.value.direccion;
        // Also clear specific fields if we want strict mirroring, but soft mirror is safer
    }
});

// Methods
const checkDispatchSimilarity = () => {
    if (!localModel.value.direccion_despacho && localModel.value.direccion) {
        dispatchSameAsCentral.value = false; 
    } else if (localModel.value.direccion_despacho === localModel.value.direccion) {
        dispatchSameAsCentral.value = true;
    }
};

const cuitError = ref(null);

const validateCuit = (cuit) => {
    if (!cuit) {
        cuitError.value = null;
        return true; 
    }

    // 1. STRICT FORMAT CHECK: If separators are used, they MUST be at positions 3 and 12 (Indices 2 and 11)
    // Acceptable separators: - _ / . space
    if (cuit.length > 11) {
        // Regex: 2 digits + separator + 8 digits + separator + 1 digit
        // Separators allowed: [- _ / . space]
        const strictPattern = /^\d{2}[-_\/.\s]\d{8}[-_\/.\s]\d{1}$/;
        if (!strictPattern.test(cuit)) {
            cuitError.value = 'Formato inválido. Usar XX-XXXXXXXX-X o solo números.';
            return false;
        }
    }

    // 2. DIGIT CHECK (Standard Algo)
    const clean = cuit.replace(/[^0-9]/g, '');
    if (clean.length !== 11) {
        cuitError.value = 'Debe tener 11 números';
        return false;
    }
    
    // Excepción de CUITs Genéricos
    if (['00000000000', '99999999999', '11111111111'].includes(clean)) {
        cuitError.value = null;
        return true;
    }
    
    const multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
    let total = 0;
    for (let i = 0; i < 10; i++) {
        total += parseInt(clean[i]) * multipliers[i];
    }
    
    let mod = total % 11;
    let digit = mod === 0 ? 0 : 11 - mod;
    if (digit === 10) digit = 9; 
    
    const valid = digit === parseInt(clean[10]);
    cuitError.value = valid ? null : 'CUIT inválido (Dígito verif. incorrecto)';
    return valid;
};

// Real-time validation
watch(() => localModel.value.cuit, (val) => {
    validateCuit(val);
});

const save = async () => {
    // Validation
    const errors = [];
    if (!localModel.value.nombre) errors.push('Razón Social');
    if (!localModel.value.condicion_iva_id) errors.push('Condición de IVA');

    // Conditional CUIT Check
    const selectedIva = condicionesIva.value.find(c => c.id === localModel.value.condicion_iva_id);
    const isConsumidorFinal = selectedIva ? selectedIva.nombre.toLowerCase().includes('consumidor final') : false;

    if (!localModel.value.cuit) {
        if (!isConsumidorFinal) {
             errors.push('CUIT (Obligatorio)');
        }
    } else {
        if (!validateCuit(localModel.value.cuit)) {
            errors.push('CUIT (' + (cuitError.value || 'Inválido') + ')');
        }
    }

    if (errors.length > 0) {
        const msg = 'Faltan datos obligatorios o son inválidos:\n\n- ' + errors.join('\n- ');
        notification.add('Verifique los datos faltantes', 'error'); 
        alert(msg); 
        return;
    }

    saving.value = true;
    try {
        if (dispatchSameAsCentral.value) {
            localModel.value.direccion_despacho = localModel.value.direccion;
        }
        
        // SANITIZE CUIT BEFORE SENDING (ARCA COMPLIANCE)
        // Ensure we send only numbers, stripping any separators used for display/input
        const payload = { ...localModel.value };
        if (payload.cuit) {
            payload.cuit = payload.cuit.replace(/[^0-9]/g, '');
        }

        let createdId = payload.id;
        
        // 1. Save Transport
        if (isNew.value) {
            const res = await logisticaStore.createEmpresa(payload);
            createdId = res.id;

            
            // 2. Save First Branch (If filled)
            if (firstBranch.value.nombre_nodo) {
                try {
                    await logisticaStore.createNodo({
                        ...firstBranch.value,
                        empresa_id: createdId
                    });
                    notification.add('Transporte y Sucursal creados', 'success');
                } catch (err) {
                    console.error(err);
                    notification.add('Advertencia: Transporte creado pero falló Sucursal 1', 'warning');
                }
            } else {
                notification.add('Transporte creado (Sin sucursal)', 'success');
            }
        } else {
            // Fix: Use sanitized payload here too
            await logisticaStore.updateEmpresa(payload.id, payload);
            notification.add('Transporte actualizado', 'success');
        }
        
        emit('save', createdId);
        emit('close');
    } catch (e) {
        console.error(e);
        const errorMsg = e.response?.data?.message || e.message || 'Error desconocido al guardar';
        notification.add(errorMsg, 'error');
        alert('Error al guardar:\n' + errorMsg);
    } finally {
        saving.value = false;
    }
};

const formatDate = (date) => {
    if (!date) return '';
    return new Date(date).toLocaleDateString();
};

onMounted(async () => {
    if (maestrosStore.provincias.length === 0) await maestrosStore.fetchProvincias();
    if (maestrosStore.condicionesIva.length === 0) await maestrosStore.fetchCondicionesIva();
    checkDispatchSimilarity();
    if (localModel.value.observaciones) showNotes.value = true;
    
    // Autofocus
    nextTick(() => {
        if (nameInput.value) nameInput.value.focus();
    });

    window.addEventListener('keydown', handleKeydown);
});

import { onUnmounted } from 'vue';

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});

const handleKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault();
        save();
    }
    if (e.key === 'Escape') {
        e.preventDefault();
        emit('close');
    }
};
</script>

<style scoped>
.input-hawe-gold {
    @apply bg-black/40 border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all placeholder-white/20;
}
.animate-fade-in-down {
    animation: fadeInDown 0.3s ease-out;
}
.animate-fade-in-up {
    animation: fadeInUp 0.3s ease-out;
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
