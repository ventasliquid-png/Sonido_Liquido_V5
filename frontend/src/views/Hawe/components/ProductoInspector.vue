<template>
  <div class="flex h-full w-full flex-col border-l border-white/10 bg-[#1a050b]/95 backdrop-blur-xl transition-all">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-white/10 p-4 shrink-0">
      <h2 class="font-outfit text-sm font-bold uppercase tracking-wider text-rose-400">Inspector de Producto</h2>
      <button @click="$emit('close')" class="text-white/50 hover:text-white">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- Content -->
    <div v-if="localProducto" class="flex-1 flex flex-col overflow-hidden">
      <!-- Top Info -->
      <div class="p-6 pb-2 text-center shrink-0">
        <div class="mb-4 flex flex-col items-center gap-3">
          <!-- Toggle Switch -->
           <button 
              @click="$emit('toggle-active', localProducto)"
              class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none bg-black/40 border border-white/10"
              :class="localProducto.activo ? 'border-green-500/50' : 'border-red-500/50'"
              title="Click para cambiar estado"
          >
              <span 
                  class="inline-block h-3 w-3 transform rounded-full transition-transform shadow-sm"
                  :class="localProducto.activo ? 'translate-x-5 bg-green-400' : 'translate-x-1 bg-red-400'"
              ></span>
          </button>

          <!-- Icon -->
          <div class="flex h-20 w-20 items-center justify-center rounded-xl bg-gradient-to-br from-[#3f0e1a] to-black text-4xl text-rose-500 shadow-lg border border-rose-500/20">
            <i class="fas fa-box"></i>
          </div>
        </div>
        <h3 class="font-outfit text-xl font-bold text-white leading-tight">{{ localProducto.nombre }}</h3>
        <p class="font-mono text-sm text-rose-400/70 mt-1">SKU: {{ localProducto.sku }}</p>
      </div>

      <!-- Tabs Header -->
      <div class="flex border-b border-white/10 px-6 mt-4 shrink-0">
          <button 
            @click="activeTab = 'general'"
            class="pb-2 px-4 text-sm font-medium transition-colors border-b-2"
            :class="activeTab === 'general' ? 'border-rose-500 text-white' : 'border-transparent text-white/50 hover:text-white'"
          >
            GENERAL
          </button>
          <button 
            @click="activeTab = 'costos'"
            class="pb-2 px-4 text-sm font-medium transition-colors border-b-2"
            :class="activeTab === 'costos' ? 'border-rose-500 text-white' : 'border-transparent text-white/50 hover:text-white'"
          >
            COSTOS
          </button>
      </div>

      <!-- Tabs Content -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-black/20 scrollbar-thumb-rose-900/50">
          
          <!-- SELECCIÓN POR PLANTILLA (F4 Flow) -->
          <div v-if="!localProducto.id" class="mb-6 p-4 rounded-lg bg-rose-500/5 border border-rose-500/20">
              <label class="text-[0.65rem] font-bold text-rose-400 uppercase tracking-widest mb-2 block">
                  Cargar desde Plantilla / Cantera
              </label>
              <SmartSelect
                v-model="templateId"
                :options="productosStore.productos"
                canteraType="productos"
                placeholder="Buscar producto para clonar..."
                :allowCreate="false"
                @update:modelValue="handleTemplateSelect"
                @select-cantera="handleTemplateSelect"
                class="dark-smart-select"
              />
              <p class="text-[10px] text-white/30 mt-2 italic">
                  Tip: Seleccione un producto similar para heredar costos y rubros.
              </p>
          </div>

          <!-- TAB GENERAL -->
          <div v-if="activeTab === 'general'" class="space-y-5">
              <!-- Nombre -->
              <div class="space-y-1">
                  <label class="text-xs font-bold text-white/60 uppercase">Nombre del Producto</label>
                  <input 
                    v-model="localProducto.nombre"
                    type="text" 
                    class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors"
                    placeholder="Ej: Jabón Líquido 5L"
                    autocomplete="off"
                    spellcheck="false"
                  />
              </div>

              <!-- Código Visual -->
              <div class="space-y-1">
                  <label class="text-xs font-bold text-white/60 uppercase">Código Visual</label>
                    v-model="localProducto.codigo_visual"
                    type="text" 
                    class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors font-mono"
                    placeholder="Ej: JL-500"
                  />
              </div>

              <!-- CALCULADORA DE MÁSCARA (V5.7 SOCRATIC LOGIC) -->
              <div class="mt-8 p-4 bg-emerald-900/10 border border-emerald-500/20 rounded-xl space-y-4">
                  <div class="flex items-center gap-2 mb-2">
                       <i class="fas fa-calculator text-emerald-400"></i>
                       <h4 class="text-xs font-bold text-emerald-400 uppercase tracking-wider">Calculadora de Máscara</h4>
                  </div>
                  
                  <div class="grid grid-cols-2 gap-4">
                      <!-- Input: LA ROCA -->
                      <div class="col-span-2 space-y-1">
                          <label class="text-[10px] uppercase font-bold text-white/50 block">Definir "La Roca" (Neto Base Real)</label>
                          <div class="relative">
                              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-white/30">$</span>
                              <input 
                                v-model.number="calculadora.roca" 
                                type="number" 
                                class="w-full bg-black/40 border border-white/10 rounded px-8 py-2 text-white font-mono font-bold text-right focus:border-emerald-500 focus:outline-none"
                                placeholder="0.00"
                              />
                          </div>
                      </div>

                      <!-- Output: LISTA 1 (FISCAL) -->
                      <div class="p-3 bg-black/20 rounded border border-white/5 relative group cursor-pointer" @click="aplicarMascara('FISCAL')">
                           <div class="absolute top-1 right-2 text-[8px] text-white/30">CLICK PARA APLICAR</div>
                           <label class="text-[9px] uppercase font-bold text-blue-400 block mb-1">Máscara Fiscal (20% OFF)</label>
                           <div class="text-lg font-mono font-bold text-white text-right">{{ formatCurrency(calculadora.maskFiscal) }}</div>
                           <div class="text-[9px] text-right text-white/40 mt-1">
                               Neto: {{ formatCurrency(calculadora.roca) }} + IVA
                           </div>
                      </div>

                      <!-- Output: LISTA 2 (BLUE) -->
                      <div class="p-3 bg-black/20 rounded border border-white/5 relative group cursor-pointer" @click="aplicarMascara('BLUE')">
                           <div class="absolute top-1 right-2 text-[8px] text-white/30">CLICK PARA APLICAR</div>
                           <label class="text-[9px] uppercase font-bold text-purple-400 block mb-1">Máscara Blue (10% OFF)</label>
                           <div class="text-lg font-mono font-bold text-white text-right">{{ formatCurrency(calculadora.maskBlue) }}</div>
                           <div class="text-[9px] text-right text-white/40 mt-1">
                               Final: {{ formatCurrency(calculadora.maskBlue * 0.90) }}
                           </div>
                      </div>
                  </div>
              </div>

              <!-- Rubro -->
              <div class="space-y-1">
                  <label class="text-xs font-bold text-white/60 uppercase">Rubro / Categoría</label>
                  <select 
                    v-model="localProducto.rubro_id"
                    class="w-full bg-[#1a050b] border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none"
                  >
                      <option :value="null" disabled class="bg-[#1a050b] text-white">Seleccione un Rubro</option>
                      <option v-for="rubro in flattenedRubros" :key="rubro.id" :value="rubro.id" class="bg-[#1a050b] text-white">
                          {{ rubro.indent }}{{ rubro.nombre }}
                      </option>
                  </select>
              </div>

              <!-- Tipo Producto -->
              <div class="space-y-1">
                  <label class="text-xs font-bold text-white/60 uppercase">Tipo Producto</label>
                  <select 
                    v-model="localProducto.tipo_producto"
                    class="w-full bg-[#1a050b] border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none"
                  >
                      <option value="VENTA" class="bg-[#1a050b] text-white">Venta</option>
                      <option value="INSUMO" class="bg-[#1a050b] text-white">Insumo</option>
                      <option value="MATERIA_PRIMA" class="bg-[#1a050b] text-white">Materia Prima</option>
                      <option value="SERVICIO" class="bg-[#1a050b] text-white">Servicio</option>
                  </select>
              </div>

              <!-- Logística de Unidades -->
              <div class="p-4 rounded-lg bg-white/5 border border-white/10 space-y-4">
                  <h4 class="text-rose-400 text-xs font-bold uppercase flex items-center gap-2">
                      <i class="fas fa-truck-loading"></i> Logística de Unidades
                  </h4>
                  
                  <div class="grid grid-cols-2 gap-4">
                      <!-- Unidad Stock -->
                      <div class="space-y-1">
                          <label class="text-xs font-bold text-white/60 uppercase">Unidad Stock</label>
                          <select 
                            v-model="localProducto.unidad_stock_id"
                            class="w-full bg-[#1a050b] border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none"
                          >
                              <option :value="null" class="bg-[#1a050b] text-white">Seleccionar...</option>
                              <option v-for="u in unidades" :key="u.id" :value="u.id" class="bg-[#1a050b] text-white">
                                  {{ u.nombre }} ({{ u.codigo }})
                              </option>
                          </select>
                      </div>

                      <!-- Unidad Compra -->
                      <div class="space-y-1">
                          <label class="text-xs font-bold text-white/60 uppercase">Unidad Compra</label>
                          <select 
                            v-model="localProducto.unidad_compra_id"
                            class="w-full bg-[#1a050b] border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none"
                          >
                              <option :value="null" class="bg-[#1a050b] text-white">Seleccionar...</option>
                              <option v-for="u in unidades" :key="u.id" :value="u.id" class="bg-[#1a050b] text-white">
                                  {{ u.nombre }} ({{ u.codigo }})
                              </option>
                          </select>
                      </div>
                  </div>

                  <!-- Factor Conversión -->
                  <div class="space-y-1">
                      <label class="text-xs font-bold text-white/60 uppercase">Factor Conversión (Compra -> Stock)</label>
                      <input 
                        v-model.number="localProducto.factor_compra"
                        type="number" 
                        step="0.01"
                        class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors font-mono"
                        placeholder="Ej: 1.00"
                      />
                  </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                  <!-- Unidad -->
                  <div class="space-y-1">
                      <label class="text-xs font-bold text-white/60 uppercase">Unidad</label>
                      <select 
                        v-model="localProducto.unidad_medida"
                        class="w-full bg-[#1a050b] border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors"
                      >
                          <option value="UN" class="bg-[#1a050b] text-white">Unidad</option>
                          <option value="LT" class="bg-[#1a050b] text-white">Litro</option>
                          <option value="KG" class="bg-[#1a050b] text-white">Kilo</option>
                          <option value="MT" class="bg-[#1a050b] text-white">Metro</option>
                      </select>
                  </div>
                  
                  <!-- Es Kit -->
                  <div class="flex items-center justify-center pt-6">
                      <label class="flex items-center gap-3 cursor-pointer group">
                          <div class="relative">
                              <input type="checkbox" v-model="localProducto.es_kit" class="peer sr-only" />
                              <div class="h-6 w-11 rounded-full bg-white/10 peer-checked:bg-rose-500 transition-colors"></div>
                              <div class="absolute left-1 top-1 h-4 w-4 rounded-full bg-white transition-transform peer-checked:translate-x-5"></div>
                          </div>
                          <span class="text-sm font-medium text-white/70 group-hover:text-white transition-colors">Es Kit</span>
                      </label>
                  </div>
              </div>
          </div>

          <!-- TAB COSTOS -->
          <div v-if="activeTab === 'costos'" class="space-y-6">
              <div class="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20">
                  <h4 class="text-rose-400 text-xs font-bold uppercase mb-3 flex items-center gap-2">
                      <i class="fas fa-coins"></i> Estructura de Costos
                  </h4>

                  <!-- Proveedor Habitual -->
                  <div class="mb-4">
                      <label class="text-xs text-white/60 block mb-1">Proveedor Habitual</label>
                      <select 
                        v-model="localProducto.proveedor_habitual_id"
                        class="w-full bg-[#1a050b] border border-white/10 rounded px-3 py-2 text-white focus:border-rose-500 focus:outline-none appearance-none"
                      >
                          <option :value="null" class="bg-[#1a050b] text-white">Seleccionar Proveedor...</option>
                          <option v-for="p in proveedores" :key="p.id" :value="p.id" class="bg-[#1a050b] text-white">
                              {{ p.razon_social || p.nombre }}
                          </option>
                      </select>
                  </div>
                  
                  <div class="space-y-4">
                      <!-- Costo Reposición -->
                      <div>
                          <label class="text-xs text-white/60 block mb-1">Costo Reposición (Neto)</label>
                          <div class="relative">
                              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-white/30">$</span>
                              <input 
                                v-model.number="localCostos.costo_reposicion"
                                type="number" 
                                step="0.01"
                                class="w-full bg-black/40 border border-white/10 rounded px-3 py-2 pl-7 text-white font-mono focus:border-rose-500 focus:outline-none"
                              />
                          </div>
                      </div>

                      <div class="grid grid-cols-2 gap-3">
                          <!-- Margen -->
                          <div>
                              <label class="text-xs text-white/60 block mb-1">Margen Mayorista %</label>
                              <input 
                                v-model.number="localCostos.margen_mayorista"
                                type="number" 
                                step="0.1"
                                class="w-full bg-black/40 border border-white/10 rounded px-3 py-2 text-white font-mono focus:border-rose-500 focus:outline-none text-right"
                              />
                          </div>
                          <!-- IVA -->
                          <div>
                              <label class="text-xs text-white/60 block mb-1">Alícuota IVA</label>
                              <select 
                                v-model="localProducto.tasa_iva_id"
                                class="w-full bg-[#1a050b] border border-white/10 rounded px-3 py-2 text-white font-mono focus:border-rose-500 focus:outline-none appearance-none text-right"
                                @change="updateLocalIvaRate"
                              >
                                  <option :value="null" class="bg-[#1a050b] text-white">Seleccionar...</option>
                                  <option v-for="t in tasasIva" :key="t.id" :value="t.id" class="bg-[#1a050b] text-white">
                                      {{ t.nombre }} ({{ t.valor }}%)
                                  </option>
                              </select>
                          </div>
                      </div>
                  </div>
              </div>
                  
              <!-- MOTOR HIBRIDO (NUEVO) -->
              <div class="mt-4 p-4 rounded-lg bg-black/40 border border-white/10 space-y-4">
                  <h4 class="text-rose-400 text-[0.6rem] font-bold uppercase tracking-widest flex items-center justify-between">
                      <span>Estrategia Artesanal (V6)</span>
                      <span class="text-white/20">Prioridad Alta</span>
                  </h4>

                  <div class="grid grid-cols-2 gap-4">
                      <!-- CM Objetivo -->
                      <div>
                          <label class="text-[0.65rem] text-white/50 block mb-1 uppercase">CM Objetivo (%)</label>
                          <div class="relative">
                              <input 
                                v-model.number="localCostos.cm_objetivo"
                                type="number" 
                                class="w-full bg-rose-500/5 border border-white/10 rounded px-3 py-2 text-white font-mono focus:border-rose-500 focus:outline-none text-right"
                                placeholder="Libre"
                              />
                              <span class="absolute left-2 top-1/2 -translate-y-1/2 text-[0.6rem] text-rose-500/50 font-bold">CM</span>
                          </div>
                      </div>

                      <!-- Precio Fijo -->
                      <div>
                          <label class="text-[0.65rem] text-white/50 block mb-1 uppercase text-right">Precio Fijo Manual</label>
                          <div class="relative">
                              <input 
                                v-model.number="localCostos.precio_fijo_override"
                                type="number" 
                                class="w-full bg-rose-500/5 border border-white/10 rounded px-3 py-2 text-white font-mono focus:border-rose-500 focus:outline-none text-right"
                                placeholder="Auto"
                              />
                              <span class="absolute left-2 top-1/2 -translate-y-1/2 text-[0.6rem] text-rose-500/50 font-bold">$</span>
                          </div>
                      </div>
                  </div>

                  <!-- Contexto Rubro -->
                  <div v-if="selectedRubro" class="pt-2 flex justify-between items-center text-[0.65rem]">
                      <span class="text-white/30 italic">Propuesta por Rubro ({{ selectedRubro.nombre }}):</span>
                      <span class="text-rose-400 font-bold">{{ selectedRubro.margen_default || 0 }}%</span>
                  </div>
              </div>

              <!-- Simulador -->
              <div class="space-y-3 pt-2">
                  <h4 class="text-white/40 text-xs font-bold uppercase text-center">Simulador de Precios (Estimado)</h4>
                  
                  <!-- Mayorista -->
                  <div class="flex justify-between items-center p-3 rounded bg-white/5 border border-white/5">
                      <span class="text-sm text-white/70">Precio Mayorista</span>
                      <span class="font-mono font-bold text-green-400 text-lg">{{ formatCurrency(simulatedPrices.mayorista) }}</span>
                  </div>
                  
                  <!-- Distribuidor -->
                  <div class="flex justify-between items-center p-2 rounded hover:bg-white/5 transition-colors">
                      <span class="text-xs text-white/50">Distribuidor (+10.5%)</span>
                      <span class="font-mono text-white/80">{{ formatCurrency(simulatedPrices.distribuidor) }}</span>
                  </div>

                  <!-- Minorista -->
                  <div class="flex justify-between items-center p-2 rounded hover:bg-white/5 transition-colors">
                      <span class="text-xs text-white/50">Minorista (+40%)</span>
                      <span class="font-mono text-white/80">{{ formatCurrency(simulatedPrices.minorista) }}</span>
                  </div>
              </div>
          </div>
      </div>

      <!-- Footer Actions -->
      <div class="p-4 border-t border-white/10 bg-black/20 shrink-0 flex gap-3">
          <button 
            @click="save"
            class="flex-1 bg-rose-600 hover:bg-rose-500 text-white font-bold py-2 px-4 rounded-lg shadow-lg shadow-rose-900/20 transition-all active:scale-95"
          >
            <i class="fas fa-save mr-2"></i> Guardar (F10)
          </button>
          
          <button 
            v-if="localProducto.id && localProducto.activo"
            @click="toggleActive"
            class="px-4 py-2 rounded-lg text-red-400 hover:bg-red-900/20 hover:text-red-300 text-sm font-medium transition-colors border border-transparent hover:border-red-500/30"
          >
            Dar de Baja
          </button>
          <button 
            v-if="localProducto.id && !localProducto.activo"
            @click="toggleActive"
            class="px-4 py-2 rounded-lg text-green-400 hover:bg-green-900/20 hover:text-green-300 text-sm font-medium transition-colors border border-transparent hover:border-green-500/30"
          >
            Activar
          </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-1 flex-col items-center justify-center p-8 text-center text-white/30">
      <i class="fas fa-box-open mb-4 text-4xl opacity-50"></i>
      <p class="text-sm">Selecciona un producto para editar</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductosStore } from '../../../stores/productos'
import { useNotificationStore } from '@/stores/notification' // Add Notification Store
import SmartSelect from '../../../components/ui/SmartSelect.vue'

const productosStore = useProductosStore()
const notification = useNotificationStore() // Init Store
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
    margen_mayorista: 0,
    iva_alicuota: 21,
    cm_objetivo: null,
    precio_fijo_override: null
})

// --- CALCULADORA MÁSCARA (V5.7 SOCRATIC LOGIC) ---
const calculadora = ref({
    roca: 0, // Base Neta Real
    maskFiscal: 0, // Precio Lista para Factura A (20% OFF)
    maskBlue: 0 // Precio Lista para Blue (10% OFF)
})

// Auto-fill Roca when loading product
watch(() => localCostos.value.costo_reposicion, (newVal) => {
    // Solo si roca esta vacia o es igual al costo anterior
    if (!calculadora.value.roca) {
        calculadora.value.roca = Number(newVal) || 0
    }
}, { immediate: true })

// Recalcular Máscaras cuando cambia La Roca
watch(() => calculadora.value.roca, (newRoca) => {
    const roca = Number(newRoca) || 0
    if (roca <= 0) {
        calculadora.value.maskFiscal = 0
        calculadora.value.maskBlue = 0
        return
    }

    // FISCAL: Queremos que (Máscara * 0.80) = Roca
    // Entonces Máscara = Roca / 0.80
    calculadora.value.maskFiscal = roca / 0.80

    // BLUE: Queremos que (Máscara * 0.90) = Roca (o Roca + MargenBlue?)
    // El usuario dijo: "Si lo quiere sin factura? Es $14.000 menos el 10%"
    // Y verificó que $14.000 - 10% = $12.600 que es cercano a su objetivo.
    // Asumiremos que la Máscara es única (Sugerida la Fiscal) y veremos cómo cae el Blue.
    // PERO, en la UI mostramos DOS máscaras sugeridas.
    // Si aplico Fiscal, el Blue cae en: MáscaraFiscal * 0.90 = (Roca/0.80)*0.90 = Roca * 1.125 (+12.5% sobre Roca)
    
    // Si quisiera forzar que el Blue sea diferente, tendría otra Máscara.
    // Pero el precio de lista es UNO solo en el sistema.
    // Así que calcularemos la "Máscara Blue Ideal" para referencia.
    // Blue Ideal = Roca / 0.90 (Para caer EXACTO en la Roca con 10% descuento)
    calculadora.value.maskBlue = roca / 0.90
})

const aplicarMascara = (tipo) => {
    if (tipo === 'FISCAL') {
        localCostos.value.precio_fijo_override = Math.ceil(calculadora.value.maskFiscal / 100) * 100 // Redondeo a 100
        notification.add('Máscara Fiscal aplicada como Precio Fijo', 'success')
    } else if (tipo === 'BLUE') {
        localCostos.value.precio_fijo_override = Math.ceil(calculadora.value.maskBlue / 100) * 100 // Redondeo a 100
        notification.add('Máscara Blue aplicada como Precio Fijo', 'success')
    }
}
// --------------------------------------------------

const templateId = ref(null)
const pristineName = ref('')

// Flatten rubros for select
const flattenedRubros = computed(() => {
    const result = []
    const traverse = (items, level = 0) => {
        for (const item of items) {
            result.push({
                ...item,
                indent: '\u00A0\u00A0'.repeat(level) + (level > 0 ? '└ ' : '')
            })
            if (item.hijos && item.hijos.length) {
                traverse(item.hijos, level + 1)
            }
        }
    }
    traverse(props.rubros)
    return result
})

const selectedRubro = computed(() => {
    if (!localProducto.value?.rubro_id) return null
    return flattenedRubros.value.find(r => r.id === localProducto.value.rubro_id)
})

// Watch for prop changes to update local state
watch(() => props.producto, (newVal) => {
    if (newVal) {
        localProducto.value = JSON.parse(JSON.stringify(newVal))
        if (newVal.costos) {
            localCostos.value = { ...newVal.costos }
        } else {
            // Default costs if missing
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
    
    // Track pristine name to detect changes for auto-cloning logic
    pristineName.value = localProducto.value?.nombre || ''
    templateId.value = null 
}, { immediate: true })

const handleTemplateSelect = (itemOrId) => {
    let template = null;
    if (typeof itemOrId === 'object') {
        template = itemOrId;
    } else {
        template = productosStore.productos.find(p => p.id === itemOrId);
    }

    if (template) {
        // Inherit everything except ID and SKU
        const originalActive = localProducto.value.activo;
        localProducto.value = {
            ...JSON.parse(JSON.stringify(template)),
            id: null,
            sku: 'AUTO',
            activo: originalActive // Maintain current intent
        };
        if (template.costos) {
            localCostos.value = { ...template.costos };
        }
        // Update pristineName to template's name for comparison on save
        pristineName.value = template.nombre;
        
        // Focus name to allow modification
        nextTick(() => {
            const nameInput = document.querySelector('input[placeholder="Ej: Jabón Líquido 5L"]');
            if (nameInput) nameInput.focus();
        });
    }
}

// Simulated Prices
const simulatedPrices = computed(() => {
    const costo = Number(localCostos.value.costo_reposicion) || 0
    const margen_propio = Number(localCostos.value.margen_mayorista) || 0
    const iva = Number(localCostos.value.iva_alicuota) || 0
    const cm = localCostos.value.cm_objetivo
    const fijo = localCostos.value.precio_fijo_override
    const margen_rubro = selectedRubro.value?.margen_default || 0

    let base_rock = 0
    
    // HIERARCHY
    if (fijo > 0) {
        base_rock = fijo
    } else if (cm > 0) {
        base_rock = costo / (1 - cm / 100)
    } else if (margen_rubro > 0) {
        base_rock = costo * (1 + margen_rubro / 100)
    } else {
        base_rock = costo * (1 + margen_propio / 100)
    }

    const mayorista = base_rock * (1 + iva / 100)
    
    // Formulas from prompt
    const distribuidor = mayorista * 1.105
    const minorista = (distribuidor / 0.90) * 1.105

    return {
        mayorista,
        distribuidor,
        minorista
    }
})

const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(val)
}

const save = () => {
    if (!localProducto.value) return
    
    // [DEOU Flow] If no changes in name for a new template-based item, cancel save
    if (!localProducto.value.id && localProducto.value.nombre === pristineName.value) {
        alert('No se detectaron cambios en el nombre. No se generará un nuevo registro.');
        emit('close');
        return;
    }

    // Merge costs back into product
    const payload = {
        ...localProducto.value,
        costos: { ...localCostos.value }
    }
    emit('save', payload)
}

const toggleActive = () => {
    if (localProducto.value) {
        emit('toggle-active', localProducto.value)
    }
}

const updateLocalIvaRate = () => {
    const selectedTasa = tasasIva.value.find(t => t.id === localProducto.value.tasa_iva_id)
    if (selectedTasa) {
        localCostos.value.iva_alicuota = Number(selectedTasa.valor)
    }
}

// Keyboard Shortcuts
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
