// [IDENTIDAD] - frontend\src\components\informes\CeldaInforme.vue
// [S875] Celda de los listados del módulo Informes: el Estado y el Circuito del pedido salen como
// cartel de color (misma paleta que la lista de pedidos, ver utils/estadosPedido.js); el resto es texto.
// ------------------------------------------

<template>
  <!-- [S876] Con pedido, el Estado se cambia desde acá sin abrir la ficha (EstadoEditable); sin pedido, cartel fijo. -->
  <EstadoEditable v-if="columna === 'estado' && valor && fila.pedido_id != null"
    :pedido-id="fila.pedido_id" :estado="fila.estado_base" :texto="valor"
    @cambiado="(nuevo) => emit('estado-cambiado', { pedidoId: fila.pedido_id, estado: nuevo })" />
  <span v-else-if="columna === 'estado' && valor"
    class="inline-block px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider"
    :class="estadoClase(fila.estado_base)">{{ valor }}</span>
  <!-- [S876] Igual con el Circuito (Blanco / Rosa): se cambia desde el informe con la rutina del Tablero (CircuitoEditable). -->
  <CircuitoEditable v-else-if="columna === 'circuito' && valor && fila.pedido_id != null"
    :pedido-id="fila.pedido_id" :circuito="valor" />
  <span v-else-if="columna === 'circuito' && valor"
    class="inline-block px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider"
    :class="claseCircuito(valor)">{{ valor }}</span>
  <!-- [S876] El número de pedido lleva al pedido (el mismo destino que el doble clic del Tablero), en una pestaña
       nueva para no perder los filtros del informe. Solo en pantalla: los archivos exportados no llevan enlaces. -->
  <EnlacePedido v-else-if="columna === 'pedido_id' && valor != null" :pedido-id="valor" />
  <template v-else>{{ valor ?? '-' }}</template>
</template>

<script setup>
import { estadoClase, claseCircuito } from '@/utils/estadosPedido'
import EstadoEditable from '@/components/informes/EstadoEditable.vue'
import EnlacePedido from '@/components/informes/EnlacePedido.vue'
import CircuitoEditable from '@/components/informes/CircuitoEditable.vue'

const emit = defineEmits(['estado-cambiado'])

defineProps({
  columna: { type: String, required: true },
  fila: { type: Object, required: true },
  valor: { type: [String, Number, Boolean], default: null },
})
</script>
