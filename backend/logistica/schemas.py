# backend/logistica/schemas.py
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

# --- EmpresaTransporte ---
class EmpresaTransporteBase(BaseModel):
    nombre: str
    web_tracking: Optional[str] = None
    telefono_reclamos: Optional[str] = None
    requiere_carga_web: bool = False
    formato_etiqueta: str = 'PROPIA' # 'PROPIA', 'EXTERNA_PDF'
    activo: bool = True

class EmpresaTransporteCreate(EmpresaTransporteBase):
    pass

class EmpresaTransporteUpdate(BaseModel):
    nombre: Optional[str] = None
    web_tracking: Optional[str] = None
    telefono_reclamos: Optional[str] = None
    requiere_carga_web: Optional[bool] = None
    formato_etiqueta: Optional[str] = None
    activo: Optional[bool] = None

class EmpresaTransporteResponse(EmpresaTransporteBase):
    id: UUID
    class Config:
        from_attributes = True

# --- NodoTransporte ---
class NodoTransporteBase(BaseModel):
    nombre_nodo: str
    direccion_completa: Optional[str] = None
    provincia_id: str
    es_punto_despacho: bool = False
    es_punto_retiro: bool = False
    horario_operativo: Optional[str] = None
    contacto_operativo: Optional[str] = None

class NodoTransporteCreate(NodoTransporteBase):
    empresa_id: UUID

class NodoTransporteUpdate(BaseModel):
    nombre_nodo: Optional[str] = None
    direccion_completa: Optional[str] = None
    provincia_id: Optional[str] = None
    es_punto_despacho: Optional[bool] = None
    es_punto_retiro: Optional[bool] = None
    horario_operativo: Optional[str] = None
    contacto_operativo: Optional[str] = None

class NodoTransporteResponse(NodoTransporteBase):
    id: UUID
    empresa_id: UUID
    class Config:
        from_attributes = True
