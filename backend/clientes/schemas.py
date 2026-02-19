from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
import re
from backend.agenda.schemas import VinculoComercialCreate, VinculoComercialUpdate



# --- Domicilio Schemas ---
class DomicilioBase(BaseModel):
    alias: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    piso: Optional[str] = None
    depto: Optional[str] = None
    maps_link: Optional[str] = None
    notas_logistica: Optional[str] = None
    contacto_id: Optional[int] = None
    cp: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[str] = None
    activo: bool = True
    es_fiscal: bool = False
    es_entrega: bool = False
    transporte_id: Optional[UUID] = None
    intermediario_id: Optional[UUID] = None
    metodo_entrega: Optional[str] = None
    modalidad_envio: Optional[str] = None
    origen_logistico: Optional[str] = None
    observaciones: Optional[str] = None
    
    calle_entrega: Optional[str] = None
    numero_entrega: Optional[str] = None
    piso_entrega: Optional[str] = None
    depto_entrega: Optional[str] = None
    cp_entrega: Optional[str] = None
    localidad_entrega: Optional[str] = None
    provincia_entrega_id: Optional[str] = None

class DomicilioCreate(DomicilioBase):
    pass

class DomicilioUpdate(BaseModel):
    alias: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    piso: Optional[str] = None
    depto: Optional[str] = None
    maps_link: Optional[str] = None
    notas_logistica: Optional[str] = None
    contacto_id: Optional[int] = None
    cp: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[str] = None
    activo: Optional[bool] = None
    es_fiscal: Optional[bool] = None
    es_entrega: Optional[bool] = None
    transporte_id: Optional[UUID] = None
    intermediario_id: Optional[UUID] = None
    metodo_entrega: Optional[str] = None
    modalidad_envio: Optional[str] = None
    origen_logistico: Optional[str] = None

class DomicilioResponse(BaseModel):
    id: UUID
    cliente_id: UUID
    alias: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    piso: Optional[str] = None
    depto: Optional[str] = None
    maps_link: Optional[str] = None
    notas_logistica: Optional[str] = None
    contacto_id: Optional[int] = None
    cp: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[str] = None
    activo: bool = True
    es_fiscal: bool = False
    es_entrega: bool = False
    transporte_habitual_nodo_id: Optional[UUID] = None
    transporte_id: Optional[UUID] = None
    intermediario_id: Optional[UUID] = None
    metodo_entrega: Optional[str] = None
    modalidad_envio: Optional[str] = None
    origen_logistico: Optional[str] = None

    class Config:
        from_attributes = True

    @model_validator(mode='after')
    def parse_calle_pipe(self) -> 'DomicilioResponse':
        if self.calle and '|' in self.calle:
            parts = self.calle.split('|')
            self.calle = parts[0]
            if len(parts) > 1:
                self.piso = parts[1]
            if len(parts) > 2:
                self.depto = parts[2]
        return self

# --- Cliente Schemas ---
class ClienteBase(BaseModel):
    razon_social: str
    nombre_fantasia: Optional[str] = None
    # [V5-X] Hybrid Architecture: CUIT is optional
    cuit: Optional[str] = None
    
    # [V5-X] Hybrid Flags
    flags_estado: int = 0
    codigo_interno: Optional[int] = None
    
    condicion_iva_id: Optional[UUID] = None
    lista_precios_id: Optional[UUID] = None
    segmento_id: Optional[UUID] = None
    activo: Optional[bool] = True
    requiere_auditoria: Optional[bool] = False
    
    # Nuevos campos V5.1
    legacy_id_bas: Optional[str] = None
    whatsapp_empresa: Optional[str] = None
    web_portal_pagos: Optional[str] = None
    datos_acceso_pagos: Optional[str] = None
    observaciones: Optional[str] = None
    estado_arca: Optional[str] = "PENDIENTE"
    
    # Referencia al vendedor
    vendedor_id: Optional[int] = None
    estrategia_precio: Optional[str] = "MAYORISTA_FISCAL"

    @field_validator('cuit')
    @classmethod
    def clean_cuit(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return re.sub(r'[^0-9]', '', v)
        return v

class ClienteCreate(ClienteBase):
    domicilios: List[DomicilioCreate] = []
    vinculos: List[VinculoComercialCreate] = []

    # [V5-X] Pydantic Validator for Hybrid Logic
    @model_validator(mode='after')
    def check_fiscal_consistency(self):
        # Bitmasks constants (Hardcoded to avoid circular imports)
        FISCAL_REQUIRED = 0x004
        
        is_strict = (self.flags_estado & FISCAL_REQUIRED) != 0
        has_cuit = bool(self.cuit and len(self.cuit) > 5)
        
        if is_strict and not has_cuit:
            raise ValueError("Incoherencia: Flag FISCAL_REQUIRED activo pero falta CUIT (Modo Gold/Silver requiere CUIT).")
            
        if not is_strict and not self.razon_social:
             raise ValueError("Mínimo Vital: Un cliente Bronze requiere al menos Razón Social.")
             
        return self

class ClienteUpdate(BaseModel):
    razon_social: Optional[str] = None
    nombre_fantasia: Optional[str] = None
    cuit: Optional[str] = None
    flags_estado: Optional[int] = None
    condicion_iva_id: Optional[UUID] = None
    lista_precios_id: Optional[UUID] = None
    segmento_id: Optional[UUID] = None
    activo: Optional[bool] = None
    requiere_auditoria: Optional[bool] = None
    legacy_id_bas: Optional[str] = None
    whatsapp_empresa: Optional[str] = None
    web_portal_pagos: Optional[str] = None
    datos_acceso_pagos: Optional[str] = None
    observaciones: Optional[str] = None
    estado_arca: Optional[str] = None
    transporte_id: Optional[UUID] = None
    vendedor_id: Optional[int] = None
    estrategia_precio: Optional[str] = None

    @field_validator('cuit')
    @classmethod
    def clean_cuit_update(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return re.sub(r'[^0-9]', '', v)
        return v

from backend.contactos.schemas import ContactoRead, VinculoRead, PersonaBasicRead
from pydantic import computed_field

class ClienteVinculoResponse(BaseModel):
    """
    Schema híbrido para mostrar vinculos DESDE la perspectiva del Cliente.
    Muestra la Persona adjunta al vinculo.
    """
    id: UUID
    rol: Optional[str] = None
    area: Optional[str] = None
    activo: bool
    persona: Optional[PersonaBasicRead] = None # Nested Persona info (Basic to avoid recursion)

    class Config:
        from_attributes = True

class ClienteResponse(ClienteBase):
    id: UUID
    codigo_interno: Optional[int] = None
    saldo_actual: Optional[float] = 0.0
    contador_uso: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    domicilios: List[DomicilioResponse] = []
    # [GY-TEMP] Disable vinculos to fix 500 error on list view
    # vinculos: List[ClienteVinculoResponse] = []
    
    # Nuevos Campos Visuales (Propiedades @property del modelo)
    domicilio_fiscal_resumen: Optional[str] = None
    requiere_entrega: bool = False

    class Config:
        from_attributes = True

class ClienteListResponse(ClienteBase):
    id: UUID
    codigo_interno: Optional[int] = None
    saldo_actual: Optional[float] = 0.0
    contador_uso: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Nuevos Campos Visuales (Propiedades @property del modelo)
    domicilio_fiscal_resumen: Optional[str] = None
    requiere_entrega: bool = False
    # [GY-TEMP] Disable contacto_principal_nombre to fix 500 error on list view
    # contacto_principal_nombre: Optional[str] = None
    
    # Exclude nested lists for performance

    class Config:
        from_attributes = True

class ClienteSummary(BaseModel):
    id: UUID
    razon_social: str
    nombre_fantasia: Optional[str] = None
    domicilio_principal: Optional[str] = None
    lista_precios_nombre: Optional[str] = None
    segmento_nombre: Optional[str] = None
    lista_precios_id: Optional[UUID] = None
    segmento_id: Optional[UUID] = None
    activo: bool

    class Config:
        from_attributes = True

class CuitCheckResponse(BaseModel):
    status: str # NEW, EXISTS, INACTIVE
    existing_clients: List[ClienteSummary] = []
