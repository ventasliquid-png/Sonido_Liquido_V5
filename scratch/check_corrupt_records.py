
import sqlite3
import os

DB_PATH = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- INVENTARIO DE REMITOS SOSPECHOSOS ---")
    cursor.execute("SELECT id, numero_legal, pedido_id FROM remitos WHERE numero_legal LIKE '%00002529%';")
    remitos = cursor.fetchall()
    for r in remitos:
        print(f"Remito ID: {r[0]} | Numero: {r[1]} | Pedido ID: {r[2]}")
        
        cursor.execute(f"SELECT id, total FROM pedidos WHERE id={r[2]};")
        pedido = cursor.fetchone()
        if pedido:
            print(f"  -> Pedido ID: {pedido[0]} | Total: {pedido[1]}")
        else:
            print(f"  -> [ALERTA] Pedido {r[2]} NO EXISTE en la tabla 'pedidos'.")

    conn.close()

if __name__ == "__main__":
    check_db()
