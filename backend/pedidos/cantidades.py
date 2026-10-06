"""
Cantidades de un renglon de pedido contra lo remitido y lo facturado (Card #154, S879; dictamen Nike 05/10).

El pedido manda la entrega, pero un renglon tiene tres numeros que tienen que poder compararse:
pedido (PedidoItem.cantidad), remitido (suma de RemitoItem.cantidad_remitida) y facturado (suma de
FacturaItem.cantidad que apuntan al renglon por `pedido_item_id`). Esto calcula el tercero.

Que cuenta como FACTURADO (decisiones de esta Card):
  - Solo comprobantes con `estado == 'AUTORIZADA_AFIP'` (sellados o conciliados contra el PDF). Un BORRADOR
    no es una factura: ademas se vuelve a clonar desde el pedido en cada guardado (espejo), asi que contarlo
    haria que el renglon siempre apareciera "facturado por lo que dice el pedido". ANULADA tampoco cuenta.
  - Las NOTAS DE CREDITO restan (`cantidad_acreditada`); las NOTAS DE DEBITO no cuentan: ajustan importes,
    no cantidades (mismo criterio que RemitoItem.cantidad_acreditada).
  - La suma se hace por consulta SQL en cada llamada (no por la relacion del ORM): una relacion cacheada
    queda desactualizada dentro de la misma sesion (Card #136).
"""
from typing import Dict, Iterable, Optional, Tuple

from sqlalchemy import case, func

EPS = 0.001
ESTADO_FACTURA_VIGENTE = "AUTORIZADA_AFIP"


def facturado_por_renglon(db, pedido_item_ids: Iterable[int]) -> Dict[int, Tuple[float, float]]:
    """{pedido_item_id: (facturada_bruta, acreditada)} de los renglones pedidos, en UNA consulta.
    Los renglones sin ninguna factura vigente no aparecen en el resultado (equivalen a (0.0, 0.0))."""
    from backend.facturacion.models import Factura, FacturaItem

    ids = [i for i in set(pedido_item_ids) if i is not None]
    if not ids:
        return {}
    es_nc = func.substr(Factura.tipo_comprobante, 1, 12) == "NOTA_CREDITO"
    es_nd = func.substr(Factura.tipo_comprobante, 1, 11) == "NOTA_DEBITO"
    cant = func.coalesce(FacturaItem.cantidad, 0.0)
    filas = (
        db.query(
            FacturaItem.pedido_item_id,
            func.sum(case((es_nc | es_nd, 0.0), else_=cant)),
            func.sum(case((es_nc, cant), else_=0.0)),
        )
        .join(Factura, Factura.id == FacturaItem.factura_id)
        .filter(FacturaItem.pedido_item_id.in_(ids), Factura.estado == ESTADO_FACTURA_VIGENTE)
        .group_by(FacturaItem.pedido_item_id)
        .all()
    )
    return {pid: (float(bruta or 0.0), float(acred or 0.0)) for pid, bruta, acred in filas}


def _g(n: float) -> str:
    """5.0 -> '5', 2.5 -> '2.5' (para mensajes de error legibles)."""
    return f"{n:g}"


def mensaje_baja_de_cantidad(item, nueva_cantidad: float) -> Optional[str]:
    """Guarda de edicion (dictamen Nike 05/10, punto 6): la cantidad de un renglon nunca puede quedar por
    debajo de lo remitido ni de lo facturado (neto de NC). None = se puede. Para bajarla por debajo de lo
    facturado hace falta una NC (o anular la factura): el pedido no desmiente un comprobante emitido.

    Solo juzga una BAJA: si la cantidad queda igual o sube, no se mete (en P hay renglones viejos con
    remitido mayor que lo pedido, como el 127 del pedido #72: guardar el pedido sin tocarlos tiene que andar)."""
    if nueva_cantidad >= (item.cantidad or 0.0) - EPS:
        return None
    remitida = item.cantidad_remitida
    if nueva_cantidad < remitida - EPS:
        return (f"No se puede bajar la cantidad a {nueva_cantidad}: "
                f"ya se entregaron {remitida} unidades de este renglón.")
    facturada = item.cantidad_facturada_neta
    if nueva_cantidad < facturada - EPS:
        return (f"CANTIDAD_BAJO_FACTURADO: no se puede bajar la cantidad a {_g(nueva_cantidad)}: ya se facturaron "
                f"{_g(facturada)} unidades de este renglón. Para bajarla hace falta una nota de crédito "
                f"(o anular la factura).")
    return None


def mensaje_baja_de_renglon(item) -> Optional[str]:
    """Quitar un renglon: no se puede si tiene entrega real (ya lo controla el router) ni si alguna factura
    vigente lo referencia (un comprobante emitido no pierde su renglon)."""
    if item.cantidad_facturada > EPS:
        return (f"CANTIDAD_BAJO_FACTURADO: no se puede eliminar el renglón: ya se facturaron "
                f"{_g(item.cantidad_facturada)} unidades. Para quitarlo hace falta una nota de crédito "
                f"(o anular la factura).")
    return None
