
import sqlite3

def check():
    conn = sqlite3.connect('c:/dev/Sonido_Liquido_V5/pilot_v5x.db')
    cursor = conn.cursor()
    
    print("--- REMITOS ---")
    cursor.execute("SELECT id, pedido_id, numero_legal, estado FROM remitos")
    remitos = cursor.fetchall()
    for r in remitos:
        print(f"Remito ID: {r[0]}, Pedido ID: {r[1]}, Num: {r[2]}")
        
    print("\n--- REMITOS_ITEMS (Trazabilidad) ---")
    cursor.execute("""
        SELECT ri.remito_id, r.numero_legal, ri.pedido_item_id, pi.pedido_id 
        FROM remitos_items ri 
        JOIN remitos r ON ri.remito_id = r.id
        JOIN pedidos_items pi ON ri.pedido_item_id = pi.id
    """)
    items = cursor.fetchall()
    for i in items:
        print(f"R_ID: {i[0][:8]}, R_Num: {i[1]}, PI_ID: {i[2]}, P_ID: {i[3]}")

    conn.close()

if __name__ == "__main__":
    check()
