import sqlite3

db_path = r'c:\dev\V5-LS\data\V5_LS_MASTER.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Re-link Remito to Pedido 28
    cursor.execute("UPDATE remitos SET pedido_id = 28 WHERE id = 'dd3d45c971964a8da8c053599a532afd'")
    
    # 2. Re-link RemitoItem to PedidoItem 48
    cursor.execute("UPDATE remitos_items SET pedido_item_id = 48 WHERE remito_id = 'dd3d45c971964a8da8c053599a532afd'")
    
    conn.commit()
    print("Database links fixed successfully.")
except Exception as e:
    conn.rollback()
    print(f"Error fixing links: {e}")
finally:
    conn.close()
