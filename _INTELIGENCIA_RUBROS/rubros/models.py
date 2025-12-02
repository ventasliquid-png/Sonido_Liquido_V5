# Archivo: backend\rubros\models.py (CORREGIDO - Timezone Aplicado)

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone # Importamos 'timezone' para la gestión UTC aware

# --- [INICIO REFACTOR V10.10] ---
# Importamos la Base desde el módulo 'core' (import absoluto)
from core.database import Base
# --- [FIN REFACTOR V10.10] ---

class Rubro(Base):
    __tablename__ = "rubros"

    id = Column(Integer, primary_key=True, index=True)
    # CUMPLIMIENTO V5 (SKU BOBO/Regla de Negocio): Se mantiene unique=True y String(3).
    codigo = Column(String(3), unique=True, index=True, nullable=False)
    descripcion = Column(String(30), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relación padre-hijo (self-referential)
    padre_id = Column(Integer, ForeignKey("rubros.id"), nullable=True)
    
    # Campos de auditoría
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    
    # CORRECCIÓN V5 (TIMEZONE): Actualizado a UTC aware.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relaciones
    padre = relationship("Rubro", remote_side=[id], backref="hijos")

print("--- [Rubros V1.0]: Modelo 'Rubro' definido. (Timezone a UTC aware) ---")