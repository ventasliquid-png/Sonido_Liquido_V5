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

def force_inactive(product_id):
    db = SessionLocal()
    try:
        print(f"Forcing Product {product_id} to INACTIVE...")
        p = db.query(models.Producto).get(product_id)
        if not p:
            print("Product not found")
            return
        
        p.activo = False
        db.commit()
        print("Done. Product is now Inactive.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    force_inactive(289)
