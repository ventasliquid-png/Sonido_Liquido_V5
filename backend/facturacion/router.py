# backend/facturacion/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from backend.core.database import get_db
from backend.facturacion import schemas, service, models

router = APIRouter(
    prefix="/facturacion",
    tags=["Facturación (Asistente ARCA)"],
    responses={404: {"description": "Not found"}},
)

@router.post("/borrador/pedido/{pedido_id}", response_model=schemas.FacturaResponse, status_code=status.HTTP_201_CREATED)
def crear_borrador_desde_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Paso 1 del Asistente: Crea la estructura fiscal (Draft) basada en un Pedido operativo.
    """
    return service.FacturacionService.create_draft_from_pedido(db, pedido_id)

@router.get("/{factura_id}", response_model=schemas.FacturaResponse)
def leer_factura(factura_id: str, db: Session = Depends(get_db)):
    """
    Recupera el borrador o factura final para renderizar el "Modo Espejo AFIP" en el frontend.
    """
    return service.FacturacionService.get_factura(db, factura_id)

@router.patch("/{factura_id}/sellar", response_model=schemas.FacturaResponse)
def sellar_factura(factura_id: str, payload: schemas.FacturaUpdate, db: Session = Depends(get_db)):
    """
    Paso 3 del Asistente: El usuario pegó el CAE de la página de AFIP, sellando nuestro registro.
    """
    return service.FacturacionService.sellar_factura(db, factura_id, payload)

@router.patch("/{factura_id}/anular", response_model=schemas.FacturaResponse)
def anular_factura(factura_id: str, payload: schemas.FacturaAnularPayload, db: Session = Depends(get_db)):
    """
    [T4, S868] Anula una factura ya sellada/liquidada ("hacéme NC y te lo pago en negro", error de
    carga). Requiere nota forense. El/los remito(s) vinculados quedan marcados con la cicatriz
    REMITO_DESFACTURADO (Bit 41) y dejan de mostrar la referencia a esta factura -- sin borrar el
    vínculo, que queda como registro histórico.
    """
    return service.FacturacionService.anular_factura(db, factura_id, payload)

@router.get("/", response_model=List[schemas.FacturaResponse])
def listar_facturas(
    limit: int = 50, 
    offset: int = 0, 
    db: Session = Depends(get_db)
):
    """
    Directorio de Facturas emitidas o pendientes.
    """
    facturas = (
        db.query(models.Factura)
        .order_by(desc(models.Factura.created_at))
        .limit(limit)
        .offset(offset)
        .all()
    )
    return facturas
