import sqlite3
import os

DB_PATH = "pilot.db"

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check pedidos structure
    cursor.execute("PRAGMA table_info(pedidos)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Existing columns in 'pedidos': {columns}")
    
    # Missing 'estado'?
    if "estado" not in columns:
        print("⚠️ 'estado' column missing. Adding it...")
        try:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN estado VARCHAR DEFAULT 'PENDIENTE'")
            print("✅ Added 'estado' column.")
        except Exception as e:
            print(f"❌ Failed to add 'estado': {e}")
            
    # Missing 'nota'?
    if "nota" not in columns:
        print("⚠️ 'nota' column missing. Adding it...")
        try:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN nota TEXT")
            print("✅ Added 'nota' column.")
        except Exception as e:
            print(f"❌ Failed to add 'nota': {e}")

    # Missing 'total'? (Unlikely but checking)
    if "total" not in columns:
         print("⚠️ 'total' column missing. Adding it...")
         try:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN total FLOAT DEFAULT 0.0")
            print("✅ Added 'total' column.")
         except Exception as e:
            print(f"❌ Failed to add 'total': {e}")
            
    # Check pedidos_items structure
    cursor.execute("PRAGMA table_info(pedidos_items)")
    item_columns = [info[1] for info in cursor.fetchall()]
    print(f"Existing columns in 'pedidos_items': {item_columns}")

    # Check for missing item columns
    expected_items = {
        "cantidad": "FLOAT DEFAULT 1.0",
        "precio_unitario": "FLOAT DEFAULT 0.0",
        "subtotal": "FLOAT DEFAULT 0.0",
        "nota": "TEXT" 
    }
    
    for col, defn in expected_items.items():
        if col not in item_columns:
            print(f"⚠️ '{col}' column missing in pedidos_items. Adding it...")
            try:
                cursor.execute(f"ALTER TABLE pedidos_items ADD COLUMN {col} {defn}")
                print(f"✅ Added '{col}' column.")
            except Exception as e:
                print(f"❌ Failed to add '{col}': {e}")
            
                print(f"❌ Failed to add '{col}': {e}")
                
    # Check clientes structure (V5.3 Vector)
    cursor.execute("PRAGMA table_info(clientes)")
    client_columns = [info[1] for info in cursor.fetchall()]
    print(f"Existing columns in 'clientes': {client_columns}")

    if "historial_cache" not in client_columns:
        print("⚠️ 'historial_cache' column missing. Adding it...")
        try:
            # SQLite stores JSON as TEXT
            cursor.execute("ALTER TABLE clientes ADD COLUMN historial_cache TEXT DEFAULT '[]'")
            print("✅ Added 'historial_cache' column.")
        except Exception as e:
            print(f"❌ Failed to add 'historial_cache': {e}")
            
    conn.commit()
    conn.close()
    print("Schema fix attempt complete.")

if __name__ == "__main__":
    fix_schema()
