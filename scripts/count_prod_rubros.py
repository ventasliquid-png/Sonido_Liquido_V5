
import sqlite3
import os

db_path = r'C:\dev\V5-LS\data\V5_LS_MASTER.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT COUNT(*) FROM rubros")
    print(f"Rubros count: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT id, nombre FROM rubros")
    for r in cursor.fetchall():
        print(f" - {r[0]}: {r[1]}")
        
except Exception as e:
    print(f"ERROR: {e}")
finally:
    conn.close()
