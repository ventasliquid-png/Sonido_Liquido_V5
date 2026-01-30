# Archivo: backend/contactos/router.py
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.contactos import models, schemas, service

router = APIRouter(
    prefix="/contactos",
    tags=["contactos"],
    responses={404: {"description": "Not found"}},
)

# --- CRUD Endpoints ---

@router.get("", response_model=List[schemas.ContactoRead])
def read_contactos(
    skip: int = 0, 
    limit: int = 100, 
    cliente_id: Optional[UUID] = None,
    transporte_id: Optional[UUID] = None,
    q: Optional[str] = None, # Buscador texto
    db: Session = Depends(get_db)
):
    return service.get_contactos(
        db, 
        skip=skip, 
        limit=limit, 
        cliente_id=cliente_id, 
        transporte_id=transporte_id, 
        q=q
    )

@router.post("", response_model=schemas.ContactoRead, status_code=status.HTTP_201_CREATED)
def create_contacto(contacto: schemas.ContactoCreate, db: Session = Depends(get_db)):
    return service.create_contacto(db, contacto)

@router.get("/{contacto_id}", response_model=schemas.ContactoRead)
def read_contacto(contacto_id: UUID, db: Session = Depends(get_db)):
    db_contacto = service.get_contacto(db, contacto_id=contacto_id)
    if db_contacto is None:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return db_contacto

@router.put("/{contacto_id}", response_model=schemas.ContactoRead)
def update_contacto(contacto_id: UUID, contacto: schemas.ContactoUpdate, db: Session = Depends(get_db)):
    db_contacto = service.update_contacto(db, contacto_id, contacto)
    if db_contacto is None:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return db_contacto

@router.delete("/{contacto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contacto(contacto_id: UUID, db: Session = Depends(get_db)):
    success = service.delete_contacto(db, contacto_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return None

# --- Vinculos Management (Multiplex) ---

@router.post("/{contacto_id}/vinculos", response_model=schemas.VinculoRead)
def add_vinculo(contacto_id: UUID, vinculo: schemas.ContactoCreate, db: Session = Depends(get_db)):
    """
    Agrega un nuevo vínculo (Rol Comercial) a una persona existente.
    """
    new_vinculo = service.add_vinculo(db, contacto_id, vinculo)
    if not new_vinculo:
        raise HTTPException(status_code=404, detail="Persona no encontrada o datos de vinculación inválidos")
    return new_vinculo

@router.delete("/{contacto_id}/vinculos/{vinculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vinculo(contacto_id: UUID, vinculo_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina un vínculo específico.
    """
    success = service.delete_vinculo(db, contacto_id, vinculo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vínculo o Persona no encontrada")
    return None
