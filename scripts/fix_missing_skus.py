
import sys
from pathlib import Path
from sqlalchemy import func

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from backend.core.database import SessionLocal
from backend.productos.models import Producto

def main(apply_fix=False):
    db = SessionLocal()
    try:
        # 1. Get Products without SKU
        missing_sku_prods = db.query(Producto).filter(Producto.sku == None).all()
        count = len(missing_sku_prods)
        
        print(f"--- REPORTE SKU ---")
        print(f"Productos sin SKU encontrados: {count}")
        
        if count == 0:
            print("El padrón está limpio.")
            return

        # 2. Get Max SKU
        max_sku = db.query(func.max(Producto.sku)).scalar() or 10000
        print(f"Último SKU utilizado: {max_sku}")
        
        if not apply_fix:
            print("\n[DRY RUN] Se asignarían los siguientes SKUs:")
            current_sku = max_sku
            for p in missing_sku_prods[:5]: # Show first 5
                current_sku += 1
                print(f" - {p.nombre}: Nuevo SKU -> {current_sku}")
            if count > 5:
                print(f" ... y {count - 5} más.")
            print("\nPara aplicar los cambios, ejecuta con el argumento '--fix'")
        else:
            print("\n[APPLYING FIX] Asignando SKUs...")
            current_sku = max_sku
            for p in missing_sku_prods:
                current_sku += 1
                p.sku = current_sku
                print(f" [FIX] {p.nombre} -> SKU {current_sku}")
            
            db.commit()
            print(f"\n✅ Se actualizaron {count} productos con nuevos SKUs.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    apply = '--fix' in sys.argv
    main(apply)
