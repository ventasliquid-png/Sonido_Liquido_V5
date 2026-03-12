
import sqlite3

DB_PATH = "pilot.db"

def fix_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Checking schema for {DB_PATH}...")

    # 1. PEDIDOS table - Add 'estado' column
    try:
        cursor.execute("SELECT estado FROM pedidos LIMIT 1")
        print("✅ Column 'estado' already exists in 'pedidos'.")
    except sqlite3.OperationalError:
        print("⚠️ Column 'estado' missing in 'pedidos'. Adding it...")
        try:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN estado VARCHAR DEFAULT 'PENDIENTE'")
            conn.commit()
            print("✅ Column 'estado' added successfully.")
        except Exception as e:
            print(f"❌ Failed to add column 'estado': {e}")

    try:
        cursor.execute("SELECT oc FROM pedidos LIMIT 1")
        print("✅ Column 'oc' already exists in 'pedidos'.")
    except sqlite3.OperationalError:
        print("⚠️ Column 'oc' missing in 'pedidos'. Adding it...")
        try:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN oc VARCHAR")
            conn.commit()
            print("✅ Column 'oc' added successfully.")
        except Exception as e:
            print(f"❌ Failed to add column 'oc': {e}")

            
    # 2. Check for PEDIDOS_ITEMS vs PEDIDO_ITEMS
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    
    if "pedidos_items" in tables:
        print("✅ Table 'pedidos_items' exists.")
    elif "pedido_items" in tables:
        print("⚠️ Found 'pedido_items' (Singular). Renaming to 'pedidos_items' (Plural)...")
        try:
            cursor.execute("ALTER TABLE pedido_items RENAME TO pedidos_items")
            conn.commit()
            print("✅ Renamed successfully.")
        except Exception as e:
            print(f"❌ Failed to rename table: {e}")
    else:
        print("❌ CRITICAL: Neither 'pedidos_items' nor 'pedido_items' found.")

    # 3. PEDIDOS_ITEMS - Check 'nota'
    try:
        cursor.execute("SELECT nota FROM pedidos_items LIMIT 1")
        print("✅ Column 'nota' already exists in 'pedidos_items'.")
    except sqlite3.OperationalError:
        print("⚠️ Column 'nota' missing in 'pedidos_items'. Adding it...")
        try:
            cursor.execute("ALTER TABLE pedidos_items ADD COLUMN nota VARCHAR")
            conn.commit()
            print("✅ Column 'nota' added successfully.")
        except Exception as e:
            print(f"❌ Failed to add column 'nota': {e}")
            
    conn.close()

if __name__ == "__main__":
    fix_schema()
