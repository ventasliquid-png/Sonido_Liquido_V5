// [S876] Cambiar el estado de un pedido desde un informe, SIN abrir la ficha. Es exactamente lo que hace el menú de
// estados del Tablero de Pedidos (PedidoList.vue, handleStatusChange): PATCH /pedidos/{id} con { estado }, y si el
// servidor responde 409 CIERRE_CON_DISCREPANCIA (se cierra un pedido cuya entrega no coincide con lo pedido,
// doctrina del Bit 46, S863) se pide confirmación explícita y se reenvía con cierre_confirmado. Mismas reglas del
// servidor, mismo mensaje, mismo resultado: el informe no tiene una vía distinta de la ficha.
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'

// [S895, Carlos 29/10; caso Castro #145: vendido, cobrado y entregado sin factura ni remito] Lo que se hace ante el cartel de cierre con discrepancia, igual en la
// ficha, el Tablero y los informes: primero se ofrece registrar «Salió sin papel» por lo que falta remitir (un remito 0015 sin papel, en un paso); si no, el cierre con
// discrepancia de siempre (queda anotada); si no, nada. Devuelve 'sin-papel' (ya registrada: reenviar el estado SIN cierre_confirmado), 'cerrar' (reenviar con
// cierre_confirmado) o 'cancelar'.
export async function resolverCierreConDiscrepancia(pedidoId, mensaje) {
  const notification = useNotificationStore()
  if (confirm(`⚠️ ${mensaje}

¿La mercadería ya salió y falta el remito?
ACEPTAR = registrar «Salió sin papel» por lo que falta y cerrar.
CANCELAR = ver otras opciones.`)) {
    try {
      const { data } = await api.post(`/remitos/pedido/${pedidoId}/salida-sin-papel`, {})
      notification.add(`Salida registrada sin papel: remito ${data?.numero_legal || ''}`, 'success')
      return 'sin-papel'
    } catch (e) {
      notification.add('No se pudo registrar la salida: ' + (e.response?.data?.detail || e.message), 'error')
      return 'cancelar'
    }
  }
  return confirm('¿Cerrar igual, con la discrepancia? Queda anotada en el pedido.') ? 'cerrar' : 'cancelar'
}

export function usePedidoEstado() {
  const notification = useNotificationStore()

  // true si el estado quedó cambiado; false si el servidor lo rechazó o el usuario no confirmó el cierre.
  const cambiarEstado = async (pedidoId, nuevoEstado) => {
    try {
      await api.patch(`/pedidos/${pedidoId}`, { estado: nuevoEstado })
    } catch (e) {
      const detalle = String(e.response?.data?.detail || '')
      if (e.response?.status === 409 && detalle.startsWith('CIERRE_CON_DISCREPANCIA')) {
        const accion = await resolverCierreConDiscrepancia(pedidoId, detalle.replace('CIERRE_CON_DISCREPANCIA: ', ''))
        if (accion === 'cancelar') return false
        try {
          await api.patch(`/pedidos/${pedidoId}`, accion === 'cerrar' ? { estado: nuevoEstado, cierre_confirmado: true } : { estado: nuevoEstado })
          notification.add(`Pedido #${pedidoId} actualizado a ${nuevoEstado}` + (accion === 'cerrar' ? ' (con nota de discrepancia)' : ''), 'success')
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
