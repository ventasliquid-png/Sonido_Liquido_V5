"""
Módulo Auth (V10.E): Lógica de Negocio de Autenticación.
Contiene las funciones de hashing y las consultas ORM puras.

--- [ACTUALIZADO A V10.E (SEGURIDAD)] ---
Añadidas funciones 'authenticate_user' y 'create_access_token'.
"""
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone # <--- Añadido en V10.E
from jose import JWTError, jwt # <--- Añadido en V10.E
from typing import Optional

# --- [INICIO REFACTOR V10.10] ---
from backend.auth import models
# --- [FIN REFACTOR V10.10] ---

# --- [INICIO FASE 10.E (SEGURIDAD)] ---
# Importamos la configuración de seguridad desde el módulo 'core'
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
# --- [FIN FASE 10.E] ---


# Definición del contexto para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funciones de Hashing (Existentes) ---

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --- Funciones de Consulta ORM (Existentes) ---

def get_usuario_by_username(db: Session, username: str):
    """Obtiene un usuario por su nombre de usuario."""
    return db.query(models.Usuario).filter(models.Usuario.username == username).first()

def get_usuario_by_email(db: Session, email: str):
    """Obtiene un usuario por su email."""
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def get_rol_by_name(db: Session, name: str):
    """Obtiene un rol por su nombre."""
    return db.query(models.Rol).filter(models.Rol.name == name).first()

# --- [INICIO FASE 10.E (LÓGICA DE TOKEN)] ---

def authenticate_user(db: Session, username: str, password: str):
    """
    Verifica si un usuario existe y si la contraseña es correcta.
    Devuelve el objeto Usuario si tiene éxito, o False si falla.
    """
    usuario = get_usuario_by_username(db, username=username)
    if not usuario:
        return False # Usuario no encontrado
    if not verify_password(password, usuario.hashed_password):
        return False # Contraseña incorrecta
    
    return usuario

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Crea un nuevo Token JWT (el "pase de acceso").
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Si no se define tiempo, usa el por defecto de config.py (30 min)
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Firma el token con nuestra SECRET_KEY y Algoritmo
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def get_current_user_from_token(token: str, db: Session) -> Optional[models.Usuario]:
    """
    Decodifica el token JWT y obtiene el usuario actual.
    Retorna el objeto Usuario o None si el token es inválido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    usuario = get_usuario_by_username(db, username=username)
    return usuario

# --- [FIN FASE 10.E] ---

print("--- [Atenea V10.E]: Auth/Service (Lógica AuthN/AuthZ y Tokens) definida. ---")
