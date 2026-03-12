import sys
import os

# Agregar directorio raíz al path (dos niveles arriba de scripts/reset_clientes_tables.py? No, un nivel si está en scripts/)
# c:\dev\Sonido_Liquido_V5\scripts\reset.py -> parent is scripts, parent of parent is root.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, 'backend')
sys.path.append(project_root)
sys.path.append(backend_dir)

from core.database import engine, Base
from backend.clientes.models import Cliente, Domicilio, Contacto
from sqlalchemy import text

def reset_tables():
    print("--- [RESET] Eliminando tablas del módulo Clientes (V5.1) ---")
    try:
        # Orden inverso por FKs
        print("Dropping table: contactos...")
        Contacto.__table__.drop(engine, checkfirst=True)
        
        print("Dropping table: domicilios...")
        Domicilio.__table__.drop(engine, checkfirst=True)
        
        print("Dropping table: clientes...")
        Cliente.__table__.drop(engine, checkfirst=True)
        
        print("✅ Tablas eliminadas correctamente. Reinicia el servidor para recrearlas.")
    except Exception as e:
        print(f"❌ Error al eliminar tablas: {e}")

if __name__ == "__main__":
    reset_tables()
