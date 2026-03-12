import sqlite3

def check():
    conn = sqlite3.connect("pilot.db")
    cursor = conn.cursor()
    
    print("\n--- CLIENTES (Paola) ---")
    cursor.execute("SELECT id, razon_social FROM clientes WHERE razon_social LIKE '%Paola%'")
    clients = cursor.fetchall()
    for c in clients:
        print(f"ID: '{c[0]}' Type: {type(c[0])} Name: {c[1]}")
        
    print("\n--- PEDIDOS (Last 5) ---")
    cursor.execute("SELECT id, cliente_id, total FROM pedidos ORDER BY id DESC LIMIT 5")
    orders = cursor.fetchall()
    for o in orders:
        print(f"Order: {o[0]} | Client_Ref: '{o[1]}' Type: {type(o[1])} | Total: {o[2]}")

    conn.close()

if __name__ == "__main__":
    check()
