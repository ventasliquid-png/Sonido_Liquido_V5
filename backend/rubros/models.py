"""
Módulo Rubros (V1.0): Modelos ORM (SQLAlchemy).
Define la tabla 'rubros' con soporte para jerarquía (padre-hijo).
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# --- [INICIO REFACTOR V10.10] ---
# Importamos la Base desde el módulo 'core' (import absoluto)
from core.database import Base
# --- [FIN REFACTOR V10.10] ---

class Rubro(Base):
    __tablename__ = "rubros"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(3), unique=True, index=True, nullable=False)
    descripcion = Column(String(30), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relación padre-hijo (self-referential)
    padre_id = Column(Integer, ForeignKey("rubros.id"), nullable=True)
    
    # Campos de auditoría
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    padre = relationship("Rubro", remote_side=[id], backref="hijos")

print("--- [Rubros V1.0]: Modelo 'Rubro' definido. ---")

