import sqlite3
import os

DB_PATH = 'pilot_v5x.db'
UUID_LAVIMAR = 'e1be0585cd3443efa33204d00e199c4e'
TARGET_FLAGS = 8205

def run_canary():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: {DB_PATH} not found.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes'")
        if not cursor.fetchone():
            print("ERROR: Table 'clientes' not found.")
            return

        cursor.execute("SELECT razon_social, flags_estado FROM clientes WHERE id=?", (UUID_LAVIMAR,))
        row = cursor.fetchone()
        
        if row:
            name, flags = row
            print(f"CANARY_RESULT: OK")
            print(f"CLIENT: {name}")
            print(f"FLAGS: {flags}")
            if flags == TARGET_FLAGS:
                print("INTEGRITY: NOMINAL GOLD")
            else:
                print(f"INTEGRITY: MISMATCH (Expected {TARGET_FLAGS}, got {flags})")
        else:
            print(f"CANARY_RESULT: FAILED (UUID {UUID_LAVIMAR} not found)")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_canary()
