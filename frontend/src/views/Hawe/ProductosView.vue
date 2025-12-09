<template>
  <div class="flex h-screen w-full overflow-hidden bg-[#1a050b]">
    <!-- Sidebar removed (handled by Layout) -->

    <!-- Main Content -->
    <main class="flex flex-1 flex-col min-w-0 relative">
      
      <!-- Top Bar -->
      <div class="flex items-center justify-between border-b border-white/10 bg-[#2e0a13]/90 px-6 py-4 backdrop-blur-md z-10 shrink-0">
        <div class="flex items-center gap-4">
          <h1 class="font-outfit text-2xl font-bold text-white">
            <i class="fas fa-boxes mr-2 text-rose-500"></i> Productos
          </h1>
          
          <!-- Search -->
          <div class="relative w-96 group">
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
            class="rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-sm text-white focus:border-rose-500 focus:outline-none"
          >
            <option :value="null">Todos los Rubros</option>
            <option v-for="rubro in flattenedRubros" :key="rubro.id" :value="rubro.id">
                {{ rubro.indent }}{{ rubro.nombre }}
            </option>
          </select>

          <!-- Active Toggle -->
          <button 
            @click="toggleShowInactive"
            class="flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm transition-colors"
            :class="!productosStore.filters.activo ? 'bg-rose-500/20 text-rose-300 border-rose-500/50' : 'bg-black/20 text-white/50 hover:bg-white/5'"
          >
            <i class="fas fa-eye-slash"></i>
            <span class="hidden sm:inline">Inactivos</span>
          </button>

          <!-- New Button -->
          <button 
            @click="createNew"
            class="flex items-center gap-2 rounded-lg bg-rose-600 px-4 py-2 text-sm font-bold text-white shadow-lg shadow-rose-900/20 transition-transform hover:bg-rose-500 active:scale-95"
          >
            <i class="fas fa-plus"></i>
            <span>Nuevo</span>
          </button>
        </div>
      </div>

      <!-- Grid Content -->
      <div class="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-rose-900/50">
        <div v-if="productosStore.loading" class="flex h-full items-center justify-center">
            <div class="h-12 w-12 animate-spin rounded-full border-4 border-rose-500 border-t-transparent"></div>
        </div>

        <div v-else-if="productosStore.productos.length === 0" class="flex h-full flex-col items-center justify-center text-white/30">
            <i class="fas fa-search mb-4 text-4xl opacity-50"></i>
            <p>No se encontraron productos</p>
        </div>

        <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
            <!-- Wrapper Strategy Implementation -->
            <div 
                v-for="producto in productosStore.productos" 
                :key="producto.id"
                class="relative min-h-[160px]"
            >
                <ProductoCard 
                    :producto="producto"
                    :selected="selectedId === producto.id"
                    class="absolute top-0 left-0 w-full"
                    @click="selectProducto(producto)"
                    @select="selectProducto(producto)"
                />
            </div>
        </div>
      </div>
    </main>

    <!-- Right Inspector (Fixed Sibling) -->
    <aside 
      class="w-96 border-l border-white/10 bg-[#2e0a13]/95 flex flex-col z-20 shadow-xl overflow-hidden shrink-0"
    >
        <!-- Empty State -->
        <div v-if="!showInspector" class="flex flex-col items-center justify-center h-full text-white/30 p-6 text-center">
             <i class="fas fa-box-open text-4xl mb-4"></i>
             <p>Seleccione un producto para ver propiedades o presione "Nuevo"</p>
        </div>
        
        <!-- Inspector Component -->
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProductosStore } from '../../stores/productos'
// Sidebar import removed to avoid duplication
import ProductoCard from './components/ProductoCard.vue'
import ProductoInspector from './components/ProductoInspector.vue'

const router = useRouter()
const productosStore = useProductosStore()

const showInspector = ref(false)
const selectedId = ref(null)
let searchTimeout = null

// Flatten rubros for filter
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
    traverse(productosStore.rubros)
    return result
})

const handleSearch = () => {
    if (searchTimeout) clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
        productosStore.fetchProductos()
    }, 300)
}

const toggleShowInactive = () => {
    productosStore.filters.activo = !productosStore.filters.activo
    productosStore.fetchProductos()
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

const handleToggleActive = async (id) => {
    await productosStore.toggleEstado(id)
    // Refresh list if we are hiding inactives
    if (productosStore.filters.activo) { // If we only show actives
         // If the product became inactive, it will disappear from list, so close inspector
         const p = productosStore.productos.find(p => p.id === id)
         if (p && !p.activo) {
             closeInspector()
         }
    }
}

const handleLogout = () => {
    localStorage.removeItem('token')
    router.push('/login')
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
