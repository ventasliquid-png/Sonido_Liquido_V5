<template>
  <div class="flex h-full w-full flex-col bg-[#1a050b] text-gray-100 rounded-2xl shadow-2xl overflow-hidden border border-rose-900/40">
    <!-- Header with Breadcrumb Style -->
    <div class="flex items-center justify-between border-b border-rose-900/30 bg-rose-950/20 p-4 shrink-0 transition-height">
      <div class="flex items-center gap-4">
          <!-- Icon -->
          <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-rose-500/20 to-black flex items-center justify-center text-rose-500 border border-rose-500/20 shadow-lg shadow-rose-900/20">
             <i class="fas fa-box text-lg"></i>
          </div>
          
          <!-- Title & Meta -->
          <div>
              <div v-if="localProducto && !localProducto.id" class="flex items-center gap-2">
                 <span class="text-xs font-bold bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded border border-rose-500/30 uppercase tracking-wider">Nuevo Producto</span>
              </div>
              <h2 class="font-outfit text-xl font-bold text-white tracking-tight leading-none mt-1">
                  {{ localProducto?.nombre || 'Definir Nombre...' }}
              </h2>
              <div class="flex items-center gap-3 mt-1 text-xs font-mono text-rose-200/40">
                  <span v-if="localProducto && localProducto.id">ID: {{ localProducto.id }}</span>
                  <span v-if="localProducto && localProducto.sku" class="flex items-center gap-1"><i class="fas fa-barcode"></i> {{ localProducto.sku }}</span>
              </div>
          </div>
      </div>
      
      <div class="flex items-center gap-3">
          <!-- Active Toggle -->
            <button 
                v-if="localProducto"
                @click="$emit('toggle-active', localProducto)"
                class="flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all"
                :class="localProducto.activo ? 'bg-green-500/10 border-green-500/30 text-green-400 hover:bg-green-500/20' : 'bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20'"
            >
                <div class="h-2 w-2 rounded-full" :class="localProducto.activo ? 'bg-green-500 shadow-lg shadow-green-500/50' : 'bg-red-500 shadow-lg shadow-red-500/50'"></div>
                <span class="text-xs font-bold uppercase">{{ localProducto.activo ? 'Activo' : 'Inactivo' }}</span>
          </button>

          <div class="h-8 w-px bg-white/10 mx-1"></div>

          <button @click="$emit('close')" class="h-9 w-9 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-colors">
             <i class="fas fa-times"></i>
          </button>
      </div>
    </div>

    <!-- MAIN CANVAS (3 Columns) -->
    <div v-if="localProducto && localProducto.nombre !== undefined" class="flex-1 flex overflow-hidden">
        
        <!-- COLUMN 1: Identity & Tax Nature (30%) -->
        <div class="w-[30%] border-r border-rose-900/30 bg-[#2e0a13]/20 flex flex-col overflow-y-auto custom-scrollbar p-6 space-y-8">
            
            <!-- Image / Avatar -->
            <div class="flex justify-center">
                <div class="relative group cursor-pointer">
                     <!-- Placeholder -->
                    <div class="h-40 w-40 rounded-2xl bg-gradient-to-br from-[#3f0e1a] to-black flex items-center justify-center text-6xl text-rose-600/50 shadow-2xl border border-rose-500/20 group-hover:border-rose-500/50 transition-all duration-300">
                        <i class="fas fa-cube transform group-hover:scale-110 transition-transform duration-300"></i>
                    </div>
                </div>
            </div>

            <!-- Basic Data Form -->
            <div class="space-y-5">
                <!-- Nombre -->
                <div class="space-y-1 group">
                   <label class="text-[10px] font-bold text-rose-200/40 uppercase tracking-widest group-focus-within:text-rose-400 transition-colors">Nombre Oficial</label>
                   <input 
                     v-model="localProducto.nombre"
                     type="text" 
                     class="w-full bg-black/20 border border-white/5 rounded-lg px-3 py-2.5 text-white font-bold tracking-wide focus:border-rose-500/50 focus:bg-black/40 focus:outline-none transition-all placeholder-white/5"
                     placeholder="Ej: Barbijo Recto"
                   />
                </div>

                    <div class="space-y-1">
                       <label class="text-[10px] font-bold text-rose-200/40 uppercase tracking-widest">Código Visual</label>
                       <input 
                         v-model="localProducto.codigo_visual"
                         type="text" 
                         class="w-full bg-black/20 border border-white/5 rounded-lg px-3 py-2 text-white font-mono text-sm focus:border-rose-500/50 focus:outline-none transition-colors"
                         placeholder="CODE-01"
                       />
                     </div>

                <!-- Rubro (Validated) -->
                <div class="space-y-1">
                    <label class="text-[10px] font-bold text-rose-200/40 uppercase tracking-widest">Rubro / Categoría <span class="text-rose-500">*</span></label>
                    <select 
                        v-model="localProducto.rubro_id"
                        class="w-full bg-black/20 border border-white/5 rounded-lg px-3 py-2.5 text-white text-sm focus:border-rose-500/50 focus:outline-none appearance-none transition-colors"
                        :class="!localProducto.rubro_id ? 'border-rose-500/30' : ''"
                    >
                        <option :value="null" disabled>Seleccionar...</option>
                        <option v-for="rubro in flattenedRubros" :key="rubro.id" :value="rubro.id">
                            {{ rubro.indent }}{{ rubro.nombre }}
                        </option>
                    </select>
                </div>

                <!-- Insumo Switch -->
                <div class="pt-4 border-t border-white/5">
                     <div class="flex items-center gap-2 p-2 rounded bg-white/5 border border-white/5 cursor-pointer" @click="localProducto.tipo_producto = localProducto.tipo_producto === 'INSUMO' ? 'VENTA' : 'INSUMO'">
                          <div class="w-8 h-4 rounded-full relative transition-colors" :class="localProducto.tipo_producto === 'INSUMO' ? 'bg-orange-500' : 'bg-gray-700'">
                              <div class="absolute top-0.5 left-0.5 w-3 h-3 rounded-full bg-white transition-transform" :class="localProducto.tipo_producto === 'INSUMO' ? 'translate-x-4' : ''"></div>
                          </div>
                          <span class="text-xs font-bold uppercase transition-colors" :class="localProducto.tipo_producto === 'INSUMO' ? 'text-orange-400' : 'text-gray-400'">
                              {{ localProducto.tipo_producto === 'INSUMO' ? 'Es Insumo Interno' : 'Producto de Venta' }}
                          </span>
                     </div>
                </div>
            </div>
        </div>

        <!-- COLUMN 2: FINANCIAL BRAIN (40%) -->
        <div class="w-[40%] flex flex-col overflow-y-auto custom-scrollbar bg-gradient-to-b from-[#1a050b] to-black/40">
             <div class="p-6 space-y-8">
                 <h3 class="text-lg font-outfit font-bold text-white/50 flex items-center gap-2 border-b border-white/5 pb-2">
                     <i class="fas fa-brain text-rose-500"></i> Estructura de Costos
                 </h3>

                 <!-- 1. COSTO DE REPOSICION -->
                 <div class="space-y-2">
                      <div class="flex justify-between items-end px-1">
                          <label class="text-xs font-bold text-rose-500 uppercase tracking-widest">Costo de Reposición (Neto)</label>
                          <div class="text-[10px] font-mono text-rose-500/40 uppercase" v-if="lastCostUpdate">
                              <i class="fas fa-clock mr-1"></i>Act: {{ lastCostUpdate }}
                          </div>
                      </div>
                      <div class="relative group">
                          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-rose-500/50 text-xl font-light">$</span>
                          <input 
                              v-model.number="localCostos.costo_reposicion"
                              @input="updateCostTimestamp"
                              type="number" step="0.01" min="0"
                              class="w-full bg-rose-950/10 border border-rose-500/20 rounded-xl px-4 py-4 pl-8 text-3xl font-mono font-bold text-white text-right focus:border-rose-500/50 focus:shadow-[0_0_20px_rgba(244,63,94,0.1)] focus:outline-none transition-all placeholder-white/5"
                              placeholder="0.00"
                          />
                      </div>
                 </div>

                 <!-- 2. RENTABILIDAD & PRECIO ROCA (ESPEJO) -->
                 <div class="bg-cyan-900/5 border border-cyan-500/20 rounded-2xl p-6 space-y-6 relative shadow-lg shadow-black/20">
                      <!-- Link Visual -->
                      <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-cyan-500/20 text-4xl pointer-events-none">
                          <i class="fas fa-arrows-alt-h"></i>
                      </div>

                      <div class="grid grid-cols-2 gap-8">
                          <!-- Margin Input -->
                           <div class="space-y-2 relative z-10">
                              <label class="text-[10px] font-bold text-cyan-500/70 uppercase tracking-widest text-center block">Margin %</label>
                              <div class="relative group">
                                 <input 
                                     v-model.number="localCostos.rentabilidad_target"
                                     @input="updateRocaFromRent"
                                     type="number" step="0.1"
                                     class="w-full bg-black/40 border border-cyan-500/30 rounded-xl px-2 py-3 text-xl font-mono font-bold text-cyan-400 text-center focus:border-cyan-400 focus:outline-none transition-all"
                                 />
                                 <span class="absolute right-3 top-1/2 -translate-y-1/2 text-cyan-500/30 font-bold text-xs">%</span>
                              </div>
                           </div>

                          <!-- Roca Input -->
                           <div class="space-y-2 relative z-10">
                              <label class="text-[10px] font-bold text-white/70 uppercase tracking-widest text-center block">Precio Roca (Neto)</label>
                              <div class="relative group">
                                 <input 
                                     v-model.number="localCostos.precio_roca"
                                     @input="updateRentFromRoca"
                                     type="number" step="0.01"
                                     class="w-full bg-white/5 border border-white/20 rounded-xl px-2 py-3 text-xl font-mono font-bold text-white text-center focus:border-white/50 focus:outline-none transition-all"
                                 />
                              </div>
                           </div>
                      </div>
                 </div>

                 <!-- 3. PRECIO FINAL (TRIDIRECCIONAL) -->
                 <div class="pt-4 border-t border-white/5 space-y-4">
                      <!-- Grid for IVA Selector and Label -->
                      <div class="flex items-center justify-between">
                          <div class="space-y-1 w-1/2">
                                <label class="text-[10px] font-bold text-white/30 uppercase tracking-widest">Tasa IVA</label>
                                <select 
                                     v-model="localProducto.tasa_iva_id"
                                     @change="updateLocalIvaRate"
                                     class="w-full bg-black/40 border border-white/10 rounded-lg px-2 py-1.5 text-white font-mono text-xs focus:border-rose-500/50 focus:outline-none"
                                 >
                                    <option v-for="t in tasasIva" :key="t.id" :value="t.id">
                                       {{ t.valor }}% ({{ t.nombre }})
                                    </option>
                                 </select>
                           </div>
                           <label class="text-xs font-bold text-green-400 uppercase tracking-widest text-right">Precio Final (Con IVA)</label>
                      </div>

                      <div class="relative group">
                          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-green-500/30 text-xl font-light">$</span>
                          <input 
                              :value="finalPrice"
                              @input="updateNetFromFinal($event.target.value)"
                              type="number" step="0.01"
                              class="w-full bg-green-900/5 border border-green-500/20 rounded-xl px-4 py-3 pl-8 text-3xl font-mono font-bold text-green-400 text-right focus:border-green-500/50 focus:shadow-[0_0_20px_rgba(74,222,128,0.1)] focus:outline-none transition-all"
                          />
                           <div class="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-bold text-green-500/30 pointer-events-none">
                               Final
                          </div>
                      </div>
                 </div>

             </div>
        </div>

        <!-- COLUMN 3: SUPPLIERS & LOGISTICS (30%) -->
         <div class="w-[30%] border-l border-rose-900/30 bg-[#2e0a13]/10 flex flex-col overflow-y-auto custom-scrollbar p-6 space-y-6">
             <!-- Suppliers Panel (Table) -->
             <div class="bg-[#1a1a1a] rounded-xl border border-white/5 flex flex-col h-[280px]">
                 <div class="p-3 border-b border-white/5 flex justify-between items-center bg-white/5">
                     <h4 class="text-xs font-bold text-white/50 uppercase flex items-center gap-2">
                         <i class="fas fa-truck text-rose-500"></i> Proveedores
                     </h4>
                     <button @click="isAddingSupplier = !isAddingSupplier" class="text-xs bg-rose-500/20 text-rose-400 px-2 py-0.5 rounded hover:bg-rose-500/30 transition-colors">
                         <i class="fas fa-plus"></i>
                     </button>
                 </div>
                 
                 <!-- Add Form -->
                 <div v-if="isAddingSupplier" class="p-3 bg-rose-900/10 border-b border-rose-500/20 space-y-2 animate-in fade-in slide-in-from-top-2">
                     <select v-model="newSupplier.proveedor_id" class="w-full bg-black/50 border border-rose-500/30 rounded px-2 py-1 text-xs text-white">
                         <option :value="null">Seleccionar Proveedor...</option>
                         <option v-for="p in (proveedores || [])" :key="p.id" :value="p.id">{{ p.razon_social }}</option>
                     </select>
                     <div class="flex gap-2">
                         <input v-model.number="newSupplier.costo" type="number" class="w-2/3 bg-black/50 border border-rose-500/30 rounded px-2 py-1 text-xs text-white" placeholder="Costo">
                         <button @click="saveSupplier" class="w-1/3 bg-rose-600 text-white text-xs rounded font-bold hover:bg-rose-500">Add</button>
                     </div>
                 </div>

                 <!-- Table List -->
                 <div class="flex-1 overflow-y-auto custom-scrollbar p-0">
                     <table class="w-full text-left border-collapse">
                         <thead class="sticky top-0 bg-[#0f0f0f] text-[10px] text-white/30 uppercase tracking-wider font-bold z-10">
                             <tr>
                                 <th class="px-3 py-2 font-light">Proveedor</th>
                                 <th class="px-3 py-2 font-light text-right">Costo</th>
                                 <th class="px-3 py-2 font-light text-right">Action</th>
                             </tr>
                         </thead>
                         <tbody class="divide-y divide-white/5">
                             <tr v-for="prov in localProveedoresList" :key="prov.id" class="group hover:bg-white/5 transition-colors">
                                 <td class="px-3 py-2 text-xs text-white/80 truncate max-w-[100px]" :title="getProvName(prov.proveedor_id)">
                                     {{ getProvName(prov.proveedor_id) }}
                                     <div class="text-[9px] text-white/30 font-mono">{{ formatDate(prov.fecha) }}</div>
                                 </td>
                                 <td class="px-3 py-2 text-xs font-mono font-bold text-rose-400 text-right">
                                     ${{ prov.costo }}
                                 </td>
                                 <td class="px-3 py-2 text-right">
                                     <button @click="removeSupplier(prov.id)" class="text-white/20 hover:text-red-500 transition-colors p-1">
                                         <i class="fas fa-trash text-[10px]"></i>
                                     </button>
                                 </td>
                             </tr>
                             <tr v-if="localProveedoresList.length === 0">
                                 <td colspan="3" class="px-3 py-8 text-center text-xs text-white/20 italic">
                                     Sin historial de proveedores
                                 </td>
                             </tr>
                         </tbody>
                     </table>
                 </div>
             </div>

             <!-- Logistics Panel -->
             <div class="pt-4 border-t border-white/5 space-y-4">
                 <h4 class="text-xs font-bold text-white/50 uppercase flex items-center gap-2">
                     <i class="fas fa-boxes text-blue-400"></i> Logística
                 </h4>

                 <div class="grid grid-cols-2 gap-3">
                     <div class="space-y-1">
                        <label class="text-[10px] font-bold text-white/30 uppercase">Unidad</label>
                        <select 
                            v-model="localProducto.unidad_medida"
                            class="w-full bg-black/40 border border-white/10 rounded-lg px-2 py-2 text-white text-xs focus:border-blue-500/50 focus:outline-none appearance-none"
                        >
                            <option value="UN">Unidad</option>
                            <option value="KG">Kilos</option>
                            <option value="LT">Litros</option>
                            <option value="MT">Metros</option>
                        </select>
                    </div>
                     <div class="space-y-1">
                        <label class="text-[10px] font-bold text-white/30 uppercase">Venta Mínima</label>
                        <input 
                         v-model.number="localProducto.venta_minima"
                         type="number" step="1"
                         class="w-full bg-black/40 border border-white/10 rounded-lg px-2 py-2 text-white text-xs focus:border-blue-500/50 focus:outline-none"
                       />
                    </div>
                 </div>

                 <div class="flex items-center gap-2 p-2 rounded bg-white/5 border border-white/5">
                      <input type="checkbox" v-model="localProducto.es_kit" class="rounded bg-black/50 border-white/20 text-rose-500 focus:ring-0 cursor-pointer">
                      <span class="text-xs text-white/70 font-bold uppercase">Es Kit / Combo</span>
                 </div>
             </div>
         </div>

    </div>

    <!-- Sticky Footer -->
    <div class="shrink-0 p-4 border-t border-rose-900/30 bg-[#2e0a13]/90 flex justify-end items-center gap-4 backdrop-blur-md z-50">
        <div class="mr-auto text-xs text-white/30 hidden md:block">
            <span class="font-bold">TIP:</span> Precio Final es calculado. El <span class="text-white">Precio Roca</span> es la base imponible.
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
import productosApi from '../../../services/productosApi' // Direct import for sub-resources
import { useNotificationStore } from '@/stores/notification'
import dayjs from 'dayjs'

const productosStore = useProductosStore()
const notification = useNotificationStore()
const { unidades, tasasIva, proveedores } = storeToRefs(productosStore)

const props = defineProps({
  producto: { type: Object, default: () => null },
  rubros: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'save', 'toggle-active'])

// SAFE OBJECT PATTERN
const localProducto = ref({}) 
const pristineName = ref('')

// FINANCIAL STATE
const localCostos = ref({
    costo_reposicion: 0,
    rentabilidad_target: 30, 
    precio_roca: 0,
    iva_alicuota: 21, // Default IVA alicuota
    moneda_costo: 'ARS'
})
const lastCostUpdate = ref('')
const lastRentUpdate = ref('')

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

// --- BRAIN LOGIC (TRIDIRECCIONAL) ---
const isUpdating = ref(false)

// Computed for Final Price (Display)
const finalPrice = computed(() => {
    const roca = Number(localCostos.value.precio_roca) || 0
    const alicuota = Number(localCostos.value.iva_alicuota) || 21
    return parseFloat((roca * (1 + alicuota/100)).toFixed(2))
})

const updateCostTimestamp = () => {
    lastCostUpdate.value = dayjs().format('DD/MM HH:mm')
    // If Cost changes, and we want to keep Rent fixed? or Price fixed?
    // Standard: Keep Rent, Recalc Price Roca
    // localCostos.value.precio_roca = cost * (1+rent) -> This is standard
    // BUT here we have updateRentFromRoca logic which implies Roca is dominant?
    // Let's stick to: Change Cost -> Keep Rent -> Update Roca
    if (isUpdating.value) return
    isUpdating.value = true
    
    const costo = Number(localCostos.value.costo_reposicion) || 0
    const rent = Number(localCostos.value.rentabilidad_target) || 0
    localCostos.value.precio_roca = parseFloat((costo * (1 + rent / 100)).toFixed(2))
    
    nextTick(() => { isUpdating.value = false })
}

const updateRocaFromRent = () => {
    if (isUpdating.value) return
    isUpdating.value = true
    
    lastRentUpdate.value = dayjs().format('DD/MM HH:mm')
    
    const costo = Number(localCostos.value.costo_reposicion) || 0
    const rent = Number(localCostos.value.rentabilidad_target) || 0
    
    localCostos.value.precio_roca = parseFloat((costo * (1 + rent / 100)).toFixed(2))
    
    nextTick(() => { isUpdating.value = false })
}

const updateRentFromRoca = () => {
    if (isUpdating.value) return
    isUpdating.value = true
    
    lastRentUpdate.value = dayjs().format('DD/MM HH:mm')

    const costo = Number(localCostos.value.costo_reposicion) || 0
    const roca = Number(localCostos.value.precio_roca) || 0
    
    if (costo > 0) {
        localCostos.value.rentabilidad_target = parseFloat((((roca / costo) - 1) * 100).toFixed(2))
    }
    
    nextTick(() => { isUpdating.value = false })
}

const updateNetFromFinal = (finalVal) => {
    if (isUpdating.value) return
    isUpdating.value = true
    
    const priceFinal = parseFloat(finalVal) || 0
    const alicuota = Number(localCostos.value.iva_alicuota) || 21
    
    // Reverse Engineering: Roca = Final / (1 + IVA)
    const newRoca = parseFloat((priceFinal / (1 + alicuota/100)).toFixed(2))
    
    localCostos.value.precio_roca = newRoca
    
    // Now trigger Rent recalc immediately
    const costo = Number(localCostos.value.costo_reposicion) || 0
    if (costo > 0) {
         localCostos.value.rentabilidad_target = parseFloat((((newRoca / costo) - 1) * 100).toFixed(2))
    }
    
    nextTick(() => { isUpdating.value = false })
}
// -----------------------------------

const updateLocalIvaRate = () => {
    const selectedTasa = tasasIva.value.find(t => t.id === localProducto.value.tasa_iva_id)
    if (selectedTasa) {
        localCostos.value.iva_alicuota = Number(selectedTasa.valor)
        // When IVA rate changes, the final price changes, which means the Roca price (net)
        // should remain the same, and the final price computed property will update.
        // No need to explicitly call updateNetFromFinal or updateRocaFromRent here,
        // as the finalPrice computed property will react to localCostos.iva_alicuota change.
        // However, if we want to keep the *final price* fixed and recalculate Roca,
        // we would call updateNetFromFinal with the current finalPrice.
        // For now, let's assume Roca is the anchor when IVA changes.
    }
}


watch(() => props.producto, (newVal) => {
    if (newVal) {
        localProducto.value = JSON.parse(JSON.stringify(newVal))
        // Default Safety
        if (localProducto.value.venta_minima === undefined) localProducto.value.venta_minima = 1.0;
        
        // Sync IVA ID if missing or populate localCostos iva from it?
        // Priority: localProducto.tasa_iva_id determines localCostos.iva_alicuota
        
        if (newVal.costos) {
            localCostos.value = { ...newVal.costos }
        } else {
            localCostos.value = { 
                costo_reposicion: 0, 
                rentabilidad_target: 30, 
                precio_roca: 0, 
                iva_alicuota: 21,
                moneda_costo: 'ARS'
            }
        }
        
        if (newVal.costos) {
            localCostos.value = { ...newVal.costos }
        } else {
            localCostos.value = { 
                costo_reposicion: 0, 
                rentabilidad_target: 30, 
                precio_roca: 0, 
                iva_alicuota: 21,
                moneda_costo: 'ARS'
            }
        }
        
        // Ensure tipo_producto has default
        if (!localProducto.value.tipo_producto) localProducto.value.tipo_producto = 'VENTA'

        // Find correct alicuota based on ID if possible
        if (localProducto.value.tasa_iva_id && tasasIva.value?.length) {
            const tasa = tasasIva.value.find(t => t.id === localProducto.value.tasa_iva_id)
            if (tasa) localCostos.value.iva_alicuota = Number(tasa.valor)
        } else if (!localProducto.value.tasa_iva_id && tasasIva.value?.length) {
            // If no tasa_iva_id is set, try to default to the first one or a common one (e.g., 21%)
            const defaultTasa = tasasIva.value.find(t => t.valor === 21) || tasasIva.value[0];
            if (defaultTasa) {
                localProducto.value.tasa_iva_id = defaultTasa.id;
                localCostos.value.iva_alicuota = Number(defaultTasa.valor);
            }
        }

    } else {
        localProducto.value = {}
        localCostos.value = { 
            costo_reposicion: 0, 
            rentabilidad_target: 30, 
            precio_roca: 0,
            iva_alicuota: 21,
            moneda_costo: 'ARS'
        }
    }
    pristineName.value = localProducto.value?.nombre || ''
    lastCostUpdate.value = ''
    lastRentUpdate.value = ''
    
    // Sync Suppliers List
    localProveedoresList.value = localProducto.value.proveedores ? [...localProducto.value.proveedores] : []
}, { immediate: true })


// --- SUPPLIER MANAGEMENT ---
const localProveedoresList = ref([])
const isAddingSupplier = ref(false)
const newSupplier = ref({ proveedor_id: null, costo: '', observaciones: '' })

const getProvName = (id) => {
    if (!proveedores.value) return 'Loading...'
    const p = proveedores.value.find(x => x.id === id)
    return p ? (p.razon_social || p.nombre) : 'Unknown'
}
const formatDate = (date) => dayjs(date).format('MM/MM/YY')

const saveSupplier = async () => {
    if (!newSupplier.value.proveedor_id || !newSupplier.value.costo) return
    try {
        const payload = {
            proveedor_id: newSupplier.value.proveedor_id,
            costo: Number(newSupplier.value.costo),
            observaciones: newSupplier.value.observaciones
        }
        const res = await productosApi.addProveedor(localProducto.value.id, payload)
        
        // Add to local list
        localProveedoresList.value.unshift(res.data)
        
        // Reset form
        newSupplier.value = { proveedor_id: null, costo: '', observaciones: '' }
        isAddingSupplier.value = false
        notification.add('Proveedor agregado', 'success')
    } catch (e) {
        console.error(e)
        notification.add('Error al agregar proveedor', 'error')
    }
}

const removeSupplier = async (costoId) => {
    if (!confirm('Eliminar registro?')) return
    try {
        await productosApi.removeProveedor(costoId)
        localProveedoresList.value = localProveedoresList.value.filter(x => x.id !== costoId)
        notification.add('Eliminado', 'success')
    } catch (e) {
        console.error(e)
        notification.add('Error al eliminar', 'error')
    }
}


const save = () => {
    if (!localProducto.value || !localProducto.value.nombre) return
    
    if (!localProducto.value.nombre) {
        notification.add('El nombre del producto es obligatorio', 'error')
        return
    }

    if (!localProducto.value.rubro_id) {
        notification.add('Debe seleccionar un Rubro / Categoría', 'error')
        return
    }

    const costo = Number(localCostos.value.costo_reposicion) || 0
    if (costo <= 0) {
        if (!confirm('⚠ ALERTA DE COSTOS: El Costo de Reposición es $0.00.\n\n¿Está SEGURO que desea continuar?')) {
             return
        }
    }

    const payload = {
        ...localProducto.value,
        costos: { ...localCostos.value }
    }
    emit('save', payload)
}

const formatCurrency = (val) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(val || 0)

const handleKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault()
        save()
    }
    if (e.key === 'Escape') {
         emit('close')
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
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
.bg-dotted-pattern {
  background-image: radial-gradient(#ffffff 1px, transparent 1px);
  background-size: 20px 20px;
}
</style>
