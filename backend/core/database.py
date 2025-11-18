# --- backend/database.py (V10.7 - Base de Datos Completa) ---
# --- [ACTUALIZADO V11.2 - PROTOCOLO DE SEGURIDAD MANUAL] ---
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import urlparse, urlunparse, quote_plus

def _ensure_database_password():
    """
    Asegura que DATABASE_URL tenga la contraseña correcta.
    SIEMPRE usa la contraseña por defecto "e" para desarrollo.
    """
    # Contraseña por defecto de desarrollo (hardcodeada)
    DEFAULT_PASSWORD = "e"
    
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    # Parsear la URL existente o construir una nueva
    if DATABASE_URL:
        parsed = urlparse(DATABASE_URL)
        user = parsed.username or "postgres"
        host = parsed.hostname or "34.95.172.190"
        port = parsed.port or "5432"
        database = parsed.path.lstrip("/") or "postgres"
    else:
        # Si no existe, construir desde cero
        print("⚠️  DATABASE_URL no encontrada en el entorno.")
        print("📋 Construyendo URL con valores por defecto...")
        user = os.environ.get("DB_USER", "postgres")
        host = os.environ.get("DB_HOST", "34.95.172.190")
        port = os.environ.get("DB_PORT", "5432")
        database = os.environ.get("DB_NAME", "postgres")
    
    # SIEMPRE usar la contraseña por defecto "e"
    # Escapar caracteres especiales en la contraseña
    password_escaped = quote_plus(DEFAULT_PASSWORD)
    
    # Reconstruir la URL completa con la contraseña correcta
    netloc = f"{user}:{password_escaped}@{host}"
    if port:
        netloc += f":{port}"
    
    DATABASE_URL = f"postgresql://{netloc}/{database}"
    
    # Establecer la URL completa en el entorno para que otros módulos la usen
    os.environ["DATABASE_URL"] = DATABASE_URL
    
    print(f"✅ DATABASE_URL configurada con contraseña por defecto.")
    print(f"📊 Servidor: {host}:{port}")
    print(f"📊 Base de datos: {database}")
    print(f"📊 Usuario: {user}\n")
    
    return DATABASE_URL

# --- [INICIO PROTOCOLO DE SEGURIDAD MANUAL V11.2] ---
# Asegurar que DATABASE_URL tenga contraseña antes de crear el engine
DATABASE_URL = _ensure_database_password()
# --- [FIN PROTOCOLO DE SEGURIDAD MANUAL V11.2] ---

# Crear el engine solo después de tener la URL completa
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta es la Base declarativa que usarán todos nuestros modelos ORM
Base = declarative_base()

# --- [INICIO PARCHE V10.7 (FUNCIÓN FALTANTE)] ---
def get_db():
    """Generador de sesión de DB para FastAPI (Dependency Injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# --- [FIN PARCHE V10.7] ---

print("--- [Atenea V10.7]: Capa ORM (SQLAlchemy) inicializada. ---")