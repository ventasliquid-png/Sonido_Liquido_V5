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
from backend.informes.export_utils import exportar

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
