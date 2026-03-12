
import sqlite3
import json
import os
from pathlib import Path

# Config
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "cantera_transfer.db"
JSON_DIR = BASE_DIR / "backend" / "data" / "json_mirror"

def export_clients():
    if not DB_PATH.exists():
        print(f"❌ Error: No se encuentra {DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"--- Exportando Clientes desde {DB_PATH} ---")
    cursor.execute("SELECT * FROM clientes")
    rows = cursor.fetchall()
    
    data = [dict(row) for row in rows]
    
    output_file = JSON_DIR / "clientes.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    print(f"✅ {len(data)} clientes exportados a {output_file}")
    conn.close()

def export_products():
    if not DB_PATH.exists():
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"--- Exportando Productos desde {DB_PATH} ---")
    try:
        cursor.execute("SELECT * FROM productos")
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
        
        output_file = JSON_DIR / "productos.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            
        print(f"✅ {len(data)} productos exportados a {output_file}")
    except Exception as e:
        print(f"❌ Error exportando productos: {e}")
    
    conn.close()

if __name__ == "__main__":
    export_clients()
    export_products()
