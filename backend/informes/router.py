# backend/informes/router.py
"""
[S875, DISENO_MODULO_INFORMES_S875_2026-09-26.md] Módulo Informes -- Nivel 1 (Listados) y
Nivel 2 (Análisis/ABC). Capa de consulta, solo lectura -- no escribe RemitoNota ni
cantidad_recibida.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.informes.export_utils import exportar, normalizar_texto
from backend.informes.notas import fragmentos_clasificados, CATEGORIAS_DISPONIBLES, MARCADOR_SISTEMA

router = APIRouter(
    prefix="/informes",
    tags=["Informes"],
    responses={404: {"description": "Not found"}},
)

# --- Informe A: remitos por fecha y/o cliente -- misma consulta que ya usa
# EntregasView.vue (GET /remitos/entregas), acá en forma de tabla plana exportable. ---

def _fecha_corta(valor) -> Optional[str]:
    """Fecha para el listado: 'AAAA-MM-DD', y con hora solo si la hora dice algo. Los pedidos guardan la
    fecha como datetime a medianoche y `isoformat()` la mostraba como '2026-09-04T00:00:00'."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d") if (valor.hour, valor.minute, valor.second) == (0, 0, 0) else valor.strftime("%Y-%m-%d %H:%M")
    texto = str(valor)
    if len(texto) >= 19 and texto[10] == "T":
        return texto[:10] if texto[11:19] == "00:00:00" else f"{texto[:10]} {texto[11:16]}"
    return texto


COLUMNAS_REMITOS = [
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "oc", "label": "OC", "width": 14},
    {"key": "pedido_id", "label": "Pedido", "width": 10},
    {"key": "circuito", "label": "Circuito", "width": 10},
    {"key": "estado", "label": "Estado", "width": 18},
    {"key": "fecha_pedido", "label": "Fecha Pedido", "width": 14},
    {"key": "producto", "label": "Producto", "width": 30},
    {"key": "cantidad_pedida", "label": "Cant. Pedida", "width": 12},
    {"key": "remito", "label": "Remito", "width": 16},
    {"key": "fecha_documento", "label": "Fecha Remito", "width": 14},
    {"key": "cantidad_remitida", "label": "Cant. Remitida", "width": 14},
    {"key": "factura", "label": "Factura", "width": 16},
]

# Cómo se presenta el Informe A (pedido de Carlos, 30/09): el orden se elige al abrir el informe.
ORDENES_REMITOS = {      # orden -> sentido por defecto
    "cliente": "asc",    # por cliente (A-Z); dentro de cada uno, por fecha y número de remito
    "fecha": "desc",     # por fecha de remito, los más recientes arriba
    "remito": "asc",     # por número de remito
}
TITULOS_ORDEN = {
    "cliente": "por cliente",
    "fecha": "por fecha de remito",
    "remito": "por número de remito",
}
CIRCUITOS = ("todos", "blanco", "rosa")


def _info_pedidos(db: Session, pedido_ids) -> dict:
    """pedido_id -> {estado_base, circuito, parcial}, con el MISMO criterio que la lista de pedidos
    (PedidoList.vue): el circuito Rosa es el bit NO_FISCAL_FORCE, y 'parcial' es que algún renglón
    tenga entrega pero no completa. Una sola consulta para todos los pedidos del informe."""
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido
    from backend.pedidos.constants import PedidoFlags

    ids = [i for i in set(pedido_ids) if i is not None]
    if not ids:
        return {}
    info = {}
    for p in db.query(Pedido).options(joinedload(Pedido.items)).filter(Pedido.id.in_(ids)).all():
        parcial = any(0 < (i.cantidad_entregada or 0) < (i.cantidad or 0) for i in p.items)
        rosa = bool((p.flags_estado or 0) & int(PedidoFlags.NO_FISCAL_FORCE))
        info[p.id] = {"estado_base": p.estado, "parcial": parcial, "circuito": "Rosa" if rosa else "Blanco"}
    return info


def _anotar_pedido(db: Session, filas: list) -> list:
    """Agrega a cada fila (que trae `pedido_id`) el circuito y el estado del pedido. `estado_base` y
    `parcial` no son columnas: los usa la pantalla para pintar; `estado` es el texto que se exporta."""
    info = _info_pedidos(db, [f.get("pedido_id") for f in filas])
    for f in filas:
        i = info.get(f.get("pedido_id"))
        f["circuito"] = i["circuito"] if i else None
        f["estado_base"] = i["estado_base"] if i else None
        f["parcial"] = bool(i and i["parcial"])
        f["estado"] = (f"{i['estado_base']} · PARCIAL" if i["parcial"] else i["estado_base"]) if i else None
    return filas


def _num_remito(numero_legal) -> tuple:
    """'0016-00002595' -> (2595, 16): primero el NÚMERO, después la serie. Los rangos son disjuntos
    (el 0016 llega a 2602 y el 0015 arranca en 3010), así que ordenar por número es también
    ordenar cronológicamente aunque haya dos talonarios."""
    if not numero_legal:
        return (-1, -1)
    partes = str(numero_legal).split("-")
    try:
        return (int(partes[-1]), int(partes[0]) if len(partes) > 1 else 0)
    except ValueError:
        return (-1, -1)


def _filas_informe_remitos(
    db: Session,
    cliente_id: Optional[str],
    desde: Optional[datetime],
    hasta: Optional[datetime],
    producto_id: Optional[int],
    oc: Optional[str],
    incluir_anulados: bool,
    orden: str = "cliente",
    sentido: Optional[str] = None,
    circuito: str = "todos",
    cliente_desde: Optional[str] = None,
    cliente_hasta: Optional[str] = None,
    producto_desde: Optional[str] = None,
    producto_hasta: Optional[str] = None,
    incluir_sin_remito: bool = False,
):
    from backend.remitos.service import RemitosService
    from backend.productos.models import Producto

    resultado = RemitosService.get_entregas(
        db,
        cliente_id=cliente_id,
        desde=desde,
        hasta=hasta,
        producto_id=producto_id,
        oc=oc,
        incluir_anulados=incluir_anulados,
    )
    filas = []
    for fila in resultado["filas"]:
        fila = dict(fila)  # get_entregas también alimenta EntregasView: no se le toca el dato original
        for clave in ("fecha_pedido", "fecha_documento"):
            if clave in fila:
                fila[clave] = _fecha_corta(fila[clave])
        filas.append(fila)

    # Es un informe de REMITOS: los renglones de pedido que todavía no tienen ninguno (los que get_entregas
    # agrega de relleno para la pantalla de Entregas) solo entran si se piden. Los pendientes son el Informe B.
    # Se mira si el REMITO existe (remito_id), no si tiene número: un remito recién armado no lo tiene hasta
    # que se imprime (número atrasado, Etapa 3/4), y una devolución también nace sin número.
    if not incluir_sin_remito:
        filas = [f for f in filas if f.get("remito_id")]
    for f in filas:
        if f.get("remito_id") and not f.get("remito"):
            f["remito"] = "(sin número)"

    _anotar_pedido(db, filas)
    for f in filas:
        f["grupo"] = f.get("remito_id") or f"sin-remito-{f.get('pedido_id')}"   # la pantalla arma una caja por grupo

    if circuito != "todos":
        filas = [f for f in filas if (f.get("circuito") or "").lower() == circuito]

    # Rangos "desde / hasta" (inclusivos). Clientes: por razón social, sin acentos ni mayúsculas, y el
    # "hasta" cubre todo lo que empieza así ("M" incluye "Mirta Rossini"). Productos: por código visual.
    if cliente_desde or cliente_hasta:
        lo = normalizar_texto(cliente_desde) if cliente_desde else None
        hi = normalizar_texto(cliente_hasta) if cliente_hasta else None

        def _en_rango_cliente(f):
            n = normalizar_texto(f.get("cliente") or "")
            return (lo is None or n >= lo) and (hi is None or n <= hi + "￿")
        filas = [f for f in filas if _en_rango_cliente(f)]
    if producto_desde or producto_hasta:
        ids_prod = {f.get("producto_id") for f in filas if f.get("producto_id")}
        codigos = {p.id: (p.codigo_visual or "").strip().upper()
                   for p in db.query(Producto).filter(Producto.id.in_(ids_prod))} if ids_prod else {}
        lo = (producto_desde or "").strip().upper() or None
        hi = (producto_hasta or "").strip().upper() or None

        def _en_rango_producto(f):
            c = codigos.get(f.get("producto_id"), "")
            return bool(c) and (lo is None or c >= lo) and (hi is None or c <= hi + "￿")
        filas = [f for f in filas if _en_rango_producto(f)]

    # Orden: primero un desempate fijo y ascendente (fecha, nº de remito, pedido, renglón) y después la clave
    # principal. El sort de Python es estable, así que las filas de un mismo remito quedan juntas (la
    # pantalla las agrupa en una caja) y el renglón conserva el orden en que se cargó el pedido.
    sentido = sentido or ORDENES_REMITOS[orden]

    def _fecha_efectiva(f):
        return f.get("fecha_documento") or f.get("fecha_pedido") or ""

    filas.sort(key=lambda f: (_fecha_efectiva(f), _num_remito(f.get("remito")), f.get("pedido_id") or 0, f.get("pedido_item_id") or 0))
    principal = {
        "cliente": lambda f: normalizar_texto(f.get("cliente") or ""),
        "fecha": _fecha_efectiva,
        "remito": lambda f: _num_remito(f.get("remito")),
    }[orden]
    filas.sort(key=principal, reverse=(sentido == "desc"))
    return filas


def _filtros_remitos(
    cliente_id: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    producto_id: Optional[int] = None,
    oc: Optional[str] = None,
    incluir_anulados: bool = False,
    orden: str = "cliente",
    sentido: Optional[str] = None,
    circuito: str = "todos",
    cliente_desde: Optional[str] = None,
    cliente_hasta: Optional[str] = None,
    producto_desde: Optional[str] = None,
    producto_hasta: Optional[str] = None,
    incluir_sin_remito: bool = False,
) -> dict:
    """Los filtros del Informe A, validados una sola vez para la pantalla y para la exportación."""
    if orden not in ORDENES_REMITOS:
        raise HTTPException(status_code=400, detail=f"orden inválido: {orden!r} (cliente | fecha | remito)")
    if sentido not in (None, "asc", "desc"):
        raise HTTPException(status_code=400, detail=f"sentido inválido: {sentido!r} (asc | desc)")
    if circuito not in CIRCUITOS:
        raise HTTPException(status_code=400, detail=f"circuito inválido: {circuito!r} (todos | blanco | rosa)")
    return dict(
        cliente_id=cliente_id, desde=desde, hasta=hasta, producto_id=producto_id, oc=oc,
        incluir_anulados=incluir_anulados, orden=orden, sentido=sentido, circuito=circuito,
        cliente_desde=cliente_desde, cliente_hasta=cliente_hasta,
        producto_desde=producto_desde, producto_hasta=producto_hasta, incluir_sin_remito=incluir_sin_remito,
    )


def _subtitulo_remitos(db: Session, f: dict) -> str:
    """Los filtros con los que se armó el listado, para que una hoja impresa o un archivo guardado
    diga de dónde salió."""
    from backend.clientes.models import Cliente

    sentido = f["sentido"] or ORDENES_REMITOS[f["orden"]]
    partes = [f"Orden: {TITULOS_ORDEN[f['orden']]} ({'descendente' if sentido == 'desc' else 'ascendente'})"]
    if f["cliente_id"]:
        c = db.query(Cliente).filter(Cliente.id == f["cliente_id"]).first()
        partes.append(f"Cliente: {c.razon_social if c else f['cliente_id']}")
    if f["cliente_desde"] or f["cliente_hasta"]:
        partes.append(f"Clientes de {f['cliente_desde'] or '...'} a {f['cliente_hasta'] or '...'}")
    if f["producto_desde"] or f["producto_hasta"]:
        partes.append(f"Productos de {f['producto_desde'] or '...'} a {f['producto_hasta'] or '...'}")
    if f["desde"] or f["hasta"]:
        partes.append(f"Fechas de {_fecha_corta(f['desde']) or '...'} a {_fecha_corta(f['hasta']) or '...'}")
    if f["oc"]:
        partes.append(f"OC: {f['oc']}")
    if f["circuito"] != "todos":
        partes.append(f"Circuito: {f['circuito'].capitalize()}")
    if f["incluir_anulados"]:
        partes.append("incluye anulados")
    if f["incluir_sin_remito"]:
        partes.append("incluye renglones sin remito")
    return " | ".join(partes)


@router.get("/remitos")
def informe_remitos(filtros: dict = Depends(_filtros_remitos), db: Session = Depends(get_db)):
    """Informe A -- tabla plana para pantalla. Mismos filtros/datos que
    GET /remitos/entregas (EntregasView.vue la usa como árbol; acá es la vista
    listado, pensada para exportar), más orden, circuito, rangos y agrupación por remito."""
    filas = _filas_informe_remitos(db, **filtros)
    return {"columnas": COLUMNAS_REMITOS, "filas": filas}


@router.get("/remitos/export")
def informe_remitos_export(formato: str, filtros: dict = Depends(_filtros_remitos), db: Session = Depends(get_db)):
    """Recalcula server-side con los mismos filtros -- nunca confía en filas que
    mande el cliente, para que el archivo exportado sea siempre una consulta
    fresca, no lo que quedó pintado en pantalla."""
    filas = _filas_informe_remitos(db, **filtros)
    try:
        return exportar(formato, "Remitos por fecha o cliente", COLUMNAS_REMITOS, filas,
                        subtitulo=_subtitulo_remitos(db, filtros))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Informe B: pedidos con pendiente -- resta calculada (PedidoItem.cantidad_entregada,
# @property), nunca los Bits 20/21 (Etapa 2 del Circuito PR: todo lector pasa a la resta). ---

COLUMNAS_PEDIDOS_PENDIENTE = [
    {"key": "pedido_id", "label": "Pedido", "width": 10},
    {"key": "circuito", "label": "Circuito", "width": 10},
    {"key": "estado", "label": "Estado", "width": 18},
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "fecha_pedido", "label": "Fecha", "width": 14},
    {"key": "oc", "label": "OC", "width": 14},
    {"key": "renglon", "label": "Renglón", "width": 30},
    {"key": "declarado", "label": "Declarado", "width": 12},
    {"key": "entregado", "label": "Entregado", "width": 12},
    {"key": "pendiente", "label": "Pendiente", "width": 12},
]


def _filas_informe_pendiente(db: Session, cliente_id: Optional[str], oc: Optional[str]):
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido, PedidoItem

    query = (
        db.query(PedidoItem)
        .join(Pedido, PedidoItem.pedido_id == Pedido.id)
        .filter(Pedido.estado != "ANULADO")
        .options(joinedload(PedidoItem.pedido).joinedload(Pedido.cliente), joinedload(PedidoItem.producto))
    )
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
    if oc:
        query = query.filter(Pedido.oc.ilike(f"%{oc.strip()}%"))

    filas = []
    for item in query.all():
        entregado = item.cantidad_entregada
        pendiente = item.cantidad - entregado
        if pendiente <= 0.001:
            continue
        pedido = item.pedido
        cliente = pedido.cliente if pedido else None
        producto = item.producto
        filas.append({
            "pedido_id": pedido.id if pedido else None,
            "cliente": cliente.razon_social if cliente else None,
            "fecha_pedido": _fecha_corta(pedido.fecha) if pedido and pedido.fecha else None,
            "oc": pedido.oc if pedido else None,
            "renglon": producto.nombre if producto else (item.nota or "Ítem"),
            "declarado": item.cantidad,
            "entregado": entregado,
            "pendiente": pendiente,
        })
    return _anotar_pedido(db, filas)


@router.get("/pedidos-pendiente")
def informe_pedidos_pendiente(
    cliente_id: Optional[str] = None,
    oc: Optional[str] = None,
    db: Session = Depends(get_db),
):
    filas = _filas_informe_pendiente(db, cliente_id, oc)
    return {"columnas": COLUMNAS_PEDIDOS_PENDIENTE, "filas": filas}


@router.get("/pedidos-pendiente/export")
def informe_pedidos_pendiente_export(
    formato: str,
    cliente_id: Optional[str] = None,
    oc: Optional[str] = None,
    db: Session = Depends(get_db),
):
    filas = _filas_informe_pendiente(db, cliente_id, oc)
    try:
        return exportar(formato, "Pedidos con pendiente", COLUMNAS_PEDIDOS_PENDIENTE, filas)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Informe: cumplimiento de OC (Card #167, S882). Para cada renglón de un pedido con OC: lo pedido, lo entregado (remitos
# no anulados) y lo facturado (neto de NC, solo facturas AUTORIZADA_AFIP: backend/pedidos/cantidades.py), con lo que falta de cada
# lado y una SITUACIÓN. Las notas de débito no cuentan: ajustan importes, no cantidades (Card #154, dictamen Nike 05/10); si hay que
# entregar más, se modifica el pedido y se factura. Los pedidos anulados no entran. ---

COLUMNAS_CUMPLIMIENTO_OC = [
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "oc", "label": "OC", "width": 14},
    {"key": "pedido_id", "label": "Pedido", "width": 10},
    {"key": "circuito", "label": "Circuito", "width": 10},
    {"key": "estado", "label": "Estado", "width": 18},
    {"key": "fecha_pedido", "label": "Fecha", "width": 14},
    {"key": "renglon", "label": "Renglón", "width": 32},
    {"key": "pedido", "label": "Pedido (cant.)", "width": 13},
    {"key": "entregado", "label": "Entregado", "width": 12},
    {"key": "facturado", "label": "Facturado (neto NC)", "width": 17},
    {"key": "a_entregar", "label": "A entregar", "width": 12},
    {"key": "a_facturar", "label": "A facturar", "width": 12},
    {"key": "situacion", "label": "Situación", "width": 18},
]

SITUACIONES_CUMPLIMIENTO = ("SOBRE-FACTURADA", "SOBRE-ENTREGADA", "FALTA ENTREGAR", "FALTA FACTURAR", "CERRADA")


def _situacion_cumplimiento(pedido: float, entregado: float, facturado: Optional[float]) -> str:
    """CERRADA = entregado y facturado cubren lo pedido. `facturado` None = el pedido no se factura (circuito Rosa / no comercial):
    solo se mira la entrega. Prioridad: lo que está de más se muestra antes que lo que falta."""
    eps = 0.001
    if facturado is not None and facturado > pedido + eps:
        return "SOBRE-FACTURADA"
    if entregado > pedido + eps:
        return "SOBRE-ENTREGADA"
    if entregado < pedido - eps:
        return "FALTA ENTREGAR"
    if facturado is not None and facturado < pedido - eps:
        return "FALTA FACTURAR"
    return "CERRADA"


def _filas_cumplimiento_oc(db: Session, cliente_id: Optional[str], oc: Optional[str], solo_abiertas: bool):
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido, PedidoItem
    from backend.pedidos.cantidades import facturado_por_renglon
    from backend.pedidos.constants import PedidoFlags

    query = (
        db.query(PedidoItem)
        .join(Pedido, PedidoItem.pedido_id == Pedido.id)
        .filter(Pedido.estado != "ANULADO", Pedido.oc.isnot(None), Pedido.oc != "")
        .options(joinedload(PedidoItem.pedido).joinedload(Pedido.cliente), joinedload(PedidoItem.producto))
        .order_by(Pedido.id, PedidoItem.id)
    )
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
    if oc:
        query = query.filter(Pedido.oc.ilike(f"%{oc.strip()}%"))
    items = query.all()
    facturado = facturado_por_renglon(db, [i.id for i in items])      # {renglón: (facturada, acreditada)}, una sola consulta
    no_factura = int(PedidoFlags.NO_FISCAL_FORCE) | int(PedidoFlags.ES_NO_COMERCIAL)

    filas = []
    for item in items:
        pedido = item.pedido
        cliente = pedido.cliente if pedido else None
        producto = item.producto
        pedido_cant = item.cantidad or 0.0
        entregado = item.cantidad_entregada
        bruta, acreditada = facturado.get(item.id, (0.0, 0.0))
        neta = bruta - acreditada
        se_factura = not ((pedido.flags_estado or 0) & no_factura)
        filas.append({
            "pedido_id": pedido.id if pedido else None,
            "cliente": cliente.razon_social if cliente else None,
            "fecha_pedido": _fecha_corta(pedido.fecha) if pedido and pedido.fecha else None,
            "oc": pedido.oc if pedido else None,
            "renglon": producto.nombre if producto else (item.nota or "Ítem"),
            "pedido": pedido_cant,
            "entregado": entregado,
            "facturado": neta if se_factura else None,
            "a_entregar": max(pedido_cant - entregado, 0.0),
            "a_facturar": max(pedido_cant - neta, 0.0) if se_factura else None,
            "situacion": _situacion_cumplimiento(pedido_cant, entregado, neta if se_factura else None),
        })
    if solo_abiertas:
        filas = [f for f in filas if f["situacion"] != "CERRADA"]
    # un cliente a la vez, y dentro de él cada OC junta (por OC y número de pedido)
    filas.sort(key=lambda f: (normalizar_texto(f["cliente"] or ""), f["oc"] or "", f["pedido_id"] or 0))
    return _anotar_pedido(db, filas)


@router.get("/cumplimiento-oc")
def informe_cumplimiento_oc(
    cliente_id: Optional[str] = None,
    oc: Optional[str] = None,
    solo_abiertas: bool = False,
    db: Session = Depends(get_db),
):
    filas = _filas_cumplimiento_oc(db, cliente_id, oc, solo_abiertas)
    return {"columnas": COLUMNAS_CUMPLIMIENTO_OC, "filas": filas}


@router.get("/cumplimiento-oc/export")
def informe_cumplimiento_oc_export(
    formato: str,
    cliente_id: Optional[str] = None,
    oc: Optional[str] = None,
    solo_abiertas: bool = False,
    db: Session = Depends(get_db),
):
    filas = _filas_cumplimiento_oc(db, cliente_id, oc, solo_abiertas)
    try:
        return exportar(formato, "Cumplimiento de OC", COLUMNAS_CUMPLIMIENTO_OC, filas)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Informe C: pedidos con OC -- filtro directo Pedido.oc IS NOT NULL. No confundir con
# pedido_origen_id/motivo_relacion_oc (vínculo pedido->pedido del Circuito PR, otro campo). ---

COLUMNAS_PEDIDOS_OC = [
    {"key": "pedido_id", "label": "Pedido", "width": 10},
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "fecha_pedido", "label": "Fecha", "width": 14},
    {"key": "oc", "label": "OC", "width": 16},
    {"key": "circuito", "label": "Circuito", "width": 10},
    {"key": "estado", "label": "Estado", "width": 18},
    {"key": "total", "label": "Total", "width": 14},
]


def _filas_informe_oc(db: Session, cliente_id: Optional[str]):
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido

    query = (
        db.query(Pedido)
        .filter(Pedido.oc.isnot(None), Pedido.oc != "")
        .options(joinedload(Pedido.cliente))
        .order_by(Pedido.fecha.desc())
    )
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)

    filas = []
    for pedido in query.all():
        cliente = pedido.cliente
        filas.append({
            "pedido_id": pedido.id,
            "cliente": cliente.razon_social if cliente else None,
            "fecha_pedido": _fecha_corta(pedido.fecha) if pedido.fecha else None,
            "oc": pedido.oc,
            "total": pedido.total,
        })
    return _anotar_pedido(db, filas)


@router.get("/pedidos-oc")
def informe_pedidos_oc(cliente_id: Optional[str] = None, db: Session = Depends(get_db)):
    filas = _filas_informe_oc(db, cliente_id)
    return {"columnas": COLUMNAS_PEDIDOS_OC, "filas": filas}


@router.get("/pedidos-oc/export")
def informe_pedidos_oc_export(formato: str, cliente_id: Optional[str] = None, db: Session = Depends(get_db)):
    filas = _filas_informe_oc(db, cliente_id)
    try:
        return exportar(formato, "Pedidos con OC", COLUMNAS_PEDIDOS_OC, filas)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Informe D: pedidos con notas relevantes -- mismo informe que "remitos auditables"
# (Carlos, 27/09): la historia vive en Pedido.nota, no en RemitoNota. Una fila por fragmento
# (línea) que matchea, no por pedido -- un pedido puede aportar varias filas. ---

COLUMNAS_NOTAS_PEDIDO = [
    {"key": "pedido_id", "label": "Pedido", "width": 10},
    {"key": "circuito", "label": "Circuito", "width": 10},
    {"key": "estado", "label": "Estado", "width": 18},
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "fecha_pedido", "label": "Fecha Pedido", "width": 14},
    {"key": "categoria", "label": "Categoría", "width": 20},
    {"key": "fragmento", "label": "Fragmento", "width": 60},
]


@router.get("/notas-categorias")
def informe_notas_categorias():
    """Catálogo de categorías (las de sistema catalogadas + sistema sin catalogar + nota humana) para poblar los checkboxes
    combinables del filtro -- se lee del mismo módulo que clasifica, nunca se hardcodea en dos
    lugares."""
    return [{"key": k, "label": l} for k, l in CATEGORIAS_DISPONIBLES]


def _filas_informe_notas(db: Session, cliente_id: Optional[str], categorias: Optional[str]):
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido

    categorias_set = set(categorias.split(",")) if categorias else None

    query = db.query(Pedido).options(joinedload(Pedido.cliente))
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)

    filas = []
    for pedido in query.all():
        for frag in fragmentos_clasificados(pedido.nota):
            if categorias_set and frag["categoria"] not in categorias_set:
                continue
            cliente = pedido.cliente
            filas.append({
                "pedido_id": pedido.id,
                "cliente": cliente.razon_social if cliente else None,
                "fecha_pedido": _fecha_corta(pedido.fecha) if pedido.fecha else None,
                "categoria": dict(CATEGORIAS_DISPONIBLES).get(frag["categoria"], frag["categoria"]),
                "fragmento": frag["texto"],
            })
    return _anotar_pedido(db, filas)


@router.get("/notas-pedidos")
def informe_notas_pedidos(
    cliente_id: Optional[str] = None,
    categorias: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """`categorias`: lista separada por comas de claves (ver /notas-categorias). Vacío =
    todas -- el filtro combina (OR), no excluye (Carlos, 27/09: "un pedido puede tener más de
    una categoría a la vez")."""
    filas = _filas_informe_notas(db, cliente_id, categorias)
    return {"columnas": COLUMNAS_NOTAS_PEDIDO, "filas": filas}


@router.get("/notas-pedidos/export")
def informe_notas_pedidos_export(
    formato: str,
    cliente_id: Optional[str] = None,
    categorias: Optional[str] = None,
    db: Session = Depends(get_db),
):
    filas = _filas_informe_notas(db, cliente_id, categorias)
    try:
        return exportar(formato, "Pedidos con notas relevantes", COLUMNAS_NOTAS_PEDIDO, filas)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Informe E: buscar en notas -- coincidencia de subcadena sin acentos, cruzada contra el
# cliente del que depende la nota (Pedido.nota directo, o el pedido del remito para RemitoNota),
# no solo el texto literal. Caso real que lo exige (DISENO...§2.3.E): el Remito Mellizo de
# Rossini -- ninguna de sus dos notas menciona "Rossini" por nombre, solo el pedido 115. ---

COLUMNAS_BUSCAR_NOTAS = [
    {"key": "origen", "label": "Origen", "width": 10},
    {"key": "pedido_id", "label": "Pedido", "width": 10},
    {"key": "circuito", "label": "Circuito", "width": 10},
    {"key": "estado", "label": "Estado", "width": 18},
    {"key": "remito", "label": "Remito", "width": 16},
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "fragmento", "label": "Fragmento", "width": 60},
    {"key": "fecha", "label": "Fecha", "width": 16},
    {"key": "autor", "label": "Autor", "width": 16},
]


def _filas_buscar_notas(db: Session, q: Optional[str], excluir_sistema: bool):
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido
    from backend.remitos.models import Remito, RemitoNota

    termino = normalizar_texto(q)
    if not termino:
        return []

    filas = []

    # --- Fuente 1: Pedido.nota -- mismo split por linea que el Informe D, una fila por
    # fragmento que matchea (no el pedido entero). Sin fecha propia (a diferencia de RemitoNota,
    # no hay columna estructurada a ese nivel). ---
    for pedido in db.query(Pedido).options(joinedload(Pedido.cliente)).all():
        cliente = pedido.cliente
        nombre_cliente = cliente.razon_social if cliente else None
        hit_cliente = bool(nombre_cliente) and termino in normalizar_texto(nombre_cliente)
        for frag in fragmentos_clasificados(pedido.nota):
            if excluir_sistema and frag["categoria"] != "nota_humana":
                continue
            if termino not in normalizar_texto(frag["texto"]) and not hit_cliente:
                continue
            filas.append({
                "origen": "Pedido",
                "pedido_id": pedido.id,
                "remito": None,
                "cliente": nombre_cliente,
                "fragmento": frag["texto"],
                "fecha": None,
                "autor": None,
            })

    # --- Fuente 2: RemitoNota.texto -- ya estructurada (Etapa 5), una fila por nota entera,
    # no se separa por linea. Trae fecha real y autor si esta cargado. ---
    query_notas = db.query(RemitoNota).options(
        joinedload(RemitoNota.remito).joinedload(Remito.pedido).joinedload(Pedido.cliente),
        joinedload(RemitoNota.autor),
    )
    for nota in query_notas.all():
        remito = nota.remito
        pedido = remito.pedido if remito else None
        cliente = pedido.cliente if pedido else None
        nombre_cliente = cliente.razon_social if cliente else None
        texto = nota.texto or ""
        if excluir_sistema and texto.startswith(MARCADOR_SISTEMA):
            continue
        hit_cliente = bool(nombre_cliente) and termino in normalizar_texto(nombre_cliente)
        if termino not in normalizar_texto(texto) and not hit_cliente:
            continue
        filas.append({
            "origen": "Remito",
            "pedido_id": pedido.id if pedido else None,
            "remito": remito.numero_legal if remito else None,
            "cliente": nombre_cliente,
            "fragmento": texto,
            "fecha": _fecha_corta(nota.fecha) if nota.fecha else None,
            "autor": nota.autor_username,
        })

    filas.sort(key=lambda f: f["fecha"] or "", reverse=True)
    return _anotar_pedido(db, filas)


def _formato_linea_buscar_notas(fila):
    """Parrafo legible para el TXT -- especialmente util acá, hay muchos resultados
    posibles (DISENO...§2.2)."""
    encabezado = f"[{fila['origen']}"
    if fila.get("pedido_id"):
        encabezado += f" #{fila['pedido_id']}"
    if fila.get("remito"):
        encabezado += f" / Remito {fila['remito']}"
    encabezado += f"] {fila.get('cliente') or '(sin cliente)'}"
    if fila.get("fecha"):
        encabezado += f" -- {fila['fecha']}"
    pie = f" (autor: {fila['autor']})" if fila.get("autor") else ""
    return f"{encabezado}\n{fila.get('fragmento') or ''}{pie}"


@router.get("/buscar-notas")
def informe_buscar_notas(
    q: str = "",
    excluir_sistema: bool = False,
    db: Session = Depends(get_db),
):
    """Informe E -- busca `q` (sin distinguir acentos ni mayusculas) en el texto de la nota o en
    la razon social del cliente del que depende. `q` vacio devuelve sin filas, nunca el universo
    completo."""
    filas = _filas_buscar_notas(db, q, excluir_sistema)
    return {"columnas": COLUMNAS_BUSCAR_NOTAS, "filas": filas}


@router.get("/buscar-notas/export")
def informe_buscar_notas_export(
    formato: str,
    q: str = "",
    excluir_sistema: bool = False,
    db: Session = Depends(get_db),
):
    filas = _filas_buscar_notas(db, q, excluir_sistema)
    try:
        return exportar(
            formato, "Buscar en notas", COLUMNAS_BUSCAR_NOTAS, filas,
            formato_linea=_formato_linea_buscar_notas,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Informe F: pedidos SIN REMITO (prueba funcional 30/09). Hoja de revisión: en la copia de producción 54 de
# 103 pedidos no tienen ningún remito vigente, y no todos son lo mismo -- los Blancos y los Rosas se separan
# porque su respaldo es distinto (DISENO_CIRCUITO_PR_S869.md §1.7/§3): el Blanco tiene remito (PR impreso) y
# factura; el Rosa tiene un PR INTERNO que nunca se imprime ni se liga a una factura (quién, cuándo y qué
# cantidades, con PIN). Solo lectura: no crea remitos ni cambia estados. ---

COLUMNAS_SIN_REMITO = [
    {"key": "pedido_id", "label": "Pedido", "width": 9},
    {"key": "circuito", "label": "Circuito", "width": 10},
    {"key": "estado", "label": "Estado", "width": 14},
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "fecha_pedido", "label": "Fecha", "width": 12},
    {"key": "antiguedad", "label": "Días", "width": 7},
    {"key": "oc", "label": "OC", "width": 12},
    {"key": "renglones", "label": "Renglones", "width": 40},
    {"key": "total", "label": "Total", "width": 14},
    {"key": "comprobante", "label": "Comprobante vinculado", "width": 24},
    {"key": "factura_candidata", "label": "Factura de ARCA candidata", "width": 28},
    {"key": "observacion", "label": "Qué revisar", "width": 50},
]
# Solo en los archivos exportados: tres columnas en blanco para que Carlos marque a mano cada caso.
COLUMNAS_SIN_REMITO_EXPORT = COLUMNAS_SIN_REMITO + [
    {"key": "hoja_entrego", "label": "¿Se entregó? (S/N)", "width": 16},
    {"key": "hoja_accion", "label": "Acción (regularizar / anular / sigue pendiente)", "width": 30},
    {"key": "hoja_nota", "label": "Nota", "width": 30},
]
DIAS_PENDIENTE_VIEJO = 60
_PRIORIDAD_ESTADO = {"CUMPLIDO": 0, "PENDIENTE": 1, "ANULADO": 3}


def _solo_digitos(valor) -> str:
    return "".join(ch for ch in str(valor or "") if ch.isdigit())


def _facturas_arca_en_ingesta(db: Session) -> list:
    """Las facturas de ARCA que están guardadas como PDF en la ingesta (sin repetir), leídas del JSON que
    ya guardó el parser: CUIT, número, totales y en qué estado quedó su PDF. Sirve para sugerir, por CUIT y
    total, cuál podría ser la factura real de un pedido que no tiene remito."""
    from backend.ingesta.models import FacturasRaw

    vistas, salida = set(), []
    for raw in db.query(FacturasRaw).all():
        datos = raw.parsed_data_raw
        if not isinstance(datos, dict):
            continue
        f, cli = datos.get("factura") or {}, datos.get("cliente") or {}
        numero = f.get("numero")
        if not numero or numero in vistas:
            continue
        vistas.add(numero)
        salida.append({
            "numero": numero, "cuit": _solo_digitos(cli.get("cuit")),
            "neto": f.get("total_neto"), "total": f.get("total_final"), "estado": raw.audit_status,
        })
    return salida


def _candidata(pedido_total, cuit_cliente, facturas_arca: list) -> Optional[str]:
    cuit = _solo_digitos(cuit_cliente)
    if not cuit or not pedido_total:
        return None
    hallas = []
    for x in facturas_arca:
        if x["cuit"] != cuit:
            continue
        for ref in (x["total"], x["neto"]):
            if ref and abs(ref - pedido_total) <= max(1.0, 0.005 * pedido_total):
                hallas.append(f"{x['numero']} ({(x['estado'] or '').lower()})")
                break
    return "; ".join(hallas) or None


def _observacion_sin_remito(estado, circuito, dias, candidata) -> str:
    if estado == "ANULADO":
        return "Anulado: no necesita remito."
    rosa = circuito == "Rosa"
    if estado == "CUMPLIDO":
        # Sin afirmar cuál es el respaldo del circuito Rosa (remito 0015, ticket interno...): está en discusión.
        base = ("Figura cumplido pero no hay ninguna salida registrada: ¿se entregó? Si sí, regularizar con un PR retroactivo"
                + (" (circuito Rosa: sin factura)." if rosa else " y conciliar su factura real."))
        if candidata and not rosa:
            base += " Hay una factura de ARCA candidata en la ingesta."
        return base
    if estado == "PENDIENTE":
        if dias is not None and dias > DIAS_PENDIENTE_VIEJO:
            return f"Pendiente hace {dias} días sin ninguna salida: ¿se entregó, se anula o sigue de verdad?"
        return "Pendiente: todavía no se armó la salida (normal)."
    return "Revisar el estado del pedido."


def _filas_sin_remito(db: Session, circuito: str, estado: str, cliente_id: Optional[str], incluir_anulados: bool):
    from datetime import date
    from sqlalchemy import and_, exists
    from sqlalchemy.orm import joinedload
    from backend.clientes.models import Cliente  # noqa: F401  (relación Pedido.cliente)
    from backend.facturacion.models import Factura
    from backend.pedidos.models import Pedido, PedidoItem
    from backend.remitos.models import Remito

    query = (
        db.query(Pedido)
        .options(joinedload(Pedido.cliente), joinedload(Pedido.items).joinedload(PedidoItem.producto))
        .filter(~exists().where(and_(Remito.pedido_id == Pedido.id, Remito.estado != "ANULADO")))
    )
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
    if estado != "todos":
        query = query.filter(Pedido.estado == estado)
    elif not incluir_anulados:
        query = query.filter(Pedido.estado != "ANULADO")
    pedidos = query.all()

    comprobantes: dict = {}
    if pedidos:
        # facturas.pedido_id está declarada CHAR(32) en el esquema heredado (D y P) y guarda el número como TEXTO
        # ('63'), aunque el modelo diga Integer: por eso las claves se comparan como texto en los dos lados.
        for f in db.query(Factura).filter(Factura.pedido_id.in_([p.id for p in pedidos])).all():
            comprobantes.setdefault(str(f.pedido_id), []).append(f"{f.tipo_comprobante} {f.estado}")
    arca = _facturas_arca_en_ingesta(db)
    hoy = date.today()

    filas = []
    for p in pedidos:
        dias = (hoy - p.fecha.date()).days if p.fecha else None
        renglones = [f"{i.cantidad:g} x {i.producto.nombre if i.producto else (i.nota or 'Ítem')}" for i in p.items]
        resumen = "; ".join(renglones[:3]) + (f" (+{len(renglones) - 3} más)" if len(renglones) > 3 else "")
        filas.append({
            "pedido_id": p.id,
            "cliente": p.cliente.razon_social if p.cliente else None,
            "fecha_pedido": _fecha_corta(p.fecha),
            "antiguedad": dias,
            "oc": p.oc,
            "renglones": resumen or "(sin renglones)",
            "total": p.total,
            "comprobante": ", ".join(comprobantes.get(str(p.id), [])) or "(ninguno)",
            "factura_candidata": _candidata(p.total, p.cliente.cuit if p.cliente else None, arca),
        })
    _anotar_pedido(db, filas)
    for f in filas:
        f["observacion"] = _observacion_sin_remito(f["estado_base"], f["circuito"], f["antiguedad"], f["factura_candidata"])
    if circuito != "todos":
        filas = [f for f in filas if (f["circuito"] or "").lower() == circuito]
    # Orden de revisión: Blancos y después Rosas; dentro de cada uno, primero lo incoherente (CUMPLIDO sin salida),
    # después los PENDIENTES, y en cada grupo los más viejos primero.
    filas.sort(key=lambda f: (
        0 if f["circuito"] == "Blanco" else 1,
        _PRIORIDAD_ESTADO.get(f["estado_base"], 2),
        f["fecha_pedido"] or "",
        f["pedido_id"],
    ))
    return filas


def _resumen_sin_remito(filas: list) -> dict:
    por = {}
    for f in filas:
        clave = (f["circuito"], f["estado_base"])
        por[clave] = por.get(clave, 0) + 1
    return {
        "total": len(filas),
        "blanco": sum(1 for f in filas if f["circuito"] == "Blanco"),
        "rosa": sum(1 for f in filas if f["circuito"] == "Rosa"),
        "cumplido_sin_salida": sum(1 for f in filas if f["estado_base"] == "CUMPLIDO"),
        "con_factura_candidata": sum(1 for f in filas if f["factura_candidata"]),
        "detalle": [{"circuito": c, "estado": e, "cantidad": n} for (c, e), n in sorted(por.items())],
    }


def _filtros_sin_remito(
    circuito: str = "todos",
    estado: str = "todos",
    cliente_id: Optional[str] = None,
    incluir_anulados: bool = False,
) -> dict:
    if circuito not in CIRCUITOS:
        raise HTTPException(status_code=400, detail=f"circuito inválido: {circuito!r} (todos | blanco | rosa)")
    estado = "todos" if (estado or "todos").lower() == "todos" else estado.upper()
    return dict(circuito=circuito, estado=estado, cliente_id=cliente_id, incluir_anulados=incluir_anulados)


@router.get("/pedidos-sin-remito")
def informe_pedidos_sin_remito(filtros: dict = Depends(_filtros_sin_remito), db: Session = Depends(get_db)):
    filas = _filas_sin_remito(db, **filtros)
    return {"columnas": COLUMNAS_SIN_REMITO, "filas": filas, "resumen": _resumen_sin_remito(filas)}


@router.get("/pedidos-sin-remito/export")
def informe_pedidos_sin_remito_export(formato: str, filtros: dict = Depends(_filtros_sin_remito), db: Session = Depends(get_db)):
    filas = _filas_sin_remito(db, **filtros)
    partes = ["Hoja de revisión: marcar en las tres últimas columnas si se entregó y qué hacer con cada pedido"]
    if filtros["circuito"] != "todos":
        partes.append(f"Circuito: {filtros['circuito'].capitalize()}")
    if filtros["estado"] != "todos":
        partes.append(f"Estado: {filtros['estado']}")
    elif filtros["incluir_anulados"]:
        partes.append("incluye anulados")
    try:
        return exportar(formato, "Pedidos sin remito", COLUMNAS_SIN_REMITO_EXPORT, filas, subtitulo=" | ".join(partes))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Informe G: renglones que salieron SIN SER VENTA FIRME (S876) -- consignación, muestra sin cargo, garantía /
# reemplazo. Es la alerta contra el riesgo "Consignación Eterna" que pidió Nike: mercadería a prueba que sale y
# se olvida sin resolver. Un renglón está ABIERTO mientras conserva su motivo_no_facturable y sigue afuera (lo
# entregado neto del renglón del pedido es mayor que cero: si volvió con una devolución, deja de figurar).
# Se cierra facturándolo (botón Facturar del remito) o devolviéndolo. A los 30 días se marca en alerta. Solo
# lectura. ---

COLUMNAS_NO_FACTURABLES = [
    {"key": "pedido_id", "label": "Pedido", "width": 9},
    {"key": "circuito", "label": "Circuito", "width": 10},
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "producto", "label": "Producto", "width": 34},
    {"key": "cantidad", "label": "Cantidad", "width": 10},
    {"key": "motivo", "label": "Motivo", "width": 20},
    {"key": "remito", "label": "Remito", "width": 16},
    {"key": "entrega", "label": "Entrega", "width": 16},
    {"key": "desde", "label": "Desde", "width": 12},
    {"key": "antiguedad", "label": "Días", "width": 7},
    {"key": "alerta", "label": "Alerta", "width": 26},
]
_ETIQUETA_MOTIVO = {
    "CONSIGNACION": "Consignación",
    "MUESTRA_SIN_CARGO": "Muestra sin cargo",
    "GARANTIA_REEMPLAZO": "Garantía / reemplazo",
}
_ETIQUETA_METODO = {
    "MOSTRADOR": "Mostrador",
    "FLETE_TERCERO": "Flete tercero",
    "TRANSPORTE_PROPIO": "Transporte propio",
    "MOTO_CADETERIA": "Moto / cadetería",
    "REMITO_EXTERNO": "Remito externo",
}


def _filas_no_facturables(db: Session, motivo: str, solo_alerta: bool, cliente_id: Optional[str]):
    from datetime import date
    from sqlalchemy.orm import joinedload
    from backend.clientes.models import Cliente  # noqa: F401  (relación Pedido.cliente)
    from backend.pedidos.models import Pedido, PedidoItem
    from backend.remitos.constants import DIAS_ALERTA_NO_FACTURABLE
    from backend.remitos.models import Remito, RemitoItem

    query = (
        db.query(RemitoItem)
        .join(Remito, RemitoItem.remito_id == Remito.id)
        .options(
            joinedload(RemitoItem.remito).joinedload(Remito.pedido).joinedload(Pedido.cliente),
            joinedload(RemitoItem.pedido_item).joinedload(PedidoItem.producto),
        )
        .filter(RemitoItem.motivo_no_facturable.isnot(None), Remito.estado != "ANULADO")
    )
    if motivo != "todos":
        query = query.filter(RemitoItem.motivo_no_facturable == motivo)
    hoy = date.today()
    filas = []
    for ri in query.all():
        remito, pi = ri.remito, ri.pedido_item
        pedido = remito.pedido if remito else None
        if cliente_id and (not pedido or str(pedido.cliente_id).replace("-", "") != str(cliente_id).replace("-", "")):
            continue
        # Abierto: sigue afuera. Una devolución (PR de cantidad negativa) sobre el mismo renglón del pedido baja
        # lo entregado neto; si llegó a cero, la mercadería volvió y ya no hay nada que resolver.
        if (ri.cantidad_remitida or 0) <= 0 or pi is None or (pi.cantidad_entregada or 0) <= 0.001:
            continue
        desde = remito.fecha_salida or remito.fecha_creacion
        dias = (hoy - desde.date()).days if desde else None
        en_alerta = dias is not None and dias >= DIAS_ALERTA_NO_FACTURABLE
        if solo_alerta and not en_alerta:
            continue
        filas.append({
            "remito_item_id": ri.id,
            "pedido_id": remito.pedido_id,
            "cliente": pedido.cliente.razon_social if pedido and pedido.cliente else None,
            "producto": pi.producto.nombre if pi.producto else (pi.nota or "Ítem"),
            "cantidad": ri.cantidad_remitida,
            "motivo_base": ri.motivo_no_facturable,
            "motivo": _ETIQUETA_MOTIVO.get(ri.motivo_no_facturable, ri.motivo_no_facturable),
            "remito": remito.numero_legal or "(sin número)",
            "entrega": _ETIQUETA_METODO.get(remito.metodo_entrega, "-") if remito.metodo_entrega else "-",
            "desde": _fecha_corta(desde),
            "antiguedad": dias,
            "en_alerta": en_alerta,
            "alerta": f"ALERTA: {dias} días sin resolver" if en_alerta else "",
        })
    _anotar_pedido(db, filas)
    filas.sort(key=lambda f: (-(f["antiguedad"] if f["antiguedad"] is not None else -1), f["pedido_id"], f["remito_item_id"]))
    return filas


def _resumen_no_facturables(filas: list) -> dict:
    por = {}
    for f in filas:
        por[f["motivo_base"]] = por.get(f["motivo_base"], 0) + 1
    return {
        "total": len(filas),
        "en_alerta": sum(1 for f in filas if f["en_alerta"]),
        "por_motivo": [{"motivo": _ETIQUETA_MOTIVO.get(m, m), "cantidad": n} for m, n in sorted(por.items())],
    }


def _filtros_no_facturables(motivo: str = "todos", solo_alerta: bool = False, cliente_id: Optional[str] = None) -> dict:
    from backend.remitos.constants import MOTIVOS_NO_FACTURABLE
    motivo = "todos" if (motivo or "todos").lower() == "todos" else motivo.upper()
    if motivo != "todos" and motivo not in MOTIVOS_NO_FACTURABLE:
        raise HTTPException(status_code=400, detail=f"motivo inválido: {motivo!r} (todos | {' | '.join(MOTIVOS_NO_FACTURABLE)})")
    return dict(motivo=motivo, solo_alerta=solo_alerta, cliente_id=cliente_id)


@router.get("/renglones-no-facturables")
def informe_renglones_no_facturables(filtros: dict = Depends(_filtros_no_facturables), db: Session = Depends(get_db)):
    filas = _filas_no_facturables(db, **filtros)
    return {"columnas": COLUMNAS_NO_FACTURABLES, "filas": filas, "resumen": _resumen_no_facturables(filas)}


@router.get("/renglones-no-facturables/export")
def informe_renglones_no_facturables_export(formato: str, filtros: dict = Depends(_filtros_no_facturables), db: Session = Depends(get_db)):
    from backend.remitos.constants import DIAS_ALERTA_NO_FACTURABLE
    filas = _filas_no_facturables(db, **filtros)
    partes = [f"Renglones que salieron sin ser venta firme y siguen abiertos (alerta a los {DIAS_ALERTA_NO_FACTURABLE} días)"]
    if filtros["motivo"] != "todos":
        partes.append(f"Motivo: {_ETIQUETA_MOTIVO.get(filtros['motivo'], filtros['motivo'])}")
    if filtros["solo_alerta"]:
        partes.append("solo en alerta")
    try:
        return exportar(formato, "Renglones sin venta firme", COLUMNAS_NO_FACTURABLES, filas, subtitulo=" | ".join(partes))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Nivel 2, ABC de clientes -- retoma el pedido del 13/09 (ANALISIS_MODULO_ESTADISTICAS_
# S864.md), ahora con piso real (cantidad_entregada confiable). "Venta" en $ neto, por las dos
# medidas que Carlos eligio (2026-09-28): entregado y facturado, por separado -- Rosa nunca
# factura por diseno, mezclar las dos en una sola columna la dejaria siempre en 0. Cortes
# estandar 80/95% (S864 §5 Q3). ---

COLUMNAS_ABC_CLIENTES = [
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "neto_entregado", "label": "$ Entregado (neto)", "width": 16},
    {"key": "clase_entregado", "label": "Clase (entregado)", "width": 10},
    {"key": "pct_acum_entregado", "label": "% acum. entregado", "width": 12},
    {"key": "neto_facturado", "label": "$ Facturado (neto, AFIP)", "width": 18},
    {"key": "clase_facturado", "label": "Clase (facturado)", "width": 10},
    {"key": "pct_acum_facturado", "label": "% acum. facturado", "width": 12},
]


def _clasificar_abc(valores_por_id: dict) -> dict:
    """Clase A/B/C por corte estandar de % acumulado (80/95), orden descendente por monto
    (S864 §5 Q3, §7.3). Devuelve {id: (clase, pct_acumulado)}."""
    total = sum(valores_por_id.values())
    resultado = {}
    acumulado = 0.0
    for id_, monto in sorted(valores_por_id.items(), key=lambda kv: kv[1], reverse=True):
        acumulado += monto
        pct = (acumulado / total * 100) if total else 0.0
        clase = "A" if pct <= 80 else ("B" if pct <= 95 else "C")
        resultado[id_] = (clase, round(pct, 1))
    return resultado


def _filas_abc_clientes(db: Session):
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido, PedidoItem
    from backend.facturacion.models import Factura
    from backend.clientes.models import Cliente

    # --- Entregado: subtotal de linea (ya neto, con descuento de renglon) prorrateado por lo
    # efectivamente entregado -- mismo dato que ya usa el Informe B (cantidad_entregada), no
    # se inventa un precio nuevo. ---
    entregado_por_cliente: dict = {}
    items = (
        db.query(PedidoItem)
        .join(Pedido, PedidoItem.pedido_id == Pedido.id)
        .filter(Pedido.estado != "ANULADO")
        .options(joinedload(PedidoItem.pedido))
        .all()
    )
    for item in items:
        pedido = item.pedido
        if not pedido or not item.cantidad:
            continue
        neto_item = (item.subtotal / item.cantidad) * item.cantidad_entregada
        entregado_por_cliente[pedido.cliente_id] = entregado_por_cliente.get(pedido.cliente_id, 0.0) + neto_item

    # --- Facturado: solo AUTORIZADA_AFIP -- BORRADOR/PRESUPUESTO_X no son un hecho fiscal real
    # (S864 §2.5). Neto = gravado + exento, nunca el total con IVA (S864 §2.4). ---
    facturado_por_cliente: dict = {}
    for factura in db.query(Factura).filter(Factura.estado == "AUTORIZADA_AFIP").all():
        neto = (factura.neto_gravado or 0.0) + (factura.exento or 0.0)
        facturado_por_cliente[factura.cliente_id] = facturado_por_cliente.get(factura.cliente_id, 0.0) + neto

    clases_entregado = _clasificar_abc(entregado_por_cliente)
    clases_facturado = _clasificar_abc(facturado_por_cliente)

    todos_ids = set(entregado_por_cliente) | set(facturado_por_cliente)
    clientes = {c.id: c.razon_social for c in db.query(Cliente).filter(Cliente.id.in_(todos_ids)).all()} if todos_ids else {}

    filas = []
    for cid in todos_ids:
        clase_e, pct_e = clases_entregado.get(cid, ("C", 0.0))
        clase_f, pct_f = clases_facturado.get(cid, ("C", 0.0))
        filas.append({
            "cliente": clientes.get(cid, "(desconocido)"),
            "neto_entregado": round(entregado_por_cliente.get(cid, 0.0), 2),
            "clase_entregado": clase_e,
            "pct_acum_entregado": pct_e,
            "neto_facturado": round(facturado_por_cliente.get(cid, 0.0), 2),
            "clase_facturado": clase_f,
            "pct_acum_facturado": pct_f,
        })
    filas.sort(key=lambda f: f["neto_entregado"], reverse=True)
    return filas


@router.get("/abc-clientes")
def informe_abc_clientes(db: Session = Depends(get_db)):
    """Nivel 2 -- ranking de clientes por $ neto, en dos medidas independientes (entregado y
    facturado). Un cliente Rosa aparece con $ facturado en 0 y clase C ahi -- correcto, no un
    error: Rosa no factura por diseno (paga primero, recibe despues)."""
    filas = _filas_abc_clientes(db)
    return {"columnas": COLUMNAS_ABC_CLIENTES, "filas": filas}


@router.get("/abc-clientes/export")
def informe_abc_clientes_export(formato: str, db: Session = Depends(get_db)):
    filas = _filas_abc_clientes(db)
    try:
        return exportar(formato, "ABC de clientes", COLUMNAS_ABC_CLIENTES, filas)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Nivel 2, ABC de productos -- retoma S864 §7.4: dos rankings por CANTIDAD DISTINTA, no por
# $ (a diferencia del ABC de clientes de arriba). "Compra" = pedido firme, mismo criterio que ya
# usa el resto de este router (Pedido.estado != ANULADO) -- no depende de si se entrego o
# facturo, porque acá no se suma plata, se cuentan relaciones. ---

COLUMNAS_ABC_PRODUCTOS_POR_PRODUCTO = [
    {"key": "producto", "label": "Producto", "width": 30},
    {"key": "clientes_distintos", "label": "Clientes distintos", "width": 14},
    {"key": "clientes", "label": "Clientes", "width": 60},
]

COLUMNAS_ABC_PRODUCTOS_POR_CLIENTE = [
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "productos_distintos", "label": "Productos distintos", "width": 14},
    {"key": "productos", "label": "Productos", "width": 60},
]


def _pares_producto_cliente(db: Session):
    from backend.pedidos.models import Pedido, PedidoItem

    return (
        db.query(PedidoItem.producto_id, Pedido.cliente_id)
        .join(Pedido, PedidoItem.pedido_id == Pedido.id)
        .filter(Pedido.estado != "ANULADO", PedidoItem.producto_id.isnot(None))
        .distinct()
        .all()
    )


def _filas_abc_productos(db: Session, vista: str):
    from backend.productos.models import Producto
    from backend.clientes.models import Cliente

    pares = _pares_producto_cliente(db)
    productos = {p.id: p.nombre for p in db.query(Producto).all()}
    clientes = {c.id: c.razon_social for c in db.query(Cliente).all()}

    if vista == "cliente":
        por_cliente: dict = {}
        for producto_id, cliente_id in pares:
            por_cliente.setdefault(cliente_id, set()).add(producto_id)
        filas = [
            {
                "cliente": clientes.get(cid, "(desconocido)"),
                "productos_distintos": len(prods),
                "productos": ", ".join(sorted(productos.get(pid, "(desconocido)") for pid in prods)),
            }
            for cid, prods in por_cliente.items()
        ]
        filas.sort(key=lambda f: f["productos_distintos"], reverse=True)
        return filas

    por_producto: dict = {}
    for producto_id, cliente_id in pares:
        por_producto.setdefault(producto_id, set()).add(cliente_id)
    filas = [
        {
            "producto": productos.get(pid, "(desconocido)"),
            "clientes_distintos": len(clis),
            "clientes": ", ".join(sorted(clientes.get(cid, "(desconocido)") for cid in clis)),
        }
        for pid, clis in por_producto.items()
    ]
    filas.sort(key=lambda f: f["clientes_distintos"], reverse=True)
    return filas


@router.get("/abc-productos")
def informe_abc_productos(vista: str = "producto", db: Session = Depends(get_db)):
    """Nivel 2 -- S864 §7.4: 'producto' (a cuantos clientes distintos se les vendio cada
    producto) o 'cliente' (cuantos productos distintos compra cada cliente). 'Compra' = pedido
    firme, igual criterio que el resto del router (Pedido.estado != ANULADO)."""
    columnas = COLUMNAS_ABC_PRODUCTOS_POR_CLIENTE if vista == "cliente" else COLUMNAS_ABC_PRODUCTOS_POR_PRODUCTO
    filas = _filas_abc_productos(db, vista)
    return {"columnas": columnas, "filas": filas}


@router.get("/abc-productos/export")
def informe_abc_productos_export(formato: str, vista: str = "producto", db: Session = Depends(get_db)):
    columnas = COLUMNAS_ABC_PRODUCTOS_POR_CLIENTE if vista == "cliente" else COLUMNAS_ABC_PRODUCTOS_POR_PRODUCTO
    filas = _filas_abc_productos(db, vista)
    titulo = "ABC de productos (por cliente)" if vista == "cliente" else "ABC de productos (por producto)"
    try:
        return exportar(formato, titulo, columnas, filas)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
