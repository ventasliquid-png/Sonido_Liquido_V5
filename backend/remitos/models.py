# backend/remitos/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base, GUID

class Remito(Base):
    """
    Cabeza de Remito (Viaje Físico).
    Desacopla la entrega de la facturación.
    """
    __tablename__ = "remitos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Vínculo Comercial
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, index=True)
    
    # Destino Físico (Sobrescribe al Pedido si es split)
    domicilio_entrega_id = Column(GUID(), ForeignKey("domicilios.id"), nullable=False)
    
    # Ejecutor Logístico
    transporte_id = Column(GUID(), ForeignKey("empresas_transporte.id"), nullable=False)
    
    # Datos Operativos
    fecha_salida = Column(DateTime, nullable=True) # Cuándo sale efectivamente
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Estado del Viaje
    # BORRADOR: Preparando
    # PREPARACION: En depósito armando cajas
    # EN_CAMINO: Salió
    # ENTREGADO: Confirmado por cliente
    # ANULADO: Cancelado
    estado = Column(String, default="BORRADOR") 
    
    # Identificación Legal / Tracking
    numero_legal = Column(String, nullable=True) # X-0001-000000...
    
    # GATEKEEPER FINANCIERO (Logic Gate)
    # Hereda del Pedido o se setea manual.
    # Si False, Depósito ve el remito pero NO puede cambiar estado a EN_CAMINO.
    aprobado_para_despacho = Column(Boolean, default=False)

    # Identificación Fiscal Manual (V5.X - Bridge Fallback)
    cae = Column(String, nullable=True)
    vto_cae = Column(DateTime, nullable=True)

    
    # Relaciones
    pedido = relationship("backend.pedidos.models.Pedido", backref="remitos")
    domicilio_entrega = relationship("backend.clientes.models.Domicilio")
    transporte = relationship("backend.logistica.models.EmpresaTransporte")
    
    items = relationship("RemitoItem", back_populates="remito", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Remito(id={self.id}, estado='{self.estado}')>"


class RemitoItem(Base):
    """
    Detalle del Remito (Qué va en la caja).
    """
    __tablename__ = "remitos_items"

    id = Column(Integer, primary_key=True, index=True)
    
    remito_id = Column(GUID(), ForeignKey("remitos.id"), nullable=False)
    
    # Trazabilidad Absoluta: Qué renglón del pedido estoy entregando
    pedido_item_id = Column(Integer, ForeignKey("pedidos_items.id"), nullable=False)
    
    # Cantidad Física en este viaje
    cantidad = Column(Float, default=0.0)
    
    # Relaciones
    remito = relationship("Remito", back_populates="items")
    pedido_item = relationship("backend.pedidos.models.PedidoItem")
    
    def __repr__(self):
        return f"<RemitoItem(cant={self.cantidad})>"
