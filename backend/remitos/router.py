# backend/remitos/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.core.database import get_db
from backend.remitos import models, schemas
from backend.pedidos.models import Pedido, PedidoItem
from backend.productos.models import Producto

router = APIRouter(
    prefix="/remitos",
    tags=["Logística Táctica (Remitos)"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.RemitoResponse, status_code=status.HTTP_201_CREATED)
def create_remito(remito: schemas.RemitoCreate, db: Session = Depends(get_db)):
    """
    Crea una cabecera de Remito para un Pedido existente.
    """
    # 1. Validar Pedido
    pedido = db.query(Pedido).get(remito.pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    # 2. Gatekeeper Financiero (Inheritance Logic)
    # Si el pedido tiene semáforo ROJO o AMARILLO, el remito nace bloqueado?
    # Por defecto, hereda False (Borrador).
    aprobado = remito.aprobado_para_despacho
    
    # 3. Crear Header
    nuevo_remito = models.Remito(
        pedido_id=remito.pedido_id,
        domicilio_entrega_id=remito.domicilio_entrega_id,
        transporte_id=remito.transporte_id,
        estado="BORRADOR",
        aprobado_para_despacho=aprobado,
        numero_legal=remito.numero_legal
    )
    db.add(nuevo_remito)
    db.flush()
    
    # 4. Crear Items
    for item in remito.items:
        # Validar trazabilidad
        p_item = db.query(PedidoItem).get(item.pedido_item_id)
        if not p_item or p_item.pedido_id != pedido.id:
            raise HTTPException(status_code=400, detail=f"Item de pedido {item.pedido_item_id} inválido para este pedido")
            
        r_item = models.RemitoItem(
            remito_id=nuevo_remito.id,
            pedido_item_id=item.pedido_item_id,
            cantidad=item.cantidad
        )
        db.add(r_item)
        
    db.commit()
    db.refresh(nuevo_remito)
    return nuevo_remito

@router.post("/{remito_id}/despachar")
def despachar_remito(remito_id: str, db: Session = Depends(get_db)):
    """
    ACCIÓN FÍSICA: Cambia estado a EN_CAMINO y descuenta STOCK FÍSICO.
    """
    remito = db.query(models.Remito).get(remito_id)
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
        
    if not remito.aprobado_para_despacho:
         raise HTTPException(status_code=403, detail="Remito BLOQUEADO por Gatekeeper Financiero")
         
    if remito.estado == "EN_CAMINO":
        raise HTTPException(status_code=400, detail="Remito ya despachado")
        
    # MOVER STOCK
    for item in remito.items:
        producto = item.pedido_item.producto
        # Lógica: Stock Físico baja, Stock Reservado baja (porque ya se cumplió la reserva)
        producto.stock_fisico -= item.cantidad
        producto.stock_reservado -= item.cantidad
        
    remito.estado = "EN_CAMINO"
    from datetime import datetime
    remito.fecha_salida = datetime.now()
    
    db.commit()
    db.commit()
    return {"status": "Despachado", "remito_id": remito_id}

@router.get("/por_pedido/{pedido_id}", response_model=List[schemas.RemitoResponse])
def get_remitos_by_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todos los remitos asociados a un pedido.
    """
    remitos = db.query(models.Remito).filter(models.Remito.pedido_id == pedido_id).all()
    return remitos

@router.post("/{remito_id}/items", response_model=schemas.RemitoItemResponse)
def add_item_to_remito(
    remito_id: str, 
    item_data: schemas.RemitoItemCreate,
    db: Session = Depends(get_db)
):
    """
    Agrega un ítem (o suma cantidad) a un remito BORRADOR.
    """
    remito = db.query(models.Remito).get(remito_id)
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
        
    if remito.estado != "BORRADOR":
        raise HTTPException(status_code=400, detail="Solo se pueden modificar remitos en BORRADOR")
        
    # Validar que el item pertenece al pedido original
    p_item = db.query(PedidoItem).get(item_data.pedido_item_id)
    if not p_item or p_item.pedido_id != remito.pedido_id:
        raise HTTPException(status_code=400, detail="El ítem no pertenece al pedido de este remito")
        
    # Buscar si ya existe el item en el remito para sumar
    existing_item = db.query(models.RemitoItem).filter(
        models.RemitoItem.remito_id == remito_id,
        models.RemitoItem.pedido_item_id == item_data.pedido_item_id
    ).first()
    
    if existing_item:
        existing_item.cantidad += item_data.cantidad
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        new_item = models.RemitoItem(
            remito_id=remito_id,
            pedido_item_id=item_data.pedido_item_id,
            cantidad=item_data.cantidad
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
