import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pilot.db')

def migrate():
    print(f"--- [MIGRATION V5.5] Logística de Compra ---")
    print(f"Target DB: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(productos)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'presentacion_compra' not in columns:
            print("[MIGRATE] Adding column 'presentacion_compra'...")
            cursor.execute("ALTER TABLE productos ADD COLUMN presentacion_compra TEXT")
        else:
            print("[SKIP] Column 'presentacion_compra' already exists.")

        if 'unidades_bulto' not in columns:
            print("[MIGRATE] Adding column 'unidades_bulto'...")
            cursor.execute("ALTER TABLE productos ADD COLUMN unidades_bulto NUMERIC DEFAULT 1.0")
        else:
             print("[SKIP] Column 'unidades_bulto' already exists.")

        conn.commit()
        print("[SUCCESS] Migration completed successfully.")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
