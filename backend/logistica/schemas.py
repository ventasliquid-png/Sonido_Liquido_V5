# backend/logistica/schemas.py
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

# --- EmpresaTransporte ---
class EmpresaTransporteBase(BaseModel):
    nombre: str
    
    # Datos Fiscales / Central
    cuit: Optional[str] = None
    condicion_iva_id: Optional[UUID] = None # UUID
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[str] = None # FK to Provincias

    # Contacto Central
    whatsapp: Optional[str] = None
    email: Optional[str] = None

    # Datos Operativos CABA
    direccion_despacho: Optional[str] = None
    horario_despacho: Optional[str] = None
    telefono_despacho: Optional[str] = None

    observaciones: Optional[str] = None

    web_tracking: Optional[str] = None
    telefono_reclamos: Optional[str] = None
    servicio_retiro_domicilio: bool = False
    requiere_carga_web: bool = False
    formato_etiqueta: str = 'PROPIA' # 'PROPIA', 'EXTERNA_PDF'
    activo: bool = True

class EmpresaTransporteCreate(EmpresaTransporteBase):
    pass

class EmpresaTransporteUpdate(BaseModel):
    nombre: Optional[str] = None
    cuit: Optional[str] = None
    condicion_iva_id: Optional[UUID] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[str] = None
    
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    
    direccion_despacho: Optional[str] = None
    horario_despacho: Optional[str] = None
    telefono_despacho: Optional[str] = None

    observaciones: Optional[str] = None
    web_tracking: Optional[str] = None
    telefono_reclamos: Optional[str] = None
    servicio_retiro_domicilio: Optional[bool] = None
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
    localidad: Optional[str] = None
    
    provincia_id: str
    
    telefono: Optional[str] = None
    email: Optional[str] = None

    es_punto_despacho: bool = False
    es_punto_retiro: bool = False
    horario_operativo: Optional[str] = None
    contacto_operativo: Optional[str] = None

class NodoTransporteCreate(NodoTransporteBase):
    empresa_id: UUID

class NodoTransporteUpdate(BaseModel):
    nombre_nodo: Optional[str] = None
    direccion_completa: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    es_punto_despacho: Optional[bool] = None
    es_punto_retiro: Optional[bool] = None
    horario_operativo: Optional[str] = None
    contacto_operativo: Optional[str] = None

class NodoTransporteResponse(NodoTransporteBase):
    id: UUID
    empresa_id: UUID
    class Config:
        from_attributes = True
