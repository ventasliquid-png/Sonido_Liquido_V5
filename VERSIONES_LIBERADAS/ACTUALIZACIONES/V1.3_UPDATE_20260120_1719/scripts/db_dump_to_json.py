import sqlite3
import json
import os
from datetime import datetime

DB_PATH = 'pilot.db'
OUTPUT_DIR = 'backend/data/json_mirror'

def dump_to_json():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: No se encuentra {DB_PATH}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"📂 Carpeta creada: {OUTPUT_DIR}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row['name'] for row in cursor.fetchall()]

    print(f"📡 Iniciando DUMP de {len(tables)} tablas...")

    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = [dict(row) for row in cursor.fetchall()]
            
            output_file = os.path.join(OUTPUT_DIR, f"{table}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(rows, f, indent=4, ensure_ascii=False)
            
            print(f"   ✅ {table}: {len(rows)} registros -> {output_file}")
        except Exception as e:
            print(f"   ❌ Error en tabla '{table}': {e}")

    conn.close()
    print(f"\n✨ Dump completado exitosamente en {OUTPUT_DIR}")

if __name__ == "__main__":
    dump_to_json()
