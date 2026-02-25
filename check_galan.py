import sqlite3
import os

db_path = 'c:/dev/Sonido_Liquido_V5/pilot.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {tables}")
        
        if ('clientes',) in tables:
            cursor.execute("SELECT id, razon_social, cuit, activo, flags_estado, created_at FROM clientes WHERE razon_social LIKE '%Galan%' OR razon_social LIKE '%Sabrina%'")
            results = cursor.fetchall()
            print(f"Results: {results}")
            if not results:
                print("No results found for Galan/Sabrina")
        else:
            print("Table 'clientes' not found")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
