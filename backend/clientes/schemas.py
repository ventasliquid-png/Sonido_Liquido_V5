from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field



# --- Domicilio Schemas ---
class DomicilioBase(BaseModel):
    calle: Optional[str] = None
    numero: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    es_fiscal: bool = False
    es_entrega: bool = False
    transporte_id: Optional[UUID] = None
    zona_id: Optional[UUID] = None

class DomicilioCreate(DomicilioBase):
    pass

class DomicilioUpdate(BaseModel):
    calle: Optional[str] = None
    numero: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    es_fiscal: Optional[bool] = None
    es_entrega: Optional[bool] = None
    transporte_id: Optional[UUID] = None
    zona_id: Optional[UUID] = None

class DomicilioResponse(BaseModel):
    id: UUID
    cliente_id: UUID
    alias: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[str] = None
    es_fiscal: bool = False
    es_entrega: bool = False
    transporte_habitual_nodo_id: Optional[UUID] = None

    class Config:
        from_attributes = True

# --- Cliente Schemas ---
class ClienteBase(BaseModel):
    razon_social: str
    cuit: str
    condicion_iva_id: Optional[UUID] = None
    lista_precios_id: Optional[UUID] = None
    activo: bool = True
    
    # Nuevos campos V5.1
    legacy_id_bas: Optional[str] = None
    whatsapp_empresa: Optional[str] = None
    web_portal_pagos: Optional[str] = None
    datos_acceso_pagos: Optional[str] = None

class ClienteCreate(ClienteBase):
    domicilios: List[DomicilioCreate] = []

class ClienteUpdate(BaseModel):
    razon_social: Optional[str] = None
    cuit: Optional[str] = None
    condicion_iva_id: Optional[UUID] = None
    lista_precios_id: Optional[UUID] = None
    activo: Optional[bool] = None
    legacy_id_bas: Optional[str] = None
    whatsapp_empresa: Optional[str] = None
    web_portal_pagos: Optional[str] = None
    datos_acceso_pagos: Optional[str] = None

from backend.agenda.schemas import VinculoComercialResponse

class ClienteResponse(ClienteBase):
    id: UUID
    codigo_interno: int
    saldo_actual: float
    created_at: datetime
    updated_at: datetime
    domicilios: List[DomicilioResponse] = []
    vinculos: List[VinculoComercialResponse] = []

    class Config:
        from_attributes = True
