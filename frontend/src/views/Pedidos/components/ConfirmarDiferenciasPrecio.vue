<!--
    ConfirmarDiferenciasPrecio.vue — [S894, Card #144] Carlos 28/10: «No quiero que solo avise: quiero que provoque una
    confirmación del operador si hay discrepancia. Que sea consciente la cosa».

    Cuando el precio de la factura no coincide con el del pedido (precio efectivo: la bonificación de la factura, el
    descuento del renglón y el general del pedido; tolerancia $1 o 0,5 %), el servidor responde 409 DIFERENCIA_DE_PRECIO
    con la lista y no registra nada. Este modal la muestra renglón por renglón; la factura entra solo si el operador
    aprieta «Confirmo las diferencias» (motivo opcional). El pedido no se cambia: si el error es del pedido, se corrige
    aparte. Lo usan la Ingesta y «Conciliar contra PR».
-->
<template>
    <Teleport to="body">
        <div class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-[9999] p-4" @keydown.esc="$emit('cancelar')">
            <div class="bg-[#0f172a]/95 border-2 border-amber-500/50 rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col">
                <div class="bg-gradient-to-r from-amber-900/40 to-orange-900/40 px-6 py-4 rounded-t-xl border-b border-amber-500/30 shrink-0">
                    <h3 class="text-lg font-bold text-amber-300">
                        <i class="fas fa-balance-scale mr-2"></i>El precio de la factura no coincide con el pedido
                    </h3>
                    <p class="text-xs text-amber-100/70 mt-1">{{ mensaje }}</p>
                </div>

                <div class="p-5 overflow-y-auto space-y-2">
                    <div v-for="(d, i) in diferencias" :key="i" class="bg-slate-900/70 border border-slate-700 rounded-lg px-4 py-3">
                        <p class="text-sm font-semibold text-white">{{ d.producto }}</p>
                        <div class="flex gap-6 mt-1 text-xs font-mono">
                            <span class="text-slate-400">Pedido: <span class="text-slate-200">{{ pesos(d.precio_pedido) }}</span>
                                <span v-if="d.descuento_pedido" class="text-slate-500"> (−{{ d.descuento_pedido }} %)</span></span>
                            <span class="text-slate-400">Factura: <span class="text-amber-300">{{ pesos(d.precio_factura) }}</span>
                                <span v-if="d.bonificacion_factura" class="text-slate-500"> (bonif. {{ d.bonificacion_factura }} %)</span></span>
                        </div>
                        <p class="text-[11px] text-slate-500 mt-1">{{ d.detalle }}</p>
                    </div>

                    <label class="block pt-2">
                        <span class="text-xs text-slate-400">Motivo (opcional)</span>
                        <input v-model="motivo" type="text" maxlength="300" placeholder="Por ejemplo: el cliente tiene 5 % de bonificación y el pedido se cargó sin el descuento"
                               class="mt-1 w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-sm text-white focus:border-amber-400 outline-none" />
                    </label>
                    <p class="text-[11px] text-slate-500">
                        Al confirmar, la factura se registra como la emitió ARCA y queda una nota en la factura y en el pedido con estas diferencias y tu usuario.
                        El pedido no se cambia.
                    </p>
                </div>

                <div class="px-5 py-4 border-t border-slate-700 flex justify-end gap-3 shrink-0">
                    <button @click="$emit('cancelar')" class="px-4 py-2 rounded-lg text-sm text-slate-300 hover:text-white hover:bg-slate-800 transition">
                        Volver sin registrar
                    </button>
                    <button @click="$emit('confirmar', motivo.trim() || null)" :disabled="enviando"
                            class="px-4 py-2 rounded-lg text-sm font-bold bg-amber-600 hover:bg-amber-500 text-white disabled:opacity-50 transition">
                        <i class="fas fa-check mr-2"></i>Confirmo las diferencias
                    </button>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
    diferencias: { type: Array, required: true },
    mensaje: { type: String, default: '' },
    enviando: { type: Boolean, default: false },
});
defineEmits(['confirmar', 'cancelar']);

const motivo = ref('');
const pesos = (x) => (x == null ? '—' : '$ ' + Number(x).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
</script>
