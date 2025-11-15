# --- backend/service_auth.py (V10.6 - Corrección Final de Importación) ---
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# [V10.6 FIX]: Importaciones directas (SIN el punto)
import models_auth 
import database 

# Definición del contexto para el hashing de contraseñas (bcrypt es el estándar)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funciones de Hashing ---

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --- Funciones de Consulta ORM ---

def get_usuario_by_username(db: Session, username: str):
    """Obtiene un usuario por su nombre de usuario."""
    return db.query(models_auth.Usuario).filter(models_auth.Usuario.username == username).first()

def get_usuario_by_email(db: Session, email: str):
    """Obtiene un usuario por su email."""
    return db.query(models_auth.Usuario).filter(models_auth.Usuario.email == email).first()

def get_rol_by_name(db: Session, name: str):
    """Obtiene un rol por su nombre."""
    return db.query(models_auth.Rol).filter(models_auth.Rol.name == name).first()

print("--- [Atenea V10.6]: Servicios de AuthN/AuthZ definidos. ---")