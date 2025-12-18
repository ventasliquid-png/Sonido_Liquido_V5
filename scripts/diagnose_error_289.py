import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload

# Setup path to handle absolute imports from backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

from backend.core.database import get_db, SessionLocal
from backend.productos import models
from backend.productos.router import calculate_prices

def test_product_fetch(product_id):
    db = SessionLocal()
    try:
        print(f"Fetching Product {product_id}...")
        producto = db.query(models.Producto).options(
            joinedload(models.Producto.costos),
            joinedload(models.Producto.rubro)
        ).filter(models.Producto.id == product_id).first()
        
        if not producto:
            print("Product not found.")
            return

        print(f"Product found: {producto.nombre}")
        print("Calculating prices...")
        
        # This function modifies the instance in place
        try:
            calculate_prices(producto)
            print("Calculate prices successful.")
            print(f"Mayorista: {getattr(producto, 'precio_mayorista', 'N/A')}")
        except Exception as e:
            print(f"ERROR inside calculate_prices: {e}")
            import traceback
            traceback.print_exc()
            return

        # Try to validate with Pydantic Schema
        print("Validating with Pydantic Schema...")
        from backend.productos import schemas
        try:
            # Pydantic v1 vs v2
            if hasattr(schemas.ProductoRead, 'from_orm'):
                pydantic_obj = schemas.ProductoRead.from_orm(producto)
            else:
                 pydantic_obj = schemas.ProductoRead.model_validate(producto)
            print("Pydantic Validation passed.")
        except Exception as e:
             print(f"ERROR Pydantic Validation: {e}")
             import traceback
             traceback.print_exc()

    except Exception as e:
        print(f"General Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_product_fetch(289)
