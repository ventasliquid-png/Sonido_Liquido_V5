# [IDENTIDAD] - backend/ingesta/router.py
# Versión: V5.6 GOLD | Sincronización: 20260508191500
# ------------------------------------------
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.ingesta.service import IngestaService

router = APIRouter(prefix="/ingesta", tags=["ingesta"])

@router.post("/raw")
async def upload_raw(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        raw = IngestaService.store_raw(db, content, file.filename)
        return {"id": raw.id, "filename": raw.filename, "status": raw.audit_status}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/raw/{raw_id}/preview")
def get_preview(raw_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return IngestaService.preview(db, raw_id)
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/raw/{raw_id}/approve")
def approve_ingesta(raw_id: uuid.UUID, edited_data: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        procesada = IngestaService.approve(db, raw_id, edited_data)
        return {"id": procesada.id, "estado": procesada.estado}
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/procesadas/{proc_id}")
def get_procesada(proc_id: uuid.UUID, db: Session = Depends(get_db)):
    procesada = IngestaService.get_procesada(db, proc_id)
    if not procesada:
        raise HTTPException(status_code=404, detail="Factura procesada no encontrada")
    return procesada
