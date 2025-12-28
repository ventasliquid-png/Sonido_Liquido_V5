from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from backend.core.database import SessionLocal
from backend.productos import models

def test_toggle(product_id):
    db = SessionLocal()
    try:
        print(f"Checking product {product_id}...")
        p = db.query(models.Producto).get(product_id)
        if not p:
            print("Product not found")
            return
        
        initial_state = p.activo
        print(f"Initial State: {initial_state}")
        
        print("Toggling...")
        p.activo = not initial_state
        db.commit()
        db.refresh(p)
        print(f"New State (In Session): {p.activo}")
        
        db.close()
        
        # New Session to verify persistence
        print("Verifying persistence with new session...")
        db2 = SessionLocal()
        p2 = db2.query(models.Producto).get(product_id)
        print(f"Persisted State: {p2.activo}")
        
        if p2.activo != initial_state:
            print("SUCCESS: State changed persistently.")
        else:
            print("FAILURE: State reverted or did not save.")
            
        # Revert
        print("Reverting...")
        p2.activo = initial_state
        db2.commit()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_toggle(289) # Using the one we fixed earlier
