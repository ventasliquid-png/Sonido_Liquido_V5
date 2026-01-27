from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from backend.clientes.schemas import ClienteCreate, ClienteResponse, ClienteUpdate
from backend.clientes import schemas
from backend.clientes.service import ClienteService
from backend.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    responses={404: {"description": "Not found"}},
)

@router.get("/check-cuit/{cuit}", response_model=schemas.CuitCheckResponse)
def check_cuit(cuit: str, exclude_id: UUID = None, db: Session = Depends(get_db)):
    return ClienteService.check_cuit(db, cuit, exclude_id)

@router.get("/{cliente_id}/transportes-habituales")
def get_transportes_habituales(cliente_id: UUID, db: Session = Depends(get_db)):
    return ClienteService.get_transportes_habituales(db, cliente_id)

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    return ClienteService.create_cliente(db, cliente)

@router.get("/", response_model=List[schemas.ClienteListResponse])
def read_clientes(skip: int = 0, limit: int = 1000, q: str = None, include_inactive: bool = False, db: Session = Depends(get_db)):
    return ClienteService.get_clientes(db, skip=skip, limit=limit, q=q, include_inactive=include_inactive)

@router.get("/top", response_model=List[ClienteResponse])
def get_top_clients(limit: int = 8, db: Session = Depends(get_db)):
    return ClienteService.get_top_clients(db, limit=limit)

@router.post("/{cliente_id}/interaction", status_code=status.HTTP_204_NO_CONTENT)
def increment_usage(cliente_id: UUID, db: Session = Depends(get_db)):
    success = ClienteService.increment_usage(db, cliente_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return None

@router.get("/{cliente_id}", response_model=ClienteResponse)
def read_cliente(cliente_id: UUID, db: Session = Depends(get_db)):
    db_cliente = ClienteService.get_cliente(db, cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # [DEBUG] Validate Data Integrity on Read
    print(f"DEBUG CLIENTE {cliente_id}: Razón Social='{db_cliente.razon_social}' CUIT='{db_cliente.cuit}' Domicilios={len(db_cliente.domicilios)}")
    
    return db_cliente

@router.put("/{cliente_id}", response_model=ClienteResponse)
def update_cliente(cliente_id: UUID, cliente: ClienteUpdate, db: Session = Depends(get_db)):
    db_cliente = ClienteService.update_cliente(db, cliente_id, cliente)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

@router.delete("/{cliente_id}", response_model=ClienteResponse)
def delete_cliente(cliente_id: UUID, db: Session = Depends(get_db)):
    db_cliente = ClienteService.delete_cliente(db, cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

@router.put("/{cliente_id}/aprobar", response_model=ClienteResponse)
def approve_cliente(cliente_id: UUID, db: Session = Depends(get_db)):
    db_cliente = ClienteService.approve_cliente(db, cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

@router.get("/{cliente_id}/integrity_check")
def check_cliente_integrity(cliente_id: UUID, db: Session = Depends(get_db)):
    """
    Verifica si es seguro eliminar físicamente un cliente.
    Retorna conteo de dependencias (Pedidos).
    """
    from backend.pedidos.models import Pedido
    from sqlalchemy import func
    
    # Count orders associated with this client
    dependency_count = db.query(Pedido).filter(Pedido.cliente_id == cliente_id).count()
    
    # Detailed breakdown if dependencies exist
    details = ""
    if dependency_count > 0:
        breakdown = db.query(Pedido.estado, func.count(Pedido.id)).filter(Pedido.cliente_id == cliente_id).group_by(Pedido.estado).all()
        status_counts = [f"{count} {status}" for status, count in breakdown]
        details = f" ({', '.join(status_counts)})"

    is_safe = dependency_count == 0
    message = "Sin dependencias. Seguro para eliminar." if is_safe else f"Tiene {dependency_count} pedidos asociados{details}. Elimine los pedidos primero."
    
    return {
        "safe": is_safe,
        "dependencies": dependency_count,
        "message": message
    }

@router.delete("/{cliente_id}/hard")
def hard_delete_cliente(cliente_id: UUID, db: Session = Depends(get_db)):
    from sqlalchemy.exc import IntegrityError
    from backend.pedidos.models import Pedido
    from sqlalchemy import func

    try:
        db_cliente = ClienteService.hard_delete_cliente(db, cliente_id)
        if db_cliente is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return {"status": "success", "message": f"Cliente {cliente_id} eliminado definitivamente"}
    except IntegrityError:
        # Generate helpful error message
        dependency_count = db.query(Pedido).filter(Pedido.cliente_id == cliente_id).count()
        details = ""
        if dependency_count > 0:
            breakdown = db.query(Pedido.estado, func.count(Pedido.id)).filter(Pedido.cliente_id == cliente_id).group_by(Pedido.estado).all()
            status_counts = [f"{count} {status}" for status, count in breakdown]
            details = f": {', '.join(status_counts)}"
            
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"No se puede eliminar: El cliente tiene {dependency_count} pedidos asociados{details}. Debe eliminarlos antes."
        )


# --- Domicilios ---
from backend.clientes.schemas import DomicilioCreate, DomicilioUpdate, DomicilioResponse

@router.post("/{cliente_id}/domicilios", response_model=DomicilioResponse, status_code=status.HTTP_201_CREATED)
def create_domicilio(cliente_id: UUID, domicilio: DomicilioCreate, db: Session = Depends(get_db)):
    return ClienteService.create_domicilio(db, cliente_id, domicilio)

@router.put("/{cliente_id}/domicilios/{domicilio_id}", response_model=DomicilioResponse)
def update_domicilio(cliente_id: UUID, domicilio_id: UUID, domicilio: DomicilioUpdate, db: Session = Depends(get_db)):
    db_domicilio = ClienteService.update_domicilio(db, domicilio_id, domicilio)
    if db_domicilio is None:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado")
    return db_domicilio

@router.delete("/{cliente_id}/domicilios/{domicilio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_domicilio(cliente_id: UUID, domicilio_id: UUID, db: Session = Depends(get_db)):
    db_domicilio = ClienteService.delete_domicilio(db, domicilio_id)
    if db_domicilio is None:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado")
    return None

# --- Vinculos (Delegated to AgendaService but exposed here for convenience) ---
from backend.agenda.schemas import VinculoComercialCreate, VinculoComercialResponse, VinculoComercialUpdate
from backend.agenda.service import AgendaService

@router.post("/{cliente_id}/vinculos", response_model=VinculoComercialResponse, status_code=status.HTTP_201_CREATED)
def create_vinculo(cliente_id: UUID, vinculo: VinculoComercialCreate, db: Session = Depends(get_db)):
    if vinculo.cliente_id != cliente_id:
        raise HTTPException(status_code=400, detail="ID de cliente no coincide")
    return AgendaService.create_vinculo(db, vinculo)

@router.put("/{cliente_id}/vinculos/{vinculo_id}", response_model=VinculoComercialResponse)
def update_vinculo(cliente_id: UUID, vinculo_id: UUID, vinculo: VinculoComercialUpdate, db: Session = Depends(get_db)):
    return AgendaService.update_vinculo(db, vinculo_id, vinculo)

@router.delete("/{cliente_id}/vinculos/{vinculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vinculo(cliente_id: UUID, vinculo_id: UUID, db: Session = Depends(get_db)):
    # Verify vinculo belongs to cliente?
    # AgendaService.delete_vinculo just deletes by ID.
    return AgendaService.delete_vinculo(db, vinculo_id)
