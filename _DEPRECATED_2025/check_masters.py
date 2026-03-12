
import sqlite3
import os

DB_PATH = "pilot.db"

def check_masters():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['condiciones_iva', 'segmentos', 'listas_precios', 'provincias']
    
    print(f"--- Checking Masters in {DB_PATH} ---")
    for t in tables:
        try:
            cursor.execute(f"SELECT count(*) FROM {t}")
            count = cursor.fetchone()[0]
            print(f"{t.upper()}: {count}")
            
            if count > 0:
                cursor.execute(f"SELECT nombre FROM {t} LIMIT 3")
                print(f"   Examples: {[r[0] for r in cursor.fetchall()]}")
        except Exception as e:
            print(f"{t.upper()}: Error ({e})")
            
    conn.close()

if __name__ == "__main__":
    check_masters()
