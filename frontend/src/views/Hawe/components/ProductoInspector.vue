// [IDENTIDAD] - frontend\src\views\Hawe\components\ProductoInspector.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

<template>
  <div
    class="flex h-[92vh] w-[1300px] max-w-[95vw] flex-col bg-[#0f172a] text-gray-100 rounded-xl shadow-2xl overflow-hidden transition-all"
    :class="localProducto?.flags_estado & 8 ? '' : 'hud-border-red'"
    :style="localProducto?.flags_estado & 8 ? 'border: 2px solid #24e70f; box-shadow: 0 0 24px #24e70f44, 0 0 60px #24e70f22' : ''"
  >
    <!-- Header with Breadcrumb Style -->
    <div class="flex items-center justify-between border-b border-rose-900/30 bg-black/40 p-3 shrink-0 backdrop-blur-md sticky top-0 z-50">
      <div class="flex items-center gap-4 flex-1">
          <!-- Icon -->
          <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-rose-500/20 to-black flex items-center justify-center text-rose-500 border border-rose-500/20 shadow-lg shadow-rose-900/20">
             <i class="fas fa-box-open text-lg"></i>
          </div>
          
          <!-- Identity Fields (UNIFIED HEADER) -->
          <div class="flex-1 grid grid-cols-12 gap-x-4 gap-y-1 items-end">
              <!-- Nombre -->
              <div class="col-span-5">
                  <div class="flex items-baseline gap-2">
                      <span v-if="localProducto && !localProducto.id" class="text-[9px] font-bold bg-orange-500/80 text-white px-1.5 py-0.5 rounded uppercase tracking-wider animate-pulse">CLON / NUEVO</span>
                      <label class="text-[9px] font-bold text-rose-400/40 uppercase tracking-widest">Nombre Oficial</label>
                  </div>
                  <input 
                    v-model="localProducto.nombre"
                    type="text" 
                    class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-1.5 text-lg font-bold text-white focus:border-rose-500/50 focus:outline-none transition-all"
                    placeholder="Nombre del Producto..."
                  />
              </div>

              <!-- SKU/ID (View only or auto) -->
              <div class="col-span-1">
                   <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest block mb-1">SKU / ID</label>
                   <div class="bg-black/40 border border-white/5 rounded-lg px-2 py-1.5 text-center font-mono text-sm text-gray-400">
                       {{ localProducto?.id || 'AUTO' }}
                   </div>
              </div>

              <!-- Código Visual -->
              <div class="col-span-2">
                   <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest block mb-1">Cod. Visual</label>
                   <input 
                     v-model="localProducto.codigo_visual"
                     type="text" 
                     class="w-full bg-black/40 border border-white/10 rounded-lg px-2 py-1.5 text-white font-mono text-sm focus:border-rose-500/50 focus:outline-none transition-all"
                     placeholder="Ej: KOD-123"
                   />
              </div>

              <!-- Rubro -->
              <div class="col-span-2">
                   <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest block mb-1">
                     Rubro <span class="text-rose-500">*</span>
                   </label>
                   <SelectorCreatable
                        v-model="localProducto.rubro_id"
                        :options="flattenedRubros"
                        item-key="id"
                        display-key="nombre"
                        size="sm"
                        placeholder="Seleccionar rubro (obligatorio)..."
                        :class="rubroError ? 'ring-1 ring-rose-500 rounded-lg' : ''"
                        @create="handleCreateRubro"
                   />
                   <p v-if="rubroError" class="text-rose-400 text-[10px] mt-1">⚠ El rubro es obligatorio para guardar</p>
              </div>

              <!-- IVA -->
              <div class="col-span-2">
                   <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest block mb-1">Tasa IVA</label>
                   <SelectorCreatable
                        v-model="localProducto.tasa_iva_id"
                        :options="tasasIva"
                        item-key="id"
                        display-key="nombre"
                        size="sm"
                        placeholder="IVA..."
                        @create="handleCreateTasaIva"
                        @update:modelValue="handleUpdateTasaIva"
                   />
              </div>
          </div>
      </div>
      
      <div class="flex items-center gap-3 ml-4">
            <!-- Active Toggle -->
            <button 
                v-if="localProducto"
                @click="$emit('toggle-active', localProducto)"
                class="flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all"
                :class="localProducto.activo ? 'bg-green-500/10 border-green-500/30 text-green-400 hover:bg-green-500/20' : 'bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20'"
            >
                <div class="h-2 w-2 rounded-full" :class="localProducto.activo ? 'bg-green-500 shadow-lg shadow-green-500/50' : 'bg-red-500 shadow-lg shadow-red-500/50'"></div>
                <span class="text-[10px] font-bold uppercase">{{ localProducto.activo ? 'Activo' : 'Baja' }}</span>
            </button>

            <button @click="$emit('close')" class="h-9 w-9 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-colors">
               <i class="fas fa-times"></i>
            </button>
      </div>
    </div>

    <!-- MAIN CANVAS (STACKED BLOCKS) -->
    <div v-if="localProducto && localProducto.nombre !== undefined" class="flex-1 overflow-y-auto custom-scrollbar bg-[#0f172a] p-4 space-y-4">
        
        <!-- BLOCK 1: ESTRUCTURA DE COSTOS (Horizontal) -->
        <section class="bg-black/20 border border-rose-500/10 rounded-2xl p-4 shadow-xl">
            <h3 class="text-xs font-bold text-rose-500/50 uppercase tracking-widest flex items-center gap-2 mb-4">
                <i class="fas fa-brain text-rose-500"></i> Estructura de Costos & Precios
            </h3>
            
            <div class="flex items-center gap-8">
                <!-- Costo Rep -->
                <div class="flex-1 space-y-2">
                    <label class="text-[10px] font-bold text-rose-400/60 uppercase tracking-widest block">Costo de Reposición (Neto)</label>
                    <div class="relative group h-14 flex items-center">
                        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-rose-500/50 text-xl font-light">$</span>
                        <!-- Ghost Label -->
                        <span v-if="localCostos.costo_reposicion && !isCostoFocused" class="absolute inset-0 flex items-center justify-end pr-3 bg-black/40 border border-rose-500/20 rounded-xl py-3 text-2xl font-mono font-bold text-white pointer-events-none">
                            {{ Number(localCostos.costo_reposicion).toLocaleString('es-AR', {minimumFractionDigits: 2}) }}
                        </span>
                        <input v-excel
                            v-model.number="localCostos.costo_reposicion"
                            @change="updateCostTimestamp"
                            @focus="isCostoFocused = true"
                            @blur="isCostoFocused = false"
                            @keydown.enter="$event.target.blur()"
                            type="number" step="0.01"
                            class="w-full h-full bg-black/40 border border-rose-500/20 rounded-xl px-3 py-3 pl-8 text-2xl font-mono font-bold text-white text-right focus:border-rose-500/50 focus:outline-none transition-all"
                            :class="{'opacity-0': !isCostoFocused && localCostos.costo_reposicion}"
                        />
                    </div>
                    <div class="flex justify-between items-center px-1">
                        <span class="text-[10px] font-mono text-rose-500/40 uppercase">Act: {{ lastCostUpdate || 'Hoy' }}</span>
                        <span class="text-[10px] font-mono font-bold text-rose-400/40">
                             c/IVA: {{ formatCurrency(localCostos.costo_reposicion * (1 + (localCostos.iva_alicuota || 21)/100)) }}
                        </span>
                    </div>
                </div>

                <div class="shrink-0 text-white/10 text-xl"><i class="fas fa-plus"></i></div>

                <!-- Mirror Component (Margin & Roca) -->
                <div class="flex-[1.5] bg-cyan-900/10 border border-cyan-500/10 rounded-xl p-4 flex items-center gap-6">
                    <div class="flex-1 space-y-2">
                        <label class="text-[9px] font-bold text-cyan-500/70 uppercase tracking-widest text-center block">Margin %</label>
                        <div class="relative">
                           <input 
                               v-model.number="localCostos.rentabilidad_target"
                               @input="updateRocaFromRent"
                               type="number" step="0.1"
                               class="w-full bg-black/40 border border-cyan-500/30 rounded-lg py-2 text-xl font-mono font-bold text-cyan-400 text-center focus:border-cyan-400 focus:outline-none"
                           />
                           <span class="absolute right-2 top-1/2 -translate-y-1/2 text-cyan-500/30 font-bold text-xs">%</span>
                        </div>
                    </div>
                    
                    <div class="shrink-0 text-cyan-500/20 text-2xl"><i class="fas fa-exchange-alt"></i></div>

                    <div class="flex-1 space-y-2">
                        <label class="text-[9px] font-bold text-white/50 uppercase tracking-widest text-center block">Precio Roca (Neto)</label>
                        <div class="relative h-11 flex items-center">
                            <!-- Ghost Label -->
                            <span v-if="localCostos.precio_roca && !isRocaFocused" class="absolute inset-0 flex items-center justify-center bg-white/5 border border-white/10 rounded-lg text-xl font-mono font-bold text-white pointer-events-none">
                                $ {{ Number(localCostos.precio_roca).toLocaleString('es-AR', {minimumFractionDigits: 2}) }}
                            </span>
                            <input v-excel
                                v-model.number="localCostos.precio_roca"
                                @change="updateRentFromRoca"
                                @focus="isRocaFocused = true"
                                @blur="isRocaFocused = false"
                                @keydown.enter="$event.target.blur()"
                                type="number" step="0.01"
                                class="w-full h-full bg-white/5 border border-white/10 rounded-lg py-2 text-xl font-mono font-bold text-white text-center focus:border-white/40 focus:outline-none"
                                :class="{'opacity-0': !isRocaFocused && localCostos.precio_roca}"
                            />
                        </div>
                    </div>
                </div>

                <div class="shrink-0 text-white/10 text-xl"><i class="fas fa-arrow-right"></i></div>

                <!-- Final Result -->
                <div class="flex-1 space-y-2">
                    <label class="text-[10px] font-bold text-green-500 uppercase tracking-widest text-right block">Precio Final (C/ IVA)</label>
                    <div class="relative group">
                        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-green-500/30 text-xl font-light">$</span>
                        <input v-excel
                            :value="finalPrice"
                            @change="e => updateNetFromFinal(e.target.value)"
                            @keydown.enter="$event.target.blur()"
                            type="number"
                            class="w-full bg-green-500/5 border border-green-500/30 rounded-xl px-3 py-3 pl-8 text-3xl font-mono font-bold text-green-400 text-right focus:border-green-500/50 focus:outline-none transition-all"
                        />
                    </div>
                </div>
            </div>
        </section>


        <!-- BLOCK 2: LOGÍSTICA (Horizontal Row) -->
        <section class="bg-black/10 border border-white/5 rounded-2xl p-4 flex items-center justify-between gap-6 shadow-lg">
            <h3 class="text-[10px] font-bold text-blue-400/50 uppercase tracking-widest flex items-center gap-2 shrink-0">
                <i class="fas fa-boxes text-blue-400"></i> Logística
            </h3>
            
            <div class="flex-1 grid grid-cols-4 gap-4">
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Unidad Compra</label>
                    <input 
                        v-model="localProducto.presentacion_compra"
                        class="w-full bg-black/40 border border-white/10 rounded-lg px-2 py-1.5 text-white text-xs focus:border-blue-500/50 focus:outline-none"
                        placeholder="Ej: Bulto, Pack"
                    />
                </div>
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Unid. x Bulto</label>
                    <input 
                        v-model.number="localProducto.unidades_bulto"
                        type="number"
                        class="w-full bg-black/40 border border-white/10 rounded-lg px-2 py-1.5 text-white text-xs font-mono focus:border-blue-500/50 focus:outline-none"
                    />
                </div>
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Unidad Venta</label>
                    <SelectorCreatable
                         v-model="localProducto.unidad_medida"
                         :options="unidades"
                         item-key="codigo"
                         display-key="nombre"
                         size="sm"
                         placeholder="Selec..."
                         @create="handleCreateUnidad"
                    />
                </div>
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Venta Mínima</label>
                    <input 
                      v-model.number="localProducto.venta_minima"
                      type="number"
                      class="w-full bg-black/40 border border-white/10 rounded-lg px-2 py-1.5 text-white text-xs font-mono focus:border-blue-500/50 focus:outline-none"
                    />
                </div>
            </div>

            <div class="shrink-0 flex items-center gap-2 p-2 rounded bg-white/5 border border-white/10 transition-colors" :class="localProducto.es_kit ? 'border-rose-500/30 bg-rose-500/5' : ''">
                 <input type="checkbox" v-model="localProducto.es_kit" class="rounded bg-black/50 border-white/20 text-rose-500 focus:ring-0 cursor-pointer">
                 <span class="text-[9px] text-white/50 font-bold uppercase">Es Kit / Combo</span>
            </div>
            
            <div class="shrink-0 pt-1">
                 <div class="flex items-center gap-2 p-1.5 rounded bg-black/20 border border-white/5 cursor-pointer" @click="localProducto.tipo_producto = localProducto.tipo_producto === 'INSUMO' ? 'VENTA' : 'INSUMO'">
                      <div class="w-6 h-3 rounded-full relative transition-colors" :class="localProducto.tipo_producto === 'INSUMO' ? 'bg-orange-500' : 'bg-gray-700'">
                          <div class="absolute top-0.5 left-0.5 w-2 h-2 rounded-full bg-white transition-transform" :class="localProducto.tipo_producto === 'INSUMO' ? 'translate-x-3' : ''"></div>
                      </div>
                      <span class="text-[9px] font-bold uppercase" :class="localProducto.tipo_producto === 'INSUMO' ? 'text-orange-400' : 'text-gray-500'">
                          {{ localProducto.tipo_producto === 'INSUMO' ? 'Insumo' : 'Venta' }}
                      </span>
                 </div>
            </div>
        </section>

        <!-- BLOCK 3: PROVEEDORES (Compact) -->
        <section class="bg-black/20 border border-white/5 rounded-2xl p-4 shadow-lg overflow-hidden flex flex-col">
            <div class="flex justify-between items-center mb-2">
                <h3 class="text-[10px] font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                    <i class="fas fa-truck text-rose-500"></i> Historial de Proveedores
                </h3>
                <button @click="isAddingSupplier = !isAddingSupplier" class="text-[9px] bg-rose-500/20 text-rose-400 px-2 py-1 rounded hover:bg-rose-500/30 transition-colors uppercase font-bold tracking-widest">
                    <i class="fas" :class="isAddingSupplier ? 'fa-times' : 'fa-plus mr-1'"></i> {{ isAddingSupplier ? 'Cerrar' : 'Agregar' }}
                </button>
            </div>

            <!-- Add Form (Inline) -->
            <transition name="fade-slide-up">
                <div v-if="isAddingSupplier" class="mb-3 p-3 bg-rose-900/10 border border-rose-500/20 rounded-xl flex gap-3 items-end animate-in fade-in slide-in-from-top-2">
                    <div class="flex-1 space-y-1">
                        <label class="text-[8px] font-bold text-rose-400/50 uppercase">Proveedor</label>
                        <select v-model="newSupplier.proveedor_id" class="w-full bg-black/50 border border-rose-500/30 rounded-lg px-2 py-1 text-xs text-white focus:outline-none">
                            <option :value="null">Seleccionar...</option>
                            <option v-for="p in (proveedores || [])" :key="p.id" :value="p.id">{{ p.razon_social }}</option>
                        </select>
                    </div>
                    <div class="w-32 space-y-1">
                        <label class="text-[8px] font-bold text-rose-400/50 uppercase">Costo (Neto)</label>
                        <input v-excel v-model.number="newSupplier.costo" type="number" class="w-full bg-black/50 border border-rose-500/30 rounded-lg px-2 py-1 text-xs text-white focus:outline-none" placeholder="$ 0.00">
                    </div>
                    <button @click="saveSupplier" class="bg-rose-600 text-white text-[10px] px-4 py-1.5 rounded-lg font-bold hover:bg-rose-500 shadow-lg shadow-rose-900/20 transition-all uppercase tracking-widest">Vincular</button>
                </div>
            </transition>

            <!-- Table (Scrollable 3 rows) -->
            <div class="max-h-[140px] overflow-y-auto custom-scrollbar border border-white/5 rounded-lg">
                <table class="w-full text-[11px] text-left">
                    <thead class="bg-white/5 text-[9px] uppercase text-gray-500 sticky top-0">
                        <tr>
                            <th class="px-4 py-2 font-bold tracking-widest">Proveedor</th>
                            <th class="px-4 py-2 font-bold tracking-widest text-right">Costo Neto</th>
                            <th class="px-4 py-2 font-bold tracking-widest text-center">Últ. Act</th>
                            <th class="px-4 py-2 font-bold tracking-widest text-center">Acciones</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-white/5">
                        <tr v-for="prov in localProveedoresList" :key="prov.id" class="hover:bg-white/[0.02] transition-colors">
                            <td class="px-4 py-2 text-white font-medium italic">{{ getProvName(prov.proveedor_id) }}</td>
                            <td class="px-4 py-2 text-right font-mono text-rose-400 font-bold">$ {{ Number(prov.costo).toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</td>
                            <td class="px-4 py-2 text-center text-gray-500">{{ formatDate(prov.fecha) }}</td>
                            <td class="px-4 py-2 text-center">
                                <button @click="removeSupplier(prov.id)" class="text-gray-600 hover:text-red-500 transition-colors p-1">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </td>
                        </tr>
                        <tr v-if="!localProveedoresList?.length">
                            <td colspan="4" class="px-4 py-8 text-center text-gray-600 italic">No hay historial de proveedores vinculado.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- BLOCK 4: NOTAS (Estilo Pedido) -->
        <section class="rounded-2xl border transition-all duration-300"
                 :class="localProducto.descripcion && localProducto.descripcion.trim() !== '' 
                    ? 'bg-orange-500/10 border-orange-500/40 shadow-[0_0_20px_rgba(249,115,22,0.05)]' 
                    : 'bg-black/20 border-white/5'">
            <div class="px-4 py-2 border-b transition-colors flex items-center justify-between"
                 :class="localProducto.descripcion && localProducto.descripcion.trim() !== '' ? 'border-orange-500/20' : 'border-white/5'">
                <div class="flex items-center gap-2">
                    <i class="fas fa-sticky-note text-xs" :class="localProducto.descripcion && localProducto.descripcion.trim() !== '' ? 'text-orange-500' : 'text-gray-500'"></i>
                    <h3 class="text-[10px] font-bold uppercase tracking-widest" :class="localProducto.descripcion && localProducto.descripcion.trim() !== '' ? 'text-orange-200' : 'text-gray-500'">
                        Notas y Observaciones Internas
                    </h3>
                </div>
                <div v-if="localProducto.descripcion && localProducto.descripcion.trim() !== ''" class="text-[8px] font-black bg-orange-500 text-white px-1 rounded animate-pulse">CONTENIDO ACTIVO</div>
            </div>
            <textarea 
                v-model="localProducto.descripcion"
                class="w-full bg-transparent p-4 text-sm text-gray-200 focus:outline-none placeholder-white/5 resize-none min-h-[120px]"
                placeholder="Escribe aquí notas sobre logística, calidad, o detalles del producto que todo el equipo deba conocer..."
            ></textarea>
        </section>

    </div>

    <!-- ===== MODAL: ALTA RÁPIDA DE RUBRO (F4) ===== -->
    <Teleport to="body">
      <div
        v-if="showRubroModal"
        class="fixed inset-0 z-[200] flex items-center justify-center bg-black/70 backdrop-blur-sm"
        @click.self="showRubroModal = false"
      >
        <div class="w-full max-w-md bg-[#0f172a] border border-amber-500/40 rounded-2xl shadow-2xl shadow-amber-900/30 overflow-hidden animate-fade-in-up">
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-amber-500/20 bg-amber-500/5">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center text-amber-400 border border-amber-500/30">
                <i class="fas fa-tag text-sm"></i>
              </div>
              <div>
                <h3 class="text-sm font-bold text-amber-300 uppercase tracking-widest">Alta de Rubro</h3>
                <p class="text-[10px] text-amber-500/50">El código se genera automáticamente</p>
              </div>
            </div>
            <button @click="showRubroModal = false" class="text-white/30 hover:text-white transition-colors">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <!-- Form -->
          <div class="p-6 space-y-4">
            <!-- Nombre -->
            <div>
              <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
                Nombre <span class="text-rose-500">*</span>
              </label>
              <input
                v-model="rubroNewForm.nombre"
                ref="rubroNombreInput"
                type="text"
                class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:border-amber-500/50 focus:outline-none transition-all"
                placeholder="Ej: Desinfectantes Industriales"
                @keydown.enter="saveRubroFromModal"
                @keydown.escape="showRubroModal = false"
              />
            </div>

            <!-- Código (lectura, auto-generado) -->
            <div>
              <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
                Código <span class="text-white/20">(auto)</span>
              </label>
              <input
                v-model="rubroNewForm.codigo"
                type="text"
                maxlength="3"
                class="w-full bg-black/20 border border-white/5 rounded-lg px-3 py-2 text-amber-400 font-mono text-sm focus:border-amber-500/50 focus:outline-none transition-all uppercase"
                placeholder="Auto"
              />
            </div>

            <!-- Margen Default -->
            <div>
              <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
                Margen Propuesto <span class="text-white/20">(%)</span>
              </label>
              <input
                v-model.number="rubroNewForm.margen_default"
                type="number"
                min="0"
                max="100"
                step="0.5"
                class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:border-amber-500/50 focus:outline-none transition-all"
                placeholder="0"
              />
            </div>
          </div>

          <!-- Footer -->
          <div class="px-6 pb-6 flex justify-end gap-3">
            <button
              @click="showRubroModal = false"
              class="px-4 py-2 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-colors text-sm font-bold uppercase tracking-wider"
            >
              Cancelar
            </button>
            <button
              @click="saveRubroFromModal"
              :disabled="!rubroNewForm.nombre.trim()"
              class="px-6 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-bold text-sm uppercase tracking-wider shadow-lg shadow-amber-900/30 transition-all active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <i class="fas fa-save"></i>
              <span>Crear Rubro</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ===== MODAL: CONFIRMACIÓN ADOPCIÓN EN GENERAL ===== -->
    <Teleport to="body">
      <div
        v-if="showAdopcionGeneralConfirm"
        class="fixed inset-0 z-[210] flex items-center justify-center bg-black/80 backdrop-blur-sm"
      >
        <div class="w-full max-w-sm bg-[#0f172a] border border-yellow-500/50 rounded-2xl shadow-2xl shadow-yellow-900/40 overflow-hidden animate-fade-in-up">
          <!-- Header -->
          <div class="flex items-center gap-3 px-6 py-4 border-b border-yellow-500/20 bg-yellow-500/5">
            <div class="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-400 border border-yellow-500/30 text-lg">
              <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div>
              <h3 class="text-sm font-bold text-yellow-300 uppercase tracking-widest">Adopción en General</h3>
              <p class="text-[10px] text-yellow-500/50">Este producto es Huérfano</p>
            </div>
          </div>

          <!-- Body -->
          <div class="px-6 py-5 space-y-3">
            <p class="text-sm text-white/80 leading-relaxed">
              Este producto no tiene un rubro propio. ¿Confirmar que queda en <span class="font-bold text-white">General</span> y se lo da por <span class="font-bold text-yellow-300">adoptado</span>?
            </p>
            <p class="text-xs text-white/30 italic">
              Si querés asignarle un rubro específico, cerrá y elegí uno antes de guardar.
            </p>
          </div>

          <!-- Footer -->
          <div class="px-6 pb-6 flex gap-3">
            <button
              @click="showAdopcionGeneralConfirm = false; _pendingPayload = null"
              class="flex-1 px-4 py-2.5 rounded-xl border border-white/10 text-white/50 hover:text-white hover:border-white/30 transition-colors text-sm font-bold uppercase tracking-wider"
            >
              <i class="fas fa-arrow-left mr-1"></i> Elegir otro rubro
            </button>
            <button
              @click="confirmAdopcionGeneral"
              class="flex-1 px-4 py-2.5 rounded-xl bg-yellow-600 hover:bg-yellow-500 text-white font-bold text-sm uppercase tracking-wider shadow-lg shadow-yellow-900/30 transition-all active:scale-95 flex items-center justify-center gap-2"
            >
              <i class="fas fa-check"></i> Sí, queda en General
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Sticky Footer -->
    <div class="shrink-0 p-4 border-t border-rose-900/30 bg-black/40 flex justify-end items-center gap-4 backdrop-blur-md z-50">
        <div class="mr-auto text-[10px] text-white/20 hidden md:block italic">
            <span class="font-bold text-rose-500/50">SISTEMA V5</span> - Los cambios en la Estructura de Costos se recalculan en tiempo real.
        </div>
        
        <button 
            @click="$emit('close')"
            class="px-6 py-2.5 rounded-xl text-white/50 font-bold text-sm hover:text-white hover:bg-white/5 transition-colors uppercase tracking-widest"
        >
            Cancelar
        </button>
        <button 
            @click="save"
            class="bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-bold py-2.5 px-8 rounded-xl shadow-lg shadow-rose-900/40 transition-all active:scale-95 flex items-center gap-2 uppercase tracking-widest text-xs"
        >
            <i class="fas fa-save"></i>
            <span>Guardar Producto (F10)</span>
        </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductosStore } from '../../../stores/productos'
import productosApi from '../../../services/productosApi' // Direct import for sub-resources
import maestrosApi from '@/services/maestros' // V5.5 Dynamic Masters
import SelectorCreatable from '@/components/common/SelectorCreatable.vue'
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
    costo_reposicion: null,
    rentabilidad_target: 30, 
    precio_roca: null,
    iva_alicuota: 21, // Default IVA alicuota
    moneda_costo: 'ARS'
})
const lastCostUpdate = ref('')
const lastRentUpdate = ref('')

const flattenedRubros = computed(() => {
    if (!props.rubros) return [] // Guard Clause
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
const rubroError = ref(false)
const isCostoFocused = ref(false)
const isRocaFocused = ref(false)

// Computed for Final Price (Display)
const finalPrice = computed(() => {
    const roca = Number(localCostos.value.precio_roca) || 0
    const val = localCostos.value.iva_alicuota
    const alicuota = (val !== null && val !== undefined && !isNaN(val)) ? Number(val) : 21
    return parseFloat((roca * (1 + alicuota/100)).toFixed(2))
})

const updateCostTimestamp = () => {
    lastCostUpdate.value = dayjs().format('DD/MM HH:mm')
    if (isUpdating.value) return
    isUpdating.value = true
    
    const costo = Number(localCostos.value.costo_reposicion) || 0
    const rent = Number(localCostos.value.rentabilidad_target) || 0
    localCostos.value.precio_roca = parseFloat((costo * (1 + rent / 100)).toFixed(4))
    
    nextTick(() => { isUpdating.value = false })
}

const updateRocaFromRent = () => {
    if (isUpdating.value) return
    isUpdating.value = true
    
    lastRentUpdate.value = dayjs().format('DD/MM HH:mm')
    
    const costo = Number(localCostos.value.costo_reposicion) || 0
    const rent = Number(localCostos.value.rentabilidad_target) || 0
    
    localCostos.value.precio_roca = parseFloat((costo * (1 + rent / 100)).toFixed(4))
    
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
    const val = localCostos.value.iva_alicuota
    const alicuota = (val !== null && val !== undefined && !isNaN(val)) ? Number(val) : 21
    
    // Reverse Engineering: Roca = Final / (1 + IVA)
    const newRoca = parseFloat((priceFinal / (1 + alicuota/100)).toFixed(4))
    
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
    }
}

// --- FIRE WIRE CALCULATOR (V5.9) ---
const handleCalculator = (val, field, callback) => {
    if (typeof val !== 'string') val = String(val);
    
    // Evaluation Logic
    if (val.startsWith('+') || val.startsWith('=')) {
        try {
            const expression = val.substring(1).replace(/,/g, '.');
            // Basic sanitization
            if (/^[0-9+\-*/().\s]+$/.test(expression)) {
                // eslint-disable-next-line no-eval
                const result = eval(expression);
                if (!isNaN(result)) {
                    if (field === 'finalPrice') {
                        callback(result);
                    } else {
                        localCostos.value[field] = parseFloat(result.toFixed(4));
                        if (callback) callback();
                    }
                }
            }
        } catch (e) {
            console.warn("Calculator Error:", e);
        }
    } else {
        // Standard Number Input
        const num = parseFloat(val.replace(',', '.'));
        if (!isNaN(num)) {
            if (field === 'finalPrice') {
                callback(num);
            } else {
                localCostos.value[field] = num;
                if (callback) callback();
            }
        }
    }
}

// --- SUPPLIER MANAGEMENT (MOVED UP FOR HOISTING) ---
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

// --- SYNC ENGINE (DATA RACE FIX V5.8.1) ---
// Centralized logic to sync local state with props AND store data
const syncLocalState = (dependencySource = 'prop') => {
    const newVal = props.producto
    
    if (newVal) {
        // [GY-FIX] Deep copy only if:
        // 1. ID changed (switching from one product to another)
        // 2. We are initializing (local state is empty)
        // 3. We are transitioning from 'existing' to 'new' (template)
        
        const idChanged = (localProducto.value.id !== newVal.id)
        const isInitializing = Object.keys(localProducto.value).length === 0
        const isNewProductSync = !newVal.id && localProducto.value.id // Resetting form to new
        
        if (idChanged || isInitializing || isNewProductSync) {
             console.log(`[ProductoInspector] full-sync triggered by ${dependencySource}. ID change:`, idChanged);
             localProducto.value = JSON.parse(JSON.stringify(newVal))
             pristineName.value = localProducto.value.nombre || ''
             
             // Defaults
             if (localProducto.value.venta_minima === undefined) localProducto.value.venta_minima = 1.0;
             if (localProducto.value.unidades_bulto === undefined || localProducto.value.unidades_bulto === null) localProducto.value.unidades_bulto = 1.0;
             if (!localProducto.value.presentacion_compra) localProducto.value.presentacion_compra = ''; 
             if (!localProducto.value.tipo_producto) localProducto.value.tipo_producto = 'VENTA'

             // Costos
             localCostos.value = newVal.costos ? { ...newVal.costos } : { 
                 costo_reposicion: null, 
                 rentabilidad_target: 30, 
                 precio_roca: null, 
                 iva_alicuota: 21,
                 moneda_costo: 'ARS'
             }
             
             // Suppliers Sync
             localProveedoresList.value = localProducto.value.proveedores ? [...localProducto.value.proveedores] : []
             
             lastCostUpdate.value = ''
             lastRentUpdate.value = ''
        } else {
             // [STABILITY-FIX] If it's the SAME product (or same "new" state), 
             // we PRESERVE local edits. We only update master data dependencies.
             console.log(`[ProductoInspector] Minor sync (preserving edits) triggered by ${dependencySource}`);
        }

        // IVA LOGIC: Retry on every sync (Store might have loaded now)
        // This MUST run even if we didn't wipe, but only if the user hasn't manually set a different IVC rate?
        // Actually, normally the IVA rate follows the TasaID.
        if (tasasIva.value?.length) {
            if (localProducto.value.tasa_iva_id) {
                const tasa = tasasIva.value.find(t => t.id === localProducto.value.tasa_iva_id)
                if (tasa) localCostos.value.iva_alicuota = Number(tasa.valor)
            } else {
                // Default fallback for new products IF not set
                const defaultTasa = tasasIva.value.find(t => t.valor === 21) || tasasIva.value[0];
                if (defaultTasa && !localProducto.value.tasa_iva_id) {
                    localProducto.value.tasa_iva_id = defaultTasa.id;
                    localCostos.value.iva_alicuota = Number(defaultTasa.valor);
                }
            }
        }
    } else {
        // Reset
        localProducto.value = {}
         localCostos.value = { 
            costo_reposicion: null, 
            rentabilidad_target: 30, 
            precio_roca: null,
            iva_alicuota: 21,
            moneda_costo: 'ARS'
        }
        pristineName.value = ''
        localProveedoresList.value = []
    }
}

// --- ALTA RÁPIDA DE RUBRO (F4) — declarado aquí para que los watches lo puedan referenciar ---
const showRubroModal = ref(false)

// Watch both Product Prop AND Store Data (TasasIva)
watch(
    () => props.producto,
    (newVal) => {
        if (showRubroModal.value) return  // 🔒 No sincronizar mientras el modal de rubro está abierto
        if (newVal) syncLocalState('prop')
    },
    { immediate: true, deep: true }
)

watch(
    tasasIva,
    (newVal) => {
        if (showRubroModal.value) return  // 🔒 No sincronizar mientras el modal de rubro está abierto
        if (newVal?.length) syncLocalState('store')
    },
    { immediate: true }
)

// [V5.9 ADOPCIÓN GENERAL] Confirmación especial cuando un huérfano queda en General
const showAdopcionGeneralConfirm = ref(false)
let _pendingPayload = null  // Guardamos el payload mientras el operador confirma

const _executeSave = async (payload) => {
    try {
        let result;
        if (payload.id) {
            result = await productosStore.updateProducto(payload.id, payload)
            notification.add('Producto actualizado correctamente', 'success')
        } else {
            result = await productosStore.createProducto(payload)
            notification.add('Producto creado correctamente', 'success')
            localProducto.value.id = result.id
            emit('close')
        }
        emit('save', result)
    } catch (e) {
        console.error('[ProductoInspector] Save Error:', e)
        const msg = e.response?.data?.detail || e.message || 'Error desconocido'
        notification.add('Error al guardar: ' + msg, 'error')
    }
}

const confirmAdopcionGeneral = async () => {
    showAdopcionGeneralConfirm.value = false
    if (_pendingPayload) await _executeSave(_pendingPayload)
    _pendingPayload = null
}

const save = async () => {
    console.log('[ProductoInspector] Start Save...');
    console.log('LocalProducto:', localProducto.value);

    if (!localProducto.value || !localProducto.value.nombre) {
        notification.add('El nombre del producto es obligatorio', 'error')
        return
    }

    if (!localProducto.value.rubro_id) {
        rubroError.value = true
        notification.add('Debe seleccionar un Rubro / Categoría', 'error')
        return
    }
    rubroError.value = false

    const costo = Number(localCostos.value.costo_reposicion) || 0
    if (costo <= 0) {
        if (!confirm('⚠ ALERTA DE COSTOS: El Costo de Reposición es $0.00.\n\n¿Está SEGURO que desea continuar?')) {
            return
        }
    }

    if (!localProducto.value.codigo_visual || localProducto.value.codigo_visual.trim() === '') {
        localProducto.value.codigo_visual = null
    }

    const payload = {
        ...localProducto.value,
        costos: { ...localCostos.value }
    }

    // [V5.9 ADOPCIÓN GENERAL] Interceptar: huérfano + rubro = General → confirmar
    const isOrphan = !!(localProducto.value.flags_estado & 8)
    const generalRubro = flattenedRubros.value.find(r => r.nombre === 'General')
    const goingToGeneral = generalRubro && localProducto.value.rubro_id === generalRubro.id

    if (isOrphan && goingToGeneral) {
        _pendingPayload = payload
        showAdopcionGeneralConfirm.value = true
        return  // Esperar confirmación del operador
    }

    await _executeSave(payload)
}

// --- Dynamic Masters Handlers (V5.5) ---
const handleCreateUnidad = async (newVal) => {
    try {
        const res = await maestrosApi.createUnidad({ nombre: newVal })
        notification.add(`Unidad "${res.data.nombre}" creada`, 'success')
        await productosStore.fetchUnidades() 
        localProducto.value.unidad_medida = res.data.codigo
    } catch (e) {
        console.error(e)
        notification.add('Error al crear unidad', 'error')
    }
}

const handleCreateTasaIva = async (newVal) => {
    try {
        const val = parseFloat(newVal)
        if (isNaN(val)) return notification.add('Ingrese un valor numérico para la Tasa', 'warning')
        
        const res = await maestrosApi.createTasaIva({ nombre: `IVA ${val}%`, valor: val })
        notification.add(`Tasa IVA ${res.data.nombre} creada`, 'success')
        
        // Refresh store
        await productosStore.fetchTasasIva()
        
        localProducto.value.tasa_iva_id = res.data.id
        localCostos.value.iva_alicuota = Number(res.data.valor)
        
    } catch (e) {
        notification.add('Error al crear Tasa IVA: ' + e.message, 'error')
    }
}

// --- ALTA RÁPIDA DE RUBRO (F4) ---
const rubroNombreInput = ref(null)
const rubroNewForm = ref({ nombre: '', codigo: '', margen_default: 0 })

const handleCreateRubro = (query = '') => {
    // Abrir modal ABM completo, pre-llenando nombre con lo que escribió el operador
    rubroNewForm.value = { nombre: query || '', codigo: '', margen_default: 0 }
    showRubroModal.value = true
    // Focus en el campo nombre al abrir
    nextTick(() => {
        if (rubroNombreInput.value) rubroNombreInput.value.focus()
    })
}

const saveRubroFromModal = async () => {
    if (!rubroNewForm.value.nombre.trim()) return
    try {
        const payload = {
            nombre: rubroNewForm.value.nombre.trim(),
            margen_default: rubroNewForm.value.margen_default || 0
        }
        if (rubroNewForm.value.codigo.trim()) {
            payload.codigo = rubroNewForm.value.codigo.trim().toUpperCase()
        }

        const res = await maestrosApi.createRubro(payload)
        const newRubro = res.data

        // Push directo al array del store — sin re-fetch, sin reemplazo reactivo
        productosStore.rubros.push(newRubro)

        // Asignación directa: no toca currentProducto, no dispara el watch del inspector
        localProducto.value.rubro_id = newRubro.id

        notification.add(`Rubro "${newRubro.nombre}" creado`, 'success')
        showRubroModal.value = false
    } catch (e) {
        console.error(e)
        const detail = e?.response?.data?.detail || e.message
        notification.add('Error al crear Rubro: ' + detail, 'error')
    }
}

const handleUpdateTasaIva = (val) => {
    // Sync localCostos.iva_alicuota when Selector changes
    if (tasasIva.value) {
        const tasa = tasasIva.value.find(t => t.id === val)
        if (tasa) {
            localCostos.value.iva_alicuota = Number(tasa.valor)
        }
    }
}

const formatCurrency = (val) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(val || 0)

const handleKeydown = (e) => {
    if (e.key === 'F10') {
        e.preventDefault()
        if (showRubroModal.value) {
            saveRubroFromModal()  // F10 confirma el modal de rubro cuando está abierto
            return
        }
        save()
    }
    if (e.key === 'Escape') {
        if (showRubroModal.value) {
            showRubroModal.value = false
            return
        }
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
