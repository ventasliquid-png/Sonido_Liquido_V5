import sqlite3
import os

DB_PATH = os.path.abspath("pilot.db")

print(f"Checking DB at: {DB_PATH}")

if not os.path.exists(DB_PATH):
    print("ERROR: DB file not found!")
    exit(1)

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n--- CONTACTOS ---")
    cursor.execute("SELECT id, nombre, apellido, cliente_id, transporte_id, estado FROM contactos")
    rows = cursor.fetchall()
    
    if not rows:
        print("No contacts found in DB.")
    else:
        for r in rows:
            print(f"ID: {r[0]} | Nombre: {r[1]} {r[2]} | Estado: {r[5]}")
            
    conn.close()
except Exception as e:
    print(f"DB Error: {e}")
    
print("\n--- END ---")
