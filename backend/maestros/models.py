# Archivo: backend/maestros/models.py
# Módulo Maestros (V5) - Tablas Base
import uuid
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base

class Provincia(Base):
    """
    Tabla 'provincias' (Maestro Estático).
    Códigos de provincia estándar (ej: 'B' para PBA, 'C' para CABA).
    """
    __tablename__ = "provincias"

    id = Column(String(1), primary_key=True, index=True) # Ej: 'B', 'C', 'X'
    nombre = Column(String, nullable=False)

    def __repr__(self):
        return f"<Provincia(id='{self.id}', nombre='{self.nombre}')>"

class CondicionIva(Base):
    """
    Tabla 'condiciones_iva' (Maestro).
    """
    __tablename__ = "condiciones_iva"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String, nullable=False, unique=True) # Ej: Responsable Inscripto
    
    def __repr__(self):
        return f"<CondicionIva(nombre='{self.nombre}')>"

class ListaPrecios(Base):
    """
    Tabla 'listas_precios' (Maestro).
    """
    __tablename__ = "listas_precios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String, nullable=False, unique=True) # Ej: Lista Mayorista
    activo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<ListaPrecios(nombre='{self.nombre}')>"

class TipoContacto(Base):
    """
    Tabla 'tipos_contacto' (Maestro Estático).
    Roles: 'COMPRAS', 'PAGOS', 'DUEÑO', 'CALIDAD'.
    """
    __tablename__ = "tipos_contacto"

    id = Column(String, primary_key=True, index=True) # Ej: 'COMPRAS'
    nombre = Column(String, nullable=False) # Descripción legible

    def __repr__(self):
        return f"<TipoContacto(id='{self.id}')>"
