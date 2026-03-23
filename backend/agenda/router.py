# backend/agenda/router.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.auth.dependencies import get_current_user
from backend.agenda import schemas, service

router = APIRouter(
    prefix="/agenda",
    tags=["Agenda"],
    responses={404: {"description": "Not found"}},
)

# --- Personas ---
@router.get("/personas", response_model=List[schemas.PersonaResponse])
def read_personas(skip: int = 0, limit: int = 100, status: str = Query("active", enum=["active", "inactive", "all"]), db: Session = Depends(get_db)):
    return service.AgendaService.get_personas(db, skip=skip, limit=limit, status=status)

@router.get("/personas/search", response_model=List[schemas.PersonaResponse])
def search_personas(q: str = Query(..., min_length=3), db: Session = Depends(get_db)):
    return service.AgendaService.search_personas(db, q)

@router.post("/personas", response_model=schemas.PersonaResponse, status_code=status.HTTP_201_CREATED)
def create_persona(persona: schemas.PersonaCreate, db: Session = Depends(get_db)):
    return service.AgendaService.create_persona(db, persona)

@router.get("/personas/{persona_id}", response_model=schemas.PersonaResponse)
def read_persona(persona_id: UUID, db: Session = Depends(get_db)):
    db_persona = service.AgendaService.get_persona(db, persona_id)
    if db_persona is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return db_persona

@router.put("/personas/{persona_id}", response_model=schemas.PersonaResponse)
def update_persona(persona_id: UUID, persona: schemas.PersonaUpdate, db: Session = Depends(get_db)):
    db_persona = service.AgendaService.update_persona(db, persona_id, persona)
    if db_persona is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return db_persona

@router.delete("/personas/{persona_id}/hard", response_model=schemas.PersonaResponse)
def hard_delete_persona(persona_id: UUID, db: Session = Depends(get_db)):
    from sqlalchemy.exc import IntegrityError
    try:
        db_persona = service.AgendaService.hard_delete_persona(db, persona_id)
        if db_persona is None:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        return db_persona
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="No se puede eliminar la persona porque tiene registros asociados."
        )

# --- Vinculos ---
@router.post("/vinculos", response_model=schemas.VinculoComercialResponse, status_code=status.HTTP_201_CREATED)
def create_vinculo(vinculo: schemas.VinculoComercialCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.AgendaService.create_vinculo(db, vinculo)

@router.put("/vinculos/{vinculo_id}", response_model=schemas.VinculoComercialResponse)
def update_vinculo(vinculo_id: UUID, vinculo: schemas.VinculoComercialUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_vinculo = service.AgendaService.update_vinculo(db, vinculo_id, vinculo)
    if db_vinculo is None:
        raise HTTPException(status_code=404, detail="Vínculo no encontrado")
    return db_vinculo

@router.delete("/vinculos/{vinculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vinculo(vinculo_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_vinculo = service.AgendaService.delete_vinculo(db, vinculo_id)
    if db_vinculo is None:
        raise HTTPException(status_code=404, detail="Vínculo no encontrado")
    return None
