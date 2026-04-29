import sys
import os

# Add backend to path (Production)
sys.path.insert(0, 'C:/dev/V5-LS/current')

# Set database URL to production
os.environ['DATABASE_URL'] = 'sqlite:///C:/dev/V5-LS/data/V5_LS_MASTER.db'

from backend.core.database import SessionLocal
from sqlalchemy import text

def run_audit():
    db = SessionLocal()
    try:
        print("\n--- INICIANDO AUDITORÍA DE INTEGRIDAD REMITO-PEDIDO ---")
        
        query = text("""
            SELECT ri.id, ri.remito_id, ri.pedido_item_id, r.pedido_id as remito_p_id, pi.pedido_id as item_p_id
            FROM remitos_items ri
            JOIN remitos r ON ri.remito_id = r.id
            JOIN pedidos_items pi ON ri.pedido_item_id = pi.id
            WHERE r.pedido_id != pi.pedido_id;
        """)
        
        results = db.execute(query).fetchall()
        
        if not results:
            print("[OK] No se encontraron inconsistencias. Todos los RemitoItems coinciden con el Pedido de su Remito.")
        else:
            print(f"[ALERTA] Se encontraron {len(results)} inconsistencias:")
            for row in results:
                print(f"  - RemitoItem {row.id}: Remito {row.remito_id} (Pedido {row.remito_p_id}) -> Item {row.pedido_item_id} (Pedido {row.item_p_id})")
        
        print("\n--- AUDITORÍA FINALIZADA ---")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_audit()
