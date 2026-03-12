import sqlite3
import os
from datetime import datetime

DB_PATH = "pilot.db"

def migrate_arca_flags():
    print(f"🚀 Iniciando Migración MDM (ARCA Flags) en {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("❌ CRITICAL: No se encontró pilot.db")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Check existing columns
    cursor.execute("PRAGMA table_info(clientes)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"📋 Columnas actuales en clientes: {columns}")
    
    # 2. Add Missing Columns
    cols_to_add = {
        "estado_arca": "VARCHAR DEFAULT 'PENDIENTE'",
        "datos_arca_last_update": "DATETIME"
    }
    
    for col, type_def in cols_to_add.items():
        if col not in columns:
            print(f"🛠 Agregando columna: {col}...")
            try:
                cursor.execute(f"ALTER TABLE clientes ADD COLUMN {col} {type_def}")
                print(f"   ✅ {col} agregada con éxito.")
            except sqlite3.OperationalError as e:
                print(f"   ⚠️ Error al agregar {col}: {e}")
        else:
            print(f"   ✅ {col} ya existe.")
            
    conn.commit()
    conn.close()
    print("🏁 Migración MDM Finalizada.")

if __name__ == "__main__":
    migrate_arca_flags()
