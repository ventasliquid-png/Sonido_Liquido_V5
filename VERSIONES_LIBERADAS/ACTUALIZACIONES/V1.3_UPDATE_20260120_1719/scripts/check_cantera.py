import sqlite3
import os

db_path = 'backend/data/cantera.db'
if not os.path.exists(db_path):
    print(f"ERROR: {db_path} not found")
    exit()

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"Tables found: {tables}")
    
    if ('clientes',) in tables:
        # Search for PET
        results = cursor.execute("SELECT razon_social, cuit FROM clientes WHERE razon_social LIKE '%pet%' OR razon_social LIKE '%PET%'").fetchall()
        print(f"Search results for 'PET': {results}")
        
        # Count total
        count = cursor.execute("SELECT count(*) FROM clientes").fetchone()[0]
        print(f"Total rows in clientes: {count}")
    else:
        print("Table 'clientes' NOT FOUND in cantera.db")

except Exception as e:
    print(f"Database Error: {e}")
