// [S875] Paleta de estados de pedido: UNA sola fuente para la lista de pedidos (PedidoList.vue) y
// para los informes. Antes vivía duplicada dentro de PedidoList; al sumar los colores a los
// informes se movió acá para que un estado nunca tenga un color en una pantalla y otro en otra.
//
// FACTURADO (21 pedidos en producción al 29/09) no tenía color en la lista: salía gris por el
// `default`. Se le asignó NARANJA (Carlos, 30/09): el celeste chocaba con el cian de INTERNO, y el
// ámbar queda reservado para el cartel PARCIAL.

// Los estados que se pueden ELEGIR a mano: los del menú de estados del Tablero de Pedidos y del selector de los
// informes. FACTURADO existe como estado pero no se elige a mano. Una sola lista para las dos pantallas.
export const ESTADOS_PEDIDO_EDITABLES = ['PENDIENTE', 'CUMPLIDO', 'ANULADO', 'PRESUPUESTO', 'INTERNO']

// Tras cambiar el estado de un pedido desde un informe, se actualizan en el lugar TODAS las filas de ese pedido
// (un pedido sale en varias filas: una por renglón, o una caja por remito), sin recargar el informe ni perder el
// lugar del scroll. El texto lleva " · PARCIAL" si el pedido tiene entregas parciales, como lo arma el servidor.
export const aplicarEstadoAFilas = (filas, pedidoId, nuevoEstado) => {
  for (const f of filas) {
    if (String(f.pedido_id) !== String(pedidoId)) continue
    f.estado_base = nuevoEstado
    f.estado = f.parcial ? `${nuevoEstado} · PARCIAL` : nuevoEstado
  }
}

// Cartel del estado (fondo + texto + borde).
export const estadoClase = (estado) => {
  switch (estado) {
    case 'PENDIENTE': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50'
    case 'BORRADOR': return 'bg-purple-600/20 text-purple-400/50 border-purple-500/20'
    case 'CUMPLIDO': return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/50'
    case 'FACTURADO': return 'bg-orange-500/20 text-orange-400 border-orange-500/50'
    case 'ANULADO': return 'bg-red-500/20 text-red-500 border-red-500/50'
    case 'PRESUPUESTO': return 'bg-purple-600/40 text-purple-300 border-purple-500/50'
    case 'INTERNO': return 'bg-cyan-600/40 text-cyan-300 border-cyan-500/50'
    default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
  }
}

// Solo el color del texto (menú desplegable de estados).
export const estadoTexto = (estado) => {
  switch (estado) {
    case 'PENDIENTE': return 'text-emerald-400'
    case 'BORRADOR': return 'text-purple-400/50'
    case 'CUMPLIDO': return 'text-yellow-500'
    case 'FACTURADO': return 'text-orange-400'
    case 'ANULADO': return 'text-red-500'
    case 'PRESUPUESTO': return 'text-purple-300'
    case 'INTERNO': return 'text-cyan-300'
    default: return 'text-gray-400'
  }
}

// Circuito Rosa (bit NO_FISCAL_FORCE del pedido) = fila teñida de rosa, igual que en la lista de pedidos.
export const claseFilaCircuito = (circuito) =>
  circuito === 'Rosa' ? 'bg-pink-950/30 border-l-2 border-pink-500/40' : 'border-l-2 border-transparent'

// Cartel del circuito.
export const claseCircuito = (circuito) =>
  circuito === 'Rosa'
    ? 'bg-pink-500/15 text-pink-300 border-pink-500/40'
    : 'bg-slate-500/10 text-slate-300 border-slate-500/30'
