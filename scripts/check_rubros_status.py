
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.main import get_db
from backend.productos.models import Rubro

def check_rubros_status():
    db = next(get_db())
    try:
        print("--- CHECKING RUBROS STATUS (DEEP CHECK) ---")
        
        # 1. Check Parent "RUBRO MASIVO TEST"
        parent_name = "RUBRO MASIVO TEST"
        parent = db.query(Rubro).filter(Rubro.nombre == parent_name).first()
        
        if parent:
            print(f"[FOUND] Parent '{parent_name}' ID: {parent.id} (Active: {parent.activo})")
            
            # Check for ANY children of this parent
            children_count = db.query(Rubro).filter(Rubro.padre_id == parent.id).count()
            print(f"   -> Children count: {children_count}")
            if children_count > 0:
                children = db.query(Rubro).filter(Rubro.padre_id == parent.id).all()
                for child in children:
                     print(f"      - Child: {child.nombre} (ID: {child.id})")
        else:
            print(f"[MISSING] Parent '{parent_name}' not found.")

        # 2. Check "HUÉRFANOS"
        orphan_name = "HUÉRFANOS"
        orphan_cat = db.query(Rubro).filter(Rubro.nombre == orphan_name).first()
        if orphan_cat:
            print(f"[FOUND] Category '{orphan_name}' ID: {orphan_cat.id}")
            # Check for ANY children
            orphan_children = db.query(Rubro).filter(Rubro.padre_id == orphan_cat.id).count()
            print(f"   -> Children count: {orphan_children}")
            if orphan_children > 0:
                 # Check if any look like test data
                 test_orphans = db.query(Rubro).filter(Rubro.padre_id == orphan_cat.id, Rubro.nombre.like("Subrubro Test %")).count()
                 print(f"   -> 'Subrubro Test' orphans: {test_orphans}")

    except Exception as e:
        print(f"Error checking status: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_rubros_status()
