
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "pilot.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. Delete Issuer CUIT
c.execute("DELETE FROM clientes WHERE cuit = '30-71560397-3' OR cuit = '30715603973'")
deleted_issuer = c.rowcount

# 2. Delete Temp CUITs
c.execute("DELETE FROM clientes WHERE cuit LIKE '99-%-9'")
deleted_temp = c.rowcount

conn.commit()
conn.close()

print(f"Deleted {deleted_issuer} issuer records.")
print(f"Deleted {deleted_temp} temp records.")
