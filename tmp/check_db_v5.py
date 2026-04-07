import sqlite3
import json
import os

DB_PATH = 'pilot_v5x.db'

def count_records():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        counts = {}
        tables = ['clientes', 'productos', 'pedidos', 'remitos', 'domicilios']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except sqlite3.OperationalError as e:
                counts[table] = f"Error: {e}"

        print(json.dumps(counts, indent=2))
        
        # Check latest 3 orders
        try:
            cursor.execute("SELECT id, fecha, total FROM pedidos ORDER BY fecha DESC LIMIT 3")
            print("\nÚltimos 3 Pedidos:")
            for row in cursor.fetchall():
                print(f" ID: {row[0]}, Fecha: {row[1]}, Total: {row[2]}")
        except:
            pass

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_records()
