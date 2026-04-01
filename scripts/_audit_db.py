import sqlite3
DB = r'C:\dev\Sonido_Liquido_V5\pilot_v5x.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print("TABLAS:", [r[0] for r in cur.fetchall()])
cur.execute("PRAGMA table_info(clientes)")
print("COLS clientes:", [r[1] for r in cur.fetchall()])
cur.execute("SELECT COUNT(*) FROM clientes")
print("COUNT clientes:", cur.fetchone()[0])
conn.close()
