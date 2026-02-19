
import sqlite3
import os

DB_PATH = os.path.join("backend", "pilot.db")

def migrate_v7():
    print(f"--- MIGRATING PILOT.DB TO V7 LOGISTICS ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. PEDIDOS: Add Logistics Columns
        print("Migrating 'pedidos'...")
        try:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN domicilio_entrega_id CHAR(32);")
            print("  [OK] Added domicilio_entrega_id")
        except sqlite3.OperationalError:
            print("  [SKIP] domicilio_entrega_id already exists")
            
        try:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN transporte_id CHAR(32);")
            print("  [OK] Added transporte_id")
        except sqlite3.OperationalError:
            print("  [SKIP] transporte_id already exists")

        # 2. REMITOS: Add CAE Columns (Manual Support)
        print("Migrating 'remitos'...")
        try:
            cursor.execute("ALTER TABLE remitos ADD COLUMN cae VARCHAR;")
            print("  [OK] Added cae")
        except sqlite3.OperationalError:
            print("  [SKIP] cae already exists")

        try:
            cursor.execute("ALTER TABLE remitos ADD COLUMN vto_cae DATE;")
            print("  [OK] Added vto_cae")
        except sqlite3.OperationalError:
            print("  [SKIP] vto_cae already exists")

        conn.commit()
        print("--- MIGRATION COMPLETE ---")
        
    except Exception as e:
        print(f"Migration Failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        migrate_v7()
    else:
        print(f"Database not found at {DB_PATH}")
