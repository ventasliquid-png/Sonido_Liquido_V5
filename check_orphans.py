import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT count(*) FROM pedidos_items WHERE pedido_id NOT IN (SELECT id FROM pedidos)")
print("Orphan items:", cursor.fetchone()[0])
conn.close()
