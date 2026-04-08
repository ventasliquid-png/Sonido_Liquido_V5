import sqlite3
import os

db_path = 'pilot_v5x.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- SCHEMA AUDIT: clientes ---")
cursor.execute("PRAGMA table_info(clientes)")
columns = cursor.fetchall()
found_history = False
for col in columns:
    print(col)
    if col[1] == 'historial_direcciones':
        found_history = True

if found_history:
    print("\n✅ SUCCESS: Column 'historial_direcciones' found.")
else:
    print("\n❌ FAILURE: Column 'historial_direcciones' NOT found.")

print("\n--- CANARY TEST: Lavimar ---")
cursor.execute("SELECT * FROM clientes WHERE razon_social LIKE ?", ('%Lavimar%',))
row = cursor.fetchone()
if row:
    print(f"Record found: {row}")
    # Verify if any column has the value 13
    if 13 in row:
        print("✅ SUCCESS: Canary Value 13 confirmed for Lavimar.")
    else:
        print("❌ FAILURE: Value 13 not found in Lavimar record.")
else:
    print("❌ FAILURE: Lavimar record not found.")

conn.close()
