"""
Módulo Rubros (V1.0): Rutas de API (/rubros).
Define los endpoints CRUD para la gestión de rubros.

--- CARACTERÍSTICAS ESPECIALES ---
- Protocolo Lázaro: Reactivación de códigos inactivos
- Validación VIL: Integridad antes de borrado físico
- Input Force: Código siempre en mayúsculas
- SEGURIDAD: Endpoints protegidos con autenticación JWT obligatoria
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

# --- [INICIO REFACTOR V10.10] ---
from core.database import get_db
from backend.auth.dependencies import get_current_active_user, get_current_user
from backend.auth import models as auth_models
from backend.rubros import models
from backend.rubros import service
from backend.rubros.schemas import RubroCreate, RubroUpdate, RubroOut, RubroLazaroResponse
# --- [FIN REFACTOR V10.10] ---

router = APIRouter(
    prefix="/rubros",
    tags=["Rubros (V1.0)"]
)

# --- Endpoint 1: Listar Rubros (con búsqueda y filtros) ---
@router.get("/", response_model=List[RubroOut])
def list_rubros(
    q: Optional[str] = None,
    activo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista rubros con búsqueda predictiva y filtros de estado.
    - q: Búsqueda por código o descripción
    - activo: Filtrar por estado (True=activos, False=inactivos, None=todos)
    """
    if q:
        return service.search_rubros(db, query=q, activo_filter=activo, skip=skip, limit=limit)
    elif activo is True:
        return service.get_rubros_activos(db, skip=skip, limit=limit)
    elif activo is False:
        return service.get_rubros_inactivos(db, skip=skip, limit=limit)
    else:
        return service.get_all_rubros(db, skip=skip, limit=limit)

# --- Endpoint 2: Obtener Rubro por ID ---
@router.get("/{rubro_id}", response_model=RubroOut)
def get_rubro(rubro_id: int, db: Session = Depends(get_db)):
    """Obtiene un rubro por su ID."""
    rubro = service.get_rubro_by_id(db, rubro_id=rubro_id)
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    return rubro

# --- Endpoint 3: Crear Rubro (Protocolo Lázaro) ---
@router.post("/", response_model=RubroOut, status_code=status.HTTP_201_CREATED)
def create_rubro(
    rubro: RubroCreate,
    db: Session = Depends(get_db),
    current_user: auth_models.Usuario = Depends(get_current_user)
):
    """
    Crea un nuevo rubro.
    
    PROTOCOLO LÁZARO:
    - Si el código existe y está activo -> Error 409
    - Si el código existe pero está inactivo -> Retorna respuesta especial para reactivación
    """
    # Input Force: Asegurar mayúsculas
    codigo_upper = rubro.codigo.upper().strip()
    
    # Verificar si el código ya existe
    rubro_existente = service.get_rubro_by_codigo(db, codigo=codigo_upper)
    
    if rubro_existente:
        if rubro_existente.activo:
            # Código activo existe -> Error 409
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El código '{codigo_upper}' ya existe y está activo."
            )
        else:
            # PROTOCOLO LÁZARO: Código inactivo existe
            # Retornamos respuesta especial (el frontend preguntará si desea reactivar)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Código inactivo existente",
                headers={"X-Lazaro-Inactive": "true", "X-Rubro-Id": str(rubro_existente.id)}
            )
    
    # Crear nuevo rubro
    # CRÍTICO: created_by y updated_by se obtienen del token (current_user), NO del body
    db_rubro = models.Rubro(
        codigo=codigo_upper,
        descripcion=rubro.descripcion,
        padre_id=rubro.padre_id,
        activo=True,
        created_by=current_user.username,  # Del token JWT
        updated_by=current_user.username   # Del token JWT
    )
    
    db.add(db_rubro)
    db.commit()
    db.refresh(db_rubro)
    
    return db_rubro

# --- Endpoint 4: Actualizar Rubro ---
@router.patch("/{rubro_id}", response_model=RubroOut)
def update_rubro(
    rubro_id: int,
    rubro_update: RubroUpdate,
    db: Session = Depends(get_db),
    current_user: auth_models.Usuario = Depends(get_current_active_user)
):
    """Actualiza un rubro existente."""
    db_rubro = service.get_rubro_by_id(db, rubro_id=rubro_id)
    if not db_rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    
    # Actualizar campos
    if rubro_update.descripcion is not None:
        db_rubro.descripcion = rubro_update.descripcion
    if rubro_update.activo is not None:
        db_rubro.activo = rubro_update.activo
    if rubro_update.padre_id is not None:
        db_rubro.padre_id = rubro_update.padre_id
    
    # CRÍTICO: updated_by se obtiene del token (current_user), NO del body
    db_rubro.updated_by = current_user.username
    
    db.commit()
    db.refresh(db_rubro)
    
    return db_rubro

# --- Endpoint 5: Reactivar Rubro (Protocolo Lázaro) ---
@router.patch("/{rubro_id}/reactivate", response_model=RubroOut)
def reactivate_rubro(
    rubro_id: int,
    rubro_update: Optional[RubroUpdate] = None,
    db: Session = Depends(get_db),
    current_user: auth_models.Usuario = Depends(get_current_active_user)
):
    """
    Reactiva un rubro inactivo (Protocolo Lázaro).
    Permite actualizar la descripción y padre_id durante la reactivación.
    """
    db_rubro = service.get_rubro_by_id(db, rubro_id=rubro_id)
    if not db_rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    
    if db_rubro.activo:
        raise HTTPException(status_code=400, detail="El rubro ya está activo")
    
    # Reactivar
    db_rubro.activo = True
    
    # Opcionalmente actualizar otros campos
    if rubro_update:
        if rubro_update.descripcion is not None:
            db_rubro.descripcion = rubro_update.descripcion
        if rubro_update.padre_id is not None:
            db_rubro.padre_id = rubro_update.padre_id
    
    # CRÍTICO: updated_by se obtiene del token (current_user), NO del body
    db_rubro.updated_by = current_user.username
    
    db.commit()
    db.refresh(db_rubro)
    
    return db_rubro

# --- Endpoint 6: Baja Lógica (por defecto) ---
@router.delete("/{rubro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rubro(
    rubro_id: int,
    force_physical: bool = False,
    db: Session = Depends(get_db),
    current_user: auth_models.Usuario = Depends(get_current_active_user)
):
    """
    Elimina un rubro.
    
    - Por defecto: Baja Lógica (activo=false)
    - Con force_physical=true: Baja Física (solo Master)
    - VIL: Valida integridad antes de borrado físico
    """
    db_rubro = service.get_rubro_by_id(db, rubro_id=rubro_id)
    if not db_rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    
    if force_physical:
        # VALIDACIÓN VIL: Verificar integridad antes de borrado físico
        puede_eliminar, mensaje_error = service.can_delete_physically(db, rubro_id)
        if not puede_eliminar:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=mensaje_error
            )
        
        # Baja física
        db.delete(db_rubro)
    else:
        # Baja lógica
        db_rubro.activo = False
        # CRÍTICO: updated_by se obtiene del token (current_user), NO del body
        db_rubro.updated_by = current_user.username
    
    db.commit()
    return None

print("--- [Rubros V1.0]: Router (Endpoints CRUD) definido. ---")

