import sqlite3
db_path = 'pilot_v5x.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM clientes WHERE id = 'e1be0585cd3443efa33204d00e199c4e' OR id = 'e1be0585-cd34-43ef-a332-04d00e199c4e'")
row = cur.fetchone()
if row:
    print(dict(row))
else:
    print("NOT_FOUND")
conn.close()
