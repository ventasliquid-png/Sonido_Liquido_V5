import sqlite3
import os

db_path = "pilot_v5x.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(clientes)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"COL:{col[1]}")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
