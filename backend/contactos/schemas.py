# Archivo: backend/contactos/schemas.py
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

# --- Schemas de Valor (Embeddables) ---

class CanalContacto(BaseModel):
    tipo: str # WHATSAPP, EMAIL, TELEFONO, LINKEDIN
    valor: str
    etiqueta: Optional[str] = None # Ej: "Laboral", "Personal"

# --- Schemas CRUD (V6 Multiplex) ---

class ContactoBase(BaseModel):
    # Ahora mapea a Persona + Vinculo implícito
    nombre: str
    apellido: Optional[str] = None
    
    # Vinculo Data (Payload simplificado para creación)
    puesto: Optional[str] = None
    # referencia_origen maps to notas_vinculo or notas_globales? 
    # Logic: referencia_origen -> notas_vinculo usually.
    referencia_origen: Optional[str] = None 
    
    domicilio_personal: Optional[str] = None
    
    # JSON Fields
    roles: Optional[List[str]] = [] # Goes to Vinculo.roles
    canales: Optional[List[CanalContacto]] = [] # Goes to Vinculo.canales_laborales (User rule)
    
    notas: Optional[str] = None # Goes to Persona.notas_globales
    estado: bool = True     # Goes to Vinculo.activo
    
    # Foreign Keys (Entidad)
    cliente_id: Optional[UUID] = None
    transporte_id: Optional[UUID] = None

class ContactoCreate(ContactoBase):
    pass

class ContactoUpdate(ContactoBase):
    pass

# --- Schema de Respuesta (Lectura - Multiplex) ---

class VinculoRead(BaseModel):
    id: UUID
    entidad_tipo: str # CLIENTE, TRANSPORTE
    entidad_id: UUID
    rol: Optional[str] = None
    area: Optional[str] = None
    activo: bool
    canales_laborales: List[Any] = []
    fecha_inicio: Optional[Any] = None

    class Config:
        from_attributes = True

class ContactoRead(BaseModel):
    # Esto es en realidad una mezcla de Persona + Vinculos
    id: UUID # ID de Persona
    nombre: str
    apellido: Optional[str] = None
    nombre_completo: str # Property
    
    domicilio_personal: Optional[str] = None
    
    # Vinculos
    vinculos: List[VinculoRead] = []
    
    # Legacy fields support (Opcional, para no romper frontend si busca 'cliente_id' directo?)
    # Frontend usa 'vinculos' ahora si lo actualizamos.
    # Pero el usuario pidio: "Ya no debe tener cliente_id ni transporte_id directos."
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
