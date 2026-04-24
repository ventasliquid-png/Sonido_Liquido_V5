import sqlite3

db_path = r'c:\dev\V5-LS\data\V5_LS_MASTER.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the last remito's domicile
cursor.execute("SELECT id, domicilio_entrega_id FROM remitos ORDER BY fecha_creacion DESC LIMIT 1")
remito_id, dom_id = cursor.fetchone()
print(f"Remito ID: {remito_id}, Domicilio ID: {dom_id}")

# Check that domicile
cursor.execute("SELECT calle, numero, localidad FROM domicilios WHERE id = ?", (dom_id,))
print(f"Domicilio Data: {cursor.fetchone()}")

conn.close()
