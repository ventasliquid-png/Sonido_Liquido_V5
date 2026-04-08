# [MIGRACION] - scripts\reparacion\inject_canon_column.py
# ---------------------------------------------------------
import sqlite3
import os

db_path = r'C:\dev\V5-LS\data\V5_LS_MASTER.db'

def inject():
    if not os.path.exists(db_path):
        print(f"Error: DB no encontrada en {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(clientes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "razon_social_canon" not in columns:
            print(f"Inyectando columna 'razon_social_canon' en {db_path}...")
            cursor.execute("ALTER TABLE clientes ADD COLUMN razon_social_canon TEXT")
            conn.commit()
            print("✅ Columna inyectada con éxito.")
        else:
            print("ℹ️ La columna 'razon_social_canon' ya existe.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inject()
