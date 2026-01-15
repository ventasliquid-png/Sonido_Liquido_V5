from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal
from uuid import UUID

# --- RUBROS ---

class RubroBase(BaseModel):
    codigo: str
    nombre: str
    padre_id: Optional[int] = None
    activo: bool = True
    margen_default: Decimal = Field(0.0, max_digits=6, decimal_places=2)

class RubroCreate(RubroBase):
    @validator('codigo')
    def validate_codigo(cls, v):
        if len(v) > 3:
            raise ValueError('El código no puede tener más de 3 caracteres')
        return v.upper()

class RubroUpdate(RubroBase):
    nombre: Optional[str] = None
    activo: Optional[bool] = None
    
    @validator('codigo')
    def validate_codigo(cls, v):
        if v is None:
            return v
        if len(v) > 3:
            raise ValueError('El código no puede tener más de 3 caracteres')
        return v.upper()

class RubroRead(RubroBase):
    id: int
    created_at: datetime
    hijos: List['RubroRead'] = []
    productos_count: int = 0

    class Config:
        from_attributes = True

# Necesario para la recursividad
RubroRead.update_forward_refs()

# --- COSTOS ---

class ProductoCostoBase(BaseModel):
    costo_reposicion: Decimal = Field(..., max_digits=12, decimal_places=4)
    # Roca Sólida Fields
    rentabilidad_target: Optional[Decimal] = Field(0.00, max_digits=6, decimal_places=2) # Antes margen
    precio_roca: Optional[Decimal] = Field(0.00, max_digits=12, decimal_places=2) # Base Real
    
    moneda_costo: str = 'ARS'
    iva_alicuota: Decimal = Field(21.00, max_digits=5, decimal_places=2)
    
    # Deprecados eliminados del schema

class ProductoCostoCreate(ProductoCostoBase):
    pass

class ProductoCostoRead(ProductoCostoBase):
    id: int
    producto_id: int

    class Config:
        from_attributes = True


# --- PRODUCTOS ---

class ProductoProveedorBase(BaseModel):
    proveedor_id: UUID
    costo: Decimal = Field(..., max_digits=12, decimal_places=4)
    moneda: str = 'ARS'
    observaciones: Optional[str] = None

class ProductoProveedorCreate(ProductoProveedorBase):
    pass

class ProductoProveedorRead(ProductoProveedorBase):
    id: int
    fecha: datetime
    # Optional: Nested Provider info if needed via service fetch
    
    class Config:
        from_attributes = True

class ProductoBase(BaseModel):
    codigo_visual: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    rubro_id: int
    unidad_medida: str = 'UN'
    activo: bool = True
    es_kit: bool = False

    # Campos Industriales (V5.2)
    tipo_producto: str = 'VENTA'
    unidad_stock_id: Optional[int] = None
    unidad_compra_id: Optional[int] = None
    factor_compra: Optional[Decimal] = 1.0
    venta_minima: Optional[Decimal] = 1.0 # V1.1.2: Minimum selling quantity
    proveedor_habitual_id: Optional[UUID] = None
    tasa_iva_id: Optional[int] = None

class ProductoCreate(ProductoBase):
    costos: ProductoCostoCreate

class ProductoUpdate(ProductoBase):
    nombre: Optional[str] = None
    rubro_id: Optional[int] = None
    costos: Optional[ProductoCostoCreate] = None
    
    # Campos Industriales Update
    tipo_producto: Optional[str] = None
    unidad_stock_id: Optional[int] = None
    unidad_compra_id: Optional[int] = None
    factor_compra: Optional[Decimal] = None
    venta_minima: Optional[Decimal] = None
    proveedor_habitual_id: Optional[UUID] = None
    tasa_iva_id: Optional[int] = None

class ProductoRead(ProductoBase):
    id: int
    sku: Optional[int] = None
    created_at: datetime
    rubro: Optional[RubroRead] = None
    costos: Optional[ProductoCostoRead] = None
    
    # New V5.4
    proveedores: List[ProductoProveedorRead] = []

    # Campos Calculados
    precio_mayorista: Optional[Decimal] = None
    precio_distribuidor: Optional[Decimal] = None
    precio_minorista: Optional[Decimal] = None

    class Config:
        from_attributes = True

    @validator('precio_mayorista', always=True, pre=True)
    def calculate_precio_mayorista(cls, v, values):
        return v
    
    # NOTA: Para simplificar, los precios calculados se deberían computar en el Service 
    # antes de pasar al Schema, o usar propiedades en el Modelo SQLAlchemy.
    # Por ahora los definimos como opcionales.

# --- MIGRATION WIZARD SCHEMAS ---

class RubroReadSimple(RubroBase):
    id: int
    class Config:
        from_attributes = True

class ProductoReadSimple(ProductoBase):
    id: int
    class Config:
        from_attributes = True

class RubroDependency(BaseModel):
    rubros_hijos: List[RubroReadSimple] = []
    productos: List[ProductoReadSimple] = []
    cantidad_hijos: int = 0
    cantidad_productos: int = 0

class RubroMigration(BaseModel):
    target_rubro_id: int
    new_status: bool = False

class RubroBulkMove(BaseModel):
    target_rubro_id: int
    subrubros_ids: List[int] = []
    productos_ids: List[int] = []

