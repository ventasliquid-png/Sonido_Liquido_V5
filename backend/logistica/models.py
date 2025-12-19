# Archivo: backend/logistica/models.py
# Módulo Logística (V5) - Hub & Spoke
import uuid
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.core.database import Base, GUID

class EmpresaTransporte(Base):
    """
    Tabla 'empresas_transporte' (La Marca).
    Ej: Cruz del Sur, Vía Cargo, Mercado Envíos.
    """
    __tablename__ = "empresas_transporte"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String, nullable=False, unique=True) # Ej: "Expreso Cruz del Sur"
    
    # Datos Core (V5)
    direccion = Column(String, nullable=True) # Sede Central
    whatsapp = Column(String, nullable=True)
    email = Column(String, nullable=True)
    observaciones = Column(Text, nullable=True)

    web_tracking = Column(String, nullable=True) # URL genérica
    telefono_reclamos = Column(String, nullable=True)
    
    # Flags operativos
    servicio_retiro_domicilio = Column(Boolean, default=False) # Pick-up logic
    requiere_carga_web = Column(Boolean, default=False) # Bloquea cierre si no se carga en portal
    formato_etiqueta = Column(Enum('PROPIA', 'EXTERNA_PDF', name='formato_etiqueta_enum'), default='PROPIA')
    activo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<EmpresaTransporte(nombre='{self.nombre}')>"

class NodoTransporte(Base):
    """
    Tabla 'nodos_transporte' (El Lugar Físico).
    Sucursales, Depósitos, Puntos de Retiro.
    """
    __tablename__ = "nodos_transporte"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    empresa_id = Column(GUID(), ForeignKey("empresas_transporte.id"), nullable=False)
    
    nombre_nodo = Column(String, nullable=False) # Ej: "Depósito Pompeya"
    direccion_completa = Column(String, nullable=True)
    localidad = Column(String, nullable=True) # Match por texto (V5)
    
    provincia_id = Column(String(1), ForeignKey("provincias.id"), nullable=False)
    
    # Contacto Nodo
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Capacidades
    es_punto_despacho = Column(Boolean, default=False) # Nosotros llevamos la carga aquí
    es_punto_retiro = Column(Boolean, default=False) # El cliente puede pasar a buscar
    
    horario_operativo = Column(String, nullable=True)
    contacto_operativo = Column(String, nullable=True) # Nombre del capataz

    # Relaciones
    empresa = relationship("EmpresaTransporte")
    provincia = relationship("backend.maestros.models.Provincia")

    def __repr__(self):
        return f"<NodoTransporte(nombre='{self.nombre_nodo}')>"

class Deposito(Base):
    """
    Tabla 'depositos' (Almacenes Internos).
    """
    __tablename__ = "depositos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    tipo = Column(Enum('FISICO', 'VIRTUAL', 'CONSIGNACION', 'MOVIL', name='tipo_deposito_enum'), default='FISICO')
    activo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Deposito(nombre='{self.nombre}')>"
