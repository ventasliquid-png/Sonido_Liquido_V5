import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT id, cliente_id, nota FROM pedidos WHERE id IN (30, 31)")
for row in cursor.fetchall():
    print(row)
conn.close()
