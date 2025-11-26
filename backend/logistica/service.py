# backend/logistica/service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.logistica import models, schemas

class LogisticaService:
    # --- EmpresaTransporte ---
    @staticmethod
    def create_empresa(db: Session, empresa_in: schemas.EmpresaTransporteCreate) -> models.EmpresaTransporte:
        # Check for existing empresa with same name (case insensitive)
        existing = db.query(models.EmpresaTransporte).filter(
            models.EmpresaTransporte.nombre.ilike(empresa_in.nombre)
        ).first()
        
        if existing:
            status_msg = "activa" if existing.activo else "inactiva"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una empresa de transporte con el nombre '{existing.nombre}' ({status_msg})."
            )

        db_empresa = models.EmpresaTransporte(**empresa_in.model_dump())
        db.add(db_empresa)
        db.commit()
        db.refresh(db_empresa)
        return db_empresa

    @staticmethod
    def get_empresas(db: Session, status: str = "active") -> List[models.EmpresaTransporte]:
        query = db.query(models.EmpresaTransporte)
        if status == "active":
            query = query.filter(models.EmpresaTransporte.activo == True)
        elif status == "inactive":
            query = query.filter(models.EmpresaTransporte.activo == False)
        # If "all", no filter applied
        return query.all()

    @staticmethod
    def get_empresa(db: Session, empresa_id: UUID) -> Optional[models.EmpresaTransporte]:
        return db.query(models.EmpresaTransporte).filter(models.EmpresaTransporte.id == empresa_id).first()

    @staticmethod
    def update_empresa(db: Session, empresa_id: UUID, empresa_in: schemas.EmpresaTransporteUpdate) -> Optional[models.EmpresaTransporte]:
        db_empresa = LogisticaService.get_empresa(db, empresa_id)
        if not db_empresa:
            return None
        
        update_data = empresa_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_empresa, key, value)
        
        db.add(db_empresa)
        db.commit()
        db.refresh(db_empresa)
        return db_empresa

    # --- NodoTransporte ---
    @staticmethod
    def create_nodo(db: Session, nodo_in: schemas.NodoTransporteCreate) -> models.NodoTransporte:
        # Validar que la empresa exista
        empresa = LogisticaService.get_empresa(db, nodo_in.empresa_id)
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa de transporte no encontrada")

        db_nodo = models.NodoTransporte(**nodo_in.model_dump())
        db.add(db_nodo)
        db.commit()
        db.refresh(db_nodo)
        return db_nodo

    @staticmethod
    def get_nodos(db: Session, empresa_id: Optional[UUID] = None) -> List[models.NodoTransporte]:
        query = db.query(models.NodoTransporte)
        if empresa_id:
            query = query.filter(models.NodoTransporte.empresa_id == empresa_id)
        return query.all()

    @staticmethod
    def get_nodo(db: Session, nodo_id: UUID) -> Optional[models.NodoTransporte]:
        return db.query(models.NodoTransporte).filter(models.NodoTransporte.id == nodo_id).first()

    @staticmethod
    def update_nodo(db: Session, nodo_id: UUID, nodo_in: schemas.NodoTransporteUpdate) -> Optional[models.NodoTransporte]:
        db_nodo = LogisticaService.get_nodo(db, nodo_id)
        if not db_nodo:
            return None
        
        update_data = nodo_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_nodo, key, value)
        
        db.add(db_nodo)
        db.commit()
        db.refresh(db_nodo)
        return db_nodo
