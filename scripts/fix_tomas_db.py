import sqlite3
import os

db_path = r"C:\SL_SYSTEM\pilot.db"

if not os.path.exists(db_path):
    print(f"❌ Error: No se encontró la base de datos en: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

print(f"--- Iniciando reparación de esquema en {db_path} ---")

try:
    # 1. Verificar si existe la columna nivel
    cols = [col[1] for col in c.execute("PRAGMA table_info(segmentos)").fetchall()]
    if 'nivel' not in cols:
        print("🛠️ Agregando columna 'nivel' a la tabla 'segmentos'...")
        c.execute("ALTER TABLE segmentos ADD COLUMN nivel INTEGER DEFAULT 1")
    else:
        print("✅ La columna 'nivel' ya existe.")

    # 2. Verificar otras discrepancias comunes en V5.X
    # (Opcional: Agregar aquí otros FIXES si se detectan más errores en los logs de Tomás)
    
    conn.commit()
    print("✨ Reparación finalizada con éxito.")
except Exception as e:
    print(f"❌ Fallo durante la reparación: {e}")
finally:
    conn.close()
