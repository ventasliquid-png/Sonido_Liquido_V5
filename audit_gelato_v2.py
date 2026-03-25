import sqlite3
conn = sqlite3.connect('pilot_v5x.db')
cur = conn.cursor()

# Master address ID
master_id = '446075364bea410ea8cf18c0fa9c40ba'

cur.execute("""
    SELECT c.razon_social, dc.flags 
    FROM clientes c 
    JOIN domicilios_clientes dc ON c.id = dc.cliente_id 
    WHERE dc.domicilio_id = ?
""", (master_id,))
print(f"Clients linked to Master Address ({master_id}):")
for r in cur.fetchall():
    print(r)

# Find Poblet ID
cur.execute("SELECT id, razon_social FROM clientes WHERE razon_social LIKE '%Poblet%'")
poblet = cur.fetchone()
print(f"\nPoblet Client: {poblet}")

if poblet:
    # Check if Poblet is linked to master_id
    cur.execute("SELECT flags FROM domicilios_clientes WHERE cliente_id = ? AND domicilio_id = ?", (poblet[0], master_id))
    link = cur.fetchone()
    if link:
        print(f"Poblet is ALREADY linked with flags {link[0]}")
    else:
        print("Poblet is NOT linked to master_id. Linking now...")
        cur.execute("INSERT INTO domicilios_clientes (cliente_id, domicilio_id, flags) VALUES (?, ?, ?)", (poblet[0], master_id, 1))
        conn.commit()
        print("Poblet linked as Fiscal (Bit 0).")

conn.close()
