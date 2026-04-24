import sqlite3
import os

db_path = r'c:\dev\V5-LS\data\V5_LS_MASTER.db'
if not os.path.exists(db_path):
    db_path = r'c:\dev\Sonido_Liquido_V5\pilot_v5x.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # We target orders with 0 total and "Ingesta" in the note
    cursor.execute("SELECT id FROM pedidos WHERE total = 0.0 AND nota LIKE '%Ingesta Automática%'")
    ids_to_delete = [row[0] for row in cursor.fetchall()]
    
    if ids_to_delete:
        print(f"Deleting orders: {ids_to_delete}")
        # Delete items first
        cursor.execute(f"DELETE FROM pedidos_items WHERE pedido_id IN ({','.join(map(str, ids_to_delete))})")
        # Delete orders
        cursor.execute(f"DELETE FROM pedidos WHERE id IN ({','.join(map(str, ids_to_delete))})")
        # Delete associated remitos
        cursor.execute(f"DELETE FROM remitos WHERE pedido_id IN ({','.join(map(str, ids_to_delete))})")
        
        conn.commit()
        print("Cleanup complete.")
    else:
        print("No $0 Ingesta orders found for cleanup.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
