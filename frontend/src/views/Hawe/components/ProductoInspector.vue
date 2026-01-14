<template>
  <div class="flex h-full w-full flex-col bg-[#1a050b] text-gray-100 rounded-2xl shadow-2xl overflow-hidden border border-rose-900/40">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-rose-900/30 bg-rose-950/20 p-4 shrink-0">
      <div class="flex items-center gap-3">
          <div class="h-8 w-8 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-500 border border-rose-500/20">
             <i class="fas fa-box"></i>
          </div>
          <div>
              <h2 class="font-outfit text-lg font-bold text-white leading-none">{{ localProducto?.nombre || 'Nuevo Producto' }}</h2>
              <p class="font-mono text-xs text-rose-400/60">{{ localProducto?.sku || '---' }}</p>
          </div>
      </div>
      <button @click="$emit('close')" class="h-8 w-8 rounded-full hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-colors">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- Content Grid -->
    <div v-if="localProducto" class="flex-1 flex overflow-hidden">
        
      <!-- Left Column: Basic Info (30%) -->
      <div class="w-1/3 border-r border-rose-900/30 bg-[#2e0a13]/30 p-6 overflow-y-auto space-y-6">
          
          <!-- Image / Icon Placeholder -->
          <div class="flex justify-center">
            <div class="relative group">
                <div class="h-40 w-40 rounded-2xl bg-gradient-to-br from-[#3f0e1a] to-black flex items-center justify-center text-6xl text-rose-600 shadow-xl border border-rose-500/20 group-hover:border-rose-500/50 transition-colors">
                    <i class="fas fa-box-open"></i>
                </div>
                <div class="absolute bottom-2 right-2">
                     <button 
                        @click="$emit('toggle-active', localProducto)"
                        class="h-8 w-8 rounded-full flex items-center justify-center shadow-lg transition-transform hover:scale-110 active:scale-95"
                        :class="localProducto.activo ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
                        :title="localProducto.activo ? 'Desactivar' : 'Activar'"
                    >
                        <i :class="localProducto.activo ? 'fas fa-check' : 'fas fa-ban'"></i>
                    </button>
                </div>
            </div>
          </div>

          <!-- Basic Fields -->
          <div class="space-y-4">
               <div>
                  <label class="text-xs font-bold text-rose-200/50 uppercase block mb-1">Nombre del Producto</label>
                  <input 
                    v-model="localProducto.nombre"
                    type="text" 
                    class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none focus:bg-black/60 transition-colors text-sm font-bold"
                    placeholder="Ej: Jabón Líquido 5L"
                  />
               </div>
               
               <div>
                  <label class="text-xs font-bold text-rose-200/50 uppercase block mb-1">Código Visual (Corto)</label>
                  <input 
                    v-model="localProducto.codigo_visual"
                    type="text" 
                    class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none focus:bg-black/60 transition-colors font-mono text-sm"
                    placeholder="Ej: JL-500"
                  />
               </div>

                <div>
                  <label class="text-xs font-bold text-rose-200/50 uppercase block mb-1">Rubro / Categoría</label>
                  <select 
                    v-model="localProducto.rubro_id"
                    class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none text-sm"
                  >
                      <option :value="null" disabled>Seleccione un Rubro</option>
                      <option v-for="rubro in flattenedRubros" :key="rubro.id" :value="rubro.id">
                          {{ rubro.indent }}{{ rubro.nombre }}
                      </option>
                  </select>
               </div>
          </div>
          
           <!-- Template Selection (Only for New) -->
          <div v-if="!localProducto.id" class="p-4 rounded-xl bg-rose-500/5 border border-rose-500/10">
              <label class="text-[0.65rem] font-bold text-rose-400 uppercase tracking-widest mb-2 block">
                  <i class="fas fa-magic mr-1"></i> Usar Plantilla
              </label>
              <SmartSelect
                v-model="templateId"
                :options="productosStore.productos"
                canteraType="productos"
                placeholder="Buscar para clonar..."
                :allowCreate="true"
                @update:modelValue="handleTemplateSelect"
                @select-cantera="handleTemplateSelect"
                @create-new="handleManualTemplate"
                class="dark-smart-select text-xs"
              />
          </div>

      </div>

      <!-- Right Column: Details Tabs (70%) -->
      <div class="w-2/3 flex flex-col bg-black/20">
          
          <!-- Tabs Navigation -->
          <div class="flex border-b border-white/5 px-6 pt-4 bg-[#2e0a13]/10">
              <button 
                @click="activeTab = 'general'"
                class="pb-3 px-6 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'general' ? 'border-rose-500 text-white' : 'border-transparent text-white/40 hover:text-white'"
              >
                <i class="fas fa-sliders-h mr-2"></i> Propiedades
              </button>
              <button 
                @click="activeTab = 'costos'"
                class="pb-3 px-6 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'costos' ? 'border-rose-500 text-white' : 'border-transparent text-white/40 hover:text-white'"
              >
                <i class="fas fa-coins mr-2"></i> Costos
              </button>
          </div>

          <!-- Tab Content Scrollable Area -->
          <div class="flex-1 overflow-y-auto p-8 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-rose-900/30">
              
               <!-- TAB GENERAL -->
               <div v-if="activeTab === 'general'" class="space-y-8 animate-fadeIn">
                   <!-- Grid Logic -->
                   <div class="grid grid-cols-2 gap-6">
                       
                        <!-- Tipo Producto -->
                       <div class="space-y-1">
                          <label class="text-xs font-bold text-rose-200/50 uppercase">Tipo de Bien</label>
                          <select 
                            v-model="localProducto.tipo_producto"
                            class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none text-sm"
                          >
                              <option value="VENTA">Venta (Mercadería)</option>
                              <option value="INSUMO">Insumo Interno</option>
                              <option value="MATERIA_PRIMA">Materia Prima</option>
                              <option value="SERVICIO">Servicio</option>
                          </select>
                       </div>

                       <!-- Unidad Medida -->
                       <div class="space-y-1">
                          <label class="text-xs font-bold text-rose-200/50 uppercase">Unidad Base</label>
                          <select 
                            v-model="localProducto.unidad_medida"
                            class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none text-sm"
                          >
                              <option value="UN">Unidad (u)</option>
                              <option value="LT">Litros (l)</option>
                              <option value="KG">Kilogramos (kg)</option>
                              <option value="MT">Metros (m)</option>
                          </select>
                       </div>
                   </div>
                   
                   <!-- Logistics Box -->
                   <div class="p-5 rounded-xl bg-white/5 border border-white/5 space-y-4">
                       <h3 class="text-rose-400 text-xs font-bold uppercase tracking-widest flex items-center gap-2 pb-2 border-b border-white/5">
                           <i class="fas fa-truck-loading"></i> Logística Avanzada (Docs V5.7)
                       </h3>
                       <div class="grid grid-cols-3 gap-6">
                           <div class="space-y-1">
                               <label class="text-[10px] uppercase font-bold text-white/40 block">Factor Compra</label>
                               <div class="relative">
                                   <input 
                                        v-model.number="localProducto.factor_compra"
                                        type="number" step="0.01"
                                        class="w-full bg-black/40 border border-white/10 rounded px-2 py-1.5 text-white text-sm font-mono text-center focus:border-rose-500 focus:outline-none" 
                                   />
                                   <div class="text-[9px] text-white/30 text-center mt-1">Unid. por Bulto</div>
                               </div>
                           </div>
                           
                           <!-- Minimum Sale Qty -->
                           <div class="space-y-1">
                               <label class="text-[10px] uppercase font-bold text-white/40 block">Venta Mínima</label>
                               <div class="relative">
                                   <input 
                                        v-model.number="localProducto.venta_minima"
                                        type="number" step="0.01"
                                        class="w-full bg-black/40 border border-white/10 rounded px-2 py-1.5 text-white text-sm font-mono text-center focus:border-rose-500 focus:outline-none" 
                                   />
                                   <div class="text-[9px] text-white/30 text-center mt-1">Min. Fraccionable</div>
                               </div>
                           </div>
                           
                           <div class="flex items-center justify-center">
                                <label class="flex items-center gap-3 cursor-pointer group bg-black/20 px-4 py-2 rounded-lg border border-white/5 hover:border-white/20 transition-all w-full justify-center">
                                    <div class="relative">
                                        <input type="checkbox" v-model="localProducto.es_kit" class="peer sr-only" />
                                        <div class="h-5 w-9 rounded-full bg-white/10 peer-checked:bg-rose-500 transition-colors"></div>
                                        <div class="absolute left-1 top-1 h-3 w-3 rounded-full bg-white transition-transform peer-checked:translate-x-4"></div>
                                    </div>
                                    <span class="text-xs font-bold text-white/70 group-hover:text-white transition-colors">Es Kit</span>
                                </label>
                           </div>
                       </div>
                   </div>

               </div>

               <!-- TAB COSTOS -->
               <div v-if="activeTab === 'costos'" class="space-y-6 animate-fadeIn">
                   
                   <!-- Costo Base -->
                   <div class="grid grid-cols-2 gap-8 items-start">
                        <div class="space-y-2">
                             <label class="text-xs font-bold text-rose-200/50 uppercase block">Costo de Reposición (Neto)</label>
                             <div class="relative group">
                                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-white/30 text-lg group-focus-within:text-rose-500">$</span>
                                <input 
                                    v-model.number="localCostos.costo_reposicion"
                                    type="number" 
                                    step="0.01"
                                    class="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 pl-8 text-white font-mono text-xl font-bold focus:border-rose-500 focus:outline-none transition-colors"
                                    placeholder="0.00"
                                />
                             </div>
                             <p class="text-[10px] text-white/30 pl-1">Precio de compra sin IVA al proveedor habitual.</p>
                        </div>
                        
                        <div class="space-y-1">
                           <label class="text-xs font-bold text-rose-200/50 uppercase block">Proveedor Habitual</label>
                           <select 
                             v-model="localProducto.proveedor_habitual_id"
                             class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-3 text-white focus:border-rose-500 focus:outline-none appearance-none text-sm"
                           >
                               <option :value="null">Seleccionar Proveedor...</option>
                               <option v-for="p in proveedores" :key="p.id" :value="p.id">
                                   {{ p.razon_social || p.nombre }}
                               </option>
                           </select>
                        </div>
                   </div>

                   <hr class="border-white/5" />

                   <!-- Margenes y Precios (BIDIRECCIONAL ROCA SÓLIDA) -->
                   <div class="grid grid-cols-3 gap-6">
                        <!-- Col 1: Rentabilidad Target % -->
                        <div class="space-y-2">
                            <label class="text-xs font-bold text-cyan-400 uppercase block">Rentabilidad Target %</label>
                            <div class="relative">
                                <input 
                                    v-model.number="localCostos.rentabilidad_target"
                                    @input="updateRocaFromRent"
                                    type="number" step="0.1"
                                    class="w-full bg-cyan-900/10 border border-cyan-500/30 rounded-lg px-3 py-2 pl-3 pr-8 text-cyan-400 font-mono text-right font-bold focus:border-cyan-500 focus:outline-none focus:bg-cyan-900/20 transition-colors"
                                />
                                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-cyan-500/50 text-xs">%</span>
                            </div>
                        </div>

                        <!-- Col 2: Arrow Indicator -->
                        <div class="flex items-center justify-center pt-6 opacity-30">
                            <i class="fas fa-arrow-right text-white"></i>
                        </div>

                        <!-- Col 3: Precio Roca (Base Real) -->
                        <div class="space-y-2">
                             <label class="text-xs font-bold text-white uppercase block">Precio Roca (Base)</label>
                             <div class="relative group">
                                <span class="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 text-xs">$</span>
                                <input 
                                    v-model.number="localCostos.precio_roca"
                                    @input="updateRentFromRoca"
                                    type="number" 
                                    step="0.01"
                                    class="w-full bg-white/5 border border-white/20 rounded-lg px-3 py-2 pl-6 text-white font-mono text-right font-bold focus:border-white/40 focus:outline-none transition-colors border-l-4 border-l-white"
                                />
                             </div>
                        </div>
                   </div>

                   <!-- Calculadora de Máscara (Visual Only) -->
                   <div class="mt-6 p-6 bg-[#0a1f2e]/50 border border-cyan-500/20 rounded-2xl relative shadow-lg">
                       <div class="absolute -top-3 left-6 px-2 bg-[#1a050b] text-cyan-400 text-xs font-bold tracking-widest uppercase border border-cyan-500/20 rounded">
                           Proyecciones de Mercado
                       </div>
                       
                       <div class="grid grid-cols-2 gap-8 mt-2">
                            <!-- IVA -->
                            <div class="space-y-2">
                                 <label class="text-[10px] uppercase font-bold text-white/50 block">Alícuota IVA</label>
                                 <select 
                                    v-model="localProducto.tasa_iva_id"
                                    class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono focus:border-rose-500 focus:outline-none appearance-none"
                                    @change="updateLocalIvaRate"
                                  >
                                      <option :value="null">Seleccionar...</option>
                                      <option v-for="t in tasasIva" :key="t.id" :value="t.id">
                                          {{ t.nombre }} ({{ t.valor }}%)
                                      </option>
                                  </select>
                            </div>

                            <!-- Opciones de Máscara OUTPUTS -->
                            <div class="space-y-3">
                                <div class="flex justify-between items-center p-2 border-b border-white/5">
                                    <div class="text-[10px] text-white/50">Precio Final (C/IVA)</div>
                                    <div class="text-lg font-mono font-bold text-white">
                                        {{ formatCurrency((localCostos.precio_roca || 0) * (1 + (localCostos.iva_alicuota || 21)/100)) }}
                                    </div>
                                </div>
                            </div>
                       </div>
                   </div>
                   
               </div>
          </div>

      </div>
        
    </div>
    
    <!-- Sticky Footer Actions -->
    <div class="shrink-0 p-4 border-t border-rose-900/30 bg-[#2e0a13]/50 flex justify-end items-center gap-4 backdrop-blur-md z-50">
        <div class="mr-auto text-xs text-white/30 hidden md:block">
            <span class="font-bold">TIP:</span> Use <span class="bg-white/10 px-1 rounded text-white/60">Tab</span> para navegar y <span class="bg-white/10 px-1 rounded text-white/60">F10</span> para guardar.
        </div>
        
        <button 
            @click="$emit('close')"
            class="px-6 py-2.5 rounded-xl text-white/50 font-bold text-sm hover:text-white hover:bg-white/5 transition-colors"
        >
            Cancelar
        </button>
        <button 
            @click="save"
            class="bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-bold py-2.5 px-8 rounded-xl shadow-lg shadow-rose-900/40 transition-all active:scale-95 flex items-center gap-2"
        >
            <i class="fas fa-save"></i>
            <span>Guardar (F10)</span>
        </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductosStore } from '../../../stores/productos'
import { useNotificationStore } from '@/stores/notification'
import SmartSelect from '../../../components/ui/SmartSelect.vue'

const productosStore = useProductosStore()
const notification = useNotificationStore()
const { unidades, tasasIva, proveedores } = storeToRefs(productosStore)

const props = defineProps({
  producto: {
    type: Object,
    default: () => null
  },
  rubros: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'save', 'toggle-active'])

const activeTab = ref('general')
const localProducto = ref(null)
const localCostos = ref({
    costo_reposicion: 0,
    rentabilidad_target: 30, 
    precio_roca: 0,
    iva_alicuota: 21,
    moneda_costo: 'ARS'
})

// --- DUAL OUTPUT LOGIC (ROCA SÓLIDA) ---
const isUpdating = ref(false)

// 1. Cost + Rent -> Roca
const updateRocaFromRent = () => {
    if (isUpdating.value) return
    isUpdating.value = true
    
    const costo = Number(localCostos.value.costo_reposicion) || 0
    const rent = Number(localCostos.value.rentabilidad_target) || 0
    
    // Formula: Roca = Costo * (1 + Rent/100)
    localCostos.value.precio_roca = parseFloat((costo * (1 + rent / 100)).toFixed(2))
    
    nextTick(() => { isUpdating.value = false })
}

// 2. Cost + Roca -> Rent
const updateRentFromRoca = () => {
    if (isUpdating.value) return
    isUpdating.value = true
    
    const costo = Number(localCostos.value.costo_reposicion) || 0
    const roca = Number(localCostos.value.precio_roca) || 0
    
    if (costo > 0) {
        // Formula: Rent = ((Roca / Costo) - 1) * 100
        localCostos.value.rentabilidad_target = parseFloat((((roca / costo) - 1) * 100).toFixed(2))
    } else {
        localCostos.value.rentabilidad_target = 0
    }
    
    nextTick(() => { isUpdating.value = false })
}

// Watch Costo Reposicion -> Update Roca by default (maintaining Rent)
watch(() => localCostos.value.costo_reposicion, () => {
    updateRocaFromRent()
})
// ----------------------------

const templateId = ref(null)
const pristineName = ref('')

const flattenedRubros = computed(() => {
    const result = []
    const traverse = (items, level = 0) => {
        for (const item of items) {
            result.push({
                ...item,
                indent: '\u00A0\u00A0'.repeat(level) + (level > 0 ? '└ ' : '')
            })
            if (item.hijos && item.hijos.length) traverse(item.hijos, level + 1)
        }
    }
    traverse(props.rubros)
    return result
})

watch(() => props.producto, (newVal) => {
    if (newVal) {
        localProducto.value = JSON.parse(JSON.stringify(newVal))
        
        // Ensure default venta_minima
        if (localProducto.value.venta_minima === undefined || localProducto.value.venta_minima === null) {
            localProducto.value.venta_minima = 1.0;
        }

        if (newVal.costos) {
            localCostos.value = { ...newVal.costos }
        } else {
            localCostos.value = { 
                costo_reposicion: 0, 
                margen_mayorista: 30, 
                iva_alicuota: 21,
                cm_objetivo: null,
                precio_fijo_override: null
            }
        }
    } else {
        localProducto.value = null
    }
    pristineName.value = localProducto.value?.nombre || ''
    templateId.value = null 
}, { immediate: true })

const handleTemplateSelect = (itemOrId) => {
    let template = typeof itemOrId === 'object' ? itemOrId : productosStore.productos.find(p => p.id === itemOrId);
    if (template) {
        const originalActive = localProducto.value.activo;
        localProducto.value = {
            ...JSON.parse(JSON.stringify(template)),
            id: null,
            sku: 'AUTO',
            activo: originalActive,
            venta_minima: template.venta_minima || 1.0
        };
        if (template.costos) {
            localCostos.value = { ...template.costos };
        }
        pristineName.value = template.nombre;
        nextTick(() => {
            const nameInput = document.querySelector('input[type="text"]');
            if (nameInput) nameInput.focus();
        });
    }
}

const handleManualTemplate = (name) => {
    if (name) {
        localProducto.value.nombre = name
        pristineName.value = name
        // Initialize simple default
        if (!localProducto.value.venta_minima) localProducto.value.venta_minima = 1.0;
        
        nextTick(() => {
             const nameInput = document.querySelector('input[type="text"]');
             if (nameInput) nameInput.focus();
        });
    }
    templateId.value = null
    notification.add('Alta Manual: Complete los datos', 'info')
}

const simulatedPrices = computed(() => {
    const costo = Number(localCostos.value.costo_reposicion) || 0
    const margen = Number(localCostos.value.margen_mayorista) || 0
    // Simplified calculation for display
    const mayoristaByMargin = costo * (1 + margen/100)
    return { mayoristaByMargin }
})

const formatCurrency = (val) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(val)

const save = () => {
    if (!localProducto.value) return
    if (!localProducto.value.id && localProducto.value.nombre === pristineName.value) {
        notification.add('Modifique el nombre para crear un nuevo producto.', 'warning')
        return;
    }
    const payload = {
        ...localProducto.value,
        costos: { ...localCostos.value }
    }
    emit('save', payload)
}

const updateLocalIvaRate = () => {
    const selectedTasa = tasasIva.value.find(t => t.id === localProducto.value.tasa_iva_id)
    if (selectedTasa) localCostos.value.iva_alicuota = Number(selectedTasa.valor)
}

const handleKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault()
        e.stopPropagation()
        save()
    }
}

onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
    productosStore.fetchUnidades()
    productosStore.fetchTasasIva()
    productosStore.fetchProveedores()
})
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<style scoped>
.animate-fadeIn {
    animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
