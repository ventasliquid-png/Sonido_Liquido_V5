
import sqlite3

def check_segments():
    conn = sqlite3.connect('pilot.db')
    cursor = conn.cursor()
    
    print("--- SEGMENTOS EN DB ---")
    cursor.execute("SELECT id, nombre FROM segmentos")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]} | Nombre: {row[1]}")
    print(f"Total: {len(rows)}")
    
    conn.close()

if __name__ == "__main__":
    check_segments()
