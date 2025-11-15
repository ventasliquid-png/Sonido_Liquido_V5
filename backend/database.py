# --- backend/database.py (V10.7 - Base de Datos Completa) ---
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Leemos la DATABASE_URL del entorno, que ya está configurada
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR DE ARRANQUE: DATABASE_URL no encontrada en el entorno.")
    exit(1)

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