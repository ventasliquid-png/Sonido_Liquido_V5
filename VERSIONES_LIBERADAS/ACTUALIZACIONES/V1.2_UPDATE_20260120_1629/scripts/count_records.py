import sqlite3
import os

db_path = 'backend/pilot.db'
if not os.path.exists(db_path):
    print(f"ERROR: {db_path} not found")
    exit()

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    clientes = cursor.execute("SELECT count(*) FROM clientes WHERE activo=1").fetchone()[0]
    productos = cursor.execute("SELECT count(*) FROM productos WHERE activo=1").fetchone()[0]
    pedidos = cursor.execute("SELECT count(*) FROM pedidos").fetchone()[0]
    
    print(f"Clientes: {clientes}")
    print(f"Productos: {productos}")
    print(f"Pedidos: {pedidos}")

except Exception as e:
    print(f"Database Error: {e}")
