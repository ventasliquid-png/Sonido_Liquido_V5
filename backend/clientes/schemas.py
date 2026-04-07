# [IDENTIDAD] - backend\clientes\schemas.py
# Versión: V5.6 GOLD | Sincronización: 20260407130827
# ---------------------------------------------------------

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, computed_field
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
    is_active: bool = True
    activo: bool = True # Legacy
    es_fiscal: bool = False
    es_entrega: bool = False
    es_predeterminado: bool = False
    transporte_id: Optional[UUID] = None
    intermediario_id: Optional[UUID] = None
    metodo_entrega: Optional[str] = None
    modalidad_envio: Optional[str] = None
    origen_logistico: Optional[str] = None
    observaciones: Optional[str] = None
    is_maps_manual: bool = False 
    bit_identidad: int = 0 
    flags_infra: int = 0
    flags_estado: int = 0 # [V5.8] Genoma Soberano
    
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
    es_predeterminado: Optional[bool] = None
    transporte_id: Optional[UUID] = None
    intermediario_id: Optional[UUID] = None
    metodo_entrega: Optional[str] = None
    modalidad_envio: Optional[str] = None
    origen_logistico: Optional[str] = None
    
    calle_entrega: Optional[str] = None
    numero_entrega: Optional[str] = None
    piso_entrega: Optional[str] = None
    depto_entrega: Optional[str] = None
    cp_entrega: Optional[str] = None
    localidad_entrega: Optional[str] = None
    provincia_entrega_id: Optional[str] = None
    
    is_active: Optional[bool] = None
    bit_identidad: Optional[int] = None
    flags_infra: Optional[int] = None
    flags_estado: Optional[int] = None

class DomicilioResponse(BaseModel):
    id: UUID
    cliente_id: Optional[UUID] = None
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
    es_predeterminado: bool = False
    transporte_habitual_nodo_id: Optional[UUID] = None
    transporte_id: Optional[UUID] = None
    intermediario_id: Optional[UUID] = None
    metodo_entrega: Optional[str] = None
    origen_logistico: Optional[str] = None

    calle_entrega: Optional[str] = None
    numero_entrega: Optional[str] = None
    piso_entrega: Optional[str] = None
    depto_entrega: Optional[str] = None
    cp_entrega: Optional[str] = None
    localidad_entrega: Optional[str] = None
    provincia_entrega_id: Optional[str] = None

    usage_count: Optional[int] = 0
    provincia_nombre: Optional[str] = None 
    clientes_vinculados: Optional[List[str]] = [] 
    vinculos_detalles: Optional[List[dict]] = []  
    is_maps_manual: bool = False 
    bit_identidad: int = 0 
    flags_infra: int = 0
    flags_estado: int = 0

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
    cuit: Optional[str] = None
    
    flags_estado: int = 0
    codigo_interno: Optional[int] = None
    
    condicion_iva_id: Optional[UUID] = None
    lista_precios_id: Optional[UUID] = None
    segmento_id: Optional[UUID] = None
    activo: Optional[bool] = True
    requiere_auditoria: Optional[bool] = False
    
    legacy_id_bas: Optional[str] = None
    whatsapp_empresa: Optional[str] = None
    web_portal_pagos: Optional[str] = None
    datos_acceso_pagos: Optional[str] = None
    observaciones: Optional[str] = None
    estado_arca: Optional[str] = "PENDIENTE"
    
    vendedor_id: Optional[int] = None
    estrategia_precio: Optional[str] = "MAYORISTA_FISCAL"
    fecha_alta: Optional[datetime] = None
    transporte_habitual_id: Optional[UUID] = None

    @field_validator('cuit')
    @classmethod
    def clean_cuit(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return re.sub(r'[^0-9]', '', v)
        return v

class ClienteCreate(ClienteBase):
    domicilios: List[DomicilioCreate] = []
    vinculos: List[VinculoComercialCreate] = []

    @model_validator(mode='after')
    def check_fiscal_consistency(self):
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
    transporte_habitual_id: Optional[UUID] = None
    vendedor_id: Optional[int] = None
    estrategia_precio: Optional[str] = None
    fecha_alta: Optional[datetime] = None

    @field_validator('cuit')
    @classmethod
    def clean_cuit_update(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return re.sub(r'[^0-9]', '', v)
        return v

from backend.contactos.schemas import ContactoRead, VinculoRead, PersonaBasicRead
from pydantic import computed_field

class ClienteVinculoResponse(BaseModel):
    id: UUID
    rol: Optional[str] = None
    area: Optional[str] = None
    activo: bool
    persona: Optional[PersonaBasicRead] = None 

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
    domicilio_fiscal_resumen: Optional[str] = None
    requiere_entrega: bool = False
    fecha_alta: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClienteListResponse(ClienteBase):
    id: UUID
    codigo_interno: Optional[int] = None
    saldo_actual: Optional[float] = 0.0
    contador_uso: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    domicilio_fiscal_resumen: Optional[str] = None
    requiere_entrega: bool = False
    fecha_alta: Optional[datetime] = None
    
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
    status: str 
    existing_clients: List[ClienteSummary] = []
