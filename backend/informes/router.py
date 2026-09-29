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
