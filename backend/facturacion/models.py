# backend/facturacion/models.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Integer, Date, Enum, Numeric, DateTime, Table
from sqlalchemy.orm import relationship
from backend.core.database import Base, GUID

# N:M relationship between Facturas and Remitos to handle complex splits and consolidations
facturas_remitos = Table(
    'facturas_remitos',
    Base.metadata,
    Column('factura_id', GUID(), ForeignKey('facturas.id'), primary_key=True),
    Column('remito_id', GUID(), ForeignKey('remitos.id'), primary_key=True)
)

class Factura(Base):
    """
    Motor de Facturación (Soberanía Fiscal V5).
    Entidad que representa el comprobante final.
    """
    __tablename__ = "facturas"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    cliente_id = Column(GUID(), ForeignKey("clientes.id"), nullable=False, index=True)
    
    # Origen primario (opcional, una factura puede no venir de un pedido)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True, index=True) 
    
    # Clasificación Fiscal
    # FACTURA_A, FACTURA_B, PRESUPUESTO_X, NOTA_CREDITO_A, etc.
    tipo_comprobante = Column(String, default="PRESUPUESTO_X") 
    
    # Estado Operativo
    # BORRADOR: Calculando, modificable.
    # LIQUIDADA_MANUAL: Transición por bloqueo de ARCA, usuario copió datos.
    # AUTORIZADA_AFIP: Cierre definitivo, CAE obtenido.
    # ANULADA: Descartada.
    estado = Column(String, default="BORRADOR") 
    
    punto_venta = Column(Integer, nullable=True) # Ej: 3
    numero_comprobante = Column(Integer, nullable=True)
    fecha_emision = Column(Date, default=lambda: datetime.now(timezone.utc).date())
    
    # Data Financiera (Neto / Impuestos)
    # Se usa Float para consistencia con el core de Pedidos V5 anterior, 
    # aunque Numeric es preferido para sistemas puramente financieros.
    neto_gravado = Column(Float, default=0.0)
    iva_21 = Column(Float, default=0.0)
    iva_105 = Column(Float, default=0.0)
    exento = Column(Float, default=0.0)
    percepciones = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Sincronización ARCA
    cae = Column(String, nullable=True)
    vto_cae = Column(Date, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    cliente = relationship("Cliente")
    pedido = relationship("Pedido")
    items = relationship("FacturaItem", back_populates="factura", cascade="all, delete-orphan")
    remitos = relationship("Remito", secondary=facturas_remitos, backref="facturas")

    def __repr__(self):
        return f"<Factura(id={self.id}, tipo='{self.tipo_comprobante}', estado='{self.estado}')>"


class FacturaItem(Base):
    """
    Renglones de Facturación. 
    Desacoplados del Pedido para asegurar inmutabilidad fiscal.
    """
    __tablename__ = "facturas_items"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    factura_id = Column(GUID(), ForeignKey("facturas.id"), nullable=False)
    
    # Trazabilidad Operativa (De dónde salió este renglón)
    pedido_item_id = Column(Integer, ForeignKey("pedidos_items.id"), nullable=True)
    remito_item_id = Column(Integer, ForeignKey("remitos_items.id"), nullable=True)
    
    # Copia dura del concepto al momento de facturar
    descripcion = Column(String, nullable=False) 
    
    cantidad = Column(Float, default=1.0)
    precio_unitario_neto = Column(Float, default=0.0) # Precio LIBRE de impuestos
    
    # Impuestos por renglón
    alicuota_iva = Column(Float, default=21.0) # 21.0, 10.5, 0.0
    subtotal_neto = Column(Float, default=0.0) # cantidad * precio_unitario_neto
    
    # Relaciones
    factura = relationship("Factura", back_populates="items")
    pedido_item = relationship("PedidoItem")
    remito_item = relationship("RemitoItem")

    def __repr__(self):
        return f"<FacturaItem({self.cantidad}x '{self.descripcion}')>"
