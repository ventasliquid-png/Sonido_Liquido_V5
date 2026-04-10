import sqlite3
import os

db_path = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"

if not os.path.exists(db_path):
    print(f"Error: No existe {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- TABLAS EN LA BASE DE DATOS ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    for t in tables:
        print(t)
        
    print("\n--- BUSCANDO TABLAS RELACIONADAS CON DOMICILIOS/DIRECCIONES ---")
    for t in tables:
        if "domicilio" in t.lower() or "direccion" in t.lower() or "sucursal" in t.lower() or "contacto" in t.lower():
            print(f"\n[SCHEMA: {t}]")
            cursor.execute(f"PRAGMA table_info({t})")
            for col in cursor.fetchall():
                print(col)
                
    conn.close()
