# Archivo: backend/clientes/models.py
# Módulo Clientes (V5) - Implementación Jerárquica (Nike S)

import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Text, DateTime, Integer, Sequence
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
    nombre_fantasia = Column(String, nullable=True)
    cuit = Column(String, unique=False, nullable=False, index=True)
    
    # Identificadores
    codigo_interno = Column(Integer, Sequence("clientes_codigo_interno_seq", start=1000), nullable=True)
    legacy_id_bas = Column(String, nullable=True) # ID del sistema BAS anterior

    # Comunicación y Pagos
    whatsapp_empresa = Column(String, nullable=True)
    web_portal_pagos = Column(String, nullable=True)
    datos_acceso_pagos = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    
    # Referencias a otras tablas
    condicion_iva_id = Column(UUID(as_uuid=True), ForeignKey("condiciones_iva.id"), nullable=True)
    lista_precios_id = Column(UUID(as_uuid=True), ForeignKey("listas_precios.id"), nullable=True)
    segmento_id = Column(UUID(as_uuid=True), ForeignKey("segmentos.id"), nullable=True)
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # Account Manager
    
    # Datos financieros
    saldo_actual = Column(Numeric(18, 2), default=0.00)
    
    # Protocolo Lázaro
    activo = Column(Boolean, default=True, nullable=False)
    requiere_auditoria = Column(Boolean, default=False)
    
    # Ranking de Uso (V5.2)
    contador_uso = Column(Integer, default=0)

    # Auditoría
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    domicilios = relationship("Domicilio", back_populates="cliente", cascade="all, delete-orphan")
    vinculos = relationship("backend.agenda.models.VinculoComercial", back_populates="cliente")
    condicion_iva = relationship("backend.maestros.models.CondicionIva")
    lista_precios = relationship("backend.maestros.models.ListaPrecios")
    segmento = relationship("backend.maestros.models.Segmento")
    vendedor = relationship("backend.auth.models.Usuario")

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
    
    alias = Column(String, nullable=True) # "Depósito Norte"
    calle = Column(String, nullable=True)
    numero = Column(String, nullable=True)
    cp = Column(String, nullable=True)
    localidad = Column(String, nullable=True)
    provincia_id = Column(String(1), ForeignKey("provincias.id"), nullable=True)
    
    # Flags de uso
    es_fiscal = Column(Boolean, default=False)
    es_entrega = Column(Boolean, default=False)
    
    # Logística
    transporte_habitual_nodo_id = Column(UUID(as_uuid=True), ForeignKey("nodos_transporte.id"), nullable=True)
    transporte_id = Column(UUID(as_uuid=True), ForeignKey("empresas_transporte.id"), nullable=True)
    intermediario_id = Column(UUID(as_uuid=True), ForeignKey("empresas_transporte.id"), nullable=True)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="domicilios")
    provincia = relationship("backend.maestros.models.Provincia")
    transporte_habitual_nodo = relationship("backend.logistica.models.NodoTransporte")
    transporte = relationship("backend.logistica.models.EmpresaTransporte", foreign_keys=[transporte_id])
    intermediario = relationship("backend.logistica.models.EmpresaTransporte", foreign_keys=[intermediario_id])

    def __repr__(self):
        return f"<Domicilio(alias='{self.alias}', calle='{self.calle}')>"
