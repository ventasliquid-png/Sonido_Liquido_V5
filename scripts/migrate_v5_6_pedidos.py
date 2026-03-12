import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'pilot.db')

def migrate():
    print(f"--- [MIGRATION V5.6] Logistics Columns in Pedidos ---")
    print(f"Target DB: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(pedidos)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'domicilio_entrega_id' not in columns:
            print("[MIGRATE] Adding column 'domicilio_entrega_id' (GUID)...")
            # SQLite does not support GUID natively, usually TEXT or CHAR(32/36)
            # SQLAlchemy GUID maps to CHAR(32) or UUID in Postgres
            # In SQLite with our GUID type it is likely CHAR(32) or TEXT
            cursor.execute("ALTER TABLE pedidos ADD COLUMN domicilio_entrega_id CHAR(32)")
        else:
            print("[SKIP] Column 'domicilio_entrega_id' already exists.")

        if 'transporte_id' not in columns:
            print("[MIGRATE] Adding column 'transporte_id' (GUID)...")
            cursor.execute("ALTER TABLE pedidos ADD COLUMN transporte_id CHAR(32)")
        else:
            print("[SKIP] Column 'transporte_id' already exists.")

        conn.commit()
        print("[SUCCESS] Migration completed successfully.")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
