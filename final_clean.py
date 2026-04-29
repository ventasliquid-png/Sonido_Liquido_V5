import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM pedidos WHERE id IN (30, 31, 32)")
cursor.execute("DELETE FROM pedidos_items WHERE pedido_id IN (30, 31, 32)")
cursor.execute("DELETE FROM remitos WHERE numero_legal='0016-00001-00002531'")
conn.commit()
print("Database cleaned (30, 31, 32 and Remito deleted)")
conn.close()
