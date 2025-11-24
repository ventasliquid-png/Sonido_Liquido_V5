from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from backend.clientes.schemas import ClienteCreate, ClienteResponse, ClienteUpdate
from backend.clientes.service import ClienteService
from backend.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    return ClienteService.create_cliente(db, cliente)

@router.get("/", response_model=List[ClienteResponse])
def read_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ClienteService.get_clientes(db, skip=skip, limit=limit)

@router.get("/{cliente_id}", response_model=ClienteResponse)
def read_cliente(cliente_id: UUID, db: Session = Depends(get_db)):
    db_cliente = ClienteService.get_cliente(db, cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

@router.put("/{cliente_id}", response_model=ClienteResponse)
def update_cliente(cliente_id: UUID, cliente: ClienteUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_cliente = ClienteService.update_cliente(db, cliente_id, cliente)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

@router.delete("/{cliente_id}", response_model=ClienteResponse)
def delete_cliente(cliente_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_cliente = ClienteService.delete_cliente(db, cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

# --- Domicilios ---
from backend.clientes.schemas import DomicilioCreate, DomicilioUpdate, DomicilioResponse

@router.post("/{cliente_id}/domicilios", response_model=DomicilioResponse, status_code=status.HTTP_201_CREATED)
def create_domicilio(cliente_id: UUID, domicilio: DomicilioCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return ClienteService.create_domicilio(db, cliente_id, domicilio)

@router.put("/{cliente_id}/domicilios/{domicilio_id}", response_model=DomicilioResponse)
def update_domicilio(cliente_id: UUID, domicilio_id: UUID, domicilio: DomicilioUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_domicilio = ClienteService.update_domicilio(db, domicilio_id, domicilio)
    if db_domicilio is None:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado")
    return db_domicilio

@router.delete("/{cliente_id}/domicilios/{domicilio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_domicilio(cliente_id: UUID, domicilio_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_domicilio = ClienteService.delete_domicilio(db, domicilio_id)
    if db_domicilio is None:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado")
    return None

# --- Vinculos (Delegated to AgendaService but exposed here for convenience) ---
from backend.agenda.schemas import VinculoComercialCreate, VinculoComercialResponse
from backend.agenda.service import AgendaService

@router.post("/{cliente_id}/vinculos", response_model=VinculoComercialResponse, status_code=status.HTTP_201_CREATED)
def create_vinculo(cliente_id: UUID, vinculo: VinculoComercialCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if vinculo.cliente_id != cliente_id:
        raise HTTPException(status_code=400, detail="ID de cliente no coincide")
    return AgendaService.create_vinculo(db, vinculo)

@router.delete("/{cliente_id}/vinculos/{vinculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vinculo(cliente_id: UUID, vinculo_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Verify vinculo belongs to cliente?
    # AgendaService.delete_vinculo just deletes by ID.
    return AgendaService.delete_vinculo(db, vinculo_id)
