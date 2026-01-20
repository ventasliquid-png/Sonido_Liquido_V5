import sqlite3
import json
import os

def audit():
    try:
        # Check root pilot.db specifically
        db_path = 'c:/dev/Sonido_Liquido_V5/pilot.db'
        print(f"Auditing DB at: {db_path}")
        if not os.path.exists(db_path):
            print("File not found")
            return

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Row counts
        res = {
            "clientes": cursor.execute('SELECT COUNT(*) FROM clientes').fetchone()[0],
            "productos": cursor.execute('SELECT COUNT(*) FROM productos').fetchone()[0],
            "segmentos": cursor.execute('SELECT COUNT(*) FROM segmentos').fetchone()[0],
            "pedidos": cursor.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]
        }
        
        print(json.dumps(res, indent=2))
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit()
