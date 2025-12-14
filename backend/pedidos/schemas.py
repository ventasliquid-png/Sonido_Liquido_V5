from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class PedidoItemCreate(BaseModel):
    producto_id: int
    cantidad: float
    precio_unitario: float
    nota: Optional[str] = None

class PedidoCreate(BaseModel):
    cliente_id: UUID
    fecha: Optional[datetime] = None
    nota: Optional[str] = None
    items: List[PedidoItemCreate]

class PedidoItemResponse(PedidoItemCreate):
    id: int
    subtotal: float
    producto_nombre: Optional[str] = None # Enriched

    class Config:
        from_attributes = True

class PedidoResponse(BaseModel):
    id: int
    fecha: datetime
    cliente_id: UUID
    total: float
    nota: Optional[str] = None
    estado: str
    items: List[PedidoItemResponse] = []

    class Config:
        from_attributes = True
