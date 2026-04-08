import sqlite3
conn = sqlite3.connect('pilot_v5x.db')
cur = conn.cursor()
search = 'Ruta provincial 36'
cur.execute("SELECT id, calle, numero, alias FROM domicilios WHERE calle LIKE ?", (f'%{search}%',))
results = cur.fetchall()
print(f"Results for '{search}':")
for r in results:
    print(r)

# Check Gelato specifically
gelato_id = '2fbeb6ebffc649ff81d1e324f410eed6'
cur.execute("SELECT d.id, d.calle, dc.flags FROM domicilios d JOIN domicilios_clientes dc ON d.id = dc.domicilio_id WHERE dc.cliente_id = ?", (gelato_id,))
print(f"\nAddresses linked to Gelato:")
for r in cur.fetchall():
    print(r)

conn.close()
