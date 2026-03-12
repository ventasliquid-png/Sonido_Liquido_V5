"""
Módulo Rubros (V1.0): Esquemas Pydantic.
Define los modelos de datos de entrada (Create/Update) y salida (Out) para la API.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# --- Esquemas de Rubro ---

class RubroBase(BaseModel):
    codigo: str = Field(..., max_length=3, description="Código único de 3 caracteres (siempre mayúsculas)")
    descripcion: str = Field(..., max_length=30, description="Descripción del rubro")
    padre_id: Optional[int] = Field(None, description="ID del rubro padre (para subrubros)")

    @field_validator('codigo')
    @classmethod
    def codigo_uppercase(cls, v: str) -> str:
        """Fuerza el código a mayúsculas."""
        return v.upper().strip()

class RubroCreate(RubroBase):
    """Esquema para crear un nuevo rubro."""
    pass

class RubroUpdate(BaseModel):
    """Esquema para actualizar un rubro (todos los campos opcionales)."""
    descripcion: Optional[str] = Field(None, max_length=30)
    activo: Optional[bool] = None
    padre_id: Optional[int] = None

class RubroOut(RubroBase):
    """Esquema de salida con todos los campos del rubro."""
    id: int
    activo: bool
    padre_id: Optional[int]
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RubroLazaroResponse(BaseModel):
    """Respuesta especial para el protocolo Lázaro (código inactivo encontrado)."""
    exists_inactive: bool
    rubro_inactivo: Optional[RubroOut] = None
    message: str

print("--- [Rubros V1.0]: Schemas (Pydantic) definidos. ---")

