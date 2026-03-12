"""
Módulo Auth (V10.10): Modelos ORM (SQLAlchemy).
Define las tablas 'roles' y 'usuarios'.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

# --- [INICIO REFACTOR V10.10] ---
# Importamos la Base desde el módulo 'core' (import absoluto)
from backend.core.database import Base
# --- [FIN REFACTOR V10.10] ---

class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    # Relación inversa: Un rol puede tener muchos usuarios
    # [CORRECCIÓN V1D: Corregido typo 'back_pop_ulates' a 'back_populates']
    usuarios = relationship("Usuario", back_populates="rol")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Clave foránea para la relación
    rol_id = Column(Integer, ForeignKey("roles.id"))

    # Relación: Un usuario pertenece a un rol
    rol = relationship("Rol", back_populates="usuarios")

print("--- [Atenea V10.10]: Auth/Models ('Usuario', 'Rol') definidos. ---")
