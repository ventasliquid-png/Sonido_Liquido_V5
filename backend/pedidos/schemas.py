from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime
from uuid import UUID

class PedidoItemCreate(BaseModel):
    producto_id: int
    cantidad: float
    precio_unitario: float
    descuento_porcentaje: Optional[float] = 0.0
    descuento_importe: Optional[float] = 0.0
    nota: Optional[str] = None

class PedidoItemUpdate(BaseModel):
    cantidad: Optional[float] = None
    precio_unitario: Optional[float] = None
    descuento_porcentaje: Optional[float] = None
    descuento_importe: Optional[float] = None
    nota: Optional[str] = None

class PedidoCreate(BaseModel):
    cliente_id: UUID
    fecha: Optional[datetime] = None
    nota: Optional[str] = None
    oc: Optional[str] = None
    estado: Optional[str] = "PENDIENTE"
    tipo_facturacion: Optional[str] = "X"
    origen: Optional[str] = "DIRECTO"
    descuento_global_porcentaje: Optional[float] = 0.0
    descuento_global_importe: Optional[float] = 0.0
    fecha_compromiso: Optional[datetime] = None
    
    # Logística
    domicilio_entrega_id: Optional[UUID] = None
    transporte_id: Optional[UUID] = None
    costo_envio_cliente: Optional[float] = 0.0
    costo_flete_interno: Optional[float] = 0.0
    estado_logistico: Optional[str] = "PENDIENTE"
    
    items: List[PedidoItemCreate]

class PedidoUpdate(BaseModel):
    cliente_id: Optional[UUID] = None
    fecha: Optional[datetime] = None
    nota: Optional[str] = None
    oc: Optional[str] = None
    estado: Optional[str] = None
    tipo_facturacion: Optional[str] = None
    origen: Optional[str] = None
    descuento_global_porcentaje: Optional[float] = None
    descuento_global_importe: Optional[float] = None
    fecha_compromiso: Optional[datetime] = None
    liberado_despacho: Optional[bool] = None

    # Logística
    domicilio_entrega_id: Optional[UUID] = None
    transporte_id: Optional[UUID] = None
    costo_envio_cliente: Optional[float] = None
    costo_flete_interno: Optional[float] = None
    estado_logistico: Optional[str] = None

    items: Optional[List[PedidoItemCreate]] = None

class CondicionIvaSummary(BaseModel):
    nombre: str
    class Config:
        from_attributes = True


class SegmentoSummary(BaseModel):
    nombre: str
    class Config:
        from_attributes = True

class ClienteSummary(BaseModel):
    id: UUID
    razon_social: str
    cuit: Optional[str] = None
    domicilio_fiscal_resumen: Optional[str] = None
    condicion_iva: Optional[CondicionIvaSummary] = None
    segmento: Optional[SegmentoSummary] = None
    
    class Config:
        from_attributes = True

class ProductoSummary(BaseModel):
    id: int
    sku: Optional[Union[str, int]] = None
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
    descuento_global_porcentaje: float = 0.0
    descuento_global_importe: float = 0.0

    # Logística
    domicilio_entrega_id: Optional[UUID] = None
    transporte_id: Optional[UUID] = None
    costo_envio_cliente: Optional[float] = 0.0
    costo_flete_interno: Optional[float] = 0.0
    estado_logistico: str = "PENDIENTE"

    items: List[PedidoItemResponse] = []

    class Config:
        from_attributes = True
