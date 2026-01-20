
import sys
import os
import uuid

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.database import SessionLocal, engine, Base
from backend.maestros.models import ListaPrecios

def seed_official_lists():
    db = SessionLocal()
    
    print("\n--- SEEDING OFFICIAL PRICE LISTS (Hard Logic V5) ---")
    
    # Define the 7 Official Lists
    official_lists = [
        {"orden": 1, "nombre": "Mayorista (Roca)"},
        {"orden": 2, "nombre": "Mayorista 1/2 IVA"},
        {"orden": 3, "nombre": "Distribuidor"},
        {"orden": 4, "nombre": "Minorista Neto"},
        {"orden": 5, "nombre": "Minorista Final"},
        {"orden": 6, "nombre": "MELI"},
        {"orden": 7, "nombre": "Tienda Propia"},
    ]
    
    for data in official_lists:
        # Check if list exists by name
        existing = db.query(ListaPrecios).filter(ListaPrecios.nombre == data["nombre"]).first()
        
        if existing:
            # Update orden if needed
            if existing.orden_calculo != data["orden"]:
                print(f"🔄 Updating '{data['nombre']}' -> Orden {data['orden']}")
                existing.orden_calculo = data["orden"]
            else:
                print(f"✅ '{data['nombre']}' OK")
        else:
            # Create new
            print(f"➕ Creating '{data['nombre']}' -> Orden {data['orden']}")
            new_list = ListaPrecios(
                nombre=data["nombre"],
                orden_calculo=data["orden"],
                activo=True
            )
            db.add(new_list)
            
    try:
        db.commit()
        print("\n--- SEEDING COMPLETE ---")
    except Exception as e:
        db.rollback()
        print(f"❌ Error during seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_official_lists()
