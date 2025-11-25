# Archivo: backend/maestros/models.py
# Módulo Maestros (V5) - Tablas Base
import uuid
from sqlalchemy import Column, String, Boolean, Integer, Numeric, Enum
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
    coeficiente = Column(Numeric(10, 4), default=1.0) # Ej: 0.9000 (10% desc)
    tipo = Column(Enum('FISCAL', 'PRESUPUESTO', name='tipo_lista_enum'), default='PRESUPUESTO')
    activo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<ListaPrecios(nombre='{self.nombre}', coef={self.coeficiente})>"

class Ramo(Base):
    """
    Tabla 'ramos' (Maestro).
    Segmentación de clientes (Ej: Gastronomía, Salud, Educación).
    """
    __tablename__ = "ramos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(String, nullable=True)
    activo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Ramo(nombre='{self.nombre}')>"

class Vendedor(Base):
    """
    Tabla 'vendedores' (Fuerza de Venta).
    """
    __tablename__ = "vendedores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    comision_porcentaje = Column(Numeric(5, 2), default=0) # Ej: 3.50
    cbu_alias = Column(String, nullable=True)
    activo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Vendedor(nombre='{self.nombre}')>"

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
