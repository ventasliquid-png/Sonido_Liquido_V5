import sqlite3
import os

db_path = "pilot_v5x.db"
uuid = "e1be0585cd3443efa33204d00e199c4e"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT flags_estado FROM clientes WHERE id = ?", (uuid,))
    row = cursor.fetchone()
    if row:
        print(f"RESULT:{row[0]}")
    else:
        print("RESULT:NOT_FOUND")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
