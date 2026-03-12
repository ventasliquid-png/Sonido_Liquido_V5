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

def check_product(name_query):
    db = SessionLocal()
    try:
        print(f"Searching for product with name like '%{name_query}%'...")
        # Exact match first
        p = db.query(models.Producto).filter(models.Producto.nombre == name_query).first()
        if not p:
            print("Exact match not found. Trying like...")
            p = db.query(models.Producto).filter(models.Producto.nombre.ilike(f"%{name_query}%")).first()
            
        if p:
            print(f"--- PRODUCT FOUND ---")
            print(f"ID: {p.id}")
            print(f"Nombre: {p.nombre}")
            print(f"SKU: {p.sku}")
            print(f"Activo: {p.activo}")
            print(f"Rubro ID: {p.rubro_id}")
        else:
            print("Product NOT found.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_product("30-52744428-0")
