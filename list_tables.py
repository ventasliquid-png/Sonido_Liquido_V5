import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [r[0] for r in cursor.fetchall()])
conn.close()
