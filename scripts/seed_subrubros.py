
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.main import get_db
from backend.productos.models import Rubro

def seed_subrubros():
    db = next(get_db())
    try:
        # Find or create a parent for testing
        parent_name = "RUBRO MASIVO TEST"
        parent = db.query(Rubro).filter(Rubro.nombre == parent_name).first()
        
        if not parent:
            print(f"Creating parent: {parent_name}")
            parent = Rubro(nombre=parent_name, codigo="TEST-MIG", activo=True, padre_id=None)
            db.add(parent)
            db.commit()
            db.refresh(parent)
        else:
            print(f"Using existing parent: {parent_name} (ID: {parent.id})")
            # Ensure it is active
            if not parent.activo:
                parent.activo = True
                db.commit()

        # Create 15 children
        print(f"Seeding 15 subrubros for {parent_name}...")
        for i in range(1, 16):
            child_name = f"Subrubro Test {i}"
            child_code = f"TEST-{i:02d}"
            
            exists = db.query(Rubro).filter(Rubro.nombre == child_name, Rubro.padre_id == parent.id).first()
            if not exists:
                child = Rubro(nombre=child_name, codigo=child_code, activo=True, padre_id=parent.id)
                db.add(child)
            else:
                # Ensure active
                exists.activo = True
        
        db.commit()
        print("Success! 15 subrubros ready.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_subrubros()
