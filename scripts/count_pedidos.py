import sqlite3
import os

DB_PATH = "c:/dev/Sonido_Liquido_V5/pilot.db"

def count_pedidos():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check integrity
        cursor.execute("SELECT count(*) FROM pedidos")
        count = cursor.fetchone()[0]
        print(f"Total entries in 'pedidos' table: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, estado, cliente_id, total FROM pedidos LIMIT 5")
            rows = cursor.fetchall()
            print("First 5 entries:")
            for r in rows:
                print(r)
    except Exception as e:
        print(f"Error querying database: {e}")
            
    conn.close()

if __name__ == "__main__":
    count_pedidos()
