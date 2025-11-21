"""
Módulo Rubros (V1.0): Lógica de Negocio de Rubros.
Contiene las funciones de consulta ORM y validaciones de integridad.
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from backend.rubros import models

def get_rubro_by_codigo(db: Session, codigo: str) -> Optional[models.Rubro]:
    """Obtiene un rubro por su código (case-insensitive, pero normalizado a mayúsculas)."""
    codigo_upper = codigo.upper().strip()
    return db.query(models.Rubro).filter(models.Rubro.codigo == codigo_upper).first()

def get_rubro_by_id(db: Session, rubro_id: int) -> Optional[models.Rubro]:
    """Obtiene un rubro por su ID."""
    return db.query(models.Rubro).filter(models.Rubro.id == rubro_id).first()

def get_rubros_activos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Rubro]:
    """Obtiene todos los rubros activos."""
    return db.query(models.Rubro).filter(models.Rubro.activo == True).offset(skip).limit(limit).all()

def get_rubros_inactivos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Rubro]:
    """Obtiene todos los rubros inactivos."""
    return db.query(models.Rubro).filter(models.Rubro.activo == False).offset(skip).limit(limit).all()

def get_all_rubros(db: Session, skip: int = 0, limit: int = 100) -> List[models.Rubro]:
    """Obtiene todos los rubros (activos e inactivos)."""
    return db.query(models.Rubro).offset(skip).limit(limit).all()

def search_rubros(db: Session, query: str, activo_filter: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[models.Rubro]:
    """
    Búsqueda predictiva de rubros por código o descripción.
    Filtra por estado activo/inactivo si se especifica.
    """
    q = db.query(models.Rubro)
    
    # Filtro por estado
    if activo_filter is not None:
        q = q.filter(models.Rubro.activo == activo_filter)
    
    # Búsqueda por código o descripción (case-insensitive)
    query_lower = query.lower().strip()
    if query_lower:
        q = q.filter(
            (models.Rubro.codigo.ilike(f"%{query_lower}%")) |
            (models.Rubro.descripcion.ilike(f"%{query_lower}%"))
        )
    
    return q.order_by(models.Rubro.codigo).offset(skip).limit(limit).all()

def has_hijos(db: Session, rubro_id: int) -> bool:
    """Verifica si un rubro tiene hijos (subrubros)."""
    rubro = get_rubro_by_id(db, rubro_id)
    if not rubro:
        return False
    return len(rubro.hijos) > 0

def has_productos(db: Session, rubro_id: int) -> bool:
    """
    Verifica si un rubro tiene productos asociados.
    NOTA: Esta función asume que existe una tabla 'productos' con un campo 'rubro_id'.
    Si no existe, retorna False por defecto.
    """
    # TODO: Implementar cuando exista la tabla productos
    # from ..productos import models as productos_models
    # count = db.query(productos_models.Producto).filter(productos_models.Producto.rubro_id == rubro_id).count()
    # return count > 0
    return False  # Por ahora, retornamos False

def can_delete_physically(db: Session, rubro_id: int) -> Tuple[bool, str]:
    """
    Valida si un rubro puede ser eliminado físicamente (VIL - Validación de Integridad).
    Retorna (puede_eliminar, mensaje_error).
    """
    if has_hijos(db, rubro_id):
        return False, "No se puede eliminar: el rubro tiene subrubros asociados."
    
    if has_productos(db, rubro_id):
        return False, "No se puede eliminar: el rubro tiene productos asociados."
    
    return True, ""

print("--- [Rubros V1.0]: Service (Lógica de Negocio) definida. ---")

