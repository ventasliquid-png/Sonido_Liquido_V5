import sqlite3
conn = sqlite3.connect('pilot_v5x.db')
cur = conn.cursor()

# 1. Identify the two addresses
# Addr 1: 446075364bea410ea8cf18c0fa9c40ba ('Ruta provincial 36 y 630,')
# Addr 2: a6c0a6b023d64d14832eab58ad72d39d ('RUTA PROVINCIAL 36 Y CALLE 630')

# 2. Merge links from Addr 2 to Addr 1
cur.execute("UPDATE domicilios_clientes SET domicilio_id = '446075364bea410ea8cf18c0fa9c40ba' WHERE domicilio_id = 'a6c0a6b023d64d14832eab58ad72d39d'")
print(f"Merged {cur.rowcount} links from 'RUTA PROVINCIAL 36 Y CALLE 630' to 'Ruta provincial 36 y 630,'.")

# 3. Delete the duplicate address
cur.execute("DELETE FROM domicilios WHERE id = 'a6c0a6b023d64d14832eab58ad72d39d'")
print(f"Deleted duplicate address record.")

# 4. Clean up the label for Addr 1
cur.execute("UPDATE domicilios SET calle = 'Ruta Provincial 36 y 630', alias = 'POBLET / GELATO' WHERE id = '446075364bea410ea8cf18c0fa9c40ba'")
print(f"Cleaned up label and alias for the master record.")

conn.commit()
conn.close()
