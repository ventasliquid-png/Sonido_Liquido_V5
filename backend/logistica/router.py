# [IDENTIDAD] - backend\logistica\router.py
# Versión: V5.6 GOLD | Sincronización: 20260407130827
# ---------------------------------------------------------

# backend/logistica/router.py
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.auth.dependencies import get_current_user
from backend.logistica import schemas, service
from backend.contactos import schemas as contactos_schemas
from backend.contactos import service as contactos_service

router = APIRouter(
    prefix="/logistica",
    tags=["Logística"],
    responses={404: {"description": "Not found"}},
)

# --- Empresas ---
from fastapi import APIRouter, Depends, HTTPException, status, Query

# ...

# --- Empresas ---
@router.get("/empresas", response_model=List[schemas.EmpresaTransporteResponse])
def read_empresas(status: str = Query("active", enum=["active", "inactive", "all"]), db: Session = Depends(get_db)):
    return service.LogisticaService.get_empresas(db, status)

@router.post("/empresas", response_model=schemas.EmpresaTransporteResponse, status_code=status.HTTP_201_CREATED)
def create_empresa(empresa: schemas.EmpresaTransporteCreate, db: Session = Depends(get_db)):
    return service.LogisticaService.create_empresa(db, empresa)

@router.get("/empresas/{empresa_id}", response_model=schemas.EmpresaTransporteResponse)
def read_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    db_empresa = service.LogisticaService.get_empresa(db, empresa_id)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return db_empresa

@router.put("/empresas/{empresa_id}", response_model=schemas.EmpresaTransporteResponse)
def update_empresa(empresa_id: UUID, empresa: schemas.EmpresaTransporteUpdate, db: Session = Depends(get_db)):
    db_empresa = service.LogisticaService.update_empresa(db, empresa_id, empresa)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return db_empresa

@router.delete("/empresas/{empresa_id}/hard", response_model=schemas.EmpresaTransporteResponse)
def hard_delete_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    from sqlalchemy.exc import IntegrityError
    try:
        db_empresa = service.LogisticaService.hard_delete_empresa(db, empresa_id)
        if db_empresa is None:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        return db_empresa
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="No se puede eliminar la empresa porque tiene registros asociados."
        )

# --- Vinculos (V6 Multiplex Sync) ---

@router.post("/empresas/{empresa_id}/vinculos", response_model=contactos_schemas.VinculoRead, status_code=status.HTTP_201_CREATED)
def create_vinculo(empresa_id: UUID, vinculo: contactos_schemas.ContactoCreate, db: Session = Depends(get_db)):
    """
    [V6 MULTIPLEX] Crea un vínculo entre una empresa de transporte y una persona.
    """
    if vinculo.transporte_id != empresa_id:
        raise HTTPException(status_code=400, detail="ID de transporte no coincide")
    
    return contactos_service.create_contacto(db, vinculo)

@router.put("/empresas/{empresa_id}/vinculos/{vinculo_id}", response_model=contactos_schemas.VinculoRead)
def update_vinculo(empresa_id: UUID, vinculo_id: UUID, vinculo: contactos_schemas.VinculoUpdate, db: Session = Depends(get_db)):
    """
    [V6 MULTIPLEX] Actualiza un vínculo existente.
    """
    db_vinculo = db.query(contactos_service.models.Vinculo).filter(contactos_service.models.Vinculo.id == vinculo_id).first()
    if not db_vinculo:
        raise HTTPException(status_code=404, detail="Vínculo no encontrado")
        
    return contactos_service.update_vinculo(db, db_vinculo.persona_id, vinculo_id, vinculo)

@router.delete("/empresas/{empresa_id}/vinculos/{vinculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vinculo(empresa_id: UUID, vinculo_id: UUID, db: Session = Depends(get_db)):
    """
    [V6 MULTIPLEX] Elimina un vínculo.
    """
    db_vinculo = db.query(contactos_service.models.Vinculo).filter(contactos_service.models.Vinculo.id == vinculo_id).first()
    if not db_vinculo:
        raise HTTPException(status_code=404, detail="Vínculo no encontrado")
        
    success = contactos_service.delete_vinculo(db, db_vinculo.persona_id, vinculo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vínculo no encontrado")
    return None

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

@router.delete("/nodos/{nodo_id}/hard", response_model=schemas.NodoTransporteResponse)
def hard_delete_nodo(nodo_id: UUID, db: Session = Depends(get_db)):
    from sqlalchemy.exc import IntegrityError
    try:
        db_nodo = service.LogisticaService.hard_delete_nodo(db, nodo_id)
        if db_nodo is None:
            raise HTTPException(status_code=404, detail="Nodo no encontrado")
        return db_nodo
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="No se puede eliminar el nodo porque tiene registros asociados."
        )
