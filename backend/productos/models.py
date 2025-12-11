from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from backend.core.database import Base

class Rubro(Base):
    __tablename__ = "rubros"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(3), unique=True, index=True, nullable=False)
    nombre = Column(String(50), unique=True, index=True, nullable=False)
    padre_id = Column(Integer, ForeignKey('rubros.id'), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    hijos = relationship("Rubro", backref=backref("padre", remote_side=[id]), uselist=True)
    productos = relationship("Producto", back_populates="rubro")

    @property
    def productos_count(self):
        return len(self.productos)

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    # [FIX PILOT] Removed Sequence for SQLite
    sku = Column(Integer, unique=True, index=True)
    codigo_visual = Column(String(30), unique=True, nullable=True, index=True)
    nombre = Column(String(150), index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    rubro_id = Column(Integer, ForeignKey('rubros.id'), nullable=False)
    
    # Logística de Compra
    proveedor_habitual_id = Column(UUID(as_uuid=True), ForeignKey('proveedores.id'), nullable=True)
    
    # Fiscal
    tasa_iva_id = Column(Integer, ForeignKey('tasas_iva.id'), nullable=True)
    
    # Naturaleza
    tipo_producto = Column(String, default='VENTA') # VENTA, INSUMO, MATERIA_PRIMA, SERVICIO

    # Matemática de Unidades
    unidad_stock_id = Column(Integer, ForeignKey('unidades.id'), nullable=True)
    unidad_compra_id = Column(Integer, ForeignKey('unidades.id'), nullable=True)
    factor_compra = Column(Numeric(10, 2), default=1.0)

    # Legacy (Deprecado pero mantenido por compatibilidad temporal)
    unidad_medida = Column(String(10), default='UN')
    
    activo = Column(Boolean, default=True)
    es_kit = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    rubro = relationship("Rubro", back_populates="productos")
    costos = relationship("ProductoCosto", uselist=False, back_populates="producto", cascade="all, delete-orphan")
    
    # Relaciones Satelitales
    proveedor_habitual = relationship("backend.proveedores.models.Proveedor")
    tasa_iva = relationship("backend.maestros.models.TasaIVA")
    unidad_stock = relationship("backend.maestros.models.Unidad", foreign_keys=[unidad_stock_id])
    unidad_compra = relationship("backend.maestros.models.Unidad", foreign_keys=[unidad_compra_id])

class ProductoCosto(Base):
    __tablename__ = "productos_costos"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), unique=True, nullable=False)
    costo_reposicion = Column(Numeric(12, 4), nullable=False)
    margen_mayorista = Column(Numeric(6, 2), nullable=False)
    moneda_costo = Column(String(3), default='ARS')
    iva_alicuota = Column(Numeric(5, 2), default=21.00)

    # Relaciones
    producto = relationship("Producto", back_populates="costos")
