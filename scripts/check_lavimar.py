import sqlite3
import os

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot.db"

def check():
    if not os.path.exists(DB_PATH):
        print(f"DB NOT FOUND at {DB_PATH}")
        return

    print(f"Checking DB at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        print("--- SEARCHING FOR LAVIMAR ---")
        c.execute("SELECT razon_social, cuit, flags_estado, estado_arca FROM clientes WHERE razon_social LIKE '%AVIMAR%'")
        rows = c.fetchall()
        for row in rows:
            print(f"MATCH: {row['razon_social']} | CUIT: {row['cuit']} | Flags: {row['flags_estado']} | State: {row['estado_arca']}")

        print("\n--- RECENTLY CREATED (Today) ---")
        c.execute("SELECT razon_social, cuit, flags_estado, estado_arca, created_at FROM clientes ORDER BY created_at DESC LIMIT 10")
        rows = c.fetchall()
        for row in rows:
            print(f"NEW: {row['razon_social']} | CUIT: {row['cuit']} | Flags: {row['flags_estado']} | State: {row['estado_arca']} | Created: {row['created_at']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check()
