<!--
    AsistenteEntregaParcial.vue — [T5, S868] ESTUDIO_DISCOVERY_BAS_S866.md §4-bis, aporte de Carlos.

    "Deberíamos ayudar al operador... toma los datos del pedido... copiar ese pedido al remito
    sería lo lógico pero no necesariamente igual (puede un cliente pedir que le factures 120
    cofias y que le entregues 40 por semana)."

    Al confirmar una ingesta con pedido vinculado, muestra ANTES de generar el remito, renglón
    por renglón del PEDIDO (no del texto de la factura): pedido / ya remitido / pendiente /
    factura dice / a remitir ahora (editable, tope = pendiente). El operador ve el panorama y
    decide, en vez de recibir un bloqueo de texto después de intentar (mismo control que hubiera
    evitado el caso de la factura 2600 de Lácteos, AUDITORIA_LACTEOS_S866.md §4).

    La factura y el remito quedan separados a propósito: "cantidad" (lo que dice la factura) no
    se toca acá, solo se decide "cantidad_remitir" (lo que sale hoy). El backend usa la primera
    para el FacturaItem espejo (dato fiscal) y la segunda para el RemitoItem (dato logístico).
-->
<template>
    <Teleport to="body">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[9998] p-4">
            <div class="bg-[#0f172a]/95 border border-blue-900/50 rounded-xl shadow-2xl w-full max-w-3xl max-h-[85vh] flex flex-col">
                <!-- Header -->
                <div class="bg-gradient-to-r from-blue-900/80 to-cyan-900/80 text-white px-6 py-4 rounded-t-xl border-b border-blue-700/40 shrink-0">
                    <h3 class="text-lg font-bold font-mono tracking-wide text-blue-300">
                        <i class="fas fa-truck-loading mr-2"></i>¿QUÉ SE REMITE HOY?
                    </h3>
                    <p class="text-xs text-blue-200/70 mt-1">
                        Pedido #{{ pedido?.id }} — {{ pedido?.cliente?.razon_social || 'Cliente' }}.
                        La factura queda registrada igual; acá se decide solo lo que sale en este viaje.
                    </p>
                </div>

                <!-- Content -->
                <div class="p-5 overflow-y-auto flex-1">
                    <div v-if="filas.length === 0" class="text-center text-slate-400 text-sm py-8">
                        Ningún renglón de la factura corresponde a un producto pendiente de este pedido.
                    </div>
                    <table v-else class="w-full text-sm">
                        <thead>
                            <tr class="text-[10px] uppercase tracking-widest text-blue-400/70 border-b border-blue-900/40">
                                <th class="text-left pb-2">Producto</th>
                                <th class="text-right pb-2">Pedido</th>
                                <th class="text-right pb-2">Remitido</th>
                                <th class="text-right pb-2">Pendiente</th>
                                <th class="text-right pb-2">Factura dice</th>
                                <th class="text-right pb-2 pl-3">A remitir ahora</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="f in filas" :key="f.pedido_item_id"
                                class="border-b border-white/5"
                                :class="{ 'bg-amber-500/10': f.excede }">
                                <td class="py-2 pr-2 text-slate-200">{{ f.descripcion }}</td>
                                <td class="py-2 text-right font-mono text-slate-400">{{ f.cantidad_pedido }}</td>
                                <td class="py-2 text-right font-mono text-slate-400">{{ f.cantidad_entregada }}</td>
                                <td class="py-2 text-right font-mono text-emerald-400 font-bold">{{ f.pendiente }}</td>
                                <td class="py-2 text-right font-mono" :class="f.excede ? 'text-amber-400 font-bold' : 'text-slate-400'">
                                    {{ f.factura_dice || '—' }}
                                    <i v-if="f.excede" class="fas fa-triangle-exclamation ml-1" title="La factura dice más de lo pendiente en este pedido"></i>
                                </td>
                                <td class="py-2 pl-3 text-right">
                                    <input type="number" min="0" step="any" :max="f.pendiente"
                                        v-model.number="f.a_remitir"
                                        @input="clampFila(f)"
                                        class="w-20 bg-slate-900 border rounded px-2 py-1 text-right font-mono text-white focus:outline-none"
                                        :class="f.a_remitir > f.pendiente ? 'border-red-500' : 'border-slate-700 focus:border-emerald-500'"
                                    >
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    <p v-if="hayExcedidas" class="text-xs text-amber-400 mt-3">
                        <i class="fas fa-triangle-exclamation mr-1"></i>
                        Algún renglón factura más de lo pendiente en el pedido — la cantidad a remitir quedó
                        topeada a lo pendiente. Si corresponde entregar más, corregí antes el pedido.
                    </p>
                </div>

                <!-- Footer -->
                <div class="px-5 py-3 border-t border-blue-900/40 flex justify-between items-center shrink-0">
                    <span class="text-xs text-slate-500 font-mono">
                        {{ totalARemitir }} unidad(es) a remitir en {{ filasConEnvio.length }} renglón(es)
                    </span>
                    <div class="flex gap-3">
                        <button @click="$emit('cancel')" class="text-slate-400 hover:text-white px-4 py-2 text-sm">
                            Cancelar
                        </button>
                        <button @click="confirmar" :disabled="filasConEnvio.length === 0"
                            class="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-bold text-sm flex items-center gap-2">
                            <i class="fas fa-check"></i> Confirmar y generar remito
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
    pedido: { type: Object, required: true },
    // itemsFactura: [{ producto_id, cantidad, descripcion }] -- ya resueltos contra el catálogo
    itemsFactura: { type: Array, default: () => [] },
});
const emit = defineEmits(['confirmado', 'cancel']);

const filas = ref([]);

const construirFilas = () => {
    const porProducto = new Map();
    for (const it of props.itemsFactura || []) {
        const pid = String(it.producto_id);
        porProducto.set(pid, (porProducto.get(pid) || 0) + (parseFloat(it.cantidad) || 0));
    }
    filas.value = (props.pedido?.items || [])
        .map(pi => {
            const pid = String(pi.producto_id);
            const facturaDice = porProducto.get(pid) || 0;
            const pendiente = Math.max(0, (pi.cantidad || 0) - (pi.cantidad_entregada || 0));
            const excede = facturaDice > pendiente + 0.001;
            return {
                pedido_item_id: pi.id,
                producto_id: pi.producto_id,
                descripcion: pi.producto?.nombre || pi.nota || 'Ítem',
                cantidad_pedido: pi.cantidad,
                cantidad_entregada: pi.cantidad_entregada || 0,
                pendiente,
                factura_dice: facturaDice,
                excede,
                // Default: lo que dice la factura, topeado al pendiente. Si la factura no
                // menciona este renglón (facturaDice === 0), arranca en 0 -- no se agrega
                // sin que el operador lo decida a mano.
                a_remitir: Math.min(facturaDice, pendiente),
            };
        })
        // Solo renglones con algo pendiente o mencionados por la factura -- ocultar lo ya
        // 100% entregado y ajeno a esta factura, para no alargar la tabla sin motivo.
        .filter(f => f.pendiente > 0 || f.factura_dice > 0);
};

watch(() => [props.pedido, props.itemsFactura], construirFilas, { immediate: true });

const clampFila = (f) => {
    if (f.a_remitir < 0 || Number.isNaN(f.a_remitir)) f.a_remitir = 0;
    if (f.a_remitir > f.pendiente) f.a_remitir = f.pendiente;
};

const hayExcedidas = computed(() => filas.value.some(f => f.excede));
const filasConEnvio = computed(() => filas.value.filter(f => (f.a_remitir || 0) > 0));
const totalARemitir = computed(() => filasConEnvio.value.reduce((s, f) => s + f.a_remitir, 0));

const confirmar = () => {
    emit('confirmado', filasConEnvio.value.map(f => ({
        producto_id: f.producto_id,
        cantidad_remitir: f.a_remitir,
    })));
};
</script>
