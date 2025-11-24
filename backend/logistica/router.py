# backend/logistica/router.py
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from backend.auth.dependencies import get_current_user
from backend.logistica import schemas, service

router = APIRouter(
    prefix="/logistica",
    tags=["Logística"],
    responses={404: {"description": "Not found"}},
)

# --- Empresas ---
@router.get("/empresas", response_model=List[schemas.EmpresaTransporteResponse])
def read_empresas(db: Session = Depends(get_db)):
    return service.LogisticaService.get_empresas(db)

@router.post("/empresas", response_model=schemas.EmpresaTransporteResponse, status_code=status.HTTP_201_CREATED)
def create_empresa(empresa: schemas.EmpresaTransporteCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.LogisticaService.create_empresa(db, empresa)

@router.get("/empresas/{empresa_id}", response_model=schemas.EmpresaTransporteResponse)
def read_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    db_empresa = service.LogisticaService.get_empresa(db, empresa_id)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return db_empresa

@router.put("/empresas/{empresa_id}", response_model=schemas.EmpresaTransporteResponse)
def update_empresa(empresa_id: UUID, empresa: schemas.EmpresaTransporteUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_empresa = service.LogisticaService.update_empresa(db, empresa_id, empresa)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return db_empresa

# --- Nodos ---
@router.get("/nodos", response_model=List[schemas.NodoTransporteResponse])
def read_nodos(empresa_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    return service.LogisticaService.get_nodos(db, empresa_id)

@router.post("/nodos", response_model=schemas.NodoTransporteResponse, status_code=status.HTTP_201_CREATED)
def create_nodo(nodo: schemas.NodoTransporteCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.LogisticaService.create_nodo(db, nodo)

@router.get("/nodos/{nodo_id}", response_model=schemas.NodoTransporteResponse)
def read_nodo(nodo_id: UUID, db: Session = Depends(get_db)):
    db_nodo = service.LogisticaService.get_nodo(db, nodo_id)
    if db_nodo is None:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return db_nodo

@router.put("/nodos/{nodo_id}", response_model=schemas.NodoTransporteResponse)
def update_nodo(nodo_id: UUID, nodo: schemas.NodoTransporteUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_nodo = service.LogisticaService.update_nodo(db, nodo_id, nodo)
    if db_nodo is None:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return db_nodo
