import sqlite3
import os

db_path = "C:/dev/V5-LS/data/V5_LS_MASTER.db"
if not os.path.exists(db_path):
    print(f"File {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    for table_name in [t[0] for t in tables]:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print(f"\nTable {table_name}:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    conn.close()
