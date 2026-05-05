# [IDENTIDAD] - backend\logistica\schemas.py
# Versión: V5.6 GOLD | Sincronización: 20260407130827
# ---------------------------------------------------------

# backend/logistica/schemas.py
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

# --- EmpresaTransporte ---
class EmpresaTransporteBase(BaseModel):
    nombre: str
    
    # [V5] Datos Fiscales
    cuit: Optional[str] = None
    condicion_iva_id: Optional[UUID] = None # UUID

    # Contacto Central
    whatsapp: Optional[str] = None
    email: Optional[str] = None

    observaciones: Optional[str] = None

    web_tracking: Optional[str] = None
    telefono_reclamos: Optional[str] = None
    formato_etiqueta: str = 'PROPIA' # 'PROPIA', 'EXTERNA_PDF'
    flags_estado: int = 3 # Existence + Active

class EmpresaTransporteCreate(EmpresaTransporteBase):
    pass

class EmpresaTransporteUpdate(BaseModel):
    nombre: Optional[str] = None
    # [V5]
    cuit: Optional[str] = None
    condicion_iva_id: Optional[UUID] = None
    
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    
    observaciones: Optional[str] = None
    web_tracking: Optional[str] = None
    telefono_reclamos: Optional[str] = None
    formato_etiqueta: Optional[str] = None
    flags_estado: Optional[int] = None

from backend.clientes.schemas import DomicilioResponse

class VinculoGeograficoResponse(BaseModel):
    id: UUID
    entidad_tipo: str
    entidad_id: UUID
    domicilio_id: UUID
    alias: Optional[str] = None
    flags_relacion: int = 0
    activo: bool = True
    domicilio: Optional[DomicilioResponse] = None

    class Config:
        from_attributes = True

class TransporteVinculoResponse(BaseModel):
    id: UUID # Vinculo ID
    persona_id: UUID
    tipo_contacto_id: str
    nombre: str # Persona name
    email: Optional[str] = None # Email laboral (Multiplex)
    telefono: Optional[str] = None # Teléfono escritorio (Multiplex)
    es_principal: bool = False
    rol: Optional[str] = None # Puesto (Multiplex)

    class Config:
        from_attributes = True

class EmpresaTransporteResponse(EmpresaTransporteBase):
    id: UUID
    vinculos_geograficos: List[VinculoGeograficoResponse] = []
    vinculos_multiplex: List[TransporteVinculoResponse] = [] # V6 Multiplex
    
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
