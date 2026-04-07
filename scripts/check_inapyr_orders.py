import sqlite3
import os

PROD_DB = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"

def check_orders(db_path, ids):
    if not os.path.exists(db_path):
        print(f" [!] Error: DB not found in {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for client_id in ids:
        print(f"\n--- Verificando Pedidos para Client ID: {client_id} ---")
        try:
            cursor.execute("SELECT id, estado, total FROM pedidos WHERE cliente_id = ?;", (client_id,))
            orders = cursor.fetchall()
            if not orders:
                print(" [OK] No tiene pedidos asociados.")
            else:
                print(f" [!] ALERTA: Tiene {len(orders)} pedido(s) asociado(s).")
                for o in orders:
                    print(f"   ∟ Pedido ID: {o[0]} | Estado: {o[1]} | Total: {o[2]}")
        except Exception as e:
            print(f" [!] Error query: {str(e)}")
            
    conn.close()

if __name__ == "__main__":
    # INAPYR S.R.L. and INAPYR S. R. L. from previous audit
    ids_to_check = [
        '65ae103173c04371bdf7f4cd5567598e', # RS: INAPYR S.R.L.
        '70ab1441f2b046a09e78edfc7d72dea2'  # RS: INAPYR S. R. L.
    ]
    check_orders(PROD_DB, ids_to_check)
