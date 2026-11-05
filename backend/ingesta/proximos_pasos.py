# [IDENTIDAD] - backend/ingesta/proximos_pasos.py
# [S900, Card #214; Carlos 05/11, a raíz de la 2603 y el pedido #155]
# ------------------------------------------
"""Qué queda por hacer después de conciliar una factura: dos propuestas, ninguna automática (solo lectura).

1. FECHA DEL REMITO. «El remito que se carga después, como ese que tiene fecha de hoy, debería ofrecer fecha rto = fecha FAC, que el operador la cambie si es necesario»
   (regla de Carlos del 20/09: «lo normal manda: default, resta y nota»). Se propone fechar el remito como la factura cuando es MÁS DE UN DÍA POSTERIOR a ella (un remito
   anterior a la factura es el caso normal y no se toca; una factura de adelanto con envío posterior es legítima: por eso es una propuesta y no una regla).
2. CUMPLIDO. «Si la conciliación lee Pedido = entregado / facturado, que proponga «¿Pasamos a Cumplido?»». Se propone cuando el pedido (PENDIENTE) quedó COMPLETO: cada renglón
   remitido por lo menos lo pedido y todo lo remitido facturable está facturado, con remitos que no están en depósito esperando retiro. Cerrar un pedido sigue siendo una acción
   del operador (con sus guardas de siempre en el cambio de estado): acá solo se calcula si corresponde preguntar.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.facturacion.models import Factura
from backend.remitos.constants import RemitoFlags

EPS = 1e-6
DIAS_UMBRAL = 1   # se propone fechar el remito como la factura si es más de este número de días posterior a ella


def _fecha_remito(remito) -> Optional[datetime]:
    """La fecha del remito es la de EMISIÓN (S890); si no la tiene, la de salida o la de creación (como `cambiar_fecha`)."""
    return remito.fecha_emision or remito.fecha_salida or remito.fecha_creacion


def _activo(remito) -> bool:
    return str(remito.estado or "").upper() != "ANULADO" and not (int(remito.flags_estado or 0) & int(RemitoFlags.ANULADO))


def _iso(d) -> Optional[str]:
    if d is None:
        return None
    return d.isoformat()[:10]


def proximos_pasos(db: Session, factura: Factura) -> Dict[str, Any]:
    f_fecha: Optional[date] = factura.fecha_emision
    remitos: List[Dict[str, Any]] = []
    pedidos_ids: List[Any] = []
    vistos = set()
    for v in (factura.vinculos_remitos or []):
        r = v.remito
        if r is None or not _activo(r) or not r.numero_legal:
            continue
        fr = _fecha_remito(r)
        dias = (fr.date() - f_fecha).days if (fr is not None and f_fecha is not None) else None
        remitos.append({
            "remito_id": str(r.id), "numero_legal": r.numero_legal, "pedido_id": int(r.pedido_id) if r.pedido_id is not None else None,
            "fecha": _iso(fr), "dias_despues_de_la_factura": dias,
            "proponer_fecha": dias is not None and dias > DIAS_UMBRAL,
        })
        if r.pedido_id is not None and int(r.pedido_id) not in vistos:   # en P el pedido_id puede venir como texto en una tabla y entero en otra
            vistos.add(int(r.pedido_id))
            pedidos_ids.append(int(r.pedido_id))
    if factura.pedido_id is not None and int(factura.pedido_id) not in vistos:
        pedidos_ids.append(int(factura.pedido_id))

    pedidos: List[Dict[str, Any]] = []
    from backend.pedidos.models import Pedido
    for pid in pedidos_ids:
        p = db.query(Pedido).filter(Pedido.id == int(pid)).first()
        if p is None:
            continue
        items = list(p.items or [])
        pedida = sum(float(i.cantidad or 0) for i in items)
        remitida = sum(float(i.cantidad_remitida or 0) for i in items)
        facturada = sum(float(i.cantidad_facturada_neta or 0) for i in items)
        sin_remitir = [i for i in items if float(i.cantidad_remitida or 0) + EPS < float(i.cantidad or 0)]
        sin_facturar = [i for i in items if float(i.remitido_sin_facturar or 0) > EPS]
        remitos_activos = [r for r in (p.remitos or []) if _activo(r)]
        en_deposito = any(int(r.flags_estado or 0) & int(RemitoFlags.EN_DEPOSITO) for r in remitos_activos)
        salida_asumida = any(not (int(r.flags_estado or 0) & int(RemitoFlags.SALIDA_CONFIRMADA | RemitoFlags.RECIBIDO)) for r in remitos_activos)
        abierto = str(p.estado or "").upper() == "PENDIENTE"
        completo = bool(items) and bool(remitos_activos) and not sin_remitir and not sin_facturar and not en_deposito
        pedidos.append({
            "pedido_id": int(p.id), "estado": p.estado, "renglones": len(items),
            "pedida": pedida, "remitida": remitida, "facturada": facturada,
            "completo": completo, "en_deposito": en_deposito, "salida_asumida": bool(salida_asumida and remitos_activos),
            "proponer_cumplido": bool(abierto and completo),
            "remitos": [r.numero_legal or "PR sin número" for r in remitos_activos],   # un PR todavía no impreso no tiene número (ni fecha: la toma al emitirse)
        })

    return {
        "factura": {"factura_id": str(factura.id), "numero": factura.numero_completo, "fecha": _iso(f_fecha), "tipo": factura.tipo_comprobante},
        "remitos": remitos, "pedidos": pedidos,
        "remitos_a_fechar": [r for r in remitos if r["proponer_fecha"]],
        "pedidos_a_cumplir": [p for p in pedidos if p["proponer_cumplido"]],
    }
