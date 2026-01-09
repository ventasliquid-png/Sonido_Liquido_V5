import sqlite3
import os

def check_db(db_path):
    print(f"\n--- Verificando {db_path} ---")
    if not os.path.exists(db_path):
        print("ERROR: Archivo no encontrado.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Check tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        
        if 'clientes' in tables:
            # Check for Gelato or specific ID part
            cur.execute("SELECT id, razon_social, activo FROM clientes WHERE razon_social LIKE '%GELATO%' OR id LIKE '%0d9dfdce%'")
            rows = cur.fetchall()
            print(f"Resultados encontrados ({len(rows)}):")
            for r in rows:
                print(f"  - ID (DB): {r[0]} | Razón Social: {r[1]} | Activo: {r[2]}")
        else:
            print("ERROR: La tabla 'clientes' no existe.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

check_db('pilot.db')
