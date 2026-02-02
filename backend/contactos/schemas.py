from datetime import datetime
from uuid import UUID
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

# --- VINCULOS / ROLES ---
class VinculoRead(BaseModel):
    id: UUID
    entidad_tipo: str # CLIENTE, TRANSPORTE
    entidad_id: UUID
    
    tipo_contacto_id: Optional[str] = None # [Legacy V5]
    
    rol: Optional[str] = None
    area: Optional[str] = None
    activo: bool
    canales_laborales: Optional[List[Dict[str, Any]]] = None
    fecha_inicio: Optional[Any] = None

    class Config:
        from_attributes = True

class VinculoUpdate(BaseModel):
    # Update specific link fields
    tipo_contacto_id: Optional[str] = None
    rol: Optional[str] = None
    puesto: Optional[str] = None # Legacy Alias
    activo: Optional[bool] = None

# --- CONTACTOS (PERSONAS) ---
class PersonaBasicRead(BaseModel):
    id: UUID
    nombre: str
    apellido: Optional[str] = None
    nombre_completo: str
    domicilio_personal: Optional[str] = None
    canales_personales: Optional[List[Dict[str, Any]]] = None
    notas_globales: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContactoRead(BaseModel):
    # Esto es en realidad una mezcla de Persona + Vinculos
    id: UUID # ID de Persona
    nombre: str
    apellido: Optional[str] = None
    nombre_completo: str # Property
    
    domicilio_personal: Optional[str] = None
    canales_personales: Optional[List[Dict[str, Any]]] = None # [FIX] Include Personal Channels
    notas_globales: Optional[str] = None # [FIX] Include Notes
    
    # Vinculos
    vinculos: List[VinculoRead] = []
    
    # Legacy fields support (Opcional, para no romper frontend si busca 'cliente_id' directo?)
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContactoCreate(BaseModel):
    nombre: str
    apellido: Optional[str] = None
    notas: Optional[str] = None # Mapped to notas_globales
    domicilio_personal: Optional[str] = None
    
    # Canales Personales
    canales: Optional[List[Dict[str, Any]]] = None
    
    # Vinculo Inicial (Opcional)
    cliente_id: Optional[UUID] = None
    transporte_id: Optional[UUID] = None
    
    tipo_contacto_id: Optional[str] = None
    puesto: Optional[str] = None # Mapped to rol
    roles: List[str] = []
    
    estado: bool = True # Activo
    referencia_origen: Optional[str] = None

class ContactoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    notas: Optional[str] = None
    domicilio_personal: Optional[str] = None
    
    canales: Optional[List[Dict[str, Any]]] = None
    
    # Update Vinculo Principal fields
    # (Frontend sends these along with persona data sometimes)
    cliente_id: Optional[UUID] = None
    transporte_id: Optional[UUID] = None
    
    tipo_contacto_id: Optional[str] = None
    puesto: Optional[str] = None
    roles: Optional[List[str]] = None
    estado: Optional[bool] = None
