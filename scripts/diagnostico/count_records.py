import sqlite3
import os

def count_records(db_path):
    if not os.path.exists(db_path):
        print(f"ERROR: {db_path} not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        counts = {}
        for table in ['clientes', 'productos', 'pedidos']:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cur.fetchone()[0]
            except sqlite3.OperationalError:
                counts[table] = "TABLE_MISSING"
        
        print(f"Conteos en {db_path}:")
        print(f"Clientes: {counts['clientes']}")
        print(f"Productos: {counts['productos']}")
        print(f"Pedidos: {counts['pedidos']}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_records('pilot.db')
