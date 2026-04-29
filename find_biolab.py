import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT id, razon_social FROM clientes WHERE razon_social LIKE '%BIO-LAB%'")
for row in cursor.fetchall():
    print(row)
conn.close()
