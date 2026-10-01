// [IDENTIDAD] - frontend\src\components\informes\EnlacePedido.vue
// [S876] El número de pedido (o un icono) como enlace en un informe. Un clic abre, en esta misma pestaña, la ficha (la misma que abre
// el doble clic del Tablero de Pedidos) o, con destino="logistica", su pantalla de remitos y entregas. Al volver (la flecha de la
// ficha, o la del navegador) el informe queda como lo dejaste: filtros, orden y posición se recuerdan (usePersistirFiltros,
// useScrollRecordado). Ctrl / Mayús / clic del medio conservan el comportamiento normal del navegador (pestaña nueva).
// ------------------------------------------

<template>
  <a :href="href" :class="clase || CLASE_POR_DEFECTO" :title="title || TITULO[destino]" @click="alClic">
    <slot>#{{ pedidoId }}</slot>
  </a>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { hrefPedido } from '@/composables/useAbrirPedido'

const props = defineProps({
  pedidoId: { type: [Number, String], required: true },
  destino: { type: String, default: 'editar' }, // 'editar' | 'logistica'
  clase: { type: String, default: '' },
  title: { type: String, default: '' },
})

const CLASE_POR_DEFECTO = 'font-mono text-blue-300 hover:text-blue-100 underline decoration-dotted'
const TITULO = {
  editar: 'Abrir el pedido (Ctrl+clic: en una pestaña nueva)',
  logistica: 'Abrir la logística del pedido para facturar o devolver (Ctrl+clic: en una pestaña nueva)',
}

const router = useRouter()
const href = computed(() => hrefPedido(router, props.pedidoId, props.destino))

const alClic = (e) => {
  if (e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) return
  e.preventDefault()
  router.push(href.value)
}
</script>
