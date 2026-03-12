
import sqlite3
import os

# Manual mappings based on typical SQLAlchemy/FastAPI patterns
DB_FILES = ['pilot.db', 'sql_app.db', 'produccion.db', 'data/pilot.db']

def check_raw():
    for db_path in DB_FILES:
        if not os.path.exists(db_path):
            continue
            
        print(f"\n--- Checking {db_path} ---")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # List tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r[0] for r in cursor.fetchall()]
            print(f"Tables: {len(tables)} found")
            
            # Count Clientes
            if 'clientes' in tables:
                cursor.execute("SELECT count(*) FROM clientes")
                print(f"CLIENTES: {cursor.fetchone()[0]}")
            else:
                print("CLIENTES: Table not found")

            # Count Productos
            if 'productos' in tables:
                cursor.execute("SELECT count(*) FROM productos")
                print(f"PRODUCTOS: {cursor.fetchone()[0]}")
            else:
                print("PRODUCTOS: Table not found")
                
            conn.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_raw()
