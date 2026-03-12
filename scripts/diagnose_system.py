
import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text
from backend.core.database import DATABASE_URL


print(f"--- [DATABASE] Usando URL: {DATABASE_URL} ---")
# FORCE LOCAL PILOT.DB for diagnosis (Ignere weird shell env)
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # scripts/
ROOT_DIR = os.path.dirname(BASE_DIR) # root/
pilot_db_path = os.path.join(ROOT_DIR, "pilot.db")
DATABASE_URL = f"sqlite:///{pilot_db_path}"
print(f"--- [DIAGNOSIS] FORCING LOCAL DB: {DATABASE_URL} ---")

engine = create_engine(DATABASE_URL)

def check_rubro_cycles():
    print("\n--- CHECKING RUBRO CYCLES (RAW SQL) ---")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, padre_id, nombre FROM rubros"))
        rubros = result.fetchall()
        
    print(f"Total Rubros: {len(rubros)}")
    
    # Build Map
    rubro_map = {r.id: r for r in rubros}
    
    has_cycle = False
    for r in rubros:
        visited = set()
        curr_id = r.id
        path = []
        
        while curr_id:
            if curr_id in visited:
                curr_name = rubro_map[curr_id].nombre if curr_id in rubro_map else 'Unknown'
                print(f"  [ERROR] Cycle detected! Rubro ID {r.id} ({r.nombre}) loops back to {curr_id} ({curr_name})")
                print(f"  Path: {' -> '.join([str(x) for x in path])} -> {curr_id}")
                has_cycle = True
                break
            
            visited.add(curr_id)
            path.append(curr_id)
            
            if curr_id not in rubro_map:
                break # Parent missing?
                
            curr_obj = rubro_map[curr_id]
            curr_id = curr_obj.padre_id # Might be None
            
    if not has_cycle:
        print("  [OK] No cycles detected in Rubros.")

def check_client_fiscal():
    print("\n--- CHECKING CLIENTE FISCAL ADDRESSES (RAW SQL) ---")
    with engine.connect() as conn:
        # Get active clients
        clients = conn.execute(text("SELECT id, razon_social FROM clientes WHERE activo = true")).fetchall()
        
        issues = 0
        for c in clients:
            doms = conn.execute(text(f"SELECT id, es_fiscal, es_entrega, calle, numero FROM domicilios WHERE cliente_id = '{c.id}' AND activo = true")).fetchall()
            
            fiscals = [d for d in doms if d.es_fiscal]
            
            if len(fiscals) == 0:
                print(f"  [WARNING] Cliente ID {c.id} ('{c.razon_social}') has NO active Fiscal Address.")
                issues += 1
                for d in doms:
                    print(f"    - Dom ID {d.id}: {d.calle} {d.numero} (Fiscal: {d.es_fiscal}, Entrega: {d.es_entrega})")
            elif len(fiscals) > 1:
                print(f"  [WARNING] Cliente ID {c.id} ('{c.razon_social}') has MULTIPLE Fiscal Addresses ({len(fiscals)}).")
                issues += 1
                
        if issues == 0:
            print("  [OK] All active clients have exactly one active fiscal address.")

def check_products_integrity():
    print("\n--- CHECKING PRODUCTS INTEGRITY (RAW SQL) ---")
    with engine.connect() as conn:
        try:
            # Check products with null costs or rubro issues
            # Assuming 'productos' has 'id' and 'rubro_id'
            # Assuming 'productos_costos' has 'producto_id' and 'costo_reposicion'
            
            # Check costorphans or nulls
            query = text("""
                SELECT p.id, p.nombre, pc.costo_reposicion, pc.rentabilidad_target 
                FROM productos p 
                LEFT JOIN productos_costos pc ON p.id = pc.producto_id
                WHERE p.activo = true 
                LIMIT 50
            """)
            rows = conn.execute(query).fetchall()
            print(f"  [OK] Sampled {len(rows)} active products.")
            
            for row in rows:
                if row.costo_reposicion is None:
                     print(f"    [ERROR] Prod ID {row.id} ({row.nombre}): Missing Costo Reposicion (NULL or No Record)")
                elif row.costo_reposicion == 0:
                     pass # 0 is allowed but suspicious for pricing engine logic if handled poorly
                     
        except Exception as e:
            print(f"  [ERROR] querying products: {e}")

if __name__ == "__main__":
    try:
        check_rubro_cycles()
        check_client_fiscal()
        check_products_integrity()
    except Exception as e:
        print(f"CRITICAL SCRIPT ERROR: {e}")
