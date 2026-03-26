# Archivo: backend/logistica/models.py
# Módulo Logística (V5) - Hub & Spoke
import uuid
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey, Integer, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from backend.core.database import Base, GUID
from backend.maestros.models import CondicionIva, Provincia
from backend.contactos.models import VinculoGeografico

class EmpresaTransporte(Base):
    """
    Tabla 'empresas_transporte' (La Marca).
    Ej: Cruz del Sur, Vía Cargo, Mercado Envíos.
    """
    __tablename__ = "empresas_transporte"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String, nullable=False, unique=True) # Ej: "Expreso Cruz del Sur"
    
    # Datos Fiscales / Central
    cuit = Column(String(15), nullable=True)
    condicion_iva_id = Column(GUID(), ForeignKey("condiciones_iva.id"), nullable=True) # UUID FK

    # Contacto Central
    whatsapp = Column(String(30), nullable=True)
    email = Column(String(100), nullable=True)
    
    observaciones = Column(Text, nullable=True)
    web_tracking = Column(String(255), nullable=True)
    telefono_reclamos = Column(String(50), nullable=True)
    
    # [GENOMA 64-bit] Sovereign Flags (64-bit)
    # Bit 0: EXISTENCE (1)
    # Bit 1: ACTIVE (2)
    # Bit 2: PICKUP (4) 
    # Bit 3: RECOMMENDED (8)
    # Bit 4: WH_PICKUP (16) 
    # Bit 5: WEB_REQUIRED (32) 
    # Bit 21: MIRROR (2097152) -> Despacho = Fiscal
    flags_estado = Column(BigInteger, default=3, nullable=False) # 1+2 (Existence + Active)
    
    formato_etiqueta = Column(Enum('PROPIA', 'EXTERNA_PDF', name='formato_etiqueta_enum'), default='PROPIA')

    # Relaciones
    condicion_iva = relationship("CondicionIva")
    
    # [V5 UNIVERSAL VAULT] - Address Hub Integration
    vinculos_geograficos = relationship(
        "VinculoGeografico",
        primaryjoin="and_(foreign(VinculoGeografico.entidad_id)==EmpresaTransporte.id, VinculoGeografico.entidad_tipo=='TRANSPORTE')",
        viewonly=True,
    )

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
    
    provincia_id = Column(String(5), ForeignKey("provincias.id"), nullable=False)
    
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
    provincia = relationship("Provincia")
    
    # [V5 UNIVERSAL VAULT]
    vinculos_geograficos = relationship(
        "VinculoGeografico",
        primaryjoin="and_(foreign(VinculoGeografico.entidad_id)==NodoTransporte.id, VinculoGeografico.entidad_tipo=='NODO_TRANSPORTE')",
        viewonly=True,
    )

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
