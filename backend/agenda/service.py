# backend/agenda/service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from backend.agenda import models, schemas
from backend.clientes.models import Cliente

class AgendaService:
    # --- Persona ---
    @staticmethod
    def create_persona(db: Session, persona_in: schemas.PersonaCreate) -> models.Persona:
        # Check for existing email if provided
        if persona_in.email_personal:
            existing = db.query(models.Persona).filter(models.Persona.email_personal == persona_in.email_personal).first()
            if existing:
                raise HTTPException(status_code=400, detail="Ya existe una persona con este email personal.")
        
        db_persona = models.Persona(**persona_in.model_dump())
        db.add(db_persona)
        db.commit()
        db.refresh(db_persona)
        return db_persona

    @staticmethod
    def get_personas(db: Session, skip: int = 0, limit: int = 100, status: str = "active") -> List[models.Persona]:
        query = db.query(models.Persona)
        if status == "active":
            query = query.filter(models.Persona.activo == True)
        elif status == "inactive":
            query = query.filter(models.Persona.activo == False)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_persona(db: Session, persona_id: UUID) -> Optional[models.Persona]:
        return db.query(models.Persona).filter(models.Persona.id == persona_id).first()

    @staticmethod
    def search_personas(db: Session, query: str) -> List[models.Persona]:
        # Search by name or email
        return db.query(models.Persona).filter(
            or_(
                models.Persona.nombre_completo.ilike(f"%{query}%"),
                models.Persona.email_personal.ilike(f"%{query}%")
            )
        ).limit(20).all()

    @staticmethod
    def update_persona(db: Session, persona_id: UUID, persona_in: schemas.PersonaUpdate) -> Optional[models.Persona]:
        db_persona = AgendaService.get_persona(db, persona_id)
        if not db_persona:
            return None
        
        update_data = persona_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_persona, key, value)
        
        db.add(db_persona)
        db.commit()
        db.refresh(db_persona)
        return db_persona

    # --- VinculoComercial ---
    @staticmethod
    def create_vinculo(db: Session, vinculo_in: schemas.VinculoComercialCreate) -> models.VinculoComercial:
        # Validar Persona
        persona = AgendaService.get_persona(db, vinculo_in.persona_id)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        
        # Validar Cliente
        cliente = db.query(Cliente).filter(Cliente.id == vinculo_in.cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        db_vinculo = models.VinculoComercial(**vinculo_in.model_dump())
        db.add(db_vinculo)
        db.commit()
        db.refresh(db_vinculo)
        return db_vinculo

    @staticmethod
    def get_vinculos_by_cliente(db: Session, cliente_id: UUID) -> List[models.VinculoComercial]:
        return db.query(models.VinculoComercial).filter(models.VinculoComercial.cliente_id == cliente_id).all()

    @staticmethod
    def update_vinculo(db: Session, vinculo_id: UUID, vinculo_in: schemas.VinculoComercialUpdate) -> Optional[models.VinculoComercial]:
        db_vinculo = db.query(models.VinculoComercial).filter(models.VinculoComercial.id == vinculo_id).first()
        if not db_vinculo:
            return None
        
        update_data = vinculo_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_vinculo, key, value)
        
        db.add(db_vinculo)
        db.commit()
        db.refresh(db_vinculo)
        return db_vinculo

    @staticmethod
    def delete_vinculo(db: Session, vinculo_id: UUID):
        db_vinculo = db.query(models.VinculoComercial).filter(models.VinculoComercial.id == vinculo_id).first()
        if db_vinculo:
            db.delete(db_vinculo)
            db.commit()
        return db_vinculo
