import sqlite3
import sys

def force_update():
    try:
        print("Connecting to pilot_v5x.db...")
        conn = sqlite3.connect('pilot_v5x.db', timeout=30)
        # Try to switch to WAL to increase concurrency/overcome locks
        print("Setting WAL mode...")
        # conn.execute('PRAGMA journal_mode=WAL') # This might block too
        print("Executing UPDATE...")
        cur = conn.execute('UPDATE clientes SET flags_estado = 8205 WHERE id = "e1be0585cd3443efa33204d00e199c4e"')
        print(f"Rows affected: {cur.rowcount}")
        print("Committing...")
        conn.commit()
        print("Closing...")
        conn.close()
        print("SUCCESS")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    force_update()
