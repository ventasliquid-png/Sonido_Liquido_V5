import sys
import os

# Set up module path
sys.path.append(os.getcwd())

from backend.core.database import engine, Base
from backend.auth import models as auth_models
from backend.clientes import models as clientes_models
from backend.productos import models as productos_models
from backend.logistica import models as logistica_models
from backend.maestros import models as maestros_models
from backend.proveedores import models as proveedores_models

def init_db():
    print("--- Forcing DB Initialization ---")
    print(f"Engine URL: {engine.url}")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables Created Successfully.")
    except Exception as e:
        print(f"❌ Error Creating Tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_db()
