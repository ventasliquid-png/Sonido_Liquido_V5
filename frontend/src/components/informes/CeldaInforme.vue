// [IDENTIDAD] - frontend\src\components\informes\CeldaInforme.vue
// [S875] Celda de los listados del módulo Informes: el Estado y el Circuito del pedido salen como
// cartel de color (misma paleta que la lista de pedidos, ver utils/estadosPedido.js); el resto es texto.
// ------------------------------------------

<template>
  <span v-if="columna === 'estado' && valor"
    class="inline-block px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider"
    :class="estadoClase(fila.estado_base)">{{ valor }}</span>
  <span v-else-if="columna === 'circuito' && valor"
    class="inline-block px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider"
    :class="claseCircuito(valor)">{{ valor }}</span>
  <template v-else>{{ valor ?? '-' }}</template>
</template>

<script setup>
import { estadoClase, claseCircuito } from '@/utils/estadosPedido'

defineProps({
  columna: { type: String, required: true },
  fila: { type: Object, required: true },
  valor: { type: [String, Number, Boolean], default: null },
})
</script>
