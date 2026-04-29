import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT id, razon_social FROM clientes WHERE razon_social LIKE '%GELATO%'")
clients = cursor.fetchall()
for c in clients:
    print(f"Cliente: {c[1]} (ID: {c[0]})")
    cursor.execute("SELECT d.id, d.calle, d.numero, d.es_entrega, d.es_fiscal FROM domicilios d JOIN vinculos_geograficos v ON d.id = v.domicilio_id WHERE v.entidad_id = ?", (c[0],))
    doms = cursor.fetchall()
    for d in doms:
        print(f"  - Domicilio: {d[1]} {d[2]} | Entrega: {d[3]} | Fiscal: {d[4]}")
conn.close()
