import sqlite3

DB_PATH = 'pilot_v5x.db'

def inspect_zombies():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Auditoría de Datos ---")
    
    # Clientes
    cursor.execute("SELECT count(*) FROM clientes")
    count = cursor.fetchone()[0]
    print(f"Total Clientes: {count}")
    
    # Pedidos
    cursor.execute("SELECT count(*) FROM pedidos")
    count = cursor.fetchone()[0]
    print(f"Total Pedidos: {count}")
    
    # Productos
    cursor.execute("SELECT count(*) FROM productos")
    count = cursor.fetchone()[0]
    print(f"Total Productos: {count}")

    print("\n--- Analizando Clientes ---")
    cursor.execute("SELECT id, razon_social, flags_estado FROM clientes LIMIT 20")
    for row in cursor.fetchall():
        print(f" - {row[1]} (Flags: {row[2]})")

    conn.close()

if __name__ == "__main__":
    inspect_zombies()
