# Archivo: backend/clientes/models.py
# Módulo Clientes (V5) - Implementación Jerárquica (Nike S)

import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from core.database import Base

class Cliente(Base):
    """
    Tabla 'clientes' (La Cuenta).
    Representa la entidad comercial principal.
    """
    __tablename__ = "clientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    razon_social = Column(String, nullable=False, index=True)
    cuit = Column(String, unique=True, nullable=False, index=True)
    
    # Referencias a otras tablas (se asume que existen o existirán, por ahora UUID)
    condicion_iva_id = Column(UUID(as_uuid=True), nullable=True) # FK futura
    lista_precios_id = Column(UUID(as_uuid=True), nullable=True) # FK futura
    
    # Datos financieros
    saldo_actual = Column(Numeric(18, 2), default=0.00)
    
    # Protocolo Lázaro
    activo = Column(Boolean, default=True, nullable=False)
    
    # Auditoría
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    domicilios = relationship("Domicilio", back_populates="cliente", cascade="all, delete-orphan")
    contactos = relationship("Contacto", back_populates="cliente", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cliente(razon_social='{self.razon_social}', cuit='{self.cuit}')>"


class Domicilio(Base):
    """
    Tabla 'domicilios' (Logística).
    Soporte multi-sucursal.
    """
    __tablename__ = "domicilios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    
    calle = Column(String, nullable=True)
    numero = Column(String, nullable=True)
    localidad = Column(String, nullable=True)
    provincia = Column(String, nullable=True)
    
    # Flags de uso
    es_fiscal = Column(Boolean, default=False)
    es_entrega = Column(Boolean, default=False)
    
    # Logística
    transporte_id = Column(UUID(as_uuid=True), nullable=True) # FK futura
    zona_id = Column(UUID(as_uuid=True), nullable=True) # FK futura

    # Relaciones
    cliente = relationship("Cliente", back_populates="domicilios")

    def __repr__(self):
        return f"<Domicilio(calle='{self.calle}', localidad='{self.localidad}')>"


class Contacto(Base):
    """
    Tabla 'contactos' (Personas).
    """
    __tablename__ = "contactos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)

    # Relaciones
    cliente = relationship("Cliente", back_populates="contactos")

    def __repr__(self):
        return f"<Contacto(nombre='{self.nombre}')>"
