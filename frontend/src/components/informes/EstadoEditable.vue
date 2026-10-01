// [IDENTIDAD] - frontend\src\components\informes\EstadoEditable.vue
// [S876] El cartel de Estado de un pedido, editable desde el informe sin abrir la ficha (pedido de Carlos, 01/10:
// "todos los pedidos están cumplidos y quiero cambiarlos sin ir uno por uno abriendo la ficha"). El teclado y la lista son
// los de SelectorInline. El cambio es el mismo que el del Tablero de Pedidos (usePedidoEstado), con la misma confirmación
// de cierre con discrepancia. Los estados elegibles son los del Tablero (FACTURADO no se elige a mano).
// ------------------------------------------

<template>
  <SelectorInline
    :opciones="OPCIONES" :valor="estado" :texto="texto || estado" :clase-badge="estadoClase(estado)"
    :guardando="guardando" etiqueta="Estado del pedido"
    :titulo="`Cambiar el estado del pedido #${pedidoId}: clic, o flecha abajo; escribí la inicial para saltar`"
    @elegido="elegir" />
</template>

<script setup>
import { ref } from 'vue'
import SelectorInline from '@/components/informes/SelectorInline.vue'
import { estadoClase, estadoTexto, ESTADOS_PEDIDO_EDITABLES } from '@/utils/estadosPedido'
import { usePedidoEstado } from '@/composables/usePedidoEstado'

const props = defineProps({
  pedidoId: { type: [Number, String], required: true },
  estado: { type: String, default: '' },  // estado base del pedido (PENDIENTE, CUMPLIDO...)
  texto: { type: String, default: '' },   // lo que se muestra (puede traer " · PARCIAL")
})
const emit = defineEmits(['cambiado'])

const OPCIONES = ESTADOS_PEDIDO_EDITABLES.map((e) => ({ value: e, label: e, clase: estadoTexto(e) }))
const { cambiarEstado } = usePedidoEstado()
const guardando = ref(false)

const elegir = async (nuevo) => {
  guardando.value = true
  try {
    if (await cambiarEstado(props.pedidoId, nuevo)) emit('cambiado', nuevo)
  } finally {
    guardando.value = false
  }
}
</script>
