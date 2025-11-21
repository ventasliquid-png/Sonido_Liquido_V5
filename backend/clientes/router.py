from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from backend.clientes.schemas import ClienteCreate, ClienteResponse, ClienteUpdate
from backend.clientes.service import ClienteService

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
