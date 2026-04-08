import sqlite3
import os

db_path = 'pilot.db'
if not os.path.exists(db_path):
    print(f"File {db_path} does not exist.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check count
cursor.execute("SELECT COUNT(*) FROM clientes WHERE id BETWEEN 2 AND 39")
count = cursor.fetchone()[0]
print(f"ID Range [2-39] Count: {count}")

# Check schema
cursor.execute("PRAGMA table_info(clientes)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Columns in 'clientes': {columns}")
has_flags = 'flags_estado' in columns
print(f"Has 'flags_estado': {has_flags}")

conn.close()

if count >= 38 and has_flags:
    print("INTEGRITY OK")
else:
    print("INTEGRITY FAILED")
