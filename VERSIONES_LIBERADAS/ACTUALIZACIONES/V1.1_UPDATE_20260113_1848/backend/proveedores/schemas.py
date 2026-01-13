from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class ProveedorBase(BaseModel):
    razon_social: str
    cuit: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: bool = True

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(ProveedorBase):
    razon_social: Optional[str] = None
    activo: Optional[bool] = None

class ProveedorRead(ProveedorBase):
    id: UUID

    class Config:
        orm_mode = True
