# Archivo: backend/contactos/router.py
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.contactos import models, schemas

router = APIRouter(
    prefix="/contactos",
    tags=["contactos"],
    responses={404: {"description": "Not found"}},
)

# --- CRUD Endpoints ---

@router.get("/", response_model=List[schemas.ContactoRead])
def read_contactos(
    skip: int = 0, 
    limit: int = 100, 
    cliente_id: Optional[UUID] = None,
    transporte_id: Optional[UUID] = None,
    q: Optional[str] = None, # Buscador texto
    db: Session = Depends(get_db)
):
    query = db.query(models.Contacto)
    
    # Filtros
    if cliente_id:
        query = query.filter(models.Contacto.cliente_id == cliente_id)
    if transporte_id:
        query = query.filter(models.Contacto.transporte_id == transporte_id)
        
    # Buscador simple (Nombre o Apellido)
    if q:
        search = f"%{q}%"
        query = query.filter(
            (models.Contacto.nombre.ilike(search)) | 
            (models.Contacto.apellido.ilike(search))
        )
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.ContactoRead, status_code=status.HTTP_201_CREATED)
def create_contacto(contacto: schemas.ContactoCreate, db: Session = Depends(get_db)):
    # Conversión directa de Pydantic a Modelo SQLAlchemy
    # Nota: Los campos JSON (roles, canales) Pydantic los pasa como list/dict, 
    # SQLAlchemy con tipo JSON los acepta directamente.
    
    # [Validación] Pydantic ya validó tipos, pero convertimos 'canales' a lista de dicts
    # porque el modelo espera JSON compatible.
    canales_data = [c.model_dump() for c in contacto.canales]
    
    db_contacto = models.Contacto(
        nombre=contacto.nombre,
        apellido=contacto.apellido,
        puesto=contacto.puesto,
        referencia_origen=contacto.referencia_origen,
        domicilio_personal=contacto.domicilio_personal,
        roles=contacto.roles,
        canales=canales_data,
        notas=contacto.notas,
        estado=contacto.estado,
        cliente_id=contacto.cliente_id,
        transporte_id=contacto.transporte_id
    )
    
    db.add(db_contacto)
    db.commit()
    db.refresh(db_contacto)
    return db_contacto

@router.get("/{contacto_id}", response_model=schemas.ContactoRead)
def read_contacto(contacto_id: UUID, db: Session = Depends(get_db)):
    db_contacto = db.query(models.Contacto).filter(models.Contacto.id == contacto_id).first()
    if db_contacto is None:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return db_contacto

@router.put("/{contacto_id}", response_model=schemas.ContactoRead)
def update_contacto(contacto_id: UUID, contacto: schemas.ContactoUpdate, db: Session = Depends(get_db)):
    db_contacto = db.query(models.Contacto).filter(models.Contacto.id == contacto_id).first()
    if db_contacto is None:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    
    # Update manual de campos
    db_contacto.nombre = contacto.nombre
    db_contacto.apellido = contacto.apellido
    db_contacto.puesto = contacto.puesto
    db_contacto.referencia_origen = contacto.referencia_origen
    db_contacto.domicilio_personal = contacto.domicilio_personal
    db_contacto.roles = contacto.roles
    db_contacto.canales = [c.model_dump() for c in contacto.canales]
    db_contacto.notas = contacto.notas
    db_contacto.estado = contacto.estado
    # Permitimos mover de cliente/transporte? Sí.
    db_contacto.cliente_id = contacto.cliente_id
    db_contacto.transporte_id = contacto.transporte_id
    
    db.commit()
    db.refresh(db_contacto)
    return db_contacto

@router.delete("/{contacto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contacto(contacto_id: UUID, db: Session = Depends(get_db)):
    db_contacto = db.query(models.Contacto).filter(models.Contacto.id == contacto_id).first()
    if db_contacto is None:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    
    db.delete(db_contacto)
    db.commit()
    return None
