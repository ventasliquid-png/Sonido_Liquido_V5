from backend.core.database import SessionLocal
from backend.productos import models
import sys

def inspect_97():
    db = SessionLocal()
    try:
        p = db.query(models.Producto).get(97)
        if not p:
            print("Product 97 not found")
            return

        print(f"--- PRODUCT 97 DETAILS ---")
        print(f"ID: {p.id}")
        print(f"Nombre: {p.nombre}")
        print(f"SKU: {p.sku}")
        print(f"Rubro ID: {p.rubro_id}")
        print(f"Activo: {p.activo}")
        
        # Check Relations
        print(f"--- RELATIONS ---")
        if p.rubro:
            print(f"Rubro Obj: {p.rubro.nombre} (ID: {p.rubro.id})")
        else:
            print(f"Rubro Obj: NONE (Rubro ID is {p.rubro_id})")

        if p.costos:
            print(f"Costos: YES")
            print(f"  Costo Reposicion: {p.costos.costo_reposicion} ({type(p.costos.costo_reposicion)})")
            print(f"  Margen: {p.costos.margen_mayorista}")
            print(f"  IVA: {p.costos.iva_alicuota}")
        else:
            print(f"Costos: NONE")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_97()
