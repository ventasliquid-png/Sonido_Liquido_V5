import sqlite3
import os

db_path = "pilot_v5x.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding 'bultos' column...")
    cursor.execute("ALTER TABLE remitos ADD COLUMN bultos INTEGER DEFAULT 1")
    print("Adding 'valor_declarado' column...")
    cursor.execute("ALTER TABLE remitos ADD COLUMN valor_declarado FLOAT DEFAULT 0.0")
    conn.commit()
    print("Migration SUCCESS.")
except Exception as e:
    print(f"Migration ERROR: {e}")
finally:
    conn.close()
