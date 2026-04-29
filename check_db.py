import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT id, nota FROM pedidos WHERE created_at >= '2026-04-29'")
print("Pedidos hoy:", cursor.fetchall())
conn.close()
