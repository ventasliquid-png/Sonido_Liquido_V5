import sqlite3

db_path = r'C:\dev\V5-LS\data\V5_LS_MASTER.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, calle FROM domicilios WHERE calle LIKE '%Zuviría%'")
rows = cursor.fetchall()
print(f"Addresses with Zuviría: {rows}")

conn.close()
