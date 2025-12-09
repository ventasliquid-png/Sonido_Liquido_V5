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
        orm_mode = True

# Necesario para la recursividad
RubroRead.update_forward_refs()

# --- COSTOS ---

class ProductoCostoBase(BaseModel):
    costo_reposicion: Decimal = Field(..., max_digits=12, decimal_places=4)
    margen_mayorista: Decimal = Field(..., max_digits=6, decimal_places=2)
    moneda_costo: str = 'ARS'
    iva_alicuota: Decimal = Field(21.00, max_digits=5, decimal_places=2)

class ProductoCostoCreate(ProductoCostoBase):
    pass

class ProductoCostoRead(ProductoCostoBase):
    id: int
    producto_id: int

    class Config:
        orm_mode = True

# --- PRODUCTOS ---

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
    proveedor_habitual_id: Optional[UUID] = None
    tasa_iva_id: Optional[int] = None

class ProductoRead(ProductoBase):
    id: int
    sku: int
    created_at: datetime
    rubro: Optional[RubroRead] = None
    costos: Optional[ProductoCostoRead] = None

    # Campos Calculados
    precio_mayorista: Optional[Decimal] = None
    precio_distribuidor: Optional[Decimal] = None
    precio_minorista: Optional[Decimal] = None

    class Config:
        orm_mode = True

    @validator('precio_mayorista', always=True, pre=True)
    def calculate_precio_mayorista(cls, v, values):
        # Si viene del ORM, 'costos' estará en values (si se cargó)
        # Nota: values contiene los datos crudos del objeto ORM si from_orm es True? 
        # No, en Pydantic v1 values es un dict de campos ya validados.
        # Pero si usamos orm_mode, pydantic trata de sacar los datos del objeto.
        # Para campos calculados que dependen de relaciones, es mejor usar un getter property en el modelo o un validator que acceda al objeto original si es posible.
        # En Pydantic v1 con orm_mode, es complejo acceder al objeto original en validator.
        # Simplificación: El cálculo se hará en el servicio o se asume que el backend lo entrega.
        # O mejor, usamos un @root_validator(pre=True) para interceptar el objeto ORM.
        return v

    # NOTA: Para simplificar, los precios calculados se deberían computar en el Service 
    # antes de pasar al Schema, o usar propiedades en el Modelo SQLAlchemy.
    # Por ahora los definimos como opcionales.

# --- MIGRATION WIZARD SCHEMAS ---

class RubroReadSimple(RubroBase):
    id: int
    class Config:
        orm_mode = True

class ProductoReadSimple(ProductoBase):
    id: int
    class Config:
        orm_mode = True

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

