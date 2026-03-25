import sqlite3
conn = sqlite3.connect('pilot_v5x.db')
cur = conn.cursor()

# Master address ID
master_id = '446075364bea410ea8cf18c0fa9c40ba'

# 1. Update GELATO SA
cur.execute("UPDATE domicilios_clientes SET flags = flags | 1 WHERE cliente_id = '2fbeb6ebffc649ff81d1e324f410eed6' AND domicilio_id = ?", (master_id,))
print(f"Gelato: {cur.rowcount} link updated with Fiscal bit.")

# 2. Update Poblet
# Find Poblet ID first
cur.execute("SELECT id FROM clientes WHERE razon_social LIKE '%Poblet%'")
poblet_id = cur.fetchone()[0]
cur.execute("UPDATE domicilios_clientes SET flags = flags | 1 WHERE cliente_id = ? AND domicilio_id = ?", (poblet_id, master_id))
print(f"Poblet: {cur.rowcount} link updated with Fiscal bit.")

conn.commit()
conn.close()
