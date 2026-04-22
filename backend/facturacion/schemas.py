from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID

# Shared properties
class FacturaItemBase(BaseModel):
    descripcion: str
    cantidad: float
    precio_unitario_neto: float
    alicuota_iva: float
    subtotal_neto: float
    pedido_item_id: Optional[int] = None
    remito_item_id: Optional[int] = None

class FacturaItemCreate(FacturaItemBase):
    pass

class FacturaItemResponse(FacturaItemBase):
    id: int
    factura_id: UUID

    model_config = ConfigDict(from_attributes=True)


class FacturaBase(BaseModel):
    cliente_id: UUID
    pedido_id: Optional[int] = None
    tipo_comprobante: str = "PRESUPUESTO_X"
    estado: str = "BORRADOR"
    punto_venta: Optional[int] = None
    numero_comprobante: Optional[int] = None
    fecha_emision: Optional[date] = None
    
    neto_gravado: float = 0.0
    iva_21: float = 0.0
    iva_105: float = 0.0
    exento: float = 0.0
    percepciones: float = 0.0
    total: float = 0.0

class FacturaCreate(FacturaBase):
    items: List[FacturaItemCreate]

class FacturaUpdate(BaseModel):
    estado: Optional[str] = None
    cae: Optional[str] = None
    vto_cae: Optional[date] = None
    punto_venta: Optional[int] = None
    numero_comprobante: Optional[int] = None

class FacturaResponse(FacturaBase):
    id: UUID
    cae: Optional[str]
    vto_cae: Optional[date]
    created_at: datetime
    items: List[FacturaItemResponse]
    
    # Aditional data could be added for frontend rendering (cliente name, etc)
    model_config = ConfigDict(from_attributes=True)
