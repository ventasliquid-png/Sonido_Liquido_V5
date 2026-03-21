import sqlite3
import os

db_path = "pilot_v5x.db"
lavimar_id = "e1be0585cd3443efa33204d00e199c4e"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT id, razon_social, flags_estado FROM clientes WHERE id = ? OR razon_social LIKE '%LAVIMAR%'", (lavimar_id,))
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"RESULT: ID={row[0]}, NAME={row[1]}, FLAGS={row[2]}")
    else:
        print("RESULT:NOT_FOUND")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
