# backend/agenda/schemas.py
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

# --- Persona ---
class PersonaBase(BaseModel):
    nombre_completo: str
    celular_personal: Optional[str] = None
    email_personal: Optional[EmailStr] = None
    linkedin: Optional[str] = None
    observaciones: Optional[str] = None
    activo: bool = True

class PersonaCreate(PersonaBase):
    pass

class PersonaUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    celular_personal: Optional[str] = None
    email_personal: Optional[EmailStr] = None
    linkedin: Optional[str] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None

class PersonaResponse(PersonaBase):
    id: UUID
    class Config:
        from_attributes = True

# --- VinculoComercial ---
class VinculoComercialBase(BaseModel):
    cliente_id: UUID
    persona_id: UUID
    tipo_contacto_id: str
    email_laboral: Optional[EmailStr] = None
    telefono_escritorio: Optional[str] = None
    es_principal: bool = False
    activo: bool = True

class VinculoComercialCreate(VinculoComercialBase):
    pass

class VinculoComercialUpdate(BaseModel):
    tipo_contacto_id: Optional[str] = None
    email_laboral: Optional[EmailStr] = None
    telefono_escritorio: Optional[str] = None
    es_principal: Optional[bool] = None
    activo: Optional[bool] = None

class VinculoComercialResponse(VinculoComercialBase):
    id: UUID
    # Include nested objects if needed, but for now keep it flat or use separate schema
    class Config:
        from_attributes = True
