# --- backend/database.py (V10.7 - Base de Datos Completa) ---
# --- [ACTUALIZADO V11.3 - FIX IP FANTASMA] ---
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import urlparse, quote_plus
from dotenv import dotenv_values

# --- [FIX IP FANTASMA] ---
# No confiamos en os.environ["DATABASE_URL"] porque puede estar sucia.
# Leemos directamente del archivo .env
config = dotenv_values(".env")
DATABASE_URL_FROM_ENV_FILE = config.get("DATABASE_URL")

def _get_clean_database_url():
    """
    Construye la URL de conexión ignorando variables de entorno viciadas.
    Prioriza el archivo .env local.
    """
    # 1. Intentar usar la del archivo .env
    url_candidate = DATABASE_URL_FROM_ENV_FILE
    
    # 2. Si no está en el archivo, usar hardcode de emergencia (Nueva IP)
    if not url_candidate:
        print("⚠️  DATABASE_URL no encontrada en .env. Usando hardcode de seguridad.")
        # Hardcode actualizado a la IP 104.197.57.226
        url_candidate = "postgresql://postgres:Spawn1482.@104.197.57.226:5432/postgres?sslmode=require"

    # 3. Parsear para asegurar que la contraseña esté bien (aunque venga del file)
    try:
        parsed = urlparse(url_candidate)
        
        # Extracción de componentes
        user = parsed.username or "postgres"
        password = parsed.password or "Spawn1482."
        host = parsed.hostname or "104.197.57.226" # Forzar nueva IP si falla parseo
        port = parsed.port or "5432"
        dbname = parsed.path.lstrip("/") or "postgres"
        query = parsed.query # sslmode=require

        # Validación anti-fantasma
        if host == "34.95.172.190":
            print("🚨 ALERTA: IP Fantasma detectada en .env! Forzando corrección a 104.197.57.226")
            host = "104.197.57.226"

        # Reconstrucción limpia
        password_escaped = quote_plus(password)
        netloc = f"{user}:{password_escaped}@{host}:{port}"
        
        clean_url = f"postgresql://{netloc}/{dbname}"
        if query:
            clean_url += f"?{query}"
            
        print(f"✅ CONEXIÓN DB: {host}:{port} ({dbname})")
        return clean_url

    except Exception as e:
        print(f"❌ Error parseando URL de DB: {e}")
        return url_candidate

# --- [INICIO] ---
DATABASE_URL = _get_clean_database_url()
# Actualizamos os.environ para que otras libs (como alembic o scripts) la vean correcta
os.environ["DATABASE_URL"] = DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print("--- [Atenea V10.7]: Capa ORM (SQLAlchemy) inicializada. ---")