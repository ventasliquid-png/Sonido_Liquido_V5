
import sqlite3

def check():
    conn = sqlite3.connect('c:/dev/Sonido_Liquido_V5/pilot_v5x.db')
    cursor = conn.cursor()
    
    print("--- REMITOS ---")
    cursor.execute("SELECT id, pedido_id, numero_legal, estado FROM remitos")
    remitos = cursor.fetchall()
    for r in remitos:
        print(r)
        
    print("\n--- REMITOS_ITEMS (Count per Remito) ---")
    cursor.execute("SELECT remito_id, COUNT(*) FROM remitos_items GROUP BY remito_id")
    counts = cursor.fetchall()
    for c in counts:
        print(c)
        
    print("\n--- SAMPLE ITEMS FOR A REMITO ---")
    if remitos:
        rid = remitos[0][0]
        cursor.execute("SELECT ri.id, ri.pedido_item_id, pi.pedido_id FROM remitos_items ri JOIN pedidos_items pi ON ri.pedido_item_id = pi.id WHERE ri.remito_id = ?", (rid,))
        items = cursor.fetchall()
        for i in items:
            print(i)

    conn.close()

if __name__ == "__main__":
    check()
