import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal, engine, Base
from backend.clientes.models import Cliente
from backend.pedidos.models import Pedido
# Ensure all models are registered
from backend.maestros.models import *

def warm_cache():
    print("--- Starting History Cache Warmer ---")
    db = SessionLocal()
    
    try:
        clients = db.query(Cliente).all()
        print(f"Found {len(clients)} clients.")
        
        count = 0
        for c in clients:
            # Fetch orders via ORM relationship or direct query
            # Direct query is safer if relationship has lazy loading issues in scripts
            # Casting ID to string comparison to be 100% safe against UUID/String mismatch in SQLite
            
            # Using Python-side filtering for max robustness (Vector Strategy Philosophy)
            raw_orders = db.query(Pedido).order_by(Pedido.fecha.desc()).all()
            
            my_orders = []
            c_id_str = str(c.id).replace("-", "")
            
            for p in raw_orders:
                p_id_str = str(p.cliente_id).replace("-", "")
                if p_id_str == c_id_str:
                    my_orders.append(p)
                    if len(my_orders) >= 5:
                        break
            
            if my_orders:
                cache = []
                for p in my_orders:
                    cache.append({
                        "id": p.id,
                        "cliente_id": str(c.id),
                        "fecha": p.fecha.isoformat() if p.fecha else None,
                        "total": p.total,
                        "estado": p.estado or "PENDIENTE",
                        "nota": p.nota
                    })
                
                c.historial_cache = cache
                db.add(c)
                count += 1
                print(f" -> {c.razon_social}: Updated with {len(cache)} orders.")
        
        db.commit()
        print(f"--- Completed. Updated {count} clients. ---")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    warm_cache()
