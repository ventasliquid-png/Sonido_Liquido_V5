import sqlite3
import os

db_path = 'C:/dev/V5-LS/current/pilot_v5x.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} no existe")
else:
    print(f"Abriendo {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tablas encontradas:")
    for t in tables:
        print(f"- {t[0]}")
    conn.close()
