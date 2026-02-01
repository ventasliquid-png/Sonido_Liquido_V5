# Archivo: backend/contactos/models.py
# Módulo: Contactos Multiplex (V6 Core)
# Color Identidad: ÍNDIGO / VIOLETA

import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON, DateTime, Date, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from backend.core.database import Base, GUID

class Persona(Base):
    """
    Tabla 'personas' (El Ser Humano).
    Entidad única que representa a un individuo.
    """
    __tablename__ = "personas"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Identidad
    nombre = Column(String, nullable=False) # Nombre de pila o funcional (ej: "Guardia")
    apellido = Column(String, nullable=True) # Opcional (ej: para contactos genéricos)
    
    # Datos Personales (Globales)
    domicilio_personal = Column(String, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    
    # Canales Personales (Privados)
    # Ej: [{"tipo": "WHATSAPP", "valor": "+54...", "etiqueta": "Personal"}]
    canales_personales = Column(JSON, default=list)

    notas_globales = Column(Text, nullable=True)
    
    # Auditoría
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    vinculos = relationship("Vinculo", back_populates="persona", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Persona({self.nombre} {self.apellido or ''})>"
        
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido or ''}".strip()


class Vinculo(Base):
    """
    Tabla 'vinculos' (Roles y Relación con Entidades).
    N:M entre Personas y Entidades comerciales.
    """
    __tablename__ = "vinculos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Persona (FK)
    persona_id = Column(GUID(), ForeignKey("personas.id"), nullable=False, index=True)
    
    # Entidad Polimórfica (Cliente, Transporte, Proveedor, Vendedor)
    entidad_tipo = Column(Enum('CLIENTE', 'TRANSPORTE', 'PROVEEDOR', 'VENDEDOR', name='entidad_tipo_enum'), nullable=False)
    entidad_id = Column(GUID(), nullable=False, index=True) # ID no forzado por FK dura para permitir polimorfismo simple
    
    # Detalles del Rol
    tipo_contacto_id = Column(String, nullable=True) # [Legacy V5 Support] FK to tipos_contacto table (soft link here)
    rol = Column(String, nullable=True) # Ej: "Gerente de Compras"
    area = Column(String, nullable=True) # Ej: "Administración"
    roles = Column(JSON, default=list) # Etiquetas: [DECISOR, COBRANZAS]
    
    # Canales Laborales (Contextuales a esta empresa)
    # Ej: [{"tipo": "EMAIL", "valor": "pedro@transporte.com", "etiqueta": "Corporativo"}]
    canales_laborales = Column(JSON, default=list)
    
    notas_vinculo = Column(Text, nullable=True)
    
    # Estado y Tiempo
    activo = Column(Boolean, default=True)
    fecha_inicio = Column(Date, default=lambda: datetime.now(timezone.utc).date())
    fecha_fin = Column(Date, nullable=True)

    # Auditoría
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    persona = relationship("Persona", back_populates="vinculos")
