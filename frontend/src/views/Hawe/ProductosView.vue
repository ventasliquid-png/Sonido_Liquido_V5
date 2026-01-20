<template>
  <div class="flex h-full w-full bg-[#0f172a] overflow-hidden tokyo-bg neon-red rounded-2xl border-2 border-rose-500 shadow-[0_0_30px_rgba(244,63,94,0.4)] p-6 relative">
    <!-- Sidebar is handled by Layout -->

    <!-- Main Content -->
    <main class="flex flex-1 flex-col min-w-0 relative">
      
      <!-- Top Bar -->
      <div class="flex items-center justify-between border-b border-white/10 bg-black/10 backdrop-blur-md px-6 py-4 z-30 shrink-0">
        <div class="flex items-center gap-4">
          <h1 class="font-outfit text-2xl font-bold text-white">
            <i class="fas fa-boxes mr-2 text-rose-500"></i> Productos
          </h1>
          <!-- Bulk Action Indicator & Button -->
          <div v-if="selectedIds.length > 0" class="flex items-center gap-2 ml-4">
              <span class="text-xs font-bold text-red-400 bg-red-900/20 px-2 py-1 rounded border border-red-500/30 animate-pulse">
                  {{ selectedIds.length }} SELECCIONADOS
              </span>
              <button 
                @click="handleBulkAction"
                class="flex items-center gap-2 rounded-lg px-3 py-1 text-xs font-bold text-white shadow-lg transition-transform active:scale-95"
                :class="filterStatus === 'inactive' ? 'bg-red-600 hover:bg-red-500 shadow-red-500/20' : 'bg-orange-600 hover:bg-orange-500 shadow-orange-500/20'"
                :title="filterStatus === 'inactive' ? 'Eliminar Definitivamente' : 'Desactivar (Baja Lógica)'"
              >
                <i :class="filterStatus === 'inactive' ? 'fas fa-trash-alt' : 'fas fa-archive'"></i>
                <span>{{ filterStatus === 'inactive' ? `Eliminar` : `Baja` }}</span>
              </button>
          </div>
          
          <!-- Search -->
          <div class="relative w-64 group">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-white/30 group-focus-within:text-rose-400 transition-colors"></i>
            <input 
              v-model="productosStore.filters.search"
              @input="handleSearch"
              type="text" 
              placeholder="Buscar por Nombre, SKU o Código (F3)..." 
              class="w-full rounded-lg border border-white/10 bg-black/20 py-2 pl-10 pr-4 text-sm text-white placeholder-white/30 focus:border-rose-500 focus:bg-black/40 focus:outline-none transition-all"
            />
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-3">
          <!-- Rubro Filter -->
          <select 
            v-model="productosStore.filters.rubro_id"
            @change="productosStore.fetchProductos()"
            class="rounded-lg border border-white/10 bg-[#0f172a] text-white px-3 py-2 text-sm focus:border-rose-500 focus:outline-none"
          >
            <option :value="null" class="bg-[#0f172a] text-white">Todos los Rubros</option>
            <option v-for="rubro in flattenedRubros" :key="rubro.id" :value="rubro.id" class="bg-[#0f172a] text-white">
                {{ rubro.indent }}{{ rubro.nombre }}
            </option>
          </select>

          <!-- Active Toggle -->
          <!-- Filter Group (All/Active/Inactive) -->
          <div class="flex bg-black/20 rounded-lg p-1 border border-white/10">
              <button 
                  @click="setFilter('all')"
                  class="px-3 py-1.5 text-xs font-bold rounded-md transition-all"
                  :class="filterStatus === 'all' ? 'bg-indigo-600/70 text-white shadow-md ring-1 ring-indigo-500' : 'text-white/40 hover:text-white hover:bg-white/5'"
              >
                  Todos
              </button>
              <button 
                  @click="setFilter('active')"
                  class="px-3 py-1.5 text-xs font-bold rounded-md transition-all"
                  :class="filterStatus === 'active' ? 'bg-green-600/70 text-white shadow-md ring-1 ring-green-500' : 'text-white/40 hover:text-white hover:bg-white/5'"
              >
                  Activos
              </button>
              <button 
                  @click="setFilter('inactive')"
                  class="px-3 py-1.5 text-xs font-bold rounded-md transition-all"
                  :class="filterStatus === 'inactive' ? 'bg-red-600/70 text-white shadow-md ring-1 ring-red-500' : 'text-white/40 hover:text-white hover:bg-white/5'"
              >
                  Inactivos
              </button>
          </div>

          <!-- Sort Menu -->
          <div class="relative">
            <button 
                @click="showSortMenu = !showSortMenu" 
                class="flex items-center gap-2 rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-sm text-white hover:bg-white/5 transition-colors min-w-[140px] justify-between" 
                title="Ordenar"
            >
                <div class="flex items-center gap-2">
                    <i class="fas fa-sort-amount-down text-rose-500"></i>
                    <span v-if="sortBy === 'alpha_asc'">A-Z</span>
                    <span v-else-if="sortBy === 'alpha_desc'">Z-A</span>
                    <span v-else-if="sortBy === 'id_desc'">Recientes</span>
                    <span v-else>Ordenar</span>
                </div>
                <i class="fas fa-chevron-down text-xs opacity-50"></i>
            </button>
            
            <!-- Dropdown -->
            <div v-if="showSortMenu" class="absolute right-0 mt-2 w-48 bg-[#2e0a13] border border-rose-500/30 rounded-lg shadow-xl z-50 overflow-hidden">
                <div class="fixed inset-0 z-40" @click="showSortMenu = false"></div>
                <div class="relative z-50 py-1">
                    <button @click="sortBy = 'alpha_asc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-rose-100 hover:bg-rose-500/10" :class="{ 'text-rose-400 font-bold': sortBy === 'alpha_asc' }">A-Z Alfabético</button>
                    <button @click="sortBy = 'alpha_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-rose-100 hover:bg-rose-500/10" :class="{ 'text-rose-400 font-bold': sortBy === 'alpha_desc' }">Z-A Alfabético</button>
                    <button @click="sortBy = 'id_desc'; showSortMenu = false" class="block w-full text-left px-4 py-2 text-sm text-rose-100 hover:bg-rose-500/10" :class="{ 'text-rose-400 font-bold': sortBy === 'id_desc' }">Más Recientes</button>
                </div>
            </div>
          </div>

          <!-- View Toggle -->
          <div class="flex bg-white/5 rounded-lg p-1 border border-white/10">
            <button 
                @click="viewMode = 'grid'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'grid' ? 'bg-rose-500/20 text-rose-400' : 'text-white/30 hover:text-white'"
                title="Vista Cuadrícula"
            >
                <i class="fas fa-border-all"></i>
            </button>
            <button 
                @click="viewMode = 'list'"
                class="p-1.5 rounded-md transition-all"
                :class="viewMode === 'list' ? 'bg-rose-500/20 text-rose-400' : 'text-white/30 hover:text-white'"
                title="Vista Lista"
            >
                <i class="fas fa-list"></i>
            </button>
          </div>

          <!-- New Button -->
          <!-- New Button -->
          <button 
            @click="createNew"
            class="flex items-center gap-2 rounded-lg bg-rose-600 px-4 py-2 text-sm font-bold text-white shadow-lg shadow-rose-500/20 transition-transform active:scale-95 hover:bg-rose-500"
          >
            <i class="fas fa-plus"></i>
            <span>Nuevo</span>
          </button>


        </div>
      </div>

      <!-- Content Area -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-rose-900/50">
        
        <!-- Loading State -->
        <div v-if="productosStore.loading" class="flex h-full items-center justify-center">
            <div class="h-12 w-12 animate-spin rounded-full border-4 border-rose-500 border-t-transparent"></div>
        </div>

        <!-- Empty State -->
        <div v-else-if="productosStore.productos.length === 0" class="flex h-full flex-col items-center justify-center text-white/30">
            <i class="fas fa-search mb-4 text-4xl opacity-50"></i>
            <p>No se encontraron productos</p>
        </div>

        <!-- Data Display -->
        <div v-else>
            <!-- Grid View -->
            <div v-if="viewMode === 'grid'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
                <div 
                    v-for="producto in sortedProductos" 
                    :key="producto.id"
                    class="relative min-h-[160px] group"
                    @contextmenu.prevent="handleContextMenu($event, producto)"
                >
                    <!-- Selection Checkbox -->
                    <div class="absolute top-2 left-2 z-20" @click.stop>
                        <input 
                            type="checkbox" 
                            :checked="selectedIds.includes(producto.id)" 
                            @change="toggleSelection(producto.id)"
                            class="rounded bg-[#2e0a13] border-rose-500/50 text-rose-500 focus:ring-0 focus:ring-offset-0 cursor-pointer h-5 w-5 shadow-lg shadow-black/50 opacity-50 group-hover:opacity-100 transition-opacity"
                            :class="{ 'opacity-100': selectedIds.includes(producto.id) }"
                        />
                    </div>
                    <ProductoCard 
                        :producto="producto"
                        :selected="selectedId === producto.id"
                        class="w-full"
                        @click="selectProducto(producto)"
                        @select="selectProducto(producto)"
                    >
                        <template #status-action>
                            <button 
                                @click.stop="handleToggleActive(producto)"
                                v-if="producto.activo"
                                class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 bg-green-500/50"
                                title="Desactivar"
                            >
                                <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm translate-x-3.5" />
                            </button>
                             <button 
                                @click.stop="handleToggleActive(producto)"
                                v-else
                                class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0 bg-red-500/50"
                                title="Activar"
                            >
                                <span class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm translate-x-1" />
                            </button>
                        </template>
                    </ProductoCard>
                </div>
            </div>

            <!-- List View -->
            <div v-else class="space-y-1">
                <div class="flex items-center justify-between px-4 py-2 text-xs font-bold text-rose-900/50 uppercase tracking-wider border-b border-white/5 mb-2">
                    <div class="w-8">
                        <input type="checkbox" :checked="isAllSelected" @click="toggleSelectAll" class="rounded bg-transparent border-rose-800 focus:ring-0 checked:bg-rose-500 cursor-pointer"/>
                    </div>
                    <div class="flex-1">Producto</div>
                    <div class="w-32 hidden md:block">Rubro</div>
                    <div class="w-24 text-center">SKU</div>
                    <div class="w-24 text-center">Estado</div>
                    <div class="w-10"></div>
                </div>

                <div 
                    v-for="producto in sortedProductos" 
                    :key="producto.id"
                    @click="selectProducto(producto)"
                    @contextmenu.prevent="handleContextMenu($event, producto)"
                    class="group flex items-center justify-between p-2 rounded-lg border border-transparent hover:bg-rose-900/10 hover:border-rose-900/20 cursor-pointer transition-all"
                    :class="{ 'bg-rose-900/20 border-rose-500/30': selectedId === producto.id }"
                >
                    <!-- Checkbox (Always Visible) -->
                    <div class="w-8 flex items-center justify-center p-2" @click.stop>
                        <input 
                            type="checkbox" 
                            :checked="selectedIds.includes(producto.id)" 
                            @change="toggleSelection(producto.id)"
                            class="rounded bg-[#020a0f] border-rose-800/50 text-rose-500 focus:ring-0 focus:ring-offset-0 cursor-pointer h-4 w-4"
                        />
                    </div>

                    <div class="flex items-center gap-3 flex-1 min-w-0">
                        <div class="h-8 w-8 rounded bg-[#2e0a13] flex items-center justify-center text-rose-500 border border-rose-900/30">
                            <i class="fas fa-box text-xs"></i>
                        </div>
                        <div class="min-w-0">
                            <div class="font-bold text-rose-100 text-sm truncate">{{ producto.nombre }}</div>
                            <div class="text-[10px] text-rose-400/50 block md:hidden">{{ producto.sku }}</div>
                        </div>
                    </div>

                    <div class="w-32 hidden md:block text-xs text-rose-200/50 truncate pr-2">
                         {{ getRubroName(producto.rubro_id) }}
                    </div>

                    <div class="w-24 text-center hidden md:block">
                        <span class="text-xs font-mono text-rose-400">{{ producto.sku }}</span>
                    </div>
                    
                    <div class="w-24 flex justify-center">
                        <button 
                            @click.stop="handleToggleActive(producto)"
                            class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0"
                            :class="producto.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                            title="Click para cambiar estado"
                        >
                            <span 
                                class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                :class="producto.activo ? 'translate-x-3.5' : 'translate-x-1'"
                            />
                        </button>
                    </div>

                    <div class="w-10 flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                         <button @click.stop="selectProducto(producto)" class="text-rose-400 hover:text-white"><i class="fas fa-pencil"></i></button>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </main>

    <!-- Central Inspector Modal -->
    <div v-if="showInspector" class="fixed inset-0 z-[60] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 md:p-8" @click.self="closeInspector">
        <div class="w-full max-w-5xl h-[85vh] flex flex-col relative animate-fade-in-up">
            <ProductoInspector 
                class="h-full flex-1"
                :producto="productosStore.currentProducto"
                :rubros="productosStore.rubros"
                @close="closeInspector"
                @save="handleSave"
                @toggle-active="handleToggleActive"
            />
        </div>
    </div>

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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useProductosStore } from '../../stores/productos'
import { useNotificationStore } from '../../stores/notification'
import ProductoCard from './components/ProductoCard.vue'
import ProductoInspector from './components/ProductoInspector.vue'
import ContextMenu from '../../components/common/ContextMenu.vue'

const router = useRouter()
const route = useRoute()
const productosStore = useProductosStore()
const notificationStore = useNotificationStore()

const showInspector = ref(false)
const selectedId = ref(null)
const selectedIds = ref([]) 
const sortBy = ref('alpha_asc')
const viewMode = ref('grid')
const showSortMenu = ref(false)
const filterStatus = ref('active')
let searchTimeout = null

const contextMenu = ref({
    show: false,
    x: 0,
    y: 0,
    actions: []
})

const handleContextMenu = (e, producto) => {
    contextMenu.value = {
        show: true,
        x: e.clientX,
        y: e.clientY,
        actions: [
            { 
                label: 'Editar', 
                iconClass: 'fas fa-edit', 
                action: () => selectProducto(producto) 
            },
            { 
                label: 'Clonar (Copiar datos)', 
                iconClass: 'fas fa-clone', 
                action: () => handleClone(producto) 
            },
            { 
                label: producto.activo ? 'Desactivar' : 'Activar', 
                iconClass: producto.activo ? 'fas fa-eye-slash' : 'fas fa-eye', 
                action: () => handleToggleActive(producto),
                class: producto.activo ? 'text-red-400' : 'text-green-400'
            },
            {
                label: 'Ver en Inspector',
                iconClass: 'fas fa-search',
                action: () => selectProducto(producto)
            }
        ]
    }
}

const flattenedRubros = computed(() => {
    return productosStore.rubros;
})

const getRubroName = (id) => flattenedRubros.value.find(r => r.id === id)?.nombre || '-'

const sortedProductos = computed(() => {
    // Create a copy to sort
    let items = [...productosStore.productos];
    
    return items.sort((a,b) => {
        switch (sortBy.value) {
            case 'alpha_asc': return a.nombre.localeCompare(b.nombre);
            case 'alpha_desc': return b.nombre.localeCompare(a.nombre);
            case 'id_desc': return b.id - a.id; 
            default: return 0;
        }
    });
});

const handleSearch = () => {
    if (searchTimeout) clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
        productosStore.fetchProductos()
    }, 300)
}




const setFilter = (status) => {
    filterStatus.value = status
    if (status === 'all') productosStore.filters.activo = null
    else if (status === 'active') productosStore.filters.activo = true
    else if (status === 'inactive') productosStore.filters.activo = false
    
    productosStore.fetchProductos()
}

watch(filterStatus, () => {
    selectedIds.value = [] // Clear items when filter changes
})

const isAllSelected = computed(() => {
    if (sortedProductos.value.length === 0) return false
    return sortedProductos.value.every(p => selectedIds.value.includes(p.id))
})

const toggleSelection = (id) => {
    if (selectedIds.value.includes(id)) {
        selectedIds.value = selectedIds.value.filter(existingId => existingId !== id)
    } else {
        selectedIds.value = [...selectedIds.value, id]
    }
}

const toggleSelectAll = () => {
    if (isAllSelected.value) {
        selectedIds.value = []
    } else {
        selectedIds.value = sortedProductos.value.map(p => p.id)
    }
}

const handleBulkAction = async () => {
    if (filterStatus.value === 'inactive') {
        // Hard Delete
        await handleBulkHardDelete()
    } else {
        // Soft Delete (Baja Lógica)
        await handleBulkSoftDelete()
    }
}

const handleBulkSoftDelete = async () => {
    if (!confirm(`¿Está seguro que desea dar de BAJA (desactivar) a ${selectedIds.value.length} productos?`)) return
    
    let successCount = 0
    let failCount = 0
    
    productosStore.loading = true
    
    for (const id of selectedIds.value) {
        try {
            // Check status locally
            const p = productosStore.productos.find(prod => prod.id === id)
            // Even if p.activo is false locally, maybe we want to ensure? 
            // PRO TIP: User might have filtered by 'All' and wants to deactivate.
            // If p.activo is true, we deactivate.
            if (p && p.activo) {
                await productosStore.toggleEstado(id) 
                successCount++
            }
        } catch (e) {
            console.error(e)
            failCount++
        }
    }
    
    productosStore.loading = false
    
    if (successCount > 0) notificationStore.add(`${successCount} productos desactivados correctamente`, 'success')
    if (failCount > 0) notificationStore.add(`Falló la desactivación de ${failCount} productos`, 'error')
    
    selectedIds.value = []
    
    // Force wait for DB commit propagation
    setTimeout(() => {
        productosStore.fetchProductos()
    }, 500)
}

const handleBulkHardDelete = async () => {
    if (!confirm(`PELIGRO: ¿Está seguro que desea eliminar DEFINITIVAMENTE ${selectedIds.value.length} productos? Esta acción NO se puede deshacer.`)) return
    
    let successCount = 0
    let failCount = 0
    
    for (const id of selectedIds.value) {
        try {
            await productosStore.hardDeleteProducto(id)
            successCount++
        } catch (e) {
            failCount++
        }
    }
    
    if (successCount > 0) notificationStore.add(`${successCount} productos eliminados definitivamente`, 'success')
    if (failCount > 0) notificationStore.add(`${failCount} productos no se pudieron eliminar (tienen órdenes asociadas)`, 'error')
    
    selectedIds.value = []
    // Store already filters locally but let's encourage refresh if needed
}

const selectProducto = async (producto) => {
    try {
        selectedId.value = producto.id
        // Show inspector immediately with loading state (if supported) or keep stale until loaded?
        // Let's force show to ensure aside opens
        showInspector.value = true
        
        await productosStore.fetchProductoById(producto.id)
    } catch (e) {
        alert('Error cargando producto: ' + e.message)
        console.error(e)
    }
}

const createNew = () => {
    selectedId.value = null
    productosStore.currentProducto = {
        nombre: '',
        sku: 'AUTO', // Backend assigns it
        codigo_visual: '',
        rubro_id: null,
        unidad_medida: 'UN',
        activo: true,
        es_kit: false,
        costos: {
            costo_reposicion: 0,
            rentabilidad_target: 30,
            precio_roca: 0,
            iva_alicuota: 21
        },
        // Industrial Fields Defaults
        tipo_producto: 'VENTA',
        unidad_stock_id: null,
        unidad_compra_id: null,
        factor_compra: 1.0,
        proveedor_habitual_id: null,
        tasa_iva_id: null
    }
    showInspector.value = true
}

const handleClone = async (producto) => {
    try {
        // Fetch full product details including costs
        const fullData = await productosStore.fetchProductoById(producto.id);
        
        // Prepare clone
        productosStore.currentProducto = {
            ...fullData,
            id: null, // Critical: ensure it's a NEW item
            nombre: `CLON - ${fullData.nombre}`,
            sku: 'AUTO',
            activo: true
        };
        
        selectedId.value = null;
        showInspector.value = true;
        notificationStore.add('Cargando datos para clonar...', 'info');
    } catch (e) {
        notificationStore.add('Error al preparar clon: ' + e.message, 'error');
    }
}

const closeInspector = () => {
    showInspector.value = false
    selectedId.value = null
    productosStore.currentProducto = null
}

const handleSave = async (payload) => {
    try {
        let savedItem;
        if (payload.id) {
            savedItem = await productosStore.updateProducto(payload.id, payload)
            notificationStore.add('Producto actualizado', 'success')
        } else {
            savedItem = await productosStore.createProducto(payload)
            notificationStore.add('Producto creado correctamente', 'success')
        }
        
        // Logic for Satellite Mode
        if (route.query.mode === 'satellite') {
            console.log('[Satellite] Notify parent and closing...');
            if (window.opener) {
                window.opener.postMessage({ 
                    type: 'PRODUCTO_CREADO', 
                    producto: savedItem 
                }, '*');
            }
            setTimeout(() => window.close(), 500);
        } else {
            closeInspector()
        }
    } catch (e) {
        // Error handled in store but we can add UI feedback
        console.error('[Frontend] Save error:', e);
    }
}

const handleToggleActive = async (producto) => {
    // Optimistic UI Update Logic could be here, but let's rely on server for safety
    const oldStatus = producto.activo;
    const newStatus = !oldStatus;
    
    if (oldStatus && !newStatus) {
         if (!confirm(`¿Está seguro de desactivar el producto "${producto.nombre}"?`)) return
    }
    
    try {
        console.log(`[Frontend] Toggling product ${producto.id} from ${oldStatus} to ${newStatus}`);
        await productosStore.toggleEstado(producto.id)
        
        // Force strict reactivity update
        // The store should have updated the item in the list, but let's verify
        
        const currentFilter = productosStore.filters.activo;
        
        // Always refresh if we are in a filtered view to ensure consistency
        if (currentFilter !== null) {
            console.log('[Frontend] Refreshing list due to filter mismatch...');
            // Add small delay to allow DB commit propagation
            setTimeout(async () => {
                await productosStore.fetchProductos()
                
                // Close inspector if item disappeared from current view
                if (selectedId.value === producto.id) {
                     // Check if it still exists in the fetched list
                     const exists = productosStore.productos.find(p => p.id === producto.id);
                     if (!exists) {
                         closeInspector()
                     }
                }
            }, 200);
        }
    } catch (e) {
        console.error('[Frontend] Error executing toggle:', e);
        // Revert optimistic update if we did one (we didn't yet)
        alert('Error al cambiar estado: ' + e.message);
    }
}

// Keyboard Shortcuts
const handleKeydown = (e) => {
    if (e.key === 'F3') {
        e.preventDefault()
        const input = document.querySelector('input[type="text"]')
        if (input) input.focus()
    }
    if (e.key === 'Escape') {
        if (showInspector.value) closeInspector()
    }
    if (e.key === 'F4') {
        e.preventDefault()
        createNew()
    }
}

onMounted(async () => {
    window.addEventListener('keydown', handleKeydown)
    
    // [STABILITY-FIX] Data is now pre-loaded by App.vue boot sequence.
    // We only fetch if stores are empty.
    const promises = []
    if (productosStore.rubros.length === 0) promises.push(productosStore.fetchRubros())
    if (productosStore.productos.length === 0) promises.push(productosStore.fetchProductos())
    
    if (promises.length > 0) await Promise.all(promises)

    // DEOU: Check for auto-trigger new
    if (route.query.action === 'new') {
        setTimeout(() => {
            createNew();
            if (route.query.search) {
                productosStore.currentProducto.nombre = route.query.search;
                // Also put it in the filter to show context
                productosStore.filters.search = route.query.search;
            }
        }, 300);
    }
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

</script>
