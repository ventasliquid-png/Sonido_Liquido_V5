// [S876] Aviso entre pestañas: "se guardó un cambio en el pedido N". El pedido se abre desde un informe en una pestaña
// nueva; al guardar, esa pestaña avisa y el informe (en su pestaña, con sus filtros y su scroll intactos) se actualiza
// solo, sin que haya que apretar Actualizar. BroadcastChannel entrega el mensaje a las OTRAS pestañas del mismo origen.
const NOMBRE = 'v5-pedido-actualizado'

export const avisarPedidoActualizado = (pedidoId) => {
  try {
    const canal = new BroadcastChannel(NOMBRE)
    canal.postMessage({ pedidoId })
    canal.close()
  } catch {
    // Sin BroadcastChannel (navegador viejo): el informe se actualiza con su botón.
  }
}

// Devuelve la función que deja de escuchar.
export const escucharPedidoActualizado = (alRecibir) => {
  try {
    const canal = new BroadcastChannel(NOMBRE)
    canal.onmessage = (evento) => alRecibir(evento.data)
    return () => canal.close()
  } catch {
    return () => {}
  }
}
