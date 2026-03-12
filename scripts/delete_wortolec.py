import sqlite3
import os

DB_PATH = os.path.abspath("pilot.db")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check for "Wortolec"
    cursor.execute("SELECT id, nombre, apellido FROM contactos WHERE apellido LIKE '%Wortolec%'")
    rows = cursor.fetchall()
    
    if rows:
        print(f"Found {len(rows)} contact(s) to delete.")
        for r in rows:
            print(f"Deleting: {r[1]} {r[2]} (ID: {r[0]})")
            cursor.execute("DELETE FROM contactos WHERE id = ?", (r[0],))
        
        conn.commit()
        print("Deletion successful.")
    else:
        print("No 'Wortolec' found. Already clean.")
        
    conn.close()
except Exception as e:
    print(f"DB Error: {e}")
