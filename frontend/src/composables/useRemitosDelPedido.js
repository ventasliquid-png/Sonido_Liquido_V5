// [S887, pedido de Carlos 15/10] El pedido es el punto de partida del operador: ahí tiene que verse si ya tiene remito, cuál es, y poder reimprimirlo sin hacer otro.
// Lo comparten la ficha del pedido (PedidoCanvas), el Tablero de Pedidos (PedidoList) y el Remito Manual.
import api from '@/services/api'

export const CLASE_ESTADO_REMITO = {
  BORRADOR: 'bg-slate-500/20 text-slate-300 border-slate-500/40',
  EN_CAMINO: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
  ENTREGADO: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
  ANULADO: 'bg-red-500/20 text-red-300 border-red-500/40',
}
export const claseEstadoRemito = (estado) => CLASE_ESTADO_REMITO[estado] || 'bg-gray-500/10 text-gray-400 border-gray-500/20'

// Los remitos anulados no cuentan: son como si no existieran.
export const remitosVigentes = (remitos) => (remitos || []).filter((r) => r.estado !== 'ANULADO')

// Los remitos vigentes de un pedido (los más viejos primero). Si falla la consulta devuelve [] y la pantalla sigue como siempre.
export async function traerRemitosDelPedido(pedidoId) {
  try {
    const res = await api.get(`/remitos/por_pedido/${pedidoId}`)
    return remitosVigentes(res.data).sort((a, b) => String(a.fecha_creacion || '').localeCompare(String(b.fecha_creacion || '')))
  } catch (e) {
    return []
  }
}

// Reimprimir = abrir el PDF del mismo remito (mismo número, no se crea nada). Si el remito todavía no tiene número, el PDF se lo asigna (el próximo 0015):
// en ese caso se pide confirmación antes de gastar un número. `alNumerar` se llama (si se imprimió uno sin número) para que la pantalla se refresque.
export function imprimirRemitoExistente(remito, alNumerar) {
  if (!remito || !remito.id || remito.estado === 'ANULADO') return
  const sinNumero = !remito.numero_legal
  if (sinNumero && !confirm('Este remito todavía no tiene número. Al imprimirlo se le asigna el próximo número del talonario 0015. ¿Imprimir?')) return
  window.open(`/remitos/${remito.id}/pdf`, '_blank')
  if (sinNumero && alNumerar) setTimeout(alNumerar, 1500)
}
