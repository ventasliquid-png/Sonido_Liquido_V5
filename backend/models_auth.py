# --- backend/models_auth.py (V10.4) ---
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

# Importamos la Base de nuestro archivo database.py (CORREGIDO: Importación directa)
from database import Base

class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    # Relación inversa: Un rol puede tener muchos usuarios
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

print("--- [Atenea V10.4]: Modelos 'Usuario' y 'Rol' definidos. ---")