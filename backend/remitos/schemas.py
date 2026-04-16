# backend/remitos/schemas.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# --- ITEMS ---
class RemitoItemBase(BaseModel):
    pedido_item_id: int
    cantidad: float
    descripcion_display: Optional[str] = "Ítem"

class RemitoItemCreate(RemitoItemBase):
    pass

class PedidoItemMinimal(BaseModel):
    id: int
    nota: Optional[str] = ""
    producto_nombre: Optional[str] = None # Virtual field or via relationship

class RemitoItemResponse(RemitoItemBase):
    id: int
    remito_id: UUID
    pedido_item_id: int
    cantidad: float
    # Nested info for the UI (Populated from models.py properties)
    descripcion_display: Optional[str] = "Ítem"
    
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
    bultos: Optional[int] = None
    valor_declarado: Optional[float] = None
    razon_social: Optional[str] = None

class RemitoCreate(RemitoBase):
    pedido_id: int
    items: List[RemitoItemCreate]

class RemitoItemUpdate(BaseModel):
    id: Optional[int] = None # Si es nuevo, no tiene ID
    pedido_item_id: Optional[int] = None
    cantidad: float
    descripcion: Optional[str] = None # Para actualizar el PedidoItem.nota

class ForcedAddress(BaseModel):
    calle: str
    numero: Optional[str] = ""
    localidad: str
    provincia_id: Optional[str] = "X"

class RemitoUpdate(BaseModel):
    cliente_id: Optional[UUID] = None
    domicilio_entrega_id: Optional[UUID] = None
    nuevo_domicilio: Optional[ForcedAddress] = None
    transporte_id: Optional[UUID] = None
    fecha_salida: Optional[datetime] = None
    estado: Optional[str] = None
    numero_legal: Optional[str] = None
    aprobado_para_despacho: Optional[bool] = None
    cae: Optional[str] = None
    vto_cae: Optional[datetime] = None
    bultos: Optional[int] = None
    valor_declarado: Optional[float] = None
    items: Optional[List[RemitoItemUpdate]] = None

class RemitoResponse(RemitoBase):
    id: UUID
    pedido_id: int
    fecha_creacion: datetime
    items: List[RemitoItemResponse] = []
    
    # [V5] Extra info from models.py properties
    razon_social: Optional[str] = None
    cliente_id: Optional[UUID] = None
    
    class Config:
        from_attributes = True

# --- INGESTION PAYLOAD (PDF to Remito) ---
class IngestionCliente(BaseModel):
    id: Optional[str] = None
    cuit: Optional[str] = None
    razon_social: Optional[str] = None
    domicilio: Optional[str] = None
    condicion_iva: Optional[str] = None
    canal: Optional[str] = None
    domicilios_disponibles: Optional[List[dict]] = []

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
    transporte_id: Optional[UUID] = None # Permite elegir transporte en la UI de ingesta
    domicilio_id: Optional[UUID] = None # Permite elegir sucursal en la UI de ingesta
    bultos: Optional[int] = None
    valor_declarado: Optional[float] = None
    solo_actualizar_cliente: bool = False
    nuevo_domicilio: Optional[ForcedAddress] = None

# --- MANUAL REMITO (V15.1.4) ---
class ManualRemitoItem(BaseModel):
    descripcion: str
    cantidad: float
    codigo_visual: Optional[str] = None

class ManualRemitoPayload(BaseModel):
    cliente_id: Optional[str] = None # UUID
    cliente_nuevo: Optional[IngestionCliente] = None # Reuse ingestion structure
    domicilio_entrega_id: Optional[str] = None # UUID
    transporte_id: Optional[str] = None # UUID
    items: List[ManualRemitoItem]
    observaciones: Optional[str] = ""
    valor_declarado: Optional[float] = None
    bultos: Optional[int] = None
    aprobado_para_despacho: bool = True
