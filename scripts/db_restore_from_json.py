import sqlite3
import json
import os
import sys

# Ruta por defecto
DEFAULT_DB_PATH = 'pilot.db'
SOURCE_DIR = 'backend/data/json_mirror'

def restore_from_json(target_db=None):
    db_path = target_db if target_db else DEFAULT_DB_PATH
    
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Error: No se encuentra la carpeta de espejos {SOURCE_DIR}")
        return

    json_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.json')]
    if not json_files:
        print(f"⚠️ No se encontraron archivos JSON en {SOURCE_DIR}")
        return

    print(f"📡 Iniciando RESTORE desde {len(json_files)} espejos JSON hacia {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Desactivar llaves foráneas temporalmente para el wipe/reload
    cursor.execute("PRAGMA foreign_keys = OFF;")

    for json_file in json_files:
        table_name = json_file.replace('.json', '')
        file_path = os.path.join(SOURCE_DIR, json_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                print(f"   ⚠️ {table_name}: Espejo vacío, saltando.")
                continue

            # Obtener columnas del primer registro
            columns = data[0].keys()
            
            # Limpiar tabla
            cursor.execute(f"DELETE FROM {table_name};")
            
            # Insertar datos
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])})"
            cursor.executemany(query, [tuple(row.get(col) for col in columns) for row in data])
            
            print(f"   ✅ {table_name}: {len(data)} registros restaurados.")
        except Exception as e:
            print(f"   ❌ Error restaurando '{table_name}': {e}")

    conn.commit()
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.close()
    print(f"\n✨ Base de datos reconstruida exitosamente.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    restore_from_json(target)
