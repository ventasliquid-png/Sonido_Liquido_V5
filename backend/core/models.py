# Archivo: backend/core/models.py
import uuid
from sqlalchemy import Column, String, DateTime, JSON, BigInteger, Integer, Boolean
from datetime import datetime, timezone
from backend.core.database import Base, GUID

class PapeleraRegistro(Base):
    """
    Sistema de Papelera Global (V14.8).
    Almacena una copia serializada de registros eliminados físicamente.
    """
    __tablename__ = "papelera_registros"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    entidad_tipo = Column(String, nullable=False, index=True) # 'CLIENTE', 'PRODUCTO', 'CONTACTO'
    entidad_id = Column(GUID(), nullable=False, index=True)
    
    # Datos completos del objeto en formato JSON
    data = Column(JSON, nullable=False)
    
    # Auditoría
    fecha_borrado = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    borrado_por = Column(String, nullable=True) # Nombre de usuario o PIN
    
    def __repr__(self):
        return f"<PapeleraRegistro(tipo='{self.entidad_tipo}', id='{self.entidad_id}')>"

class SistemaConfig(Base):
    __tablename__ = "sistema_config"

    id = Column(Integer, primary_key=True, default=1)
    flags_estado = Column(Integer, default=0)
    version_sistema = Column(String, nullable=True)
    fecha_ultima_sync = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class BugTracking(Base):
    __tablename__ = "bugs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    nro_sesion = Column(Integer, nullable=True)
    descripcion = Column(String)
    detalle = Column(String, nullable=True)
    fecha_ocurrencia = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_resolucion = Column(DateTime, nullable=True)
    resuelto = Column(Boolean, default=False)
    entorno = Column(String)  # 'D' o 'P'
    version_sistema = Column(String, nullable=True)
