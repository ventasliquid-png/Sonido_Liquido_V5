# backend/maestros/schemas.py
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class ProvinciaResponse(BaseModel):
    id: str
    nombre: str
    class Config:
        from_attributes = True

class TipoContactoResponse(BaseModel):
    id: str
    nombre: str
    class Config:
        from_attributes = True

class CondicionIvaResponse(BaseModel):
    id: UUID
    nombre: str
    class Config:
        from_attributes = True

class ListaPreciosResponse(BaseModel):
    id: UUID
    nombre: str
    activo: bool
    class Config:
        from_attributes = True
