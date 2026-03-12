import sqlite3
import os

DB_PATH = "pilot.db"

def migrate_productos():
    print(f"🚀 Iniciando Migración V7 (Productos) en {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("❌ CRITICAL: No se encontró pilot.db")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Check existing columns
    cursor.execute("PRAGMA table_info(productos)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"📋 Columnas actuales: {columns}")
    
    # 2. Add Missing Columns
    cols_to_add = {
        "stock_fisico": "NUMERIC(10, 2) DEFAULT 0.0",
        "stock_reservado": "NUMERIC(10, 2) DEFAULT 0.0"
    }
    
    for col, type_def in cols_to_add.items():
        if col not in columns:
            print(f"🛠 Agregando columna detectada como faltante: {col}...")
            try:
                cursor.execute(f"ALTER TABLE productos ADD COLUMN {col} {type_def}")
                print(f"   ✅ {col} agregada con éxito.")
            except sqlite3.OperationalError as e:
                print(f"   ⚠️ Error al agregar {col}: {e}")
        else:
            print(f"   ✅ {col} ya existe.")
            
    conn.commit()
    conn.close()
    print("🏁 Migración V7 Productos Finalizada.")

if __name__ == "__main__":
    migrate_productos()
