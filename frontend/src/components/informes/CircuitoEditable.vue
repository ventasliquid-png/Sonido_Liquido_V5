// [IDENTIDAD] - frontend\src\components\informes\CircuitoEditable.vue
// [S876] El cartel de Circuito (Blanco / Rosa) de un pedido, editable desde el informe (pedido de Carlos, 01/10: el
// operador tiene que poder pasar un pedido de un circuito al otro y que el sistema recalcule todo). Usa EXACTAMENTE la rutina
// del Tablero de Pedidos (PATCH /pedidos/{id}/circuito-bipolar): el servidor cambia el bit NO_FISCAL_FORCE y recalcula el total
// con las reglas del circuito nuevo, y un cliente Rosa no puede pasar a Blanco (el servidor lo fuerza a Rosa y avisa).
// A diferencia del Estado, acá se pide confirmación antes de cambiar: el cambio mueve el total del pedido.
// Después del cambio avisa a los informes abiertos (utils/canalPedidos) para que se recarguen: el total y los carteles de
// todas las filas de ese pedido cambian, y en "Pedidos sin remito" la fila pasa a la otra sección.
// ------------------------------------------

<template>
  <SelectorInline
    :opciones="OPCIONES" :valor="circuito" :texto="circuito" :clase-badge="claseCircuito(circuito)"
    :guardando="guardando" etiqueta="Circuito del pedido"
    :titulo="`Cambiar el circuito del pedido #${pedidoId}: clic, o flecha abajo; escribí B o R`"
    @elegido="elegir" />
</template>

<script setup>
import { ref } from 'vue'
import SelectorInline from '@/components/informes/SelectorInline.vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'
import { claseCircuito } from '@/utils/estadosPedido'
import { avisarPedidoActualizado } from '@/utils/canalPedidos'

const props = defineProps({
  pedidoId: { type: [Number, String], required: true },
  circuito: { type: String, default: 'Blanco' }, // 'Blanco' | 'Rosa'
})
const emit = defineEmits(['cambiado'])

const OPCIONES = [
  { value: 'Blanco', label: 'Blanco', clase: 'text-slate-300' },
  { value: 'Rosa', label: 'Rosa', clase: 'text-pink-300' },
]
const notification = useNotificationStore()
const guardando = ref(false)

const elegir = async (nuevo) => {
  const aRosa = nuevo === 'Rosa'
  if (!confirm(`Pasar el pedido #${props.pedidoId} al circuito ${nuevo.toUpperCase()} (${aRosa ? 'interno' : 'oficial'}).\n\n` +
               `Se recalcula el total del pedido con las reglas del nuevo circuito. ¿Confirmás el cambio?`)) return
  guardando.value = true
  try {
    const res = await api.patch(`/pedidos/${props.pedidoId}/circuito-bipolar`, { is_interno: aRosa })
    // Un cliente Rosa no puede pasar a Blanco: el servidor lo deja en Rosa y avisa por qué (cabecera X-Aviso-Circuito).
    const aviso = res.headers?.['x-aviso-circuito']
    if (aviso) notification.add(decodeURIComponent(aviso), 'warning')
    else notification.add(`Pedido #${props.pedidoId} movido a circuito ${nuevo}`, 'success')
    avisarPedidoActualizado(props.pedidoId)
    emit('cambiado', nuevo)
  } catch (e) {
    notification.add('Error al cambiar circuito: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    guardando.value = false
  }
}
</script>
