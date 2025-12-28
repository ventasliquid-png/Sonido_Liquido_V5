import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal
# Import models to register them with SQLAlchemy
from backend.productos.models import Rubro, Producto
from backend.proveedores.models import Proveedor
from backend.maestros.models import TasaIVA, Unidad


def ensure_orphan_rubro():
    db = SessionLocal()
    try:
        # Check if "Huérfanos" exists
        orphan = db.query(Rubro).filter(Rubro.nombre == "HUÉRFANOS").first()
        
        if not orphan:
            print("Creating 'HUÉRFANOS' rubro...")
            orphan = Rubro(
                codigo="HUE",
                nombre="HUÉRFANOS",
                activo=True,
                padre_id=None
            )
            db.add(orphan)
            db.commit()
            db.refresh(orphan)
            print(f"Created 'HUÉRFANOS' rubro with ID: {orphan.id}")
        else:
            print(f"'HUÉRFANOS' rubro already exists with ID: {orphan.id}")
            
            # Ensure it is active
            if not orphan.activo:
                print("Activating 'HUÉRFANOS' rubro...")
                orphan.activo = True
                db.commit()
                
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    ensure_orphan_rubro()
