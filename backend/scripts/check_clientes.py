import sys
import os

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from core.database import SessionLocal
from backend.auth import models as auth_models
from backend.maestros import models as maestros_models
from backend.agenda import models as agenda_models
from backend.logistica import models as logistica_models
from backend.clientes import models

def check_clientes():
    print("--- Checking Clientes ---")
    db = SessionLocal()
    try:
        with open("clientes_count.txt", "w", encoding="utf-8") as f:
            count = db.query(models.Cliente).count()
            f.write(f"Total Clientes found: {count}\n")
            
            all_clientes = db.query(models.Cliente).all()
            for c in all_clientes:
                f.write(f"- {c.razon_social} (Activo: {c.activo})\n")
        print("Done writing to file.")

    except Exception as e:
        with open("clientes_count.txt", "w", encoding="utf-8") as f:
            f.write(f"ERROR: {e}")
        print(f"❌ ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_clientes()
