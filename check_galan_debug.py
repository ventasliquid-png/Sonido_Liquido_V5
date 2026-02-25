import sqlite3
import os

db_path = 'c:/dev/Sonido_Liquido_V5/pilot.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("--- Recientes (Top 5) ---")
        cursor.execute("SELECT id, razon_social, created_at, activo, flags_estado FROM clientes ORDER BY created_at DESC LIMIT 5")
        for row in cursor.fetchall():
            print(row)
            
        print("\n--- Búsqueda amplia ---")
        # In case of typos or weird encoding
        cursor.execute("SELECT id, razon_social FROM clientes WHERE razon_social LIKE '%ALA%' OR razon_social LIKE '%BRI%'")
        print(f"Resultados parciales: {cursor.fetchall()}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
