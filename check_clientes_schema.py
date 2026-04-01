import sqlite3
import os

db_path = "pilot_v5x.db"
if not os.path.exists(db_path):
    print(f"File {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    table_name = "clientes"
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print(f"Table {table_name} Columns:")
    for col in columns:
        print(f"  {col[1]}")
    conn.close()
