# Archivo: backend/core/models.py
import uuid
from sqlalchemy import Column, String, DateTime, JSON, BigInteger
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
