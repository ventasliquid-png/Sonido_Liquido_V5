import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT id, origen, fecha, created_at, nota FROM pedidos WHERE nota LIKE '%00001-00002531%'")
for row in cursor.fetchall():
    print(row)
conn.close()
