from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

from backend.core.database import get_db
from backend.core.models import BugTracking, SistemaConfig

router = APIRouter(
    prefix="/sistema",
    tags=["Sistema"]
)

class BugCreate(BaseModel):
    descripcion: str
    detalle: Optional[str] = None
    entorno: str = 'D'

@router.get("/bugs")
def get_bugs(db: Session = Depends(get_db)):
    bugs = db.query(BugTracking).order_by(BugTracking.resuelto, BugTracking.fecha_ocurrencia.desc()).all()
    return bugs

@router.post("/bugs")
def create_bug(bug_in: BugCreate, db: Session = Depends(get_db)):
    nuevo = BugTracking(
        descripcion=bug_in.descripcion,
        detalle=bug_in.detalle,
        entorno=bug_in.entorno,
        resuelto=False
    )
    db.add(nuevo)
    
    # Recalcular bit
    config = db.query(SistemaConfig).filter(SistemaConfig.id == 1).first()
    if config:
        config.flags_estado |= 32
        
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/bugs/{bug_id}/resolve")
def resolve_bug(bug_id: str, db: Session = Depends(get_db)):
    bug = db.query(BugTracking).filter(BugTracking.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug no encontrado")
        
    bug.resuelto = True
    bug.fecha_resolucion = datetime.now(timezone.utc)
    
    # Recalcular bit
    hay_pendientes = db.query(BugTracking).filter(BugTracking.resuelto == False, BugTracking.id != bug_id).count() > 0
    config = db.query(SistemaConfig).filter(SistemaConfig.id == 1).first()
    
    if config:
        if hay_pendientes:
            config.flags_estado |= 32
        else:
            config.flags_estado &= ~32
            
    db.commit()
    db.refresh(bug)
    return bug
