import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.productos.models import Producto, ProductoCosto
from sqlalchemy import func

from backend.clientes.models import Cliente

def analyze_products():
    db = SessionLocal()
    try:
        # --- PRODUCTS ---
        total_products = db.query(Producto).count()
        active_products = db.query(Producto).filter(Producto.activo == True).count()
        inactive_products = db.query(Producto).filter(Producto.activo == False).count()
        
        products_without_rubro = db.query(Producto).filter(Producto.rubro_id == None).count()
        products_without_costs = db.query(Producto).outerjoin(Producto.costos).filter(ProductoCosto.id == None).count()
        
        print(f"Total Products: {total_products}")
        print(f"Active Products: {active_products}")
        print(f"Inactive Products: {inactive_products}")
        print(f"Products without Rubro: {products_without_rubro}")
        print(f"Products without Costs: {products_without_costs}")
        
        # --- CLIENTS ---
        total_clients = db.query(Cliente).count()
        print(f"Total Clients: {total_clients}")

        # Check for duplicate names (case insensitive)
        duplicate_names = db.query(Producto.nombre, func.count(Producto.nombre)).group_by(Producto.nombre).having(func.count(Producto.nombre) > 1).all()
        if duplicate_names:
            print("\nDuplicate Names found:")
            for name, count in duplicate_names:
                print(f"  '{name}': {count} occurrences")
        else:
            print("\nNo exact duplicate names found.")

        # Sample of products with NO costs
        if products_without_costs > 0:
            print("\nSample of products without costs:")
            missing_costs = db.query(Producto).outerjoin(Producto.costos).filter(ProductoCosto.id == None).limit(5).all()
            for p in missing_costs:
                print(f"  ID: {p.id}, Nombre: {p.nombre}, SKU: {p.sku}")

    except Exception as e:
        print(f"Error analyzing products: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    analyze_products()
