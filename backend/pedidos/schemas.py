# [IDENTIDAD] - backend\pedidos\schemas.py
# Versión: V5.6 GOLD | Sincronización: 20260407130827
# ---------------------------------------------------------

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
    oc_override: Optional[bool] = False
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
    duplicate_confirmed: Optional[bool] = False
    from_ingesta: Optional[bool] = False
    pedido_origen_migracion_id: Optional[int] = None
    flags_estado: Optional[int] = 0

class NoComercialRequest(BaseModel):
    is_no_comercial: bool
    usuario: Optional[str] = "Sistema"

class PedidoUpdate(BaseModel):
    cliente_id: Optional[UUID] = None
    fecha: Optional[datetime] = None
    nota: Optional[str] = None
    oc: Optional[str] = None
    oc_override: Optional[bool] = None
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
    from_ingesta: Optional[bool] = False

class CondicionIvaSummary(BaseModel):
    nombre: str
    class Config:
        from_attributes = True


class SegmentoSummary(BaseModel):
    nombre: str
    class Config:
        from_attributes = True

class DomicilioSummary(BaseModel):
    id: UUID
    alias: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    piso: Optional[str] = None
    depto: Optional[str] = None
    localidad: Optional[str] = None
    cp: Optional[str] = None
    es_fiscal: bool = False
    es_entrega: bool = False
    es_predeterminado: bool = False
    activo: bool = True
    transporte_id: Optional[UUID] = None
    transporte_habitual_nodo_id: Optional[UUID] = None
    notas_logistica: Optional[str] = None
    metodo_entrega: Optional[str] = None

    class Config:
        from_attributes = True

class ClienteSummary(BaseModel):
    id: UUID
    razon_social: str
    cuit: Optional[str] = None
    domicilio_fiscal_resumen: Optional[str] = None
    condicion_iva: Optional[CondicionIvaSummary] = None
    segmento: Optional[SegmentoSummary] = None
    flags_estado: int = 0
    domicilios: List[DomicilioSummary] = []
    transporte_habitual_id: Optional[UUID] = None

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
    cantidad_entregada: float = 0.0
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
    contacto_responsable_id: Optional[UUID] = None
    nodo_transporte_id:      Optional[UUID] = None
    costo_envio_cliente: Optional[float] = 0.0
    costo_flete_interno: Optional[float] = 0.0
    estado_logistico: str = "PENDIENTE"
    flags_estado: int = 0

    items: List[PedidoItemResponse] = []

    class Config:
        from_attributes = True
