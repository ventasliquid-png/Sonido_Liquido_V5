# --- backend/core/database.py (V11.4 - GUID Unified) ---
from sqlalchemy import create_engine, TypeDecorator, CHAR, event
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import uuid
from urllib.parse import urlparse, quote_plus
from dotenv import dotenv_values

# --- [SINTONÍA FINA V12] ---
# Eliminación de overrides manuales.

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
    Obtiene la URL de base de datos desde el entorno (.env).
    Si es SQLite con path relativo, lo convierte a absoluto respecto a la raíz.
    """
    url = os.environ.get("DATABASE_URL")
    
    if not url:
        # Fallback de emergencia a la raíz del proyecto
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        db_path = os.path.join(project_root, "pilot_v5x.db")
        url = f"sqlite:///{db_path}"
        print(f"--- [DATABASE] ALERTA: DATABASE_URL no definida. Usando fallback: {url} ---")
        return url

    if url.startswith("sqlite:///"):
        path = url.replace("sqlite:///", "")
        if path.startswith("./") or not os.path.isabs(path):
            # Resolver path relativo a la raíz del proyecto
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
            clean_path = path.lstrip("./")
            abs_path = os.path.abspath(os.path.join(project_root, clean_path))
            url = f"sqlite:///{abs_path}"
            print(f"--- [DATABASE] Path relativo resuelto a: {url} ---")
        else:
            print(f"--- [DATABASE] Usando path absoluto: {url} ---")
    else:
        print(f"--- [DATABASE] Usando URL externa: {url} ---")
    
    return url

# --- [INICIO] ---
DATABASE_URL = _get_clean_database_url()
os.environ["DATABASE_URL"] = DATABASE_URL

if "sqlite" in DATABASE_URL:
    # check_same_thread=False is needed for SQLite ease of use in dev
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# --- [WAL MODE ENFORCEMENT] ---
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
# ------------------------------

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

print("--- [Atenea V11.4]: Capa ORM (GUID Unified) inicializada. ---")