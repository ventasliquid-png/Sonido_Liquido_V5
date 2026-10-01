// [S876] Cambiar el estado de un pedido desde un informe, SIN abrir la ficha. Es exactamente lo que hace el menú de
// estados del Tablero de Pedidos (PedidoList.vue, handleStatusChange): PATCH /pedidos/{id} con { estado }, y si el
// servidor responde 409 CIERRE_CON_DISCREPANCIA (se cierra un pedido cuya entrega no coincide con lo pedido,
// doctrina del Bit 46, S863) se pide confirmación explícita y se reenvía con cierre_confirmado. Mismas reglas del
// servidor, mismo mensaje, mismo resultado: el informe no tiene una vía distinta de la ficha.
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'

export function usePedidoEstado() {
  const notification = useNotificationStore()

  // true si el estado quedó cambiado; false si el servidor lo rechazó o el usuario no confirmó el cierre.
  const cambiarEstado = async (pedidoId, nuevoEstado) => {
    try {
      await api.patch(`/pedidos/${pedidoId}`, { estado: nuevoEstado })
    } catch (e) {
      const detalle = String(e.response?.data?.detail || '')
      if (e.response?.status === 409 && detalle.startsWith('CIERRE_CON_DISCREPANCIA')) {
        if (!confirm(`⚠️ ${detalle.replace('CIERRE_CON_DISCREPANCIA: ', '')}`)) return false
        try {
          await api.patch(`/pedidos/${pedidoId}`, { estado: nuevoEstado, cierre_confirmado: true })
          notification.add(`Pedido #${pedidoId} actualizado a ${nuevoEstado} (con nota de discrepancia)`, 'success')
          return true
        } catch (e2) {
          notification.add('Error actualizando estado: ' + (e2.response?.data?.detail || e2.message), 'error')
          return false
        }
      }
      notification.add('Error actualizando estado: ' + (detalle || e.message), 'error')
      return false
    }
    notification.add(`Pedido #${pedidoId} actualizado a ${nuevoEstado}`, 'success')
    return true
  }

  return { cambiarEstado }
}
