import sqlite3
import os

db_path = r'c:\dev\V5-LS\data\V5_LS_MASTER.db'
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    # Try local dev DB
    db_path = r'c:\dev\Sonido_Liquido_V5\pilot_v5x.db'

print(f"Checking DB: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, total, fecha, nota FROM pedidos ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    print("ID | TOTAL | FECHA | NOTA")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
