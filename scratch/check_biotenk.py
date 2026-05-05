import sqlite3

db_path = r'C:\dev\V5-LS\data\V5_LS_MASTER.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, razon_social, cuit FROM clientes WHERE razon_social LIKE '%BIOTENK%'")
client = cursor.fetchone()
print(f"Client: {client}")

if client:
    # Check addresses
    cursor.execute("SELECT id, calle, localidad, es_fiscal FROM domicilios WHERE cliente_id = ?", (client[0],))
    addresses = cursor.fetchall()
    print(f"Addresses: {addresses}")

conn.close()
