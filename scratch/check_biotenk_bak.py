import sqlite3

db_path = r'c:\dev\V5-LS\POLIZON_MAESTRO.bak'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id FROM clientes WHERE razon_social LIKE '%BIOTENK%'")
res = cursor.fetchone()
if res:
    client_id = res[0]
    cursor.execute("SELECT calle, numero, localidad FROM domicilios WHERE cliente_id = ?", (client_id,))
    addresses = cursor.fetchall()
    print(f"Biotenk Addresses in BAK: {addresses}")
else:
    print("Biotenk not found in BAK")

conn.close()
