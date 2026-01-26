from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base, GUID

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.now)
    cliente_id = Column(GUID(), ForeignKey("clientes.id"), nullable=False)
    total = Column(Float, default=0.0)
    nota = Column(Text, nullable=True)
    estado = Column(String, default="PENDIENTE") # PENDIENTE, RESERVADO, CUMPLIDO, ANULADO, BORRADOR
    tipo_facturacion = Column(String, default="X") # A, B, X
    origen = Column(String, default="DIRECTO") # MELI, TIENDA, DIRECTO
    fecha_compromiso = Column(DateTime, nullable=True) # Para pedidos con entrega futura
    liberado_despacho = Column(Boolean, default=False)
    oc = Column(String, nullable=True) # Orden de Compra
    
    # Descuento Global
    descuento_global_porcentaje = Column(Float, default=0.0)
    descuento_global_importe = Column(Float, default=0.0)
    
    # Logística (V5.6)
    domicilio_entrega_id = Column(GUID(), ForeignKey("domicilios.id"), nullable=True)
    transporte_id = Column(GUID(), ForeignKey("empresas_transporte.id"), nullable=True)
    
    # Costos Logísticos (MVP)
    costo_envio_cliente = Column(Float, default=0.0) # Lo que paga el cliente
    costo_flete_interno = Column(Float, default=0.0) # Costo "Alberto"
    estado_logistico = Column(String, default="PENDIENTE") # PENDIENTE, EN_PREPARACION, DESPACHADO, ENTREGADO

    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="pedidos")
    items = relationship("PedidoItem", back_populates="pedido", cascade="all, delete-orphan")
    domicilio_entrega = relationship("backend.clientes.models.Domicilio")
    transporte = relationship("backend.logistica.models.EmpresaTransporte")

class PedidoItem(Base):
    __tablename__ = "pedidos_items"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    cantidad = Column(Float, default=1.0)
    precio_unitario = Column(Float, default=0.0)
    
    # Descuentos por ítem
    descuento_porcentaje = Column(Float, default=0.0)
    descuento_importe = Column(Float, default=0.0)
    
    subtotal = Column(Float, default=0.0)
    nota = Column(String, nullable=True)
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")
