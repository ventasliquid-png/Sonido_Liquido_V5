# --- backend/core/database.py (V11.4 - GUID Unified) ---
from sqlalchemy import create_engine, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import uuid
from urllib.parse import urlparse, quote_plus
from dotenv import dotenv_values

# --- [FIX IP FANTASMA & RUTA ABSOLUTA] ---
# --- [FIX IP FANTASMA & RUTA ABSOLUTA] ---
config = dotenv_values(".env")
# DATABASE_URL_FROM_ENV_FILE = config.get("DATABASE_URL")
DATABASE_URL_FROM_ENV_FILE = None # FORCE LOCAL FALLBACK

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as string without dashes.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(pgUUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                try:
                    return "%.32x" % uuid.UUID(value).int
                except ValueError:
                    return value # Probablemente ya es un hex
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value

def _get_clean_database_url():
    """
    Construye la URL de conexión ignorando variables de entorno viciadas.
    Prioriza os.environ (inyectado por main.py) y luego el archivo .env local.
    FALLBACK: Si falla, busca pilot.db en la RAÍZ DEL PROYECTO (absoluto).
    """
    # 1. Prioridad: Variable de entorno explícita (fijada por main.py con path absoluto)
    # 1. Prioridad: Variable de entorno explícita (fijada por main.py con path absoluto)
    # env_url = os.environ.get("DATABASE_URL")
    # if env_url:
    #     print(f"--- [DATABASE] Usando DATABASE_URL de entorno: {env_url} ---")
    #     return env_url
    pass

    # 2. Prioridad: Archivo .env local (fallback)
    url_candidate = DATABASE_URL_FROM_ENV_FILE
    
    # 2.5: Detectar Ruta Absoluta a pilot.db (Raíz Proyecto)
    # backend/core/database.py -> backend/core -> backend -> root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    pilot_db_path = os.path.join(project_root, "pilot.db")
    
    if url_candidate and url_candidate.startswith("sqlite"):
        # Si el usuario forzó una ruta en .env, la respetamos, pero advertimos si es relativa
        if "./" in url_candidate and not "pilot.db" in url_candidate: 
             pass # Deja que pase lo que tenga que pasar
        print(f"[OK] CONEXION DB (PREF .ENV): {url_candidate}")
        return url_candidate
    
    if not url_candidate:
        print(f"⚠️  DATABASE_URL no encontrada en .env. Usando SQLITE ROOT: {pilot_db_path}")
        # FORZAMOS LA RUTA ABSOLUTA
        url_candidate = f"sqlite:///{pilot_db_path}"
        
    if url_candidate.startswith("sqlite"):
        return url_candidate

    try:
        parsed = urlparse(url_candidate)
        user = parsed.username or "postgres"
        password = parsed.password or os.getenv("DB_PASSWORD")
        host = parsed.hostname or "104.197.57.226" 
        port = parsed.port or "5432"
        dbname = parsed.path.lstrip("/") or "postgres"
        query = parsed.query

        if host == "34.95.172.190":
            host = "104.197.57.226"

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
os.environ["DATABASE_URL"] = DATABASE_URL

if "sqlite" in DATABASE_URL:
    # check_same_thread=False is needed for SQLite ease of use in dev
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print("--- [Atenea V11.4]: Capa ORM (GUID Unified) inicializada. ---")