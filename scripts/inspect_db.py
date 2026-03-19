import sqlite3
db_path = 'pilot_v5x.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("PRAGMA table_info(clientes)")
for col in cur.fetchall():
    print(col)
conn.close()
