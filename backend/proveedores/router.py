from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from backend.core.database import get_db
from backend.proveedores import models, schemas

router = APIRouter(
    prefix="/proveedores",
    tags=["Proveedores"]
)

@router.get("/", response_model=List[schemas.ProveedorRead])
def read_proveedores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Proveedor).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.ProveedorRead)
def create_proveedor(proveedor: schemas.ProveedorCreate, db: Session = Depends(get_db)):
    db_proveedor = models.Proveedor(**proveedor.dict())
    db.add(db_proveedor)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

@router.put("/{proveedor_id}", response_model=schemas.ProveedorRead)
def update_proveedor(proveedor_id: UUID, proveedor: schemas.ProveedorUpdate, db: Session = Depends(get_db)):
    db_proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()
    if not db_proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    for key, value in proveedor.dict(exclude_unset=True).items():
        setattr(db_proveedor, key, value)
    
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

@router.delete("/{proveedor_id}")
def delete_proveedor(proveedor_id: UUID, db: Session = Depends(get_db)):
    db_proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()
    if not db_proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Soft Delete
    db_proveedor.activo = not db_proveedor.activo
    db.commit()
    return {"message": "Estado de proveedor actualizado"}
