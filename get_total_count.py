import sqlite3
import os

db_path = 'pilot_v5x.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM clientes')
    count = cursor.fetchone()[0]
    print(f"TOTAL_CLIENTES_START")
    print(count)
    print(f"TOTAL_CLIENTES_END")
    conn.close()
else:
    print("FILE_NOT_FOUND")
