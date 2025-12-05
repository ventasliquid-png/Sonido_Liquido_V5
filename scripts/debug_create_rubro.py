import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.proveedores import models as proveedores_models
from backend.maestros import models as maestros_models
from backend.productos import models

def debug_create_rubro():
    db = SessionLocal()
    try:
        print("Attempting to create Rubro directly...")
        new_rubro = models.Rubro(nombre="Rubro Debug", codigo="DBG", activo=True)
        db.add(new_rubro)
        db.commit()
        db.refresh(new_rubro)
        print(f"✅ Created Rubro: {new_rubro.id} - {new_rubro.nombre}")
    except Exception as e:
        print(f"❌ Error creating rubro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_create_rubro()
