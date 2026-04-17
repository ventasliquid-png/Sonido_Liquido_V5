
import sqlite3
import os

db_path = r'C:\dev\V5-LS\data\V5_LS_MASTER.db'

if not os.path.exists(db_path):
    print(f"ERROR: DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in DB:")
    for t in tables:
        print(f" - {t[0]}")
        
except Exception as e:
    print(f"ERROR: {e}")
finally:
    conn.close()
