import sys
import os
from sqlalchemy.orm import joinedload

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.core.database import SessionLocal
from backend.productos import models

def test_query():
    db = SessionLocal()
    try:
        print("--- Testing Query ---")
        query = db.query(models.Producto).options(joinedload(models.Producto.costos), joinedload(models.Producto.rubro))
        
        # Simulate params
        # activo = True
        # query = query.filter(models.Producto.activo == True)
        
        print("Executing query...")
        results = query.limit(10).all()
        print(f"Results: {len(results)}")
        print(f"Results: {len(results)}")
        for p in results:
            print(f" - {p.nombre} (ID: {p.id})")
            if p.costos:
                print(f"   [COSTOS] Roca: {p.costos.precio_roca} ({type(p.costos.precio_roca)})")
                print(f"   [COSTOS] Rent: {p.costos.rentabilidad_target} ({type(p.costos.rentabilidad_target)})")
                
                # Test logic
                from backend.productos.router import calculate_prices
                calculate_prices(p)
                print(f"   [CALC] Mayorista: {p.precio_mayorista}")
                
                # Test schema validation
                from backend.productos import schemas
                try:
                    schema_obj = schemas.ProductoRead.model_validate(p)
                    print("   [SCHEMA] Valid ✅")
                except Exception as ve:
                    print(f"   [SCHEMA] FAIL ❌: {ve}")
                    
            else:
                print("   [COSTOS] None")

    except Exception as e:
        print("--- CRASH CAUGHT ---")
        print(e)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
