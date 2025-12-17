<template>
  <div class="flex h-screen w-full overflow-hidden bg-[#1a050b]">
    <!-- Sidebar is handled by Layout -->

    <!-- Main Content -->
    <main class="flex flex-1 flex-col min-w-0 relative">
      
      <!-- Top Bar -->
      <div class="flex items-center justify-between border-b border-white/10 bg-[#2e0a13]/90 px-6 py-4 backdrop-blur-md z-30 shrink-0">
        <div class="flex items-center gap-4">
          <h1 class="font-outfit text-2xl font-bold text-white">
            <i class="fas fa-boxes mr-2 text-rose-500"></i> Productos
          </h1>
          <!-- Bulk Action Indicator -->
          <span v-if="selectedIds.length > 0" class="ml-4 text-xs font-bold text-red-400 bg-red-900/20 px-2 py-1 rounded border border-red-500/30 animate-pulse">
              {{ selectedIds.length }} SELECCIONADOS
          </span>
          
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
            class="rounded-lg border border-white/10 bg-[#1a050b] text-white px-3 py-2 text-sm focus:border-rose-500 focus:outline-none"
          >
            <option :value="null" class="bg-[#1a050b] text-white">Todos los Rubros</option>
            <option v-for="rubro in flattenedRubros" :key="rubro.id" :value="rubro.id" class="bg-[#1a050b] text-white">
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
            <span>Nuevo</span>
          </button>

            <span>Nuevo</span>
          </button>

          <!-- Dynamic Bulk Button -->
          <button 
            v-if="selectedIds.length > 0"
            @click="handleBulkAction"
            class="ml-2 flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-bold text-white shadow-lg transition-transform active:scale-95"
            :class="filterStatus === 'inactive' ? 'bg-red-600 hover:bg-red-500 shadow-red-500/20' : 'bg-orange-600 hover:bg-orange-500 shadow-orange-500/20'"
            :title="filterStatus === 'inactive' ? 'Eliminar Definitivamente' : 'Desactivar (Baja Lógica)'"
          >
            <i :class="filterStatus === 'inactive' ? 'fas fa-trash-alt' : 'fas fa-archive'"></i>
            <span class="hidden sm:inline">{{ filterStatus === 'inactive' ? `Eliminar (${selectedIds.length})` : `Baja (${selectedIds.length})` }}</span>
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

    <!-- Right Inspector -->
    <aside 
      class="w-96 border-l border-white/10 bg-[#2e0a13]/95 flex flex-col z-50 shadow-xl overflow-hidden shrink-0"
    >
        <div v-if="!showInspector" class="flex flex-col items-center justify-center h-full text-white/30 p-6 text-center">
             <i class="fas fa-box-open text-4xl mb-4"></i>
             <p>Seleccione un producto para ver propiedades o presione "Nuevo"</p>
        </div>
        
        <ProductoInspector 
            v-else
            class="h-full flex flex-col"
            :producto="productosStore.currentProducto"
            :rubros="productosStore.rubros"
            @close="closeInspector"
            @save="handleSave"
            @toggle-active="handleToggleActive"
      />
    </aside>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProductosStore } from '../../stores/productos'
import { useNotificationStore } from '../../stores/notification'
import ProductoCard from './components/ProductoCard.vue'
import ProductoInspector from './components/ProductoInspector.vue'

const router = useRouter()
const productosStore = useProductosStore()
const notificationStore = useNotificationStore()

const showInspector = ref(false)
const selectedId = ref(null)
const selectedIds = ref([]) // IDs for bulk actions
const sortBy = ref('alpha_asc')
const viewMode = ref('grid')
const showSortMenu = ref(false)
const filterStatus = ref('active') // all, active, inactive
let searchTimeout = null

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
    for (const id of selectedIds.value) {
        try {
            // Check status locally
            const p = productosStore.productos.find(prod => prod.id === id)
            if (p && p.activo) {
                await productosStore.toggleEstado(id) 
                // toggleEstado handles notification, maybe too spammy? 
                // store handles 'Error', 'Success'.
                successCount++
            }
        } catch (e) {
            console.error(e)
        }
    }
    notificationStore.add(`${successCount} productos desactivados`, 'success')
    selectedIds.value = []
    productosStore.fetchProductos()
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
    selectedId.value = producto.id
    await productosStore.fetchProductoById(producto.id)
    showInspector.value = true
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
            margen_mayorista: 30,
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

const closeInspector = () => {
    showInspector.value = false
    selectedId.value = null
    productosStore.currentProducto = null
}

const handleSave = async (payload) => {
    try {
        if (payload.id) {
            await productosStore.updateProducto(payload.id, payload)
        } else {
            await productosStore.createProducto(payload)
        }
        closeInspector()
    } catch (e) {
        // Error handled in store
    }
}

const handleToggleActive = async (producto) => {
    const newStatus = !producto.activo
    if (producto.activo && !newStatus) {
         if (!confirm(`¿Está seguro de desactivar el producto "${producto.nombre}"?`)) return
    }
    
    await productosStore.toggleEstado(producto.id)
    
    // Auto-refresh: If we are filtering by Active/Inactive, and the product status no longer matches the filter,
    // we should remove it from the view (or refresh).
    // filters.activo is: true (Actives), false (Inactives), null (All)
    
    const currentFilter = productosStore.filters.activo;
    
    if (currentFilter !== null) { // Only if we are filtering
        // If filter is Active (true) and product became Inactive (false) -> mismatch
        // If filter is Inactive (false) and product became Active (true) -> mismatch
        if (currentFilter !== newStatus) {
             // Refresh list to remove the item
             await productosStore.fetchProductos()
             // If we were inspecting this product, close it because it disappeared
             if (selectedId.value === producto.id) {
                 closeInspector()
             }
        }
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
}

onMounted(async () => {
    window.addEventListener('keydown', handleKeydown)
    await Promise.all([
        productosStore.fetchRubros(),
        productosStore.fetchProductos()
    ])
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

</script>
