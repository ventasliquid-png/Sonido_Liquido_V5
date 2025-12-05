import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.proveedores import models as proveedores_models
from backend.maestros import models as maestros_models
from backend.productos import models
from sqlalchemy.orm import joinedload

def debug_read_productos():
    db = SessionLocal()
    try:
        print("Attempting to read productos with relationships...")
        productos = db.query(models.Producto).options(
            joinedload(models.Producto.costos), 
            joinedload(models.Producto.rubro)
        ).limit(10).all()
        
        print(f"✅ Successfully read {len(productos)} productos.")
        for p in productos:
            print(f" - ID: {p.id}, Nombre: {p.nombre}, Rubro: {p.rubro.nombre if p.rubro else 'None'}")
            if p.costos:
                print(f"   Costos: {p.costos.costo_reposicion}")
            else:
                print("   Costos: None")
                
    except Exception as e:
        print(f"❌ Error reading productos: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_read_productos()
