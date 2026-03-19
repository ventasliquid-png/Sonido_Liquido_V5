import sqlite3
import os

db_path = 'pilot_v5x.db'
if not os.path.exists(db_path):
    print(f"ERROR: {db_path} not found")
    exit(1)

size = os.path.getsize(db_path)
print(f"SIZE: {size} bytes ({size/1024:.2f} KB)")

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Checking both UUID formats just in case
    cur.execute("SELECT razonsocial, flags_estado FROM clientes WHERE id = 'e1be0585cd3443efa33204d00e199c4e' OR id = 'e1be0585-cd34-43ef-a332-04d00e199c4e'")
    row = cur.fetchone()
    if row:
        print(f"LAVIMAR_DATA: {row}")
    else:
        print("LAVIMAR_NOT_FOUND")
    conn.close()
except Exception as e:
    print(f"DB_ERROR: {e}")
