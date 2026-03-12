import sys
import os

print(">>> Initializing DB Tables...", file=sys.stderr)
sys.stdout.flush()

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# [FIX] Force SQLite to match backend/main.py behavior
ROOT_DIR = os.path.dirname(BASE_DIR)
abs_db_path = os.path.join(ROOT_DIR, "pilot.db")
os.environ["DATABASE_URL"] = f"sqlite:///{abs_db_path}"
print(f"--- [DEBUG] Forcing SQLITE LOCAL: {os.environ['DATABASE_URL']} ---", file=sys.stderr)

try:
    from backend.core.database import SessionLocal, engine, Base
    
    # Verify fix: Import dependencies to Ensure Mapper Registry has them
    import backend.auth.models
    import backend.contactos.models
    import backend.pedidos.models
    import backend.logistica.models
    import backend.productos.models
    import backend.maestros.models
    import backend.clientes.models
    import backend.agenda.models
    
    print(">>> Creating all tables...", file=sys.stderr)
    Base.metadata.create_all(bind=engine)
    print(">>> Tables created successfully.", file=sys.stderr)

except Exception as e:
    print(f"Init Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
