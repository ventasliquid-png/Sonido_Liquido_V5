# backend/remitos/schemas.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# --- ITEMS ---
class RemitoItemBase(BaseModel):
    pedido_item_id: int
    cantidad: float

class RemitoItemCreate(RemitoItemBase):
    pass

class RemitoItemResponse(RemitoItemBase):
    id: int
    remito_id: UUID
    class Config:
        from_attributes = True

# --- HEADER ---
class RemitoBase(BaseModel):
    domicilio_entrega_id: UUID
    transporte_id: UUID
    fecha_salida: Optional[datetime] = None
    estado: Optional[str] = "BORRADOR"
    numero_legal: Optional[str] = None
    aprobado_para_despacho: bool = False
    cae: Optional[str] = None
    vto_cae: Optional[datetime] = None

class RemitoCreate(RemitoBase):
    pedido_id: int
    items: List[RemitoItemCreate]

class RemitoUpdate(BaseModel):
    domicilio_entrega_id: Optional[UUID] = None
    transporte_id: Optional[UUID] = None
    fecha_salida: Optional[datetime] = None
    estado: Optional[str] = None
    numero_legal: Optional[str] = None
    aprobado_para_despacho: Optional[bool] = None
    cae: Optional[str] = None
    vto_cae: Optional[datetime] = None

class RemitoResponse(RemitoBase):
    id: UUID
    pedido_id: int
    fecha_creacion: datetime
    items: List[RemitoItemResponse] = []
    
    class Config:
        from_attributes = True

# --- INGESTION PAYLOAD (PDF to Remito) ---
class IngestionCliente(BaseModel):
    cuit: Optional[str] = None
    razon_social: Optional[str] = None

class IngestionFactura(BaseModel):
    numero: Optional[str] = None
    cae: Optional[str] = None
    vto_cae: Optional[str] = None # String dd/mm/yyyy

class IngestionItem(BaseModel):
    codigo: Optional[str] = None
    descripcion: str
    cantidad: float
    precio_unitario: Optional[float] = None

class IngestionPayload(BaseModel):
    cliente: IngestionCliente
    factura: IngestionFactura
    items: List[IngestionItem]
