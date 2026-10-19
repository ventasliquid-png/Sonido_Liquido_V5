"""
Kits del pedido (Card #177 v3, S888). Nike ratifico el diseno con Sello de Oro el 19/10/2026.

Un KIT es un grupo de renglones de UN pedido que se vendieron juntos a un precio conjunto. No es un producto ni un SKU: es el numero PedidoItem.kit_grupo (entero, NULL = sin kit),
local al pedido y sin identidad ni trazabilidad entre pedidos. Un kit EXISTE solo si 2 o mas renglones del pedido comparten el numero ("kit valido"): un numero con un solo renglon
no es un kit y no calcula nada.

Nombres canonicos (Carlos + Nike, 19/10): renglon = PedidoItem.kit_grupo (prohibidos es_kit / en_kit); descuento del renglon = PedidoItem.descuento_importe / descuento_porcentaje;
pedido = PedidoFlags.ES_KIT (bit 47). ProductoFlags.IS_KIT (bit 6) y ES_PACK (bit 11) son del PRODUCTO: nunca se mezclan con estos.

Reglas (ratificadas por Nike):
  - El bit ES_KIT lo calcula el SERVIDOR: prendido si el pedido tiene al menos un kit valido, apagado si ninguno; reversible mientras el pedido este abierto y congelado en CUMPLIDO / ANULADO.
  - El descuento del kit va POR RENGLON (descuento_importe / descuento_porcentaje del renglon), no como descuento global (el global se prorratea sobre todos los renglones al facturar y el
    conciliador lo ignora). El descuento del kit puede ser 0 (kit con regalo a precio de lista).
  - Un renglon con factura vigente (PedidoItem.cantidad_facturada > 0) no cambia de kit, y los pedidos que nacen de una factura (ORIGEN_FACTURA, bit 38) tampoco: la factura manda;
    para corregir, nota de credito o de debito.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Iterable, List, Optional

from backend.pedidos.constants import PedidoFlags as PF

EPS = 0.001
KIT_GRUPO_MAX = 99                 # el numero es una etiqueta local: 1 a 99 sobra
UMBRAL_REBAJA_KIT_PCT = 8.0        # advertencia (no bloquea) si la rebaja del kit supera este % de la suma; propuesta de NS, a confirmar con Carlos
MODOS_REPARTO = ("PAREJO", "ABSORBE")


def kits_validos(kit_grupos: Iterable[Optional[int]]) -> Dict[int, int]:
    """{numero de kit: cantidad de renglones} solo de los kits VALIDOS (2 o mas renglones con el mismo numero)."""
    cuenta: Dict[int, int] = {}
    for g in kit_grupos:
        if g is not None:
            cuenta[g] = cuenta.get(g, 0) + 1
    return {g: n for g, n in cuenta.items() if n >= 2}


def hay_kit_valido(kit_grupos: Iterable[Optional[int]]) -> bool:
    return bool(kits_validos(kit_grupos))


def sincronizar_bit_kit(db, pedido, forzar: bool = False) -> bool:
    """Prende o apaga PedidoFlags.ES_KIT segun los renglones que el pedido tiene EN LA BASE (hace flush antes). Devuelve si el pedido tiene al menos un kit valido.
    Congelado: si el pedido ya esta CUMPLIDO o ANULADO no toca nada (devuelve el valor que tiene) salvo con forzar=True (alta del pedido). No hace commit."""
    from backend.pedidos.models import PedidoItem
    flags = pedido.flags_estado or 0
    if not forzar and flags & (int(PF.ES_CUMPLIDO) | int(PF.ES_ANULADO)):
        return bool(flags & int(PF.ES_KIT))
    db.flush()
    grupos = [g for (g,) in db.query(PedidoItem.kit_grupo).filter(PedidoItem.pedido_id == pedido.id, PedidoItem.kit_grupo.isnot(None)).all()]
    quiere = hay_kit_valido(grupos)
    nuevo = (flags | int(PF.ES_KIT)) if quiere else (flags & ~int(PF.ES_KIT))
    if nuevo != flags:
        pedido.flags_estado = nuevo
    return quiere


def mensaje_kit_bloqueado(item, pedido=None) -> Optional[str]:
    """None = el renglon puede cambiar de kit. Si no, el motivo (para un 400/409): factura vigente sobre el renglon o pedido nacido de una factura."""
    pedido = pedido if pedido is not None else getattr(item, "pedido", None)
    if pedido is not None and (pedido.flags_estado or 0) & int(PF.ORIGEN_FACTURA):
        return ("KIT_PEDIDO_DE_FACTURA: este pedido nacio de una factura emitida: sus renglones no se agrupan en kits "
                "(la factura manda; para corregir hace falta una nota de credito o de debito).")
    facturada = item.cantidad_facturada
    if facturada > EPS:
        g = int(facturada) if float(facturada).is_integer() else facturada
        return (f"KIT_RENGLON_FACTURADO: el renglon ya tiene {g} unidades facturadas: no se puede marcar ni sacar de un kit "
                f"(la factura manda; para corregir hace falta una nota de credito o de debito).")
    return None


# ------------------------------------------------------------------ reparto del precio del kit (calculo puro, sin base de datos)

def _d(x) -> Decimal:
    return Decimal(repr(float(x or 0.0)))


def _c(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_reparto(items: List[dict], precio_kit: Optional[float] = None, porcentaje: Optional[float] = None,
                     modo: str = "PAREJO", absorbe_indice: Optional[int] = None) -> dict:
    """Reparte el precio de UN kit entre sus renglones. `items`: [{cantidad, precio_unitario, descuento_importe}] con el descuento que cada renglon tiene HOY.
    Todo en NETO (el pedido guarda precios netos; el equivalente con IVA lo muestra la pantalla). La base es el importe actual de cada renglon (precio x cantidad - su descuento).
    El operador informa UNO de: `precio_kit` (importe final del conjunto) o `porcentaje` (rebaja sobre la suma). Si el precio es IGUAL O MAYOR a la suma no se modifica nada.
    Modos: PAREJO = el mismo porcentaje de rebaja en cada renglon; ABSORBE = lo absorbe un renglon (el `absorbe_indice`), que es el regalo y queda mas barato o a $0.
    Devuelve, por renglon, el descuento_importe / descuento_porcentaje / subtotal resultantes (descuento total del renglon, no el incremental). ValueError con codigo KIT_*."""
    if len(items) < 2:
        raise ValueError("KIT_MENOS_DE_DOS: un kit necesita al menos 2 renglones.")
    if (precio_kit is None) == (porcentaje is None):
        raise ValueError("KIT_PRECIO_O_PORCENTAJE: informar el precio del kit o el porcentaje, uno solo.")
    modo = (modo or "PAREJO").upper()
    if modo not in MODOS_REPARTO:
        raise ValueError(f"KIT_MODO_INVALIDO: '{modo}' no es un modo de reparto ({', '.join(MODOS_REPARTO)}).")

    bruto = [_c(_d(i["precio_unitario"]) * _d(i["cantidad"])) for i in items]
    desc = [_c(_d(i.get("descuento_importe"))) for i in items]
    base = [b - d for b, d in zip(bruto, desc)]
    suma = sum(base, Decimal("0"))
    if suma <= 0:
        raise ValueError("KIT_SUMA_CERO: la suma de los renglones es cero: no hay precio para repartir.")

    if porcentaje is not None:
        if not (0 <= porcentaje <= 100):
            raise ValueError("KIT_PORCENTAJE_INVALIDO: el porcentaje va de 0 a 100.")
        objetivo = _c(suma * (Decimal(1) - _d(porcentaje) / Decimal(100)))
    else:
        if precio_kit < 0:
            raise ValueError("KIT_PRECIO_NEGATIVO: el precio del kit no puede ser negativo.")
        objetivo = _c(_d(precio_kit))

    sin_cambios = objetivo >= suma
    if sin_cambios:
        nuevos = list(base)
        objetivo = suma
    elif modo == "PAREJO":
        nuevos = [_c(b * objetivo / suma) for b in base]
        resto = objetivo - sum(nuevos, Decimal("0"))          # los centavos que sobran o faltan por redondear van al renglon mas grande
        mayor = max(range(len(base)), key=lambda k: (base[k], k))
        nuevos[mayor] += resto
    else:
        if absorbe_indice is None or not (0 <= absorbe_indice < len(items)):
            raise ValueError("KIT_ABSORBE_SIN_RENGLON: en el modo ABSORBE hay que indicar que renglon absorbe la rebaja.")
        rebaja = suma - objetivo
        if rebaja > base[absorbe_indice]:
            raise ValueError(f"KIT_ABSORBE_NO_ALCANZA: la rebaja (${rebaja}) es mayor que el importe del renglon elegido (${base[absorbe_indice]}): "
                             f"el precio del kit no puede bajar de ${suma - base[absorbe_indice]} absorbiendo en ese renglon.")
        nuevos = list(base)
        nuevos[absorbe_indice] = base[absorbe_indice] - rebaja

    rebaja = suma - objetivo
    resultado = []
    for k, (b, n) in enumerate(zip(bruto, nuevos)):
        d = _c(b - n)
        pct = float((d / b * Decimal(100)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)) if b > 0 else 0.0
        resultado.append({"indice": k, "descuento_importe": float(d), "descuento_porcentaje": pct, "subtotal": float(n)})
    rebaja_pct = float((rebaja / suma * Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return {
        "suma": float(suma), "precio_kit": float(objetivo), "rebaja_importe": float(rebaja), "rebaja_porcentaje": rebaja_pct,
        "sin_cambios": sin_cambios, "modo": modo, "umbral_porcentaje": UMBRAL_REBAJA_KIT_PCT,
        "supera_umbral": (not sin_cambios) and rebaja_pct > UMBRAL_REBAJA_KIT_PCT, "items": resultado,
    }
