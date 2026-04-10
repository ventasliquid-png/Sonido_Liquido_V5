import sqlite3
import os

db_path = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"

if not os.path.exists(db_path):
    print(f"Error: No existe {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- SCHEMA: clientes ---")
    cursor.execute("PRAGMA table_info(clientes)")
    for col in cursor.fetchall():
        print(col)
        
    print("\n--- EJEMPLO: Primeros 2 clientes ---")
    cursor.execute("SELECT cuit, razon_social, domicilio FROM clientes LIMIT 2")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()
