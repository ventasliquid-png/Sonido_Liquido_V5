import sqlite3
import os

db_path = "pilot_v5x.db"
lavimar_id = "e1be0585cd3443efa33204d00e199c4e"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT codigo_interno, flags_estado FROM clientes WHERE id = ?", (lavimar_id,))
    row = cursor.fetchone()
    if row:
        print(f"CALIBRATION: {row[1]} / {row[0]}")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
