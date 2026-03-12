import sqlite3
import os

db_path = 'c:\\dev\\Sonido_Liquido_V5\\pilot.db'

def get_count(table):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print(f"Clientes: {get_count('clientes')}")
    print(f"Productos: {get_count('productos')}")
    print(f"Pedidos: {get_count('pedidos')}")
