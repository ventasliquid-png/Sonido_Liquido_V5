# Archivo: backend/contactos/models.py
# Módulo: Agenda Contactos (Global)
# Color Identidad: ÍNDIGO / VIOLETA

import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from backend.core.database import Base, GUID

class Contacto(Base):
    """
    Tabla 'contactos' (Agenda Global).
    Representa personas físicas asociadas a Clientes o Transportes.
    Identidad Visual: Indigo/Purple.
    """
    __tablename__ = "contactos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # --- Polimorfismo de Asociación ---
    # Cliente (UUID)
    cliente_id = Column(GUID(), ForeignKey("clientes.id"), nullable=True, index=True)
    # Transporte (UUID) - Verificado en backend/logistica/models.py
    transporte_id = Column(GUID(), ForeignKey("empresas_transporte.id"), nullable=True, index=True)

    # --- Datos Personales ---
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    puesto = Column(String, nullable=True) # Ej: Gerente de Compras, Chofer
    
    # --- Contexto ---
    referencia_origen = Column(String, nullable=True) # Ej: "Nos conoció en la Expo 23"
    domicilio_personal = Column(String, nullable=True) # Texto simple por ahora

    # --- Metadata (JSON) ---
    # Roles: List[str] -> ["COMPRAS", "PAGOS", "DECISOR", "OPERATIVO"]
    roles = Column(JSON, default=list) 
    
    # Canales: List[dict] -> [{"tipo": "WHATSAPP", "valor": "+54911...", "etiqueta": "Personal"}, ...]
    canales = Column(JSON, default=list)

    # --- Extras ---
    notas = Column(Text, nullable=True)
    estado = Column(Boolean, default=True) # Activo/Inactivo

    # --- Auditoría ---
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # --- Relaciones ---
    # Usamos string para evitar importaciones circulares si no es necesario
    cliente = relationship("backend.clientes.models.Cliente", back_populates="contactos")
    transporte = relationship("backend.logistica.models.EmpresaTransporte", back_populates="contactos")

    def __repr__(self):
        return f"<Contacto({self.nombre} {self.apellido})>"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
