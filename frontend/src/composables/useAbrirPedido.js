// [S876] Abrir un pedido desde un informe: el mismo destino que el doble clic del Tablero de Pedidos (PedidoEditar), en esta misma
// pestaña. Solo en pantalla.
//
// El pedido se abre con ?from=informe: así, al terminar, la flecha de volver de la ficha regresa al informe (PedidoCanvas.goBack), que
// reaparece como lo dejaste: sus filtros, su orden y su posición se recuerdan mientras dure la pestaña (usePersistirFiltros y
// useScrollRecordado).
import { useRouter } from 'vue-router'

// Dirección del pedido: 'editar' (la ficha, la que abre el doble clic del Tablero) o 'logistica' (remitos y entregas).
export const hrefPedido = (router, pedidoId, destino = 'editar') =>
  router.resolve(
    destino === 'logistica'
      ? { name: 'PedidoLogistica', params: { id: pedidoId } }
      : { name: 'PedidoEditar', params: { id: pedidoId }, query: { from: 'informe' } },
  ).href

export function useAbrirPedido() {
  const router = useRouter()
  // `evento` es el del doble clic: si cayó sobre un enlace, botón o selector de la fila, esa pieza tiene su propia
  // acción y la fila no hace nada (si no, un doble clic sobre el enlace del pedido abriría pestañas de más).
  return (pedidoId, evento) => {
    if (pedidoId === null || pedidoId === undefined) return
    if (evento?.target?.closest?.('a, button, select, input, textarea, [data-sin-abrir]')) return
    window.getSelection?.()?.removeAllRanges?.() // el doble clic selecciona una palabra: no dejarla marcada
    router.push(hrefPedido(router, pedidoId))
  }
}
