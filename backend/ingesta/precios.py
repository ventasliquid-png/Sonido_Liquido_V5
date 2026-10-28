# backend/ingesta/precios.py
"""
[S894, Card #144; Carlos 28/10] Precios de la factura contra los del pedido, con confirmación del operador.

Carlos: «No quiero que solo avise: quiero que provoque una confirmación del operador si hay discrepancia. Que sea consciente».
Se compara SIEMPRE, renglón por renglón, el precio efectivo, o sea lo que vale la unidad después de las bonificaciones:
  - el de la factura: el subtotal que imprime ARCA dividido la cantidad (el lector lee «% Bonif» y «Subtotal» desde la S894);
  - el del pedido: el subtotal del renglón dividido la cantidad (con el descuento del renglón), y el descuento general del pedido
    prorrateado como lo hace facturacion/service.py (neto = suma de subtotales - descuento_global_importe).
Tolerancia: $1 o 0,5 %, la mayor (la misma de la conciliación). Si hay diferencia, el servidor no registra la factura hasta que
el operador confirme (409 DIFERENCIA_DE_PRECIO con la lista); al confirmar queda una nota [SISTEMA] con las diferencias, quién y
el motivo si lo dio. El pedido no se toca: es soberano y se corrige aparte.
Usado por la Ingesta (IngestaService.approve, renglones atados a un pedido) y por «Conciliar contra PR» (ConciliadorService).
"""
from datetime import datetime
from typing import Optional

from fastapi import HTTPException

TOLERANCIA_ABS = 1.0
TOLERANCIA_REL = 0.005
CODIGO = "DIFERENCIA_DE_PRECIO"


def _campo(it, nombre):
    return it.get(nombre) if isinstance(it, dict) else getattr(it, nombre, None)


def _pesos(x: float) -> str:
    return "$ " + f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(x: float) -> str:
    return f"{x:g}".replace(".", ",") + " %"


def precio_efectivo_factura(it) -> float:
    """Precio por unidad de un renglón de la factura, con la bonificación aplicada."""
    cantidad = _campo(it, "cantidad") or 0
    subtotal = _campo(it, "subtotal")
    if cantidad and subtotal:
        return subtotal / cantidad
    return (_campo(it, "precio_unitario") or 0.0) * (1 - (_campo(it, "bonificacion") or 0.0) / 100.0)


def factor_descuento_general(pedido) -> float:
    """Lo que queda de cada peso del pedido después del descuento general (1.0 sin descuento)."""
    importe = (getattr(pedido, "descuento_global_importe", None) or 0.0) if pedido is not None else 0.0
    if importe <= 0:
        return 1.0
    suma = sum((pi.subtotal or 0.0) for pi in (pedido.items or []))
    return (suma - importe) / suma if suma > 0 else 1.0


def precio_efectivo_pedido(pedido_item, factor: float = 1.0) -> Optional[float]:
    """Precio por unidad del renglón del pedido, con su descuento y el general (`factor`). None si no hay con qué comparar."""
    if pedido_item is None:
        return None
    if (pedido_item.cantidad or 0) > 0 and pedido_item.subtotal:
        return pedido_item.subtotal / pedido_item.cantidad * factor
    if pedido_item.precio_unitario:
        return pedido_item.precio_unitario * (1 - (pedido_item.descuento_porcentaje or 0.0) / 100.0) * factor
    return None


def diferencia_de_precio(pedido_item, it, factor: float = 1.0, producto: Optional[str] = None) -> Optional[dict]:
    """La diferencia entre el renglón de la factura `it` y el del pedido, o None si coinciden (o no hay precio en el pedido)."""
    p_ped = precio_efectivo_pedido(pedido_item, factor)
    if not p_ped:
        return None
    p_fac = precio_efectivo_factura(it)
    if abs(p_fac - p_ped) <= max(TOLERANCIA_ABS, p_ped * TOLERANCIA_REL):
        return None
    nombre = producto or (pedido_item.producto.nombre if getattr(pedido_item, "producto", None) else None) or _campo(it, "descripcion") or "renglón"
    bonif = _campo(it, "bonificacion") or 0.0
    dto = pedido_item.descuento_porcentaje or 0.0
    partes = []
    if bonif or dto:
        partes.append(f"la factura tiene {_pct(bonif)} de bonificación" if bonif else "la factura no tiene bonificación")
        partes.append(f"el pedido, {_pct(dto)} de descuento" if dto else "el pedido, sin descuento")
    if factor < 1.0:
        partes.append(f"con el descuento general del pedido ({_pct(round((1 - factor) * 100, 2))})")
    detalle = f"«{nombre}»: pedido {_pesos(p_ped)} por unidad, factura {_pesos(p_fac)}" + (f" ({'; '.join(partes)})" if partes else "") + "."
    return {"pedido_item_id": pedido_item.id, "producto": nombre, "precio_pedido": round(p_ped, 2), "precio_factura": round(p_fac, 2),
            "bonificacion_factura": bonif, "descuento_pedido": dto, "detalle": detalle}


def exigir_confirmacion(diferencias: list, confirmado: bool) -> None:
    """Sin la confirmación del operador, una diferencia de precio frena el registro de la factura."""
    if diferencias and not confirmado:
        raise HTTPException(status_code=409, detail={
            "codigo": CODIGO,
            "mensaje": ("El precio de la factura no coincide con el del pedido en " +
                        ("un renglón" if len(diferencias) == 1 else f"{len(diferencias)} renglones") +
                        ". Revisalo y confirmá para registrarla así; el pedido no se cambia."),
            "diferencias": diferencias,
        })


def nota_confirmacion(diferencias: list, referencia: str, usuario, motivo: Optional[str]) -> str:
    """Nota [SISTEMA] de la confirmación: qué difería, quién lo confirmó, cuándo y por qué (si lo dijo)."""
    quien = getattr(usuario, "username", None) or "sin usuario"
    texto = (f"[SISTEMA] Diferencia de precio con {referencia}, confirmada por {quien} el {datetime.now().strftime('%d/%m/%Y %H:%M')}: "
             + " ".join(d["detalle"] for d in diferencias))
    motivo = (motivo or "").strip()
    return texto + (f" Motivo: {motivo}" if motivo else "")
