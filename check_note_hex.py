import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT id, nota FROM pedidos WHERE id = 31")
row = cursor.fetchone()
if row:
    print(f"ID: {row[0]}")
    print(f"Nota (hex): {row[1].encode('utf-8').hex()}")
    print(f"Nota (raw): {row[1]}")
conn.close()
