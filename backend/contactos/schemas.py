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

# --- Schemas CRUD ---

class ContactoBase(BaseModel):
    nombre: str
    apellido: str
    puesto: Optional[str] = None
    referencia_origen: Optional[str] = None
    domicilio_personal: Optional[str] = None
    
    # JSON Fields
    roles: Optional[List[str]] = [] # Listado de etiquetas
    canales: Optional[List[CanalContacto]] = [] # Listado de objetos canal
    
    notas: Optional[str] = None
    estado: bool = True
    
    # Foreign Keys (Opcionales, una u otra)
    cliente_id: Optional[UUID] = None
    transporte_id: Optional[UUID] = None

class ContactoCreate(ContactoBase):
    pass

class ContactoUpdate(ContactoBase):
    # En Update, todo es opcional, pero Pydantic lo maneja bien si pasamos partials
    # O redefinimos campos como Optional si queremos PATCH parcial estricto
    pass

# --- Schema de Respuesta (Lectura) ---

class ContactoRead(ContactoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Include metadatos simples del padre si fuera necesario, 
    # por ahora devolvemos IDs y que el frontend resuelva nombres si ya tiene los maestros.

    class Config:
        from_attributes = True
