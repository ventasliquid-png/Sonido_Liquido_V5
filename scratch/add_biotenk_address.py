import sqlite3
import uuid

db_path = r'C:\dev\V5-LS\data\V5_LS_MASTER.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

client_id = '2b9d1fcd21d9453f8c805260fb5c1597'
dom_id = str(uuid.uuid4()).replace('-', '')

# Check if it already has this address
cursor.execute("SELECT id FROM domicilios WHERE cliente_id = ? AND calle LIKE '%Zuviría%'", (client_id,))
if cursor.fetchone():
    print("Biotenk already has Zuviría address.")
else:
    cursor.execute("""
        INSERT INTO domicilios (id, cliente_id, calle, numero, localidad, provincia_id, es_fiscal, es_entrega, activo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (dom_id, client_id, 'Zuviría', '5747', 'CABA', 'C', 1, 1, 1))
    conn.commit()
    print(f"Added address Zuviría 5747 for Biotenk (ID: {dom_id})")

conn.close()
