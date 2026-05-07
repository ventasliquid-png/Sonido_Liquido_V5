<template>
    <Teleport to="body">
        <div
            class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-[9998]"
            @keydown="handleOverlayKeydown"
            tabindex="-1"
            ref="overlayRef"
        >
            <div class="bg-[#0f172a]/95 border border-emerald-900/50 rounded-xl shadow-2xl w-full max-w-2xl mx-4 backdrop-blur-md">
                <!-- Header -->
                <div class="bg-gradient-to-r from-emerald-900/80 to-cyan-900/80 text-white px-6 py-4 rounded-t-xl flex justify-between items-center border-b border-emerald-700/40">
                    <h3 class="text-lg font-bold font-mono tracking-wide text-emerald-300">RESOLVER ÍTEMS DE FACTURA</h3>
                    <span class="text-sm font-mono text-emerald-400/70">
                        Ítem {{ currentItemIndex + 1 }} de {{ pending.length }}
                    </span>
                </div>

                <!-- Content -->
                <div class="p-6" v-if="current">
                    <!-- Referencia de factura (read-only) -->
                    <div class="bg-emerald-950/40 border border-emerald-800/30 rounded-lg p-4 mb-5">
                        <h4 class="font-bold text-emerald-400 mb-3 text-xs font-mono uppercase tracking-widest">Factura dice (referencia)</h4>
                        <div class="grid grid-cols-2 gap-3 text-sm">
                            <div class="col-span-2 flex items-center gap-2">
                                <div class="flex-1">
                                    <span class="text-emerald-600 text-xs">Descripción:</span>
                                    <p class="font-semibold text-white">{{ current.descripcion }}</p>
                                </div>
                                <button
                                    @click="searchTerm = current.descripcion"
                                    class="text-emerald-600 hover:text-emerald-400 transition shrink-0"
                                    title="Copiar al buscador"
                                >
                                    <i class="fas fa-copy text-xs"></i>
                                </button>
                            </div>
                            <div>
                                <span class="text-emerald-600 text-xs">Cantidad:</span>
                                <p class="font-semibold text-white">{{ current.cantidad }}</p>
                            </div>
                            <div>
                                <span class="text-emerald-600 text-xs">Precio Unitario:</span>
                                <p class="font-semibold text-white">${{ Number(current.precio || 0).toFixed(2) }}</p>
                            </div>
                            <div class="col-span-2">
                                <span class="text-emerald-600 text-xs">Subtotal:</span>
                                <p class="font-semibold text-cyan-300">${{ Number(current.total || 0).toFixed(2) }}</p>
                            </div>
                        </div>
                    </div>

                    <!-- Buscador de productos -->
                    <div class="mb-4">
                        <h4 class="font-bold text-emerald-400 mb-3 text-xs font-mono uppercase tracking-widest">Buscar en catálogo</h4>
                        <div class="relative">
                            <input
                                ref="searchInputRef"
                                v-model="searchTerm"
                                type="text"
                                placeholder="SKU o descripción..."
                                class="w-full px-4 py-2 bg-[#0b1120] border border-emerald-800/50 rounded-lg text-white placeholder-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono text-sm"
                                @keydown.esc.stop="handleCancel"
                            />
                        </div>

                        <div v-if="filteredProductos.length > 0" class="mt-2 border border-emerald-900/40 rounded-lg max-h-56 overflow-y-auto bg-[#0b1120]">
                            <div
                                v-for="prod in filteredProductos"
                                :key="prod.id"
                                @click="selectProduct(prod)"
                                class="px-4 py-3 border-b border-emerald-900/20 hover:bg-emerald-900/30 cursor-pointer transition"
                            >
                                <p class="font-mono text-xs text-emerald-400">{{ prod.sku }}</p>
                                <p class="text-sm text-white">{{ prod.nombre || prod.descripcion }}</p>
                            </div>
                        </div>

                        <div v-else-if="searchTerm.length > 0" class="mt-2 p-4 bg-yellow-900/20 border border-yellow-700/30 rounded-lg text-sm text-yellow-300">
                            <p class="mb-2">No se encontraron productos en el catálogo.</p>
                            <button
                                @click="openSatellite"
                                class="px-3 py-1 bg-yellow-600/60 text-white text-xs rounded hover:bg-yellow-600 transition"
                            >
                                F4 — Dar de alta producto nuevo
                            </button>
                        </div>

                        <div v-else class="mt-2 p-3 bg-cyan-950/30 border border-cyan-900/30 rounded-lg text-xs text-cyan-500 font-mono">
                            Empieza a tipear para buscar productos en catálogo
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="px-6 py-4 rounded-b-xl flex justify-end gap-3 border-t border-emerald-900/30">
                    <button
                        @click="handleCancel"
                        class="px-4 py-2 text-emerald-400 bg-transparent border border-emerald-800/50 rounded-lg hover:bg-emerald-900/30 transition text-sm font-mono"
                    >
                        ← Cancelar
                    </button>
                    <button
                        v-if="current?.producto_id"
                        @click="advance"
                        class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 transition text-sm font-mono"
                    >
                        Confirmar →
                    </button>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useProductosStore } from '../../../stores/productos';

const props = defineProps({ items: { type: Array, required: true } });
const emit = defineEmits(['resolved', 'cancel']);

const router = useRouter();
const productosStore = useProductosStore();

const overlayRef = ref(null);
const searchInputRef = ref(null);
const pending = ref([]);
const currentItemIndex = ref(0);
const searchTerm = ref('');

const current = computed(() =>
    pending.value.length === 0 ? null : pending.value[currentItemIndex.value]
);

const filteredProductos = computed(() => {
    const term = String(searchTerm.value || '').toLowerCase().trim();
    if (productosStore.productos.length === 0 || term.length < 1) return [];
    const normalize = (s) => s ? s.toString().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '') : '';
    const t = normalize(term);
    return productosStore.productos.filter(p =>
        normalize(p.sku).includes(t) || normalize(p.nombre || p.descripcion).includes(t)
    ).slice(0, 50);
});

watch(() => props.items, (newItems) => {
    if (!newItems || newItems.length === 0) return;
    pending.value = newItems.map((item, idx) => ({
        id: `line_${Math.random().toString(36).substr(2, 9)}`,
        originalIndex: idx,
        producto_id: null,
        sku: item.codigo || '',
        descripcion: item.descripcion || '',
        cantidad: Number(item.cantidad) || 1,
        precio: Number(item.precio_unitario) || 0,
        descuento_porcentaje: 0,
        descuento_valor: 0,
        total: (Number(item.cantidad) || 1) * (Number(item.precio_unitario) || 0),
        producto_obj: null
    }));
    currentItemIndex.value = 0;
    nextTick(() => {
        searchTerm.value = '';
        setTimeout(() => { overlayRef.value?.focus(); searchInputRef.value?.focus(); }, 80);
    });
}, { immediate: true });

const selectProduct = (prod) => {
    if (!current.value) return;
    current.value.producto_id = prod.id;
    current.value.producto_obj = prod;
    current.value.sku = prod.sku;
    current.value.descripcion = prod.nombre;
    advance();
};

const advance = () => {
    if (currentItemIndex.value < pending.value.length - 1) {
        currentItemIndex.value++;
        searchTerm.value = '';
        setTimeout(() => searchInputRef.value?.focus(), 50);
    } else {
        emit('resolved', [...pending.value]);
    }
};

const handleCancel = () => emit('cancel');

const openSatellite = () => {
    const w = 1700, h = 900;
    const features = `width=${w},height=${h},left=${(screen.width - w) / 2},top=${(screen.height - h) / 2},resizable=yes,scrollbars=yes,status=no,menubar=no,toolbar=no,location=no`;
    const { href } = router.resolve({ name: 'Productos', query: { action: 'new', search: searchTerm.value, mode: 'satellite' } });
    window.open(href, `AltaProducto_${Date.now()}`, features);
};

const handleOverlayKeydown = (e) => {
    if (e.key === 'F4') { e.preventDefault(); e.stopPropagation(); openSatellite(); }
    if (e.key === 'Escape') { e.stopPropagation(); handleCancel(); }
};
</script>
