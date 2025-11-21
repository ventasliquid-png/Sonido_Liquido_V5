from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# --- Contacto Schemas ---
class ContactoBase(BaseModel):
    nombre: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None

class ContactoCreate(ContactoBase):
    pass

class ContactoUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None

class ContactoResponse(ContactoBase):
    id: UUID
    cliente_id: UUID

    class Config:
        from_attributes = True

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

class DomicilioResponse(DomicilioBase):
    id: UUID
    cliente_id: UUID

    class Config:
        from_attributes = True

# --- Cliente Schemas ---
class ClienteBase(BaseModel):
    razon_social: str
    cuit: str
    condicion_iva_id: Optional[UUID] = None
    lista_precios_id: Optional[UUID] = None
    activo: bool = True

class ClienteCreate(ClienteBase):
    domicilios: List[DomicilioCreate] = []
    contactos: List[ContactoCreate] = []

class ClienteUpdate(BaseModel):
    razon_social: Optional[str] = None
    cuit: Optional[str] = None
    condicion_iva_id: Optional[UUID] = None
    lista_precios_id: Optional[UUID] = None
    activo: Optional[bool] = None

class ClienteResponse(ClienteBase):
    id: UUID
    saldo_actual: float
    created_at: datetime
    updated_at: datetime
    domicilios: List[DomicilioResponse] = []
    contactos: List[ContactoResponse] = []

    class Config:
        from_attributes = True
