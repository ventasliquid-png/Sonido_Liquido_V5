import sys
import os

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from core.database import SessionLocal
from backend.maestros import models as maestros_models
from backend.logistica import models

def check_transportes():
    print("--- Checking Transportes ---")
    db = SessionLocal()
    try:
        with open("transportes_count.txt", "w", encoding="utf-8") as f:
            count = db.query(models.EmpresaTransporte).count()
            f.write(f"Total Transportes found: {count}\n")
            
            all_transportes = db.query(models.EmpresaTransporte).all()
            for t in all_transportes:
                f.write(f"- {t.nombre} (Activo: {t.activo})\n")
        print("Done writing to file.")

    except Exception as e:
        with open("transportes_count.txt", "w", encoding="utf-8") as f:
            f.write(f"ERROR: {e}")
        print(f"❌ ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_transportes()
