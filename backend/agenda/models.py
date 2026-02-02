# Archivo: backend/agenda/models.py
# Módulo Agenda Viva (V5) - CRM Relacional
import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.core.database import Base, GUID

class PersonaLegacy(Base):
    """
    Tabla 'personas' (El Ser Humano).
    Registro único del individuo. No depende de ningún cliente.
    """
    __tablename__ = "personas_legacy"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    nombre_completo = Column(String, nullable=False, index=True)
    
    # Contacto Personal (Vida Privada)
    celular_personal = Column(String, nullable=True) # WhatsApp de vida
    email_personal = Column(String, nullable=True) # Gmail/Hotmail
    linkedin = Column(String, nullable=True)
    
    observaciones = Column(Text, nullable=True) # Gustos, cumpleaños
    activo = Column(Boolean, default=True)

    # Google Integration (V14)
    google_resource_name = Column(String, nullable=True, unique=True, index=True) # 'people/c12345...'
    google_etag = Column(String, nullable=True)

    def __repr__(self):
        return f"<Persona(nombre='{self.nombre_completo}')>"

# Alias for compatibility with Service layer
Persona = PersonaLegacy

class VinculoComercial(Base):
    """
    Tabla 'vinculos_comerciales' (El Sombrero Laboral).
    Relación N:N entre Persona y Cliente.
    """
    __tablename__ = "vinculos_comerciales"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    cliente_id = Column(GUID(), ForeignKey("clientes.id"), nullable=False)
    persona_id = Column(GUID(), ForeignKey("personas_legacy.id"), nullable=False)
    tipo_contacto_id = Column(String, ForeignKey("tipos_contacto.id"), nullable=False)
    
    email_laboral = Column(String, nullable=True)
    telefono_escritorio = Column(String, nullable=True)
    
    es_principal = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)

    # Relaciones
    # [GY-FIX V6] Removed back_populates as Cliente.vinculos no longer points here
    cliente = relationship("Cliente")
    persona = relationship("PersonaLegacy")
    tipo_contacto = relationship("backend.maestros.models.TipoContacto")

    def __repr__(self):
        return f"<VinculoComercial(cliente='{self.cliente_id}', persona='{self.persona_id}')>"
