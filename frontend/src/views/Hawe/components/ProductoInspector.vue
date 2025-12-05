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
        <div class="mb-4 flex justify-center">
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
                  />
              </div>

              <!-- Código Visual -->
              <div class="space-y-1">
                  <label class="text-xs font-bold text-white/60 uppercase">Código Visual</label>
                  <input 
                    v-model="localProducto.codigo_visual"
                    type="text" 
                    class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors font-mono"
                    placeholder="Ej: JL-500"
                  />
              </div>

              <!-- Rubro -->
              <div class="space-y-1">
                  <label class="text-xs font-bold text-white/60 uppercase">Rubro / Categoría</label>
                  <select 
                    v-model="localProducto.rubro_id"
                    class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none"
                  >
                      <option :value="null" disabled>Seleccione un Rubro</option>
                      <option v-for="rubro in flattenedRubros" :key="rubro.id" :value="rubro.id">
                          {{ rubro.indent }}{{ rubro.nombre }}
                      </option>
                  </select>
              </div>

              <!-- Tipo Producto -->
              <div class="space-y-1">
                  <label class="text-xs font-bold text-white/60 uppercase">Tipo Producto</label>
                  <select 
                    v-model="localProducto.tipo_producto"
                    class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none"
                  >
                      <option value="VENTA">Venta</option>
                      <option value="INSUMO">Insumo</option>
                      <option value="MATERIA_PRIMA">Materia Prima</option>
                      <option value="SERVICIO">Servicio</option>
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
                            class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none"
                          >
                              <option :value="null">Seleccionar...</option>
                              <option v-for="u in unidades" :key="u.id" :value="u.id">
                                  {{ u.nombre }} ({{ u.codigo }})
                              </option>
                          </select>
                      </div>

                      <!-- Unidad Compra -->
                      <div class="space-y-1">
                          <label class="text-xs font-bold text-white/60 uppercase">Unidad Compra</label>
                          <select 
                            v-model="localProducto.unidad_compra_id"
                            class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors appearance-none"
                          >
                              <option :value="null">Seleccionar...</option>
                              <option v-for="u in unidades" :key="u.id" :value="u.id">
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
                        class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-rose-500 focus:outline-none transition-colors"
                      >
                          <option value="UN">Unidad</option>
                          <option value="LT">Litro</option>
                          <option value="KG">Kilo</option>
                          <option value="MT">Metro</option>
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
                        class="w-full bg-black/40 border border-white/10 rounded px-3 py-2 text-white focus:border-rose-500 focus:outline-none appearance-none"
                      >
                          <option :value="null">Seleccionar Proveedor...</option>
                          <option v-for="p in proveedores" :key="p.id" :value="p.id">
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
                                class="w-full bg-black/40 border border-white/10 rounded px-3 py-2 text-white font-mono focus:border-rose-500 focus:outline-none appearance-none text-right"
                                @change="updateLocalIvaRate"
                              >
                                  <option :value="null">Seleccionar...</option>
                                  <option v-for="t in tasasIva" :key="t.id" :value="t.id">
                                      {{ t.nombre }} ({{ t.valor }}%)
                                  </option>
                              </select>
                          </div>
                      </div>
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
            v-if="localProducto.id"
            @click="toggleActive"
            class="px-3 py-2 rounded-lg border border-white/10 hover:bg-white/10 text-white/50 hover:text-white transition-colors"
            :title="localProducto.activo ? 'Desactivar' : 'Reactivar'"
          >
            <i class="fas" :class="localProducto.activo ? 'fa-trash' : 'fa-undo'"></i>
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

const productosStore = useProductosStore()
const { unidades, tasasIva, proveedores } = storeToRefs(productosStore)

const props = defineProps({
  producto: {
    type: Object,
    default: null
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
    iva_alicuota: 21
})

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

// Watch for prop changes to update local state
watch(() => props.producto, (newVal) => {
    if (newVal) {
        localProducto.value = JSON.parse(JSON.stringify(newVal))
        if (newVal.costos) {
            localCostos.value = { ...newVal.costos }
        } else {
            // Default costs if missing
            localCostos.value = { costo_reposicion: 0, margen_mayorista: 30, iva_alicuota: 21 }
        }
    } else {
        localProducto.value = null
    }
}, { immediate: true })

// Simulated Prices
const simulatedPrices = computed(() => {
    const costo = Number(localCostos.value.costo_reposicion) || 0
    const margen = Number(localCostos.value.margen_mayorista) || 0
    const iva = Number(localCostos.value.iva_alicuota) || 0

    const neto = costo * (1 + margen / 100)
    const mayorista = neto * (1 + iva / 100)
    
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
    // Merge costs back into product
    const payload = {
        ...localProducto.value,
        costos: { ...localCostos.value }
    }
    emit('save', payload)
}

const toggleActive = () => {
    if (localProducto.value) {
        emit('toggle-active', localProducto.value.id)
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
