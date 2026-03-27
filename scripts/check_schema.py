import sqlite3
conn = sqlite3.connect('pilot_v5x.db')
cursor = conn.cursor()
for table in ['productos', 'productos_costos', 'clientes']:
    print(f"\n--- {table} ---")
    cursor.execute(f"PRAGMA table_info({table})")
    for row in cursor.fetchall():
        print(row[1])
conn.close()
