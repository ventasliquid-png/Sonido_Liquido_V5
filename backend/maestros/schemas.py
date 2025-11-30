# backend/maestros/schemas.py
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal

class ProvinciaBase(BaseModel):
    id: str
    nombre: str

class ProvinciaCreate(ProvinciaBase):
    pass

class ProvinciaUpdate(BaseModel):
    nombre: Optional[str] = None

class ProvinciaResponse(ProvinciaBase):
    class Config:
        from_attributes = True

class TipoContactoBase(BaseModel):
    id: str
    nombre: str

class TipoContactoCreate(TipoContactoBase):
    pass

class TipoContactoUpdate(BaseModel):
    nombre: Optional[str] = None

class TipoContactoResponse(TipoContactoBase):
    class Config:
        from_attributes = True

class CondicionIvaBase(BaseModel):
    nombre: str

class CondicionIvaCreate(CondicionIvaBase):
    pass

class CondicionIvaUpdate(BaseModel):
    nombre: Optional[str] = None

class CondicionIvaResponse(CondicionIvaBase):
    id: UUID
    class Config:
        from_attributes = True

# --- Lista Precios ---
class ListaPreciosBase(BaseModel):
    nombre: str
    coeficiente: Decimal = 1.0
    tipo: str = 'PRESUPUESTO' # 'FISCAL', 'PRESUPUESTO'
    activo: bool = True

class ListaPreciosCreate(ListaPreciosBase):
    pass

class ListaPreciosUpdate(BaseModel):
    nombre: Optional[str] = None
    coeficiente: Optional[Decimal] = None
    tipo: Optional[str] = None
    activo: Optional[bool] = None

class ListaPreciosResponse(ListaPreciosBase):
    id: UUID
    class Config:
        from_attributes = True

# --- Segmento ---
class SegmentoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True

class SegmentoCreate(SegmentoBase):
    pass

class SegmentoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

class SegmentoResponse(SegmentoBase):
    id: UUID
    class Config:
        from_attributes = True

# --- Vendedor ---
class VendedorBase(BaseModel):
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    comision_porcentaje: Decimal = 0
    cbu_alias: Optional[str] = None
    activo: bool = True

class VendedorCreate(VendedorBase):
    pass

class VendedorUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    comision_porcentaje: Optional[Decimal] = None
    cbu_alias: Optional[str] = None
    activo: Optional[bool] = None

class VendedorResponse(VendedorBase):
    id: UUID
    class Config:
        from_attributes = True
