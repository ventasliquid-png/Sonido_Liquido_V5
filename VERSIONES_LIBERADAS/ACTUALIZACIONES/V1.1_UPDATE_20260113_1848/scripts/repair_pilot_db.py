import sys
import os
from pathlib import Path

# Setup path
cur_dir = os.getcwd()
sys.path.insert(0, cur_dir)

print(f"--- [DB Repair]: Iniciando desde {cur_dir} ---")

try:
    from backend.core.database import engine, Base
    
    print("--- [DB Repair]: Importando modelos... ---")
    import backend.auth.models
    import backend.maestros.models
    import backend.productos.models
    import backend.clientes.models
    import backend.proveedores.models
    import backend.logistica.models
    import backend.agenda.models
    
    print("--- [DB Repair]: Ejecutando Base.metadata.create_all... ---")
    Base.metadata.create_all(bind=engine)
    print("--- [DB Repair]: Tablas creadas exitosamente. ---")
    
except Exception as e:
    print(f"❌ [DB Repair ERROR]: {e}")
    import traceback
    traceback.print_exc()
