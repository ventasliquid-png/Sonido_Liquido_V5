import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.proveedores import models as proveedores_models
from backend.maestros import models as maestros_models
from backend.productos import models

def debug_rubros():
    db = SessionLocal()
    try:
        print("Attempting to query Rubros...")
        rubros = db.query(models.Rubro).filter(models.Rubro.padre_id == None).all()
        print(f"Found {len(rubros)} root rubros.")
        for r in rubros:
            print(f"Rubro: {r.nombre}, ID: {r.id}")
            print(f"Hijos: {len(r.hijos)}")
    except Exception as e:
        print(f"Error querying rubros: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_rubros()
