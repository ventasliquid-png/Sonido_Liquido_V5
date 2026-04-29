import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT id, numero_legal FROM remitos ORDER BY id DESC LIMIT 5")
print("Remitos:", cursor.fetchall())
conn.close()
