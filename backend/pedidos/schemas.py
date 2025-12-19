from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class PedidoItemCreate(BaseModel):
    producto_id: int
    cantidad: float
    precio_unitario: float
    nota: Optional[str] = None

class PedidoItemUpdate(BaseModel):
    cantidad: Optional[float] = None
    precio_unitario: Optional[float] = None
    nota: Optional[str] = None

class PedidoCreate(BaseModel):
    cliente_id: UUID
    fecha: Optional[datetime] = None
    nota: Optional[str] = None
    oc: Optional[str] = None
    estado: Optional[str] = "PENDIENTE"
    tipo_facturacion: Optional[str] = "X"
    origen: Optional[str] = "DIRECTO"
    fecha_compromiso: Optional[datetime] = None
    items: List[PedidoItemCreate]

class PedidoUpdate(BaseModel):
    cliente_id: Optional[UUID] = None
    fecha: Optional[datetime] = None
    nota: Optional[str] = None
    oc: Optional[str] = None
    estado: Optional[str] = None
    tipo_facturacion: Optional[str] = None
    origen: Optional[str] = None
    fecha_compromiso: Optional[datetime] = None
    liberado_despacho: Optional[bool] = None

class ClienteSummary(BaseModel):
    id: UUID
    razon_social: str
    
    class Config:
        from_attributes = True

class ProductoSummary(BaseModel):
    id: int
    nombre: str
    
    class Config:
        from_attributes = True

class PedidoItemResponse(PedidoItemCreate):
    id: int
    subtotal: float
    producto: Optional[ProductoSummary] = None

    class Config:
        from_attributes = True

class PedidoResponse(BaseModel):
    id: int
    fecha: datetime
    cliente: Optional[ClienteSummary] = None
    total: float
    nota: Optional[str] = None
    estado: str
    tipo_facturacion: str
    origen: str
    fecha_compromiso: Optional[datetime] = None
    liberado_despacho: bool = False
    oc: Optional[str] = None
    items: List[PedidoItemResponse] = []

    class Config:
        from_attributes = True
