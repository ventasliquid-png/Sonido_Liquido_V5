import sqlite3
import json
import os

DB_PATH = 'c:/dev/Sonido_Liquido_V5/backend/pilot.db'

def count_records():
    if not os.path.exists(DB_PATH):
        print(json.dumps({"error": f"Database not found at {DB_PATH}"}))
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        counts = {}
        tables = ['clientes', 'productos', 'pedidos']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                counts[table] = "Error: Table not found"

        print(json.dumps(counts, indent=2))
        conn.close()
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    count_records()
