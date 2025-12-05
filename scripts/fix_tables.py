import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import engine, Base

# Import ALL models to ensure they are registered with Base
from backend.auth import models as auth_models
from backend.maestros import models as maestros_models
from backend.clientes import models as clientes_models
from backend.productos import models as productos_models
from backend.proveedores import models as proveedores_models
from backend.agenda import models as agenda_models
from backend.logistica import models as logistica_models

def fix_tables():
    print("--- Diagnóstico de Tablas ---")
    print(f"Modelos registrados en Base.metadata: {list(Base.metadata.tables.keys())}")
    
    if "clientes" in Base.metadata.tables:
        print("✅ Tabla 'clientes' detectada en metadatos.")
    else:
        print("❌ CRÍTICO: Tabla 'clientes' NO detectada en metadatos.")

    print("\n--- Intentando crear tablas en DB ---")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Base.metadata.create_all() ejecutado correctamente.")
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")

    print("\n--- Verificación final ---")
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tablas existentes en DB: {tables}")
    
    if "clientes" in tables:
        print("✅ ÉXITO: La tabla 'clientes' existe en la base de datos.")
    else:
        print("❌ FALLO: La tabla 'clientes' sigue sin existir.")

if __name__ == "__main__":
    fix_tables()
