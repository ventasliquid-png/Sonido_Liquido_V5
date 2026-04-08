import sqlite3

db_path = 'pilot.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Check Columns
cursor.execute("PRAGMA table_info(clientes)")
cols = [c[1] for c in cursor.fetchall()]
print(f"COLUMNS: {cols}")

# 2. Check Flags 13, 15
cursor.execute("SELECT id, razon_social, flags_estado, estado_arca FROM clientes WHERE flags_estado IN (13, 15) LIMIT 5")
results = cursor.fetchall()
print(f"DNA_SAMPLE (13, 15): {results}")

# 3. Count Flag 13
cursor.execute("SELECT COUNT(*) FROM clientes WHERE flags_estado = 13")
count13 = cursor.fetchone()[0]
print(f"COUNT_FLAG_13: {count13}")

conn.close()
