import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pilot_v5x.db'))

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"Error: No se encuentra la base de datos en {DB_PATH}")
        return False
        
    backup_path = DB_PATH.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    shutil.copy2(DB_PATH, backup_path)
    print(f"[MIGRATION 034] Backup creado en {backup_path}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(pedidos_items)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'cantidad_entregada' not in columns:
            print("[MIGRATION 034] Agregando columna cantidad_entregada a pedidos_items...")
            cursor.execute("ALTER TABLE pedidos_items ADD COLUMN cantidad_entregada REAL DEFAULT 0.0")
            print("[MIGRATION 034] Columna agregada correctamente.")
        else:
            print("[MIGRATION 034] La columna cantidad_entregada ya existe en pedidos_items.")
            
        conn.commit()
        return True
    except Exception as e:
        print(f"[MIGRATION 034] ERROR: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Iniciando migración 034: cantidad_entregada")
    success = run_migration()
    if success:
        print("Migración completada con éxito.")
    else:
        print("Migración fallida.")
