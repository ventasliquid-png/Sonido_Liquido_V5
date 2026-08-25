// Derivación compartida del estado de entrega de un renglón de Pedido.
// Usado por ManualRemitoView.vue, PedidoList.vue y PedidoCanvas.vue — una sola
// fuente de verdad para que las tres pantallas no terminen discrepando.
// Ver INFORMES_HISTORICOS/2026-08-14_S854_OF.md (diagnóstico) y Card #99.

export function saldoRenglon(item) {
  return item.cantidad - (item.cantidad_entregada || 0);
}

// Tres estados, no dos — un booleano "tiene entregas/no tiene" hace
// desaparecer los parciales del circuito.
export const ESTADO_SIN_ENTREGAS = 'SIN_ENTREGAS';
export const ESTADO_PARCIAL = 'PARCIAL';
export const ESTADO_CUMPLIDO = 'CUMPLIDO';

export function estadoRenglon(item) {
  const entregada = item.cantidad_entregada || 0;
  if (entregada <= 0) return ESTADO_SIN_ENTREGAS;
  if (entregada < item.cantidad) return ESTADO_PARCIAL;
  return ESTADO_CUMPLIDO;
}

// Precio por unidad para valuar entregado/pendiente. Primario: precio_unitario
// (campo real de PedidoItemResponse, siempre presente, sin riesgo de división).
// Fallback: prorrateo de subtotal/cantidad, solo si precio_unitario no es
// utilizable, con guarda de cantidad > 0.
//
// DECISIÓN CONSCIENTE sobre descuentos: subtotal ya viene neto del
// descuento_importe del renglón (backend/pedidos/router.py:194,
// `subtotal = precio_unitario*cantidad - descuento_importe`), así que el
// camino de fallback valúa lo entregado/pendiente CON el descuento de renglón
// prorrateado — probablemente lo correcto para saber qué corresponde
// facturar — mientras que el camino primario (precio_unitario) no lo
// descuenta. No es un efecto lateral: se prioriza precio_unitario por ser el
// campo real y estable, y el fallback (con descuento incluido) solo entra
// cuando no hay precio_unitario confiable.
function precioEfectivo(item) {
  if (item.precio_unitario > 0) return item.precio_unitario;
  if (item.cantidad > 0) return item.subtotal / item.cantidad;
  return 0;
}

export function resumenEntregaPedido(items) {
  return items.reduce((acc, item) => {
    const entregada = item.cantidad_entregada || 0;
    const pendiente = saldoRenglon(item);
    const precio = precioEfectivo(item);
    acc.unidadesTotal += item.cantidad;
    acc.unidadesEntregadas += entregada;
    acc.unidadesPendientes += pendiente;
    acc.montoTotal += item.subtotal;
    acc.montoEntregado += entregada * precio;
    acc.montoPendiente += pendiente * precio;
    return acc;
  }, {
    unidadesTotal: 0, unidadesEntregadas: 0, unidadesPendientes: 0,
    montoTotal: 0, montoEntregado: 0, montoPendiente: 0,
  });
}
