import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT id, razon_social FROM clientes WHERE id = '2fbeb6ebffc649ff81d1e324f410eed6'")
row = cursor.fetchone()
print(row)
conn.close()
