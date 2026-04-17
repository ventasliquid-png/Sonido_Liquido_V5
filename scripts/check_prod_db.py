
import sqlite3
import os

db_path = r'C:\dev\V5-LS\V5_LS_MASTER.db'

if not os.path.exists(db_path):
    print(f"ERROR: DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT COUNT(*) FROM rubros")
    count = cursor.fetchone()[0]
    print(f"Rubros count: {count}")
    
    cursor.execute("SELECT id, nombre FROM rubros LIMIT 5")
    rows = cursor.fetchall()
    for r in rows:
        print(f" - {r[0]}: {r[1]}")
        
    cursor.execute("SELECT COUNT(*) FROM productos")
    prod_count = cursor.fetchone()[0]
    print(f"Productos count: {prod_count}")

except Exception as e:
    print(f"ERROR: {e}")
finally:
    conn.close()
