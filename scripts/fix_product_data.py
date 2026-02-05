
import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text
# Force Local DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # scripts/
ROOT_DIR = os.path.dirname(BASE_DIR) # root/
pilot_db_path = os.path.join(ROOT_DIR, "pilot.db")
DATABASE_URL = f"sqlite:///{pilot_db_path}"

print(f"--- FIXING DATA ON: {DATABASE_URL} ---")
engine = create_engine(DATABASE_URL)

def fix_missing_costs():
    print("\n--- FIXING MISSING COSTS ---")
    with engine.connect() as conn:
        # 1. Find Products without Costs
        # Left join where right is null
        query = text("""
            SELECT p.id, p.nombre 
            FROM productos p 
            LEFT JOIN productos_costos pc ON p.id = pc.producto_id
            WHERE pc.id IS NULL
        """)
        products = conn.execute(query).fetchall()
        
        if not products:
            print("  [OK] All products have cost records.")
            return

        print(f"  [FIX] Found {len(products)} products without cost records. Creating defaults...")
        
        for p in products:
            print(f"    - Creating costs for Prod ID {p.id} ({p.nombre})")
            # Insert default cost
            insert_sql = text("""
                INSERT INTO productos_costos (producto_id, costo_reposicion, rentabilidad_target, precio_roca, moneda_costo, iva_alicuota)
                VALUES (:pid, 0, 30.00, 0, 'ARS', 21.00)
            """)
            conn.execute(insert_sql, {"pid": p.id})
            
        print("  [DONE] Costs created.")
        conn.commit()

if __name__ == "__main__":
    try:
        fix_missing_costs()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
