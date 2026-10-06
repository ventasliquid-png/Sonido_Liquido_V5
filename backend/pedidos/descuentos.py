"""
Descuento por renglon del pedido (Card #159, S879; decision de Carlos 06/10).

El descuento se define POR UNIDAD (en $ por unidad o en %) y el total del renglon es el derivado. La base no
cambia: `PedidoItem.descuento_importe` sigue guardando el total del renglon (en centavos) y
`descuento_porcentaje` el porcentaje sobre el precio unitario. Lo que se agrega es el redondeo (importe a 2
decimales, porcentaje a 4: lo que usa el formulario de ARCA para que la factura cierre con el precio final)
y conservar el descuento por unidad cuando cambia la cantidad.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple


def redondear(valor: Optional[float], decimales: int) -> float:
    """Redondeo comercial (mitad hacia arriba) sobre la representacion decimal del numero: round(2.675, 2)
    de Python da 2.67 por el binario flotante; aca da 2.68."""
    if valor is None:
        return 0.0
    return float(Decimal(repr(float(valor))).quantize(Decimal(1).scaleb(-decimales), rounding=ROUND_HALF_UP))


def descuento_normalizado(importe: Optional[float], porcentaje: Optional[float]) -> Tuple[float, float]:
    """(importe a centavos, porcentaje a 4 decimales). El porcentaje es informativo: el importe manda."""
    return redondear(importe, 2), redondear(porcentaje, 4)


def importe_conservando_unitario(importe_actual: Optional[float], cantidad_actual: Optional[float],
                                 cantidad_nueva: float) -> float:
    """Total del descuento al cambiar la cantidad, manteniendo el descuento por unidad:
    importe / cantidad_actual * cantidad_nueva, a centavos. Sin cantidad previa no hay unidad que conservar."""
    if not importe_actual or not cantidad_actual or cantidad_actual <= 0:
        return redondear(importe_actual, 2)
    return redondear(importe_actual / cantidad_actual * cantidad_nueva, 2)
