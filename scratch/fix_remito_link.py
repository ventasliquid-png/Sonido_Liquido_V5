import sqlite3

db_path = r'c:\dev\V5-LS\data\V5_LS_MASTER.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get remito info
cursor.execute("SELECT id, pedido_id, numero_legal FROM remitos WHERE numero_legal LIKE '%2528%'")
remito = cursor.fetchone()
print(f"Remito: {remito}")

# Get items of this remito
if remito:
    cursor.execute("SELECT id, pedido_item_id, cantidad FROM remitos_items WHERE remito_id = ?", (remito[0],))
    print(f"Remito Items: {cursor.fetchall()}")

# Get items of Pedido 28
cursor.execute("SELECT id, producto_id, cantidad FROM pedidos_items WHERE pedido_id = 28")
print(f"Pedido 28 Items: {cursor.fetchall()}")

conn.close()
