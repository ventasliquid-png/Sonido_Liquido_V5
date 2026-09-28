# backend/informes/router.py
"""
[S875, DISENO_MODULO_INFORMES_S875_2026-09-26.md] Módulo Informes -- Nivel 1 (Listados).
Capa de consulta, solo lectura -- no escribe RemitoNota ni cantidad_recibida.
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

COLUMNAS_REMITOS = [
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "oc", "label": "OC", "width": 14},
    {"key": "pedido_id", "label": "Pedido", "width": 10},
    {"key": "fecha_pedido", "label": "Fecha Pedido", "width": 14},
    {"key": "producto", "label": "Producto", "width": 30},
    {"key": "cantidad_pedida", "label": "Cant. Pedida", "width": 12},
    {"key": "remito", "label": "Remito", "width": 16},
    {"key": "fecha_documento", "label": "Fecha Remito", "width": 14},
    {"key": "cantidad_remitida", "label": "Cant. Remitida", "width": 14},
    {"key": "factura", "label": "Factura", "width": 16},
]


def _filas_informe_remitos(
    db: Session,
    cliente_id: Optional[str],
    desde: Optional[datetime],
    hasta: Optional[datetime],
    producto_id: Optional[int],
    oc: Optional[str],
    incluir_anulados: bool,
):
    from backend.remitos.service import RemitosService

    resultado = RemitosService.get_entregas(
        db,
        cliente_id=cliente_id,
        desde=desde,
        hasta=hasta,
        producto_id=producto_id,
        oc=oc,
        incluir_anulados=incluir_anulados,
    )
    return resultado["filas"]


@router.get("/remitos")
def informe_remitos(
    cliente_id: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    producto_id: Optional[int] = None,
    oc: Optional[str] = None,
    incluir_anulados: bool = False,
    db: Session = Depends(get_db),
):
    """Informe A -- tabla plana para pantalla. Mismos filtros/datos que
    GET /remitos/entregas (EntregasView.vue la usa como árbol; acá es la vista
    listado, pensada para exportar)."""
    filas = _filas_informe_remitos(db, cliente_id, desde, hasta, producto_id, oc, incluir_anulados)
    return {"columnas": COLUMNAS_REMITOS, "filas": filas}


@router.get("/remitos/export")
def informe_remitos_export(
    formato: str,
    cliente_id: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    producto_id: Optional[int] = None,
    oc: Optional[str] = None,
    incluir_anulados: bool = False,
    db: Session = Depends(get_db),
):
    """Recalcula server-side con los mismos filtros -- nunca confía en filas que
    mande el cliente, para que el archivo exportado sea siempre una consulta
    fresca, no lo que quedó pintado en pantalla."""
    filas = _filas_informe_remitos(db, cliente_id, desde, hasta, producto_id, oc, incluir_anulados)
    try:
        return exportar(formato, "Remitos por fecha o cliente", COLUMNAS_REMITOS, filas)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Informe B: pedidos con pendiente -- resta calculada (PedidoItem.cantidad_entregada,
# @property), nunca los Bits 20/21 (Etapa 2 del Circuito PR: todo lector pasa a la resta). ---

COLUMNAS_PEDIDOS_PENDIENTE = [
    {"key": "pedido_id", "label": "Pedido", "width": 10},
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
            "fecha_pedido": pedido.fecha.isoformat() if pedido and pedido.fecha else None,
            "oc": pedido.oc if pedido else None,
            "renglon": producto.nombre if producto else (item.nota or "Ítem"),
            "declarado": item.cantidad,
            "entregado": entregado,
            "pendiente": pendiente,
        })
    return filas


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


# --- Informe C: pedidos con OC -- filtro directo Pedido.oc IS NOT NULL. No confundir con
# pedido_origen_id/motivo_relacion_oc (vínculo pedido->pedido del Circuito PR, otro campo). ---

COLUMNAS_PEDIDOS_OC = [
    {"key": "pedido_id", "label": "Pedido", "width": 10},
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "fecha_pedido", "label": "Fecha", "width": 14},
    {"key": "oc", "label": "OC", "width": 16},
    {"key": "estado", "label": "Estado", "width": 14},
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
            "fecha_pedido": pedido.fecha.isoformat() if pedido.fecha else None,
            "oc": pedido.oc,
            "estado": pedido.estado,
            "total": pedido.total,
        })
    return filas


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
    {"key": "cliente", "label": "Cliente", "width": 30},
    {"key": "fecha_pedido", "label": "Fecha Pedido", "width": 14},
    {"key": "categoria", "label": "Categoría", "width": 20},
    {"key": "fragmento", "label": "Fragmento", "width": 60},
]


@router.get("/notas-categorias")
def informe_notas_categorias():
    """Catálogo de las 7 categorías (6 de sistema + nota humana) para poblar los checkboxes
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
                "fecha_pedido": pedido.fecha.isoformat() if pedido.fecha else None,
                "categoria": dict(CATEGORIAS_DISPONIBLES).get(frag["categoria"], frag["categoria"]),
                "fragmento": frag["texto"],
            })
    return filas


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
            "fecha": nota.fecha.isoformat() if nota.fecha else None,
            "autor": nota.autor_username,
        })

    filas.sort(key=lambda f: f["fecha"] or "", reverse=True)
    return filas


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
