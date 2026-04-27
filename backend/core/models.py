# Archivo: backend/core/models.py
import uuid
from sqlalchemy import Column, String, DateTime, JSON, BigInteger, Integer
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


class SistemaEstado(Base):
    """
    [DOCTRINA V14] Registro único de estado del sistema.
    flags_estado sigue doctrina SystemFlags.
    PIN 1974 requerido para modificar TERMICA.
    """
    __tablename__ = "sistema_estado"

    id = Column(Integer, primary_key=True, default=1)
    identidad = Column(String(1), default="D", nullable=False)  # "D" o "P"
    version = Column(String, default="5.9.0000", nullable=False)
    flags_estado = Column(BigInteger, default=0, nullable=False)
    fecha_ultimo_git_push = Column(DateTime, nullable=True)
    fecha_ultimo_backup_drive = Column(DateTime, nullable=True)
    fecha_cierre = Column(DateTime, nullable=True)
    notas = Column(String, nullable=True)

    def __repr__(self):
        return f"<SistemaEstado(identidad='{self.identidad}', version='{self.version}', flags={self.flags_estado})>"
