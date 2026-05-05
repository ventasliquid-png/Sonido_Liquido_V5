import sqlite3
import os

db_path = r'c:\dev\V5-LS\data\V5_LS_MASTER.db'
if not os.path.exists(db_path):
    db_path = r'c:\dev\Sonido_Liquido_V5\pilot_v5x.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Check items for orders 26, 27, 28, 29
    ids = (26, 27, 28, 29)
    print(f"Checking items for IDs: {ids}")
    cursor.execute(f"SELECT pedido_id, producto_id, cantidad, precio_unitario, subtotal FROM pedidos_items WHERE pedido_id IN {ids}")
    rows = cursor.fetchall()
    print("PEDIDO_ID | PROD_ID | CANT | PRECIO | SUBTOTAL")
    print("-" * 60)
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
