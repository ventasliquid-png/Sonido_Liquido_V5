import sqlite3
try:
    conn = sqlite3.connect('pilot.db')
    cursor = conn.cursor()
    clients = cursor.execute('SELECT count(*) FROM clientes').fetchone()[0]
    orders = cursor.execute('SELECT count(*) FROM pedidos').fetchone()[0]
    print(f"CLIENTS={clients}")
    print(f"ORDERS={orders}")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    if 'conn' in locals(): conn.close()
