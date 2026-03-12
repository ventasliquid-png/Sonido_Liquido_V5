import sqlite3
import os
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "pilot.db")

def test_write():
    print(f"Checking write access to: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5) # 5s timeout
        cursor = conn.cursor()
        
        # Try to insert a dummy log
        # Assuming audit table exists or create temp
        cursor.execute("CREATE TABLE IF NOT EXISTS _debug_write_check (id TEXT PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        
        uid = str(uuid.uuid4())
        cursor.execute("INSERT INTO _debug_write_check (id) VALUES (?)", (uid,))
        conn.commit()
        print("WRITE SUCCESS")
        
        conn.close()
    except Exception as e:
        print(f"WRITE FAILED: {e}")

if __name__ == "__main__":
    test_write()
